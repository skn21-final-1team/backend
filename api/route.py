from fastapi import APIRouter

from .endpoints import auth, chat, crawl, directory, health, login, notebook, signup

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(login.router, prefix="/login", tags=["auth"])
api_router.include_router(signup.router, prefix="/signup", tags=["auth"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(crawl.router, prefix="/crawl", tags=["crawl"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(notebook.router, prefix="/notebook", tags=["notebook"])
api_router.include_router(directory.router, prefix="/directory", tags=["directory"])
