from pydantic import BaseModel
from enum import Enum


class CategoryPlant(str, Enum):
    planta_interior = "planta_interior"
    arbol_fruta = "arbol_fruta"


class TypePlant(str, Enum):
    arbusto = "arbusto"
    flor = "flor"
    arbol = "arbol"


class PlantBase(BaseModel):
    name: str
    description: str
    hora_de_riego: str
    category: CategoryPlant
    tipo: TypePlant

    class Config:
        orm_mode = True


class PlantResponse(PlantBase):
    id_plant: int

    class Config:
        orm_mode = True


class PlantRequest(PlantBase):
    pass
