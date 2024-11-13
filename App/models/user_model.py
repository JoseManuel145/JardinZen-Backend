import enum
from sqlalchemy import Column, Integer, String, Enum
from database.database import Base
from typing import Optional, Dict, Any

class RolEnum(enum.Enum):
    usuario = "usuario"
    gestor_vivero = "gestor_vivero"
    administrador = "administrador"


class Users(Base):
    __tablename__ = "Usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    ubication: Optional[Dict[str, Any]]
    img = Column(String, nullable=True) #se guardara solo el path
    rol = Column(Enum(RolEnum), nullable=False)

