from sqlalchemy import Column, LargeBinary
from database.database import Base

class Product(Base):
    __tablename__ = "photos"
    
    photo = Column(LargeBinary) 
