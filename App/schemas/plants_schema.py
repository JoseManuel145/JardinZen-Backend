from pydantic import BaseModel
from enum import Enum


class CategoryPlant(str, Enum):
    Interior = "Interior"
    Exterior = "Exterior"
    Ornamental = "Ornamental"


class TypePlant(str, Enum):
    Cactus = "Cactus"
    Suculenta = "Suculenta"
    Arbusto = "Arbusto"
    Otro = "Otro"


class PlantBase(BaseModel):
    name: str
    description: str
    hora_de_riego: str
    category: CategoryPlant
    tipo: TypePlant
    img: str
    class Config:
        from_attributes = True


class PlantResponse(PlantBase):
    id_plant: int

    class Config:
        from_attributes = True


class PlantRequest(PlantBase):
    pass
