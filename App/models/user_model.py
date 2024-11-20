from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, MappedColumn
from database.database import Base
from models.user_plant_model import UserPlant
from enum import Enum

class Role(Enum):
    usuario = 'usuario'
    gestor_vivero = 'gestor_vivero'
    administrador = 'administrador'

class User(Base):
    __tablename__ = "Users"
    
    id_user = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    ubication = Column(JSONB)
    img = Column(LargeBinary, nullable=True)
    role: Mapped[Role] = MappedColumn(SQLAlchemyEnum(Role), nullable=False)

    plants = relationship("UserPlant", back_populates="user")

    nurseries = relationship('Nursery', back_populates='manager')
