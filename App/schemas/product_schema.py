from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    photo: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Laptop",
                "price": 1000.00,
                "photo": "https://example.com/laptop.jpg"
            }
        }
