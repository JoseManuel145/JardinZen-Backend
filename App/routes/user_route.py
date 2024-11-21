from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
import jwt
from utils.security import authenticate_user, get_current_user, verify_user
from routes.auth_route import create_access_token
from models.user_model import User, Role
from database.database import Base, engine, get_db
from schemas.user_schema import LoginRequest, LoginResponse, UserResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from middlewares.password_middleware import PasswordMiddleware
from middlewares.auth_middleware import get_current_user
import json

route = APIRouter()

Base.metadata.create_all(bind=engine)

# Obtiene un usuario por ID



@route.get("/user/{id_user}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_details(id_user: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.id_user == id_user).first()
    verify_user(id_user, db, current_user)
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
    ubication: Optional[str] = Form(None),
    role: Role = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Imprimir datos recibidos
    print(f"Datos recibidos en signUp: name={name}, email={email}, password={password}, ubication={ubication}, role={role}, file={file.filename if file else None}")

    # Procesar ubicación
    
    if ubication is None:
        ubication_data = {"":"", "": ""}
    else:
        try:
            ubication_data = json.loads(ubication)
            print(f"Ubication procesada como JSON: {ubication_data}")
        except json.JSONDecodeError:
            print("Error al decodificar la ubicación.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ubication must be a valid JSON string."
            )

    # Procesar contraseña
    hashed_password = PasswordMiddleware.hash_password(password)
    print(f"Password encriptada: {hashed_password}")

    # Leer datos del archivo
    image_data = await file.read() if file else None
    print(f"Tamaño de la imagen subida: {len(image_data) if image_data else 'No file uploaded'} bytes")
    
    # Crear objeto User
    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        ubication=ubication_data,
        role=role,
        img=image_data
    )
    print(f"Nuevo usuario creado: {new_user}")

    # Insertar usuario en la base de datos
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Usuario guardado en la base de datos con ID: {new_user.id_user}")
    except IntegrityError as e:
        db.rollback()
        print(f"Error al guardar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    return new_user


# Iniciar sesión


@route.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Datos recibidos
    email = request.email
    password = request.password
    print(f"Datos recibidos en login: email={email}, password={password}")

    # Verificar credenciales
    user = authenticate_user(db, email, password)
    if not user:
        print("Credenciales inválidas.")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    print(f"Usuario autenticado: {user}")

    # Crear token de acceso
    access_token = create_access_token(
        data={"sub": str(user.id_user), "email": user.email}
    )
    print(f"Token generado: {access_token}")

    # Retornar respuesta
    response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        name=user.name,
        email=user.email,
        ubication=user.ubication,
        role=user.role,
        id_user=user.id_user
    )
    print(f"Respuesta enviada al cliente: {response}")
    return response



# Eliminar el usuario por ID


@route.delete("/user/{id_user}", status_code=status.HTTP_200_OK)
async def delete_user(id_user: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.id_user == id_user).first()
    verify_user(id_user, db, current_user)
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado"}

# Editar tu perfil


@route.patch('/account/{id_user}', status_code=status.HTTP_200_OK)
async def update_user(
    id_user: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    ubication: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) 
):
    user_db = db.query(User).filter(User.id_user == id_user).first()
    verify_user(id_user, db, current_user)

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
