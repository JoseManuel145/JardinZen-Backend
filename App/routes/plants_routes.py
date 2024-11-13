from fastapi import APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from schemas.plants_schema import PlantRequest, PlantResponse
from database.database import Base, engine, get_db
route = APIRouter()

Base.metadata.create_all(bind=engine)

#PENDIENTE POR HACER