from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pymongo import MongoClient

SQLALCHEMY_DATABASE_URL = 'postgresql://manuel:Manu145#@localhost:5432/jardinzen'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        """
MONGO_DATABASE_URL = "mongodb+srv://manuel:Manu145@jardinzen.8z95a.mongodb.net/"
MONGO_DATABASE_NAME = "jardinzen"

mongo_client = MongoClient(MONGO_DATABASE_URL)
mongo_db = mongo_client[MONGO_DATABASE_NAME]

def get_mongo_db():
    try:
        yield mongo_db
    finally:
        mongo_client.close()
        """