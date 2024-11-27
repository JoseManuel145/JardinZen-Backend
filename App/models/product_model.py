from sqlalchemy import Column, Integer, String, DECIMAL, LargeBinary
from sqlalchemy.orm import relationship
from database.database import Base

class Product(Base):
    __tablename__ = "Products"
    
    id_product = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    img = Column(String, nullable=True)

    carts = relationship("CartProduct", back_populates="product")
    
    #order_products = relationship("OrderProduct", back_populates="product")
