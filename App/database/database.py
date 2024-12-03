from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL")
MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")

mongo_client = MongoClient(MONGO_DATABASE_URL)
mongo_db = mongo_client[MONGO_DATABASE_NAME]

KEY_NAME = os.getenv("KEY_NAME")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

cloudinary.config(
    cloud_name=KEY_NAME, 
    api_key=API_KEY, 
    api_secret=API_SECRET, 
    secure=True
)               

def get_mongo_db():
   return mongo_db
