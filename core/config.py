from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="FastAPI Application", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    api_str: str = Field(default="/api", alias="API_STR")
    secret_key: str = Field(default="", alias="SECRET_KEY")

    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    database_url: str = Field(default="", alias="DATABASE_URL")
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
