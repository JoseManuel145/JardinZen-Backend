from pydantic import BaseModel
from typing import List


class CartProductResponse(BaseModel):
    id_product: int
    quantity: int

    class Config:
        orm_mode = True


class ShoppingCartResponse(BaseModel):
    id_cart: int 
    products: List[CartProductResponse] = []

    class Config:
        orm_mode = True