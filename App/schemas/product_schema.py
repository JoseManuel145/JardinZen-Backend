from typing import Optional
from pydantic import BaseModel
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int

class ProductResponse(ProductBase):
    id_product: int

    class Config:
        orm_mode = True