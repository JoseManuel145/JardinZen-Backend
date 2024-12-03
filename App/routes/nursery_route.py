from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from schemas.nursery_schema import NurseryRequest, NurseryResponse
from models.nursery_model import Nursery, Info
from models.user_model import User, Role
from database.database import Base, engine, get_db
from sqlalchemy.orm import Session
from utils.security import verify_user, get_current_user
import cloudinary.uploader
import base64

route = APIRouter()


@route.post('/{id_user}/viveros', status_code=status.HTTP_201_CREATED)
async def create_nursery(
    id_user: int,
    name: str = Form(...),
    description: str = Form(...),
    ubication: str = Form(...),
    img: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_user(id_user, db, current_user)

    user = db.query(User).filter(User.id_user == id_user).first()
    if user.role != Role.gestor_vivero:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado")

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
            
        new_nursery = Nursery(
            info=Info(name=name, description=description),
            ubication=ubication,
            img=image_url,
            id_manager=id_user
        )
        db.add(new_nursery)
        db.commit()
        db.refresh(new_nursery)
        
        return new_nursery
    
    except Exception as e:
        print(f"Error creating plant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    

@route.delete('/{id_user}/viveros/{id_nursery}', status_code=status.HTTP_200_OK, response_model=NurseryResponse)
async def delete_nursery(
    id_nursery: int,
    id_user: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_user(id_user, db, current_user)

    nursery = db.query(Nursery).filter(Nursery.id_nursery == id_nursery).first()
    if not nursery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vivero no encontrado")
    if nursery.id_manager != id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado")

    db.delete(nursery)
    db.commit()
    return {"message": "Nursery deleted successfully"}


@route.get('/{id_user}/viveros', status_code=status.HTTP_200_OK, response_model=List[NurseryResponse])
async def get_nurserys(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_user(id_user, db, current_user)

    user = db.query(User).filter(User.id_user == id_user).first()
    if user.role == Role.gestor_vivero:
        nurseries = db.query(Nursery).filter(Nursery.id_manager == id_user).all()
    else:
        nurseries = db.query(Nursery).all()

    return nurseries
