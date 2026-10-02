from typing import List

from fastapi import FastAPI, HTTPException, WebSocketDisconnect, status, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# @app.get("/")
# async def home():
#     return {"message": "Hello, World!"}

class Product(BaseModel):
    id: int
    name: str
    stock: int
    
products: List[Product] = [
    Product(id=1, name="Laptop", stock=10),
    Product(id=2, name="Mouse", stock=20)
]

@app.get("/products")
async def get_all_products():
    return products

html_code = """
<pre id = "output"></pre>

<script>
async function load() {
    const res = await fetch("/products");
    document.getElementById("output").textContent = JSON.stringify(await res.json(), null, 2);
}

load();

const ws = new WebSocket("ws://localhost:8000/ws/products");
ws.onmessage = () => load();

</script>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return html_code

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)
manager = ConnectionManager()

@app.websocket("/ws/products")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/products",response_model=Product)
async def create_product(product: Product):
    for p in products:
        if p.id == product.id:
            raise HTTPException(status_code=400, detail= f"Product with this ID already exists")
    products.append(product)
    
    await manager.broadcast(
        {
            "event": "PRODUCT_CREATED",
            "product_id": product.id,
            "product_name": product.name,
            "product_stock": product.stock
        }
    )
    
    return product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    for index, product in enumerate(products):
        if product.id == product_id:
            deleted = products.pop(index)
            
            await manager.broadcast(
                {
                    "event": "PRODUCT_DELETED",
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_stock": product.stock
                }
            )
            
            return {"message": "Deleted Product successfully", "data": deleted}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, updated_product: Product):
    if updated_product.id != product_id:
        raise HTTPException(status_code=400, detail="Path id and body id must match")
    for index, product in enumerate(products):
        if product.id == product_id:
            products[index] = updated_product


            await manager.broadcast(
                {
                    "event": "STOCK_UPDATED",
                    "product_id": product_id,
                    "product_name": updated_product.name,
                    "new_stock": updated_product.stock,
                }
            )


            return updated_product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
