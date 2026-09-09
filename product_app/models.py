from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base

# association table
product_categories = Table(
    "product_category",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=False)
    price = Column(Float, index=False)

    categories = relationship(
        "CategoryDB", secondary=product_categories,
        back_populates="products"
    )


class CategoryDB(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    products = relationship(
        "ProductDB", secondary=product_categories,
        back_populates="categories"
    )