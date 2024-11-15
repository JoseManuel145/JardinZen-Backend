from sqlalchemy import Column, Integer, String, Enum, LargeBinary
from sqlalchemy.orm import composite, relationship
from database.database import Base
from enum import Enum

class Category_Plant(Enum):
    categoriaA = "planta_interior"
    categoriaB = "arbol_fruta"

class Type_Plant(Enum):
    arbusto = "arbusto"
    flor = "flor"
    arbol = "arbol"

class Info:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __composite_values__(self):
        return self.name, self.description

    name = Column(String, nullable=False)
    description = Column(String)

class Plant(Base):
    __tablename__ = "Plants"

    id_plant = Column(Integer, primary_key=True, autoincrement=True)
    info = composite(Info, Column("name", String), Column("description", String))
    hora_de_riego = Column(String, nullable=False)
    category = Column(Enum(Category_Plant), nullable=False)
    tipo = Column(Enum(Type_Plant), nullable=False)
    img = Column(LargeBinary, nullable=True)
    
    users = relationship("UserPlant", back_populates="plant")

