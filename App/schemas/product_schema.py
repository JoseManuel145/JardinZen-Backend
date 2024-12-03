from typing import Optional
from pydantic import BaseModel
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    img : str

class ProductResponse(BaseModel):
    id_product: int
    name: str
    description: str
    price: float
    stock: int
    img: str

    class Config:
        from_attributes = True
