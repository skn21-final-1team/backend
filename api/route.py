from fastapi import APIRouter

from .endpoints import auth, chat, directory, health, login, notebook, report_workflow, signup, source

api_router = APIRouter(redirect_slashes=False)

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(login.router, prefix="/login", tags=["auth"])
api_router.include_router(signup.router, prefix="/signup", tags=["auth"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(report_workflow.router, prefix="/report-workflow", tags=["report-workflow"])
api_router.include_router(notebook.router, prefix="/notebook", tags=["notebook"])
api_router.include_router(directory.router, prefix="/directory", tags=["directory"])
api_router.include_router(source.router, prefix="/source", tags=["source"])
