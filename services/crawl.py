from httpx import AsyncClient

from schemas.crawl import CrawlRequestBody


class CrawlService:
    async def crawl_and_save(self, body: CrawlRequestBody) -> bool:
        async with AsyncClient(
            base_url="https://ae8rlv5eumkv2a-8001.proxy.runpod.net/",
            headers={
                "Content-Type": "application/json",
            },
        ) as ac:
            response = await ac.post("/crawl", json=body.model_dump())
            print(response)
            return True


crawl_service = CrawlService()
