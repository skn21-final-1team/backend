from fastapi import APIRouter

from .endpoints import auth, health, login, signup

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(login.router, prefix="/login", tags=["auth"])
api_router.include_router(signup.router, prefix="/signup", tags=["auth"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
