from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import composite
from database.database import Base

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
    media = Column(String)
    
   