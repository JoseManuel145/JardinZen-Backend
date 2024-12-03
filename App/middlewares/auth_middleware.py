from fastapi import HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from models.user_model import User
from database.database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 100
oauth2_scheme = HTTPBearer()

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise ValueError("Invalid token payload")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

def get_current_user(db: Session = Depends(get_db),
                           token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    payload = verify_token(token.credentials)
    user_id = int(payload.get("sub"))
    email = payload.get("email")
    
    user_query = db.execute(select(User).filter(User.id_user == user_id))
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    print(user)
    return {
        "user_id": user_id,
        "email": email,
    }
