from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from database.database import get_db
from middlewares.auth_middleware import get_current_user
from models.user_model import User  # Asegúrate de importar tu modelo de Usuario

# Configuración de JWT
SECRET_KEY = "66a106ad2e03e1443fd25f00261a1516d492d388b82d8917a4089000c6991ed6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Instancia del contexto de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo para la autenticación
class UserAuth(BaseModel):
    email: str
    password: str

# Función para autenticar al usuario
def authenticate_user(db: Session, email: str, password: str):
    # Buscar al usuario en la base de datos
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar si la contraseña es correcta
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Verificar si las contraseñas coinciden
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Generar el JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_user(id_user: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {id_user} not found")
    if current_user.get("email") != user.email:
        raise HTTPException(
            status_code=403, detail="No tienes permisos para acceder a este recurso"
        )
    return None  # Retorna explícitamente