from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from schemas.plants_schema import PlantRequest, PlantResponse
from database.database import Base, engine, get_db
from models.plant_model import Plant, TypePlant, CategoryPlant
from models.user_model import User
from models.user_plant_model import UserPlant
from middlewares.auth_middleware import get_current_user
from utils.security import verify_user
from typing import Optional
import cloudinary.uploader
import base64


route = APIRouter()

# Obtiene todas las plantas de un usuario
@route.get('/{id_user}/plants', status_code=status.HTTP_200_OK )
def get_plantas(id_user: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    verify_user(id_user, db, current_user)

    plants = db.query(UserPlant).filter(UserPlant.id_user == id_user).all()
    if not plants:
#        raise HTTPException(
#            status_code=status.HTTP_404_NOT_FOUND, detail="No plants found for this user"
        print("No plants found for this user")
    return [p.plant for p in plants]

# Obtiene una planta específica
@route.get('/{id_user}/plants/{id_plant}', response_model=PlantResponse, status_code=status.HTTP_200_OK)
def get_plant(id_user: int, id_plant: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verify_user(id_user, db, current_user)

    verify = db.query(UserPlant).filter(
        UserPlant.id_user == id_user,
        UserPlant.id_plant == id_plant
    ).first()
    if not verify:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No plant found for user {id_user} with plant ID {id_plant}"
        )
    plant = db.query(Plant).filter(Plant.id_plant == id_plant).first()
    return plant


#Crea una nueva planta para un usuario
@route.post("/{id_user}/plants", status_code=status.HTTP_201_CREATED)
async def create_plant(
    id_user: int,
    name: str = Form(...), 
    description: str = Form(...), 
    hora_de_riego: str = Form(...), 
    category: str = Form(...), 
    tipo: str = Form(...), 
    img: Optional[UploadFile] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    verify_user(id_user, db, current_user)
    try:
        image_url = ""
        if img:
            try:
                # Leer el contenido del archivo
                contents = await img.read()
                print(img)
                if not contents:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El archivo de imagen está vacío"
                    )

                # Subir a Cloudinary
                upload_result = cloudinary.uploader.upload(
                    "data:image/jpeg;base64," + base64.b64encode(contents).decode("utf-8"),
                    folder="plants",  # Carpeta en Cloudinary
                    resource_type="auto"
                )

                image_url = upload_result.get("secure_url", "")
                print(image_url)
            except Exception as e:
                print(f"Error al procesar la imagen: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al procesar la imagen: {str(e)}"
                )
        
        # Validar y convertir category y tipo
        try:
            category_enum = CategoryPlant(category)
            tipo_enum = TypePlant(tipo)
        except ValueError as e:
            raise HTTPException(
                detail=f"Valor inválido para category o tipo: {str(e)}"
            )

        # Crear la planta
        plant = Plant(
            name=name,
            description=description,
            hora_de_riego=hora_de_riego,
            category=category_enum,
            tipo=tipo_enum,
            img=image_url
        )

        db.add(plant)
        db.commit()
        db.refresh(plant)
        
        # Crear la relación usuario-planta
        user_plant = UserPlant(
            id_user=id_user,
            id_plant=plant.id_plant
        )
        db.add(user_plant)
        db.commit()
        
        return plant

    except Exception as e:
        print(f"Error creating plant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

# Actualiza una planta
@route.put('/{id_user}/plants/{id_plant}', response_model=PlantResponse, status_code=status.HTTP_200_OK)
def update_plant(id_user: int, id_plant: int, plant: PlantRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verify_user(id_user, db, current_user)

    existing_plant = db.query(Plant).filter(Plant.id_plant == id_plant).first()
    if not existing_plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

    for key, value in plant.dict(exclude_unset=True).items():
        setattr(existing_plant, key, value)
    db.commit()
    db.refresh(existing_plant)
    return existing_plant

# Elimina una planta
@route.delete('/{id_user}/plants/{id_plant}', status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(id_user: int, id_plant: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verify_user(id_user, db, current_user)

    plant = db.query(Plant).filter(Plant.id_plant == id_plant).first()
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

    user_plant = db.query(UserPlant).filter(UserPlant.id_user == id_user, UserPlant.id_plant == id_plant).first()
    if user_plant:
        db.delete(user_plant)
        db.commit()

    db.delete(plant)
    db.commit()

    return {"message": "Plant deleted successfully"}
