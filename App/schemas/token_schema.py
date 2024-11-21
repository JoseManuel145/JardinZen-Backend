from pydantic import BaseModel


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    tipo_usuario: str
   

    class Config:
        from_attributes = True

class UserLoginSchema(BaseModel):
    email: str
    password: str