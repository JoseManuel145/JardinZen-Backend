from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, JSON, LargeBinary
from sqlalchemy.orm import relationship
from database.database import Base
from models.user_plant_model import UserPlant
from enum import Enum 

class Role(Enum):
    user = 'usuario'
    nursery_manager = 'gestor_vivero'
    admin = 'administrador'

class User(Base):
    __tablename__ = "Users"
    
    id_user = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    ubication = Column(JSON)
    img = Column(LargeBinary)
    # Uso correcto del Enum de SQLAlchemy
    role = Column(SQLAlchemyEnum(Role), nullable=False)

    plants = relationship("UserPlant", back_populates="user")
