from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from database.database import Base
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


class Plant(Base):
    __tablename__ = "Plants"

    id_plant = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    hora_de_riego = Column(String, nullable=False)
    category = Column(SQLAlchemyEnum(CategoryPlant), nullable=False)
    tipo = Column(SQLAlchemyEnum(TypePlant), nullable=False)
    img = Column(String, nullable=True)

    users = relationship("UserPlant", back_populates="plant")
