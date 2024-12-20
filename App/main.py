from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Base, engine
from routes import plants_routes, user_route, nursery_route, publication_route, products_route, cart_route
from middlewares import password_middleware

app = FastAPI()
app.add_middleware(password_middleware.PasswordMiddleware)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


@app.get('/')
def welcome():
    return {"message": "Welcome to the API"}


app.include_router(user_route.route,  tags=["users"])
app.include_router(plants_routes.route,  tags=["plants"])
app.include_router(nursery_route.route, tags=["nurseries"])
app.include_router(publication_route.route,  tags=["publications"])
app.include_router(products_route.route, tags=["products"])
app.include_router(cart_route.route , tags=["cart"])