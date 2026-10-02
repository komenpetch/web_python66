import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import CategoryDB, ProductDB

router = APIRouter()

HELP_TEXT = (
    "I can help you with:\n"
    "- list: show all products\n"
    "- product <id or name>: show product details\n"
    "- price <name>: show a product's price\n"
    "- search <keyword>: find products by name or description\n"
    "- categories: show all categories\n"
    "- category <name>: show products in a category\n"
    "- cheapest / most expensive\n"
    "- count: number of products"
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        # copy the list so a dead connection can be removed while looping
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


def format_price(price: float) -> str:
    return f"${price:,.2f}"


def format_product(product: ProductDB) -> str:
    categories = ", ".join(c.name for c in product.categories) or "None"
    return (
        f"#{product.id} {product.name} - {format_price(product.price)}\n"
        f"{product.description}\n"
        f"Categories: {categories}"
    )


def format_product_list(products: list[ProductDB]) -> str:
    return "\n".join(
        f"#{p.id} {p.name} - {format_price(p.price)}" for p in products
    )


def find_product(db: Session, query: str) -> ProductDB | None:
    if query.isdigit():
        return db.query(ProductDB).filter(ProductDB.id == int(query)).first()
    return db.query(ProductDB).filter(ProductDB.name.ilike(query)).first() or (
        db.query(ProductDB).filter(ProductDB.name.ilike(f"%{query}%")).first()
    )


def bot_reply(db: Session, message: str) -> str:
    text = message.strip()
    lower = text.lower()

    if not text:
        return "Please type something. Type 'help' to see what I can do."

    if lower in ("hi", "hello", "hey", "sawasdee", "สวัสดี"):
        return "Hello! I'm the product bot. Type 'help' to see what I can do."

    if lower in ("help", "?"):
        return HELP_TEXT

    if lower in ("list", "products", "all products"):
        products = db.query(ProductDB).order_by(ProductDB.id).all()
        if not products:
            return "There are no products yet."
        return "Here are all products:\n" + format_product_list(products)

    if lower == "count":
        return f"There are {db.query(ProductDB).count()} products."

    if lower == "cheapest":
        product = db.query(ProductDB).order_by(ProductDB.price.asc()).first()
        if product is None:
            return "There are no products yet."
        return "The cheapest product is:\n" + format_product(product)

    if lower in ("most expensive", "expensive"):
        product = db.query(ProductDB).order_by(ProductDB.price.desc()).first()
        if product is None:
            return "There are no products yet."
        return "The most expensive product is:\n" + format_product(product)

    if lower == "categories":
        categories = db.query(CategoryDB).order_by(CategoryDB.name).all()
        if not categories:
            return "There are no categories yet."
        return "Categories:\n" + "\n".join(
            f"- {c.name} ({len(c.products)} products)" for c in categories
        )

    command, _, argument = text.partition(" ")
    command = command.lower()
    argument = argument.strip()

    if command == "price":
        if argument.lower().startswith("of "):
            argument = argument[3:].strip()
        if not argument:
            return "Which product? Example: price Laptop"
        product = find_product(db, argument)
        if product is None:
            return f"I couldn't find a product called '{argument}'."
        return f"{product.name} costs {format_price(product.price)}."

    if command == "product":
        if not argument:
            return "Which product? Example: product 1 or product Laptop"
        product = find_product(db, argument)
        if product is None:
            return f"I couldn't find product '{argument}'."
        return format_product(product)

    if command == "search":
        if not argument:
            return "What should I search for? Example: search phone"
        pattern = f"%{argument}%"
        products = (
            db.query(ProductDB)
            .filter(ProductDB.name.ilike(pattern) | ProductDB.description.ilike(pattern))
            .order_by(ProductDB.id)
            .all()
        )
        if not products:
            return f"No products match '{argument}'."
        return f"Found {len(products)} product(s):\n" + format_product_list(products)

    if command == "category":
        if not argument:
            return "Which category? Example: category Electronics"
        category = (
            db.query(CategoryDB).filter(CategoryDB.name.ilike(argument)).first()
        )
        if category is None:
            return f"I couldn't find category '{argument}'. Type 'categories' to see them all."
        if not category.products:
            return f"Category '{category.name}' has no products."
        return f"Products in {category.name}:\n" + format_product_list(category.products)

    return "Sorry, I don't understand that. Type 'help' to see what I can do."


@router.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.send(websocket, {
        "type": "bot",
        "text": "Hi! I'm the product bot. Type 'help' to see what I can do.",
    })
    try:
        while True:
            raw = await websocket.receive_text()
            # accept {"text": "..."} JSON from the frontend, or plain text (e.g. Postman)
            try:
                data = json.loads(raw)
                message = str(data.get("text", "")) if isinstance(data, dict) else raw
            except json.JSONDecodeError:
                message = raw

            db = SessionLocal()
            try:
                reply = bot_reply(db, message)
            finally:
                db.close()

            await manager.send(websocket, {"type": "bot", "text": reply})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_product_event(event: str, product: ProductDB):
    messages = {
        "PRODUCT_CREATED": f"New product added: {product.name} ({format_price(product.price)})",
        "PRODUCT_UPDATED": f"Product updated: {product.name} is now {format_price(product.price)}",
        "PRODUCT_DELETED": f"Product removed: {product.name}",
    }
    await manager.broadcast({
        "type": "event",
        "event": event,
        "product_id": product.id,
        "product_name": product.name,
        "product_price": product.price,
        "text": messages[event],
    })
