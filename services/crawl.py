from httpx import AsyncClient

from core.config import get_settings
from schemas.crawl import CrawlRequestBody

settings = get_settings()


class CrawlService:
    async def crawl_and_save(self, body: CrawlRequestBody) -> bool:
        async with AsyncClient(
            base_url=settings.chunking_crawl_url,
            headers={
                "Content-Type": "application/json",
            },
        ) as ac:
            response = await ac.post("/crawl", json=body.model_dump())
            print(response)
            return True


crawl_service = CrawlService()
