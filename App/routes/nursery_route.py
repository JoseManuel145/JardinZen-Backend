from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from schemas.nursery_schema import NurseryRequest, NurseryResponse
from models.nursery_model import NurseryModel, Info
from models.user_model import User, Role
from database.database import Base, engine, get_db
from sqlalchemy.orm import Session

route = APIRouter()

async def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user

@route.post('{id_user}/viveros/', response_model=NurseryResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo vivero")
async def create_nursery(
    id_user: int,
    nursery: NurseryRequest,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    user = await get_user_by_id(id_user, db)

    if user.role != Role.nursery_manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado")

    image_data = await file.read() if file else None

    new_nursery = NurseryModel(
        info=Info(name=nursery.info.name, description=nursery.info.description),
        ubication=nursery.ubication,
        img=image_data,
        id_manager=id_user
    )
    db.add(new_nursery)
    db.commit()
    db.refresh(new_nursery)
    return new_nursery

@route.delete('{id_user}/viveros/{id_nursery}', status_code=status.HTTP_200_OK, response_model=NurseryResponse)
async def delete_nursery(id_nursery: int, id_user: int, db: Session = Depends(get_db)):
    nursery = db.query(NurseryModel).filter(NurseryModel.id_nursery == id_nursery).first()
    if nursery.id_manager != id_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acceso no autorizado")
    
    if nursery is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vivero no encontrado")

    db.delete(nursery)
    db.commit()
    return nursery