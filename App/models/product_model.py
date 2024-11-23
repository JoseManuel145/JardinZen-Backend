from sqlalchemy import Column, Integer, String, LargeBinary
from database.database import Base

class Product(Base):
    __tablename__ = "productoss"

    id_product = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    img = Column(LargeBinary, nullable=False)
