import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.route import api_router
from core.auth_guard import AuthMiddleware
from core.config import get_settings
from core.exceptions.exception_handlers import init_exception_handlers
from db.database import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
logger.info(f"DATABASE_URL: {settings.database_url}")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    redirect_slashes=False,
    openapi_url=f"{settings.api_str}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_str)

init_exception_handlers(app)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to FastAPI"}
