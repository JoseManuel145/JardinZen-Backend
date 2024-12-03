from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import bcrypt

class PasswordMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self._salt = bcrypt.gensalt()

    async def dispatch(self, request: Request, call_next):
        return await call_next(request)

    @staticmethod
    def hash_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), hashed_password.encode())
        except Exception:
            return False
