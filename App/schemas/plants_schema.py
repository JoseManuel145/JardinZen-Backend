from enum import Enum
from pydantic import BaseModel
from typing import Optional


class CategoryPlantEnum(str, Enum):
    categoriaA = "planta_interior"
    categoriaB = "arbol_fruta"


class TypePlantEnum(str, Enum):
    arbusto = "arbusto"
    flor = "flor"
    arbol = "arbol"


class Info(BaseModel):
    name: str
    description: str


class PlantBase(BaseModel):
    info: Info
    hora_de_riego: str
    category: CategoryPlantEnum
    tipo: TypePlantEnum
    img: Optional[str] = None

    class Config:
        orm_mode = True


class PlantRequest(PlantBase):
    id_user: int


class PlantResponse(PlantBase):
    id_plant: int

    class Config:
        orm_mode = True
