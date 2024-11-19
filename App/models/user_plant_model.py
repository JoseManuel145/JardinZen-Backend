#user_plant_model
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class UserPlant(Base):
    __tablename__ = "User_Plant"

    id_user = Column(Integer, ForeignKey("Users.id_user"), primary_key=True)
    id_plant = Column(Integer, ForeignKey("Plants.id_plant"), primary_key=True)

    user = relationship("User", back_populates="plants")
    plant = relationship("Plant", back_populates="users")
