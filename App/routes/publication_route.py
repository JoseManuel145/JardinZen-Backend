from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from models.user_model import User
from middlewares.auth_middleware import get_current_user
from schemas.publication_schema import PublicationResponse
from models.publication_model import Publication
from database.database import Base, engine, get_db
from utils.security import verify_user

route = APIRouter()
Base.metadata.create_all(bind=engine)

@route.post("/{id_user}/publications/create", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_publication(
    id_user: int,
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_user(id_user, db, current_user)

    image_data = await file.read()

    new_publication = Publication(
        name=title,
        description=content,
        id_author=id_user,
        media=image_data
    )
    db.add(new_publication)
    db.commit()
    db.refresh(new_publication)
    return new_publication


@route.get("/publications", response_model=list[PublicationResponse], status_code=status.HTTP_200_OK)
async def get_publications(db: Session = Depends(get_db)):

    publications = db.query(Publication).all()
    return publications


@route.delete("/{id_user}/publications/{id_publication}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(id_user: int, id_publication: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    verify_user(id_user, db, current_user)

    publication = db.query(Publication).filter(
        Publication.id_publication == id_publication).first()
    if publication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    if publication.id_author != id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to delete this publication")
    db.delete(publication)
    db.commit()
    return {"message": "Publication deleted"}
