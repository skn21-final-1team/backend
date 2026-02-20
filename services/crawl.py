from crawl.client import hybrid_client
from schemas.crawl import CrawlResult


class CrawlService:
    async def crawl(self, url: str) -> CrawlResult:
        return await hybrid_client.scrape(url)


crawl_service = CrawlService()
