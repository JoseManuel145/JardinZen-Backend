from pydantic import BaseModel
from typing import List

class CartProductCreate(BaseModel):
    product_id: int
    quantity: int

class ShoppingCartAddProducts(BaseModel):
    user_id: int

    products: List[CartProductCreate]

    class Config:
        orm_mode = True

class CartProductResponse(BaseModel):
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class ShoppingCartResponse(BaseModel):
    id_cart: int
    user_id: int
    products: List[CartProductResponse] = []

    class Config:
        orm_mode = True
