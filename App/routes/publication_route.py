from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from schemas.publication_schema import PublicationRequest, PublicationResponse
from models.publication_model import Publication
from database.database import Base, engine, get_db
from sqlalchemy.orm import Session

route = APIRouter()
Base.metadata.create_all(bind=engine)

@route.post("/publications", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_publication(id_user: int, publication: PublicationRequest, db: Session = Depends(get_db), file: UploadFile = File(...)):
   
    image_data = await file.read()
    
    new_publication = Publication(**publication.model_dump())
    new_publication.id_author = id_user
    new_publication.media = image_data
    
    db.add(new_publication)
    db.commit()
    db.refresh(new_publication)
    return new_publication

@route.get("/publications", response_model=list[PublicationResponse], status_code=status.HTTP_200_OK)
async def get_publications(db: Session = Depends(get_db)):
    publications = db.query(Publication).all()
    return publications

@route.delete("publications/{id_publication}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(id_user: int, id_publication: int, db: Session = Depends(get_db)):
    publication = db.query(Publication).filter(Publication.id_publication == id_publication).first()
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    if publication.id_author != id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this publication")
    db.delete(publication)
    db.commit()
    return {"message": "Publication deleted"}
