from pydantic import BaseModel, Field


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
    quantity: int = Field(default=0, ge=0)

class ProductCreate(Product):
    pass

class ProductResponse(Product):
    id: int
    image_url: str | None = None
    categories: list[CategoryResponse] = []
    class Config:
        from_attributes = True


# Reservation
class ReservationCreate(BaseModel):
    amount: int = Field(gt=0)

class Confirmation(BaseModel):
    reservation_token: str = Field(min_length=1, max_length=100)


# User
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True