
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


sqlite_file_name = "product_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=False)
    price = Column(Float, index=False)
    
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    
class ProductCreate(Product):
    pass

class ProductResponse(Product):
    id: int
    class Config:
        from_attributes = True
        
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/products",response_model=Product,status_code=status.HTTP_201_CREATED,)
async def create_product(
    product: Product,
    db: Session = Depends(get_db),
):
    existing_product = (
        db.query(ProductDB)
        .filter(ProductDB.id == product.id)
        .first()
    )

    if existing_product is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with id {product.id} already exists",
        )

    db_product = ProductDB(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

@app.get("/products", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(ProductDB).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.delete("/products/{product_id}", response_model=ProductResponse)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)