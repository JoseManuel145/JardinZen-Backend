from typing import Optional
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: int
    quantity: int
    description: Optional[str] = None

    class Config:
        orm_mode = True

class ProductResponse(Product):
    id_product: int
    
    class Config:
        orm_mode = True