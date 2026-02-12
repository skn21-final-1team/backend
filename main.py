from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.route import api_router
from core.config import get_settings
from core.exceptions.exception_handlers import init_exception_handlers
from db.database import Base, engine

Base.metadata.create_all(bind=engine)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    openapi_url=f"{settings.api_str}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Refresh-Token"],
)

app.include_router(api_router, prefix=settings.api_str)

init_exception_handlers(app)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to FastAPI"}
