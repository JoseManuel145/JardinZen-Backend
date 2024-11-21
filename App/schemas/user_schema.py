from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, Any

class RoleEnum(str, Enum):
    usuario = 'usuario'
    gestor_vivero = 'gestor_vivero'
    administrador = 'administrador'

class UserBase(BaseModel):  # El boceto de los datos
    name: str
    email: str
    ubication: Optional[Dict[str, Any]]
    role: RoleEnum
    file: Optional[UploadFile] = None

    class Config:
        from_attributes = True
        orm_mode = True  # Tells Pydantic to treat the model as an ORM model.

class UserRequest(UserBase):
    pass
    password: str

    def handle_image(self, file: UploadFile):
        return file.file.read() 
    
class UserResponse(UserBase):  # Lo que devuelve el servidor
    id_user: int

    class Config:
        orm_mode = True  # Tells Pydantic to treat the model as an ORM model.
   
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    name: str
    email: str
    ubication: Dict[str, Any]
    role: str
    id_user: int
