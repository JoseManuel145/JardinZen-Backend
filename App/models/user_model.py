# user_model.py
from sqlalchemy import Column, Integer, String, Enum, JSON, LargeBinary
from sqlalchemy.orm import relationship
from database.database import Base
from models.user_plant_model import UserPlant

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
    role = Column(Enum(Role), nullable=False)

    plants = relationship("UserPlant", back_populates="user")
