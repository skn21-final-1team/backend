from fastapi import APIRouter

from .endpoints import health, login

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(login.router, prefix="/login", tags=["auth"])
