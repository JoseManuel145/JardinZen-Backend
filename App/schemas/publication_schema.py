from enum import Enum
from pydantic import BaseModel

class Info(BaseModel):
    name: str
    description: str

class PublicationBase(BaseModel):
    info : Info
    
    class Config:
        from_attributes = True

class PublicationRequest(PublicationBase): 
    pass  

class PublicationResponse(PublicationBase):
    id_publication: int
    media: str
    class Config:
        from_attributes = True

