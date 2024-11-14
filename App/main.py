from fastapi import FastAPI
from database.database import Base, engine
from routes import plants_routes, user_route
app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a tu API!"}

app.include_router(user_route)
app.include_router(plants_routes)