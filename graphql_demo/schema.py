import strawberry
from typing import AsyncGenerator, Optional

from .database import SessionLocal
from .models import ProductDB


async def get_context() -> AsyncGenerator[dict, None]:
    db = SessionLocal()
    try:
        yield {"db": db}
    finally:
        db.close()


@strawberry.type
class Product:
    id: int
    name: str
    description: str
    price: float

    @classmethod
    def from_db(cls, product: ProductDB) -> "Product":
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
        )


@strawberry.type
class Query:
    @strawberry.field
    def products(self, info: strawberry.types.Info) -> list[Product]:
        db = info.context["db"]
        return [Product.from_db(p) for p in db.query(ProductDB).all()]

    @strawberry.field
    def product(self, info: strawberry.types.Info, id: int) -> Optional[Product]:
        db = info.context["db"]
        product = db.query(ProductDB).filter(ProductDB.id == id).first()
        return Product.from_db(product) if product else None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(
        self,
        info: strawberry.types.Info,
        name: str,
        description: str,
        price: float,
    ) -> Product:
        db = info.context["db"]
        db_product = ProductDB(name=name, description=description, price=price)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return Product.from_db(db_product)

    @strawberry.mutation
    def update_product(
        self,
        info: strawberry.types.Info,
        id: int,
        name: str,
        description: str,
        price: float,
    ) -> Optional[Product]:
        db = info.context["db"]
        db_product = db.query(ProductDB).filter(ProductDB.id == id).first()
        if db_product is None:
            return None
        db_product.name = name
        db_product.description = description
        db_product.price = price
        db.commit()
        db.refresh(db_product)
        return Product.from_db(db_product)

    @strawberry.mutation
    def delete_product(self, info: strawberry.types.Info, id: int) -> bool:
        db = info.context["db"]
        db_product = db.query(ProductDB).filter(ProductDB.id == id).first()
        if db_product is None:
            return False
        db.delete(db_product)
        db.commit()
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
