from fastapi import FastAPI
from database.database import Base, engine
from routes import plants_routes, user_route, nursery_route, publication_route
from middlewares import password_middleware

app = FastAPI()
app.add_middleware(password_middleware.PasswordMiddleware)
Base.metadata.create_all(bind=engine)

app.include_router(user_route.route, prefix="/users", tags=["users"])
app.include_router(plants_routes.route , prefix="/plants", tags=["plants"])
app.include_router(nursery_route.route , prefix="/nurseries", tags=["nurseries"])
app.include_router(publication_route.route , prefix="/publications", tags=["publications"])
