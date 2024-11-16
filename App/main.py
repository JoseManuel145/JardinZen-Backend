from fastapi import FastAPI
from database.database import Base, engine
from routes import plants_routes, user_route, nursery_route, publication_route
from middlewares.password_middleware import PasswordMiddleware  

app = FastAPI()
app.add_middleware(PasswordMiddleware)  
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a tu API!"}

app.include_router(user_route.route)
app.include_router(plants_routes.route)
app.include_router(nursery_route.route)
app.include_router(publication_route.route)
