import os
import base64
import string
import uuid
from fastapi import APIRouter, Depends, FastAPI, status, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
import jwt
from utils.security import authenticate_user, get_current_user, verify_user
from routes.auth_route import create_access_token
from models.user_model import User, Role
from database.database import Base, engine, get_db, get_mongo_db
from schemas.user_schema import LoginRequest, LoginResponse, UserResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from middlewares.password_middleware import PasswordMiddleware
from middlewares.auth_middleware import get_current_user
import json

route = APIRouter()
app = FastAPI()

# Directorio para archivos estáticos (imágenes)
app.mount("/media", StaticFiles(directory=os.path.join(os.getcwd(), "media")), name="media")

Base.metadata.create_all(bind=engine)

# Directorio para guardar imágenes
IMAGEDIR = "media/"

# Crear usuario
@route.post('/signUp', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signUp(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    ubication: Optional[str] = Form(None),
    role: Role = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db)
):
    if ubication is None:
        ubication_data = {"": ""}
    else:
        try:
            ubication_data = json.loads(ubication)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ubication must be a valid JSON string."
            )

    hashed_password = PasswordMiddleware.hash_password(password)

    img_path = None
    if file:
        os.makedirs(IMAGEDIR, exist_ok=True)
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(IMAGEDIR, filename)

        with open(filepath, "wb") as f:
            f.write(await file.read())

        img_path = filepath

        mongo_db["photos"].insert_one({"email": email, "img_path": img_path})

    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        ubication=ubication_data,
        role=role,
        img=img_path
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

@route.get("/user/{id_user}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id_user} not found."
        )

    verify_user(id_user, db, current_user)

    user_data = {
        "id_user": user.id_user,
        "name": user.name,
        "email": user.email,
        "ubication": user.ubication,
        "role": user.role.value,
        "img": None  # Aquí almacenaremos la URL
    }

    if user.img:
        if isinstance(user.img, memoryview):
            user.img = user.img.tobytes().decode('utf-8') 
        
        if os.path.exists(user.img):
            user_data["img"] = f"/media/{os.path.basename(user.img)}"
        else:
            user_data["img"] = "Image not found or path is incorrect."

    return user_data

# Obtener usuarios
@route.get("/users/", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Iniciar sesión
@route.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email
    password = request.password
    print(f"Datos recibidos en login: email={email}, password={password}")

    user = authenticate_user(db, email, password)
    if not user:
        print("Credenciales inválidas.")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    print(f"Usuario autenticado: {user}")

    access_token = create_access_token(
        data={"sub": str(user.id_user), "email": user.email}
    )
    print(f"Token generado: {access_token}")

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

@route.delete("/user/{id_user}", status_code=status.HTTP_200_OK)
async def delete_user(
    id_user: int,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    verify_user(id_user, db, current_user)

    if isinstance(user.img, str) and os.path.exists(user.img):
        try:
            os.remove(user.img)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")

    if mongo_db["photos"].find_one({"email": user.email}):
        mongo_db["photos"].delete_one({"email": user.email})
    else:
        raise HTTPException(status_code=404, detail="Image path not found in MongoDB")

    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user from database: {str(e)}")

    return {"message": "User and associated image deleted successfully"}

# Editar perfil
@route.patch('/account/{id_user}', status_code=status.HTTP_200_OK)
async def update_user(
    id_user: int,  
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    ubication: Optional[str] = Form(None),
    role: Optional[Role] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    current_user: dict = Depends(get_current_user)
):
    user_db = db.query(User).filter(User.id_user == id_user).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

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
        if user_db.img and isinstance(user_db.img, str) and os.path.exists(user_db.img):
            os.remove(user_db.img)

        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(IMAGEDIR, filename)

        with open(filepath, "wb") as f:
            f.write(await file.read())  # Guardamos el contenido del archivo

        # Actualizar la ruta de la imagen en la base de datos
        user_db.img = filepath

        # Actualizar ruta en MongoDB
        mongo_db["photos"].update_one(
            {"email": user_db.email},
            {"$set": {"img_path": filepath}}
        )

    db.commit()
    db.refresh(user_db)
    return {"message": "User has updated"}
