import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models.user_model import User
from middlewares.auth_middleware import get_current_user
from schemas.publication_schema import PublicationResponse
from models.publication_model import Publication
from database.database import Base, engine, get_db, get_mongo_db
from utils.security import verify_user

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
    mongo_db=Depends(get_mongo_db)
):
    verify_user(id_user, db, current_user)

    img_path = None
    if file:
        os.makedirs(IMAGEDIR, exist_ok=True)
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(IMAGEDIR, filename)

        # Save the uploaded file to disk
        with open(filepath, "wb") as f:
            f.write(await file.read())

        img_path = filepath

        mongo_db["photos"].insert_one({"tittle": title, "img_path": img_path})

    new_publication = Publication(
        name=title,
        description=content,
        id_author=id_user,
        media=img_path
    )
    db.add(new_publication)
    db.commit()
    db.refresh(new_publication)
    return new_publication

@route.get("/publications", response_model=list[PublicationResponse], status_code=status.HTTP_200_OK)
async def get_publications(db: Session = Depends(get_db)):
    # Obtén las publicaciones desde la base de datos
    publications = db.query(Publication).all()

    for publication in publications:
        if publication.media and isinstance(publication.media, memoryview):
            try:
                publication.media = publication.media.tobytes().decode('utf-8')
                print("Media decodificada correctamente.")
            except UnicodeDecodeError:
                publication.media = "None"
                print("No se puede decodificar como UTF-8.")
        else:
            publication.media = "None"
            print("No hay cadena o media no es memoryview.")

    return publications


@route.delete("/{id_user}/publications/{id_publication}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(
    id_user: int,
    id_publication: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db)
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

    # Eliminar el archivo de medios si existe
    if publication.media:
        # Asegurarse de que publication.media sea un string (por ejemplo, una ruta de archivo)
        if isinstance(publication.media, memoryview):
            publication.media = publication.media.tobytes().decode('utf-8')  # Si es un memoryview, convertir a string

        # Comprobar si la media es una ruta de archivo en el sistema
        if isinstance(publication.media, str) and os.path.exists(publication.media):
            try:
                os.remove(publication.media)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")

        # Eliminar la foto en MongoDB
        try:
            result = mongo_db["photos"].delete_one({"img_path": publication.media})
            if result.deleted_count == 0:
                raise HTTPException(status_code=500, detail="Error deleting photo from MongoDB")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting photo from MongoDB: {str(e)}")

    # Eliminar la publicación de la base de datos SQL
    try:
        db.delete(publication)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting publication: {str(e)}")

    return {"message": "Publication deleted"}
