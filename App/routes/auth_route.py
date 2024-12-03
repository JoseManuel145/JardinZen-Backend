from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from datetime import datetime, timedelta
from models.user_model import User
from schemas.token_schema import TokenResponseSchema, UserLoginSchema
from utils.security import verify_password
from database.database import get_db
from sqlalchemy.future import select
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token", response_model=TokenResponseSchema)
async def login_for_access_token(form_data: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    user_query = await db.execute(select(User).filter(User.email == form_data.email))
    user = user_query.scalars().first()

    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={
        "sub": str(user.id_user),
        "email": user.email,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
        "email": user.email,
        "ubication": user.ubication,
        "role": user.role,
        "id_user": user.id_user
    }