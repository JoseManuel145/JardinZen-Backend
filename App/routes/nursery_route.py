from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from schemas.nursery_schema import NurseryRequest, NurseryResponse
from models.nursery_model import Nursery, Info
from models.user_model import User, Role
from database.database import Base, engine, get_db
from sqlalchemy.orm import Session

route = APIRouter()

Base.metadata.create_all(bind=engine)

async def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user

@route.post('/{id_user}/viveros/', response_model=NurseryResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo vivero")
async def create_nursery(
    id_user: int,
    name: str = Form(...),
    description: str = Form(...),
    ubication: str = Form(...),
    file: Optional[UploadFile] = File(None), 
    db: Session = Depends(get_db)
):
    user = await get_user_by_id(id_user, db)

    if user.role != Role.gestor_vivero:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado")

    image_data = await file.read() if file else None

    new_nursery = Nursery(
        info=Info(name=name, description=description),
        ubication=ubication,
        img=image_data,
        id_manager=id_user
    )
    db.add(new_nursery)
    db.commit()
    db.refresh(new_nursery)
    return new_nursery

@route.delete('/{id_user}/viveros/{id_nursery}', status_code=status.HTTP_200_OK, response_model=NurseryResponse)
async def delete_nursery(id_nursery: int, id_user: int, db: Session = Depends(get_db)):
    nursery = db.query(Nursery).filter(Nursery.id_nursery == id_nursery).first()
    if nursery.id_manager != id_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acceso no autorizado")
    
    if nursery is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vivero no encontrado")

    db.delete(nursery)
    db.commit()
    return {"message": "Nursery deleted successfully"}

@route.get('/{id_user}/viveros', status_code=status.HTTP_200_OK, response_model=List[NurseryResponse])
async def get_nurserys(id_user: int, db: Session = Depends(get_db)):    
    user = await get_user_by_id(id_user, db)
    print("hola")
    if user.role == Role.gestor_vivero:
        nurseries = db.query(Nursery).filter(Nursery.id_manager == id_user).all()
    else:
        nurseries = db.query(Nursery).all()
    
    return nurseries