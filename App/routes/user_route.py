from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from models.user_model import User, Role
from database.database import Base, engine, get_db
from schemas.user_schema import UserRequest, UserResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from middlewares.password_middleware import PasswordMiddleware
import json

route = APIRouter()

Base.metadata.create_all(bind=engine)

# Obtiene un usuario por ID


@route.get('/user/{id_user}', status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_user(id_user: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id_user} not found")
    return user

# Crea un usuario


@route.get("/users/", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@route.post('/signUp', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signUp(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    ubication: str = Form(...),
    role: Role = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        ubication_data = json.loads(ubication)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ubication must be a valid JSON string."
        )
    
    hashed_password = PasswordMiddleware.hash_password(password)
    
    image_data = await file.read() if file else None
    
    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        ubication=ubication_data,
        role=role,
        img=image_data
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    return new_user

# Iniciar sesión


@route.post('/login', status_code=status.HTTP_200_OK, response_model=UserResponse)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None or not PasswordMiddleware.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if user.role == "usuario":
        return 'token de usuario'
    elif user.role == "gestor_vivero":
        return 'token de gestor_vivero'
    return user

# Eliminar el usuario por ID


@route.delete('/account/{id_user}', status_code=status.HTTP_200_OK, response_model=UserResponse)
def delete_user(id_user: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id_user == id_user).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id_user} not found")
    db.delete(user)
    db.commit()
    return user

# Editar tu perfil


@route.patch('/account/{id_user}', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(
    id_user: int,
    name: Optional[str] = Form(None), 
    email: Optional[str] = Form(None), 
    ubication: Optional[str] = Form(None), 
    role: Optional[str] = Form(None), 
    file: Optional[UploadFile] = File(None), 
    db: Session = Depends(get_db)
):
    user_db = db.query(User).filter(User.id_user == id_user).first()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id_user} not found")

    if name:
        user_db.name = name
    if email:
        user_db.email = email
    if ubication:
        try:
            user_db.ubication = json.loads(ubication)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ubication must be a valid JSON string."
            )
    if role:
        user_db.role = role
    if file:
        image_data = await file.read()
        user_db.img = image_data

    db.commit()
    db.refresh(user_db)
    return user_db
