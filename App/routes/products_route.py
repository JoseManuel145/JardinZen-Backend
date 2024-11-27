from fastapi import APIRouter, Form, status, HTTPException, Depends, UploadFile, File
from typing import List
from schemas.product_schema import ProductBase, ProductResponse
from models.product_model import Product
from models.user_model import User, Role
from database.database import Base, engine, get_db, get_mongo_db
from sqlalchemy.orm import Session
from utils.security import verify_user, get_current_user
import uuid
import os

route = APIRouter()

Base.metadata.create_all(bind=engine)

IMAGEDIR = "media/"
os.makedirs(IMAGEDIR, exist_ok=True)  

@route.get('/products/', status_code=status.HTTP_200_OK, response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@route.get('/{id_user}/products/{id_product}', status_code=status.HTTP_200_OK, response_model=ProductResponse)
async def get_product(id_user: int, id_product: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    product = db.query(Product).filter(Product.id_product == id_product).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@route.post('/{id_user}/products/', status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
async def create_product(
    id_user: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    img: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db)
):
    verify_user(id_user, db, current_user)

    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None or user.role != Role.administrador:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    img_path = None
    if img:
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(IMAGEDIR, filename)
        with open(filepath, "wb") as f:
            f.write(await img.read())
        img_path = filepath

        # Registrar la imagen en MongoDB
        mongo_db["photos"].insert_one({"name": name, "img_path": img_path})

    product = Product(name=name, description=description, price=price, stock=stock, img=img_path)
    db.add(product)
    db.commit()
    db.refresh(product)

    return product

@route.delete('/{id_user}/products/{id_product}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id_user: int, id_product: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    verify_user(id_user, db, current_user)
    
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    product = db.query(Product).filter(Product.id_product == id_product).first()
    if user.role != Role.administrador:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have")
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}