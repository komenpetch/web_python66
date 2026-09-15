from pydantic import BaseModel


# Category
class Category(BaseModel):
    name: str

class CategoryCreate(Category):
    pass

class CategoryUpdate(Category):
    pass

class CategoryResponse(Category):
    id: int
    class Config:
        from_attributes = True


# Product
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float

class ProductCreate(Product):
    pass

class ProductResponse(Product):
    id: int
    categories: list[CategoryResponse] = []
    class Config:
        from_attributes = True


# User
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True