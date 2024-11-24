from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime
from models.product_model import Product

class ShoppingCart(Base):
    __tablename__ = "ShoppingCarts"
    
    id_cart = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("Users.id_user"), nullable=False)
    
    # Relación con el usuario
    user = relationship("User", back_populates="shopping_cart")
    
    # Relación con los productos en el carrito (a través de una tabla intermedia)
    products = relationship("CartProduct", back_populates="cart")
    

class CartProduct(Base):
    __tablename__ = "CartProducts"
    
    id_cart_product = Column(Integer, primary_key=True, autoincrement=True)
    id_cart = Column(Integer, ForeignKey("ShoppingCarts.id_cart"), nullable=False)
    id_product = Column(Integer, ForeignKey("Products.id_product"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Relación con ShoppingCart
    cart = relationship("ShoppingCart", back_populates="products")
    
    # Relación con Product
    product = relationship("Product", back_populates="carts")
