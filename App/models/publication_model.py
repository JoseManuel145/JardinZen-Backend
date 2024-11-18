from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Enum
from sqlalchemy.orm import composite, relationship
from database.database import Base
from enum import Enum

"""
class Type_reaction(Enum):
    Like = 'like'
    Love = 'love'
    funny = 'funny'
    sad = 'sad'
    angry = 'angry'
"""
class Info:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __composite_values__(self):
        return self.name, self.description

class Publication(Base):
    __tablename__ = "Publication"

    id_publication = Column(Integer, primary_key=True, autoincrement=True)
    id_author = Column(Integer, ForeignKey("Users.id_user"))
    info = composite(Info, Column("name", String, nullable=False), Column("description", String))
    media = Column(LargeBinary)
    
    #reactions = relationship("Reaction", back_populates="publication")

"""
class Reaction(Base):
    __tablename__ = "Reactions"

    id_reaction = Column(Integer, primary_key=True, autoincrement=True)
    id_publication = Column(Integer, ForeignKey("Publication.id_publication"))
    reaction = Column(Enum(Type_reaction), nullable=False)

    publication = relationship("Publication", back_populates="reactions")
"""