from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any

class RoleEnum(str, Enum):
    user = 'usuario'
    nursery_manager = 'gestor_vivero'
    admin = 'administrador'

class UserBase(BaseModel): #el boceto de los datos
    name: str
    email: str
    ubication: Optional[Dict[str, Any]]
    rol: RoleEnum

    class Config:
        orm_mode = True

class UserRequest(UserBase): #lo que envia el usuario
    password: str  

class UserResponse(UserBase): #lo que devuelve el servidor
    id_user: int

    class Config:
        orm_mode = True

