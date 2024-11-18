from enum import Enum
from pydantic import BaseModel

"""
class Type_reaction(str, Enum):
    Like = 'like'
    Love = 'love'
    funny = 'funny'
    sad = 'sad'
    angry = 'angry'
"""

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

    class Config:
        from_attributes = True

