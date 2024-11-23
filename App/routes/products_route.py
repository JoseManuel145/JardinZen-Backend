from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from models.user_model import User, Role
from models.product_model import Product
from middlewares.auth_middleware import get_current_user
from database.database import Base, engine, get_db
from utils.security import verify_user
from schemas.product_schema import ProductResponse
import logging

logger = logging.getLogger(__name__)


route = APIRouter()
Base.metadata.create_all(bind=engine)


@route.post("/{id_user}/products/create", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
async def create_product(
    id_user: int,
    name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    
    verify_user(id_user, db, current_user)

    user = db.query(User).filter(User.id_user == id_user).first()
    
    if user.role != Role.administrador:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to create products")
        
    
    image_data = await file.read() if file else ""
    print(f"Creating product for user {id_user} with data: {name}, {price}, {quantity}")

    if description is None:
        description = ""

    new_product = Product(
        name=name,
        price=price,
        quantity=quantity,
        description=description,
        img=image_data
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@route.get("/products", status_code=status.HTTP_200_OK, response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


# Endpoint para obtener un producto por su ID
@route.get("/products/{id_product}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
async def get_product(id_product: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id_product == id_product).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {id_product} not found"
        )
    return product


# Endpoint para eliminar un producto
@route.delete("/{id_user}/products/{id_product}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id_user: int,
    id_product: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_user(id_user, db, current_user)

    user = db.query(User).filter(User.id_user == id_user).first()
    
    if user.role != Role.administrador:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this product")
    
    product = db.query(Product).filter(
        Product.id_product == id_product).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
