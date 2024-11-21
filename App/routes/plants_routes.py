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

route = APIRouter()

Base.metadata.create_all(bind=engine)

# Obtiene todas las plantas de un usuario
@route.get('/{id_user}/plants', response_model=list[PlantResponse], status_code=status.HTTP_200_OK)
def get_plants(id_user: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verify_user(id_user, db, current_user)

    plants = db.query(UserPlant).filter(UserPlant.id_user == id_user).all()
    if not plants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No plants found for this user"
        )
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

# Crea una nueva planta para un usuario
@route.post("/{id_user}/plants", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
def create_plant(
    id_user: int,
    name: str = Form(...), 
    description: str = Form(...), 
    hora_de_riego: str = Form(...), 
    category: CategoryPlant = Form(...), 
    tipo: TypePlant = Form(...), 
    img: UploadFile = File(None), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_user(id_user, db, current_user)

    # Leer contenido de la imagen si existe
    image_data = img.file.read() if img else None

    new_plant = Plant(
        name=name,
        description=description,
        hora_de_riego=hora_de_riego,
        category=category,
        tipo=tipo,
        img=image_data
    )
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    connection = UserPlant(id_user=id_user, id_plant=new_plant.id_plant)
    db.add(connection)
    db.commit()

    return new_plant

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
