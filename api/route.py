from fastapi import APIRouter

from .endpoints import health, login, signup, user

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(login.router, prefix="/login", tags=["auth"])
api_router.include_router(signup.router, prefix="/signup", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
