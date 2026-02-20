from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CrawlSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    playwright_timeout: int = 30000
    playwright_headless: bool = True
    static_fallback_threshold: int = 150


@lru_cache
def get_crawl_settings() -> CrawlSettings:
    return CrawlSettings()
