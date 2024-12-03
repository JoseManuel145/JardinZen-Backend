import os
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models.user_model import User
from middlewares.auth_middleware import get_current_user
from schemas.publication_schema import PublicationResponse
from models.publication_model import Publication
from database.database import Base, engine, get_db
from utils.security import verify_user
import cloudinary.uploader
import base64

route = APIRouter()
Base.metadata.create_all(bind=engine)
IMAGEDIR = "media/"
route.mount("/media", StaticFiles(directory=os.path.join(os.getcwd(), "media")), name="media")


@route.post("/{id_user}/publications/create", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_publication(
    id_user: int,
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_user(id_user, db, current_user)

    try:
        image_url = ""
        if file:
            try:
                # Leer el contenido del archivo
                contents = await file.read()
                print(file)
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

        # Crear la planta
        new_publication = Publication(
            name=title,
            description=content,
            id_author=id_user,
            media=image_url
        )
        db.add(new_publication)
        db.commit()
        db.refresh(new_publication)
        return new_publication

    except Exception as e:
        print(f"Error creating plant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@route.get("/publications", response_model=list[PublicationResponse], status_code=status.HTTP_200_OK)
async def get_publications(db: Session = Depends(get_db)):
        
    publications = db.query(Publication).all()

    print(publications)
    return publications


@route.delete("/{id_user}/publications/{id_publication}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(
    id_user: int,
    id_publication: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar si el usuario tiene permiso para eliminar la publicación
    verify_user(id_user, db, current_user)

    # Buscar la publicación en la base de datos SQL
    publication = db.query(Publication).filter(Publication.id_publication == id_publication).first()
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    # Verificar que el usuario sea el autor de la publicación
    if publication.id_author != id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this publication")

    # Eliminar la publicación de la base de datos SQL
    try:
        db.delete(publication)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting publication: {str(e)}")

    return {"message": "Publication deleted"}
