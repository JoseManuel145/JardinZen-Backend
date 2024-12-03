from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship, composite
from database.database import Base

class Info:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __composite_values__(self):
        return self.name, self.description


class Nursery(Base):
    __tablename__ = 'Nursery'

    id_nursery = Column(Integer, primary_key=True)
    info = composite(Info, Column("name", String, nullable=False), Column("description", String))
    ubication = Column(String, nullable=True)
    img = Column(String)
    id_manager = Column(Integer, ForeignKey("Users.id_user"))
    
    manager = relationship('User', back_populates='nurseries')
