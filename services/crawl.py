from crawl.client import firecrawl_client
from crawl.docker_manager import docker_manager
from schemas.crawl import CrawlResult


class CrawlService:
    async def crawl(self, url: str) -> CrawlResult:
        await docker_manager.acquire()
        try:
            async with firecrawl_client.session() as client:
                return await firecrawl_client.scrape(client, url)
        finally:
            await docker_manager.release()


crawl_service = CrawlService()
