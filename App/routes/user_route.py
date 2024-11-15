from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from models.user_model import User
from database.database import Base, engine, get_db
from schemas.user_schema import UserRequest, UserResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from middlewares.password_middleware import PasswordMiddleware

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
@route.post('/signUp', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    user: UserRequest,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Hashea la contraseña antes de guardarla
    hashed_password = PasswordMiddleware.hash_password(user.password)
    image_data = await file.read() if file else None
    new_user = User(name=user.name, email=user.email, password=hashed_password, img=image_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Iniciar sesión
@route.post('/login', status_code=status.HTTP_200_OK, response_model=UserResponse)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None or not PasswordMiddleware.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
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
@route.put('/account/{id_user}', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(
    id_user: int,
    user: UserRequest,
    file: Optional[UploadFile] = File(None),  # Imagen opcional
    db: Session = Depends(get_db)
):
    user_db = db.query(User).filter(User.id_user == id_user).first()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id_user} not found")
    
    # Actualizar los datos básicos del usuario
    user_db.name = user.name
    user_db.email = user.email
    user_db.ubication = user.ubication

    # Actualizar la imagen solo si se proporciona una nueva
    if file:
        image_data = await file.read()
        user_db.img = image_data

    db.commit()
    db.refresh(user_db)
    return user_db
