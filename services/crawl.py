from httpx import AsyncClient, ConnectError, HTTPStatusError

from core.config import get_settings
from core.exceptions.crawl import CrawlFailedException, FirecrawlConnectionException
from schemas.crawl import CrawlRequestBody, CrawlNewRequest, CrawlResponse

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

    async def request_crawl(self, body: CrawlNewRequest) -> CrawlResponse:
        try:
            async with AsyncClient(
                base_url=settings.chunking_crawl_url,
                headers={"Content-Type": "application/json"},
            ) as ac:
                response = await ac.post("/crawl", json=body.model_dump())
                response.raise_for_status()
                return CrawlResponse.model_validate(response.json())
        except ConnectError:
            raise FirecrawlConnectionException from None
        except HTTPStatusError:
            raise CrawlFailedException from None


crawl_service = CrawlService()
