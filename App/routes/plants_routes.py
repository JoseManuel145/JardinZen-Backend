# plants_routes.py
from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from schemas.plants_schema import PlantRequest, PlantResponse
from database.database import Base, engine, get_db
from models.plant_model import Plant

route = APIRouter()

Base.metadata.create_all(bind=engine)

# Obtiene todas las plantas de x usuario
@route.get('/{id_user}/plants', response_model=list[PlantResponse], status_code=status.HTTP_200_OK)
def get_plants(id_user: int, db: Session = Depends(get_db)):
    plants = db.execute(
        text("SELECT * FROM get_user_plants(:user_id)"), {"user_id": id_user}).fetchall()
    if not plants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No plants found for this user"
        )
    return plants

# Obtiene una planta en especifico de x usuario
@route.get('/{id_user}/plants/{id_plant}', response_model=PlantResponse, status_code=status.HTTP_200_OK)
def get_plant(id_user: int, id_plant: int, db: Session = Depends(get_db)):
    plant = db.execute(
        text("SELECT * FROM get_user_plant(:user_id, :plant_id)"),
        {"user_id": id_user, "plant_id": id_plant}
    ).fetchone()
    if plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found"
        )
    return plant

# crea una nueva planta
@route.post('/{id_user}/plants', response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    id_user: int,
    plant: PlantRequest,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    image_data = await file.read()

    new_plant_id = db.execute(
        text(
            "SELECT add_plant_to_user(:user_id, :plant_name, :plant_description, :plant_hora_de_riego, :plant_category, :plant_tipo, :plant_img)"
        ),
        {
            "user_id": id_user,
            "plant_name": plant.info.name,
            "plant_description": plant.info.description,
            "plant_hora_de_riego": plant.hora_de_riego,
            "plant_category": plant.category.value,
            "plant_tipo": plant.tipo.value,
            "plant_img": image_data
        }
    ).scalar()

    new_plant = db.execute(
        text("SELECT * FROM Plants WHERE id_plant = :new_plant_id"),
        {"new_plant_id": new_plant_id}
    ).fetchone()

    db.commit()
    return new_plant

# Edita la planta
@route.put('/{id_user}/plants/{id_plant}', response_model=PlantResponse, status_code=status.HTTP_200_OK)
def update_plant(id_plant: int, plant: PlantRequest, db: Session = Depends(get_db)):
    existing_plant = db.query(Plant).filter(Plant.id_plant == id_plant).first()
    if not existing_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found"
        )
    for key, value in plant.model_dump().items():
        setattr(existing_plant, key, value)
    db.commit()
    db.refresh(existing_plant)
    return existing_plant

# Elimina la planta
@route.delete('/{id_user}/plants/{id_plant}', status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(id_plant: int, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id_plant == id_plant).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found"
        )
    db.delete(plant)
    db.commit()
    return HTTPException(status_code=status.HTTP_200_OK)
