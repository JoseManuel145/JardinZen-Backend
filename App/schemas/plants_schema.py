from enum import Enum
from pydantic import BaseModel
from typing import Optional


class Category_Plant(str, Enum):
    categoriaA = "planta_interior"
    categoriaB = "arbol_fruta"


class Type_Plant(str, Enum):
    arbusto = "arbusto"
    flor = "flor"
    arbol = "arbol"


class Info(BaseModel):
    name: str
    description: str


class PlantBase(BaseModel):
    info: Info
    hora_de_riego: str
    category: Category_Plant
    tipo: Type_Plant

    class Config:
        from_attributes = True


class PlantRequest(PlantBase):
    id_user: int


class PlantResponse(PlantBase):
    id_plant: int

    class Config:
        from_attributes = True
