from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, status, Form
from sqlalchemy.orm import Session
from pymongo.collection import Collection
from bson import ObjectId
from gridfs import GridFS
from database.database import get_mongo_db, get_db
from fastapi.responses import StreamingResponse
from models.user_model import User, Role
from utils.security import get_current_user, verify_user

route = APIRouter()


# Crear productos en MongoDB (con imagen)
@route.post("/products/{id_user}", response_model=dict)
async def create_product_in_mongodb(
    id_user: int,
    name: str,
    price: float,
    file: UploadFile = File(...),
    mongo_db: Collection = Depends(get_mongo_db),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_user(id_user, db, user)
    
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user.role != Role.administrador:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado")

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato no permitido. Solo JPEG o PNG.")

    file_data = await file.read()

    fs = GridFS(mongo_db)
    image_id = fs.put(file_data, filename=file.filename, content_type=file.content_type)

    product_dict = {
        "name": name,
        "price": price,
        "image_id": image_id
    }

    result = mongo_db["products"].insert_one(product_dict)
    created_product = mongo_db["products"].find_one({"_id": result.inserted_id})
    if not created_product:
        raise HTTPException(status_code=500, detail="Failed to create product in MongoDB")
    
    created_product["_id"] = str(created_product["_id"])
    created_product["image_id"] = str(created_product["image_id"])
    return created_product


@route.get("/products", response_model=list[dict])
def get_products(mongo_db: Collection = Depends(get_mongo_db)):
    products = list(mongo_db["products"].find())
    for product in products:
        product["_id"] = str(product["_id"])
        product["image_id"] = str(product["image_id"])
    return products


@route.get("/products/image/{image_id}")
def get_image_from_gridfs(image_id: str, mongo_db: Collection = Depends(get_mongo_db)):
    try:
        fs = GridFS(mongo_db)
        file = fs.get(ObjectId(image_id))
        return StreamingResponse(file, media_type=file.content_type)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")


@route.delete("/products/{id_user}/{product_id}")
def delete_product_from_mongodb(
    id_user: int,
    product_id: str,
    mongo_db: Collection = Depends(get_mongo_db),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_user(id_user, db, user)
    
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.role != Role.administrador:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado")

    fs = GridFS(mongo_db)
    product = mongo_db["products"].find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado en MongoDB")

    # Eliminar imagen asociada del GridFS
    image_id = product.get("image_id")
    if image_id:
        fs.delete(ObjectId(image_id))

    # Eliminar producto
    result = mongo_db["products"].delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado en MongoDB")

    return {"message": "Producto y su imagen eliminados exitosamente"}
