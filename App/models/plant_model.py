from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from database.database import Base
from enum import Enum


class CategoryPlant(str, Enum):
    planta_interior = "planta_interior"
    arbol_fruta = "arbol_fruta"


class TypePlant(str, Enum):
    arbusto = "arbusto"
    flor = "flor"
    arbol = "arbol"


class Plant(Base):
    __tablename__ = "Plants"

    id_plant = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    hora_de_riego = Column(String, nullable=False)
    category = Column(SQLAlchemyEnum(CategoryPlant), nullable=False)
    tipo = Column(SQLAlchemyEnum(TypePlant), nullable=False)
    img = Column(LargeBinary, nullable=True)

    users = relationship("UserPlant", back_populates="plant")
