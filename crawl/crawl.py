from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CrawlSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 기본값 세팅구조, 지우고 .env 파일에서 컨트롤 해도 괜찮습니다.
    firecrawl_base_url: str = "http://localhost:3002"
    firecrawl_compose_path: str = "docker/firecrawl/docker-compose.yml"
    firecrawl_timeout: float = 60.0
    firecrawl_health_max_retries: int = 30
    firecrawl_health_retry_interval: float = 2.0


@lru_cache
def get_crawl_settings() -> CrawlSettings:
    return CrawlSettings()
