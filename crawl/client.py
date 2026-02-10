import httpx
import trafilatura

from core.exceptions.crawl import CrawlFailedException, FirecrawlConnectionException
from crawl.crawl import get_crawl_settings
from schemas.crawl import CrawlResult


class FirecrawlClient:
    def session(self) -> httpx.AsyncClient:
        settings = get_crawl_settings()
        return httpx.AsyncClient(
            base_url=settings.firecrawl_base_url,
            timeout=settings.firecrawl_timeout,
        )

    async def scrape(self, client: httpx.AsyncClient, url: str) -> CrawlResult:
        try:
            response = await client.post(
                "/v1/scrape",
                json={"url": url, "formats": ["html"]},
            )
            response.raise_for_status()
        except httpx.ConnectError as e:
            raise FirecrawlConnectionException from e
        except (httpx.HTTPStatusError, httpx.RemoteProtocolError, httpx.ReadError) as e:
            raise CrawlFailedException from e

        data = response.json()
        if not data.get("success"):
            raise CrawlFailedException

        scrape_data = data.get("data", {})
        metadata = scrape_data.get("metadata", {})
        html = scrape_data.get("html", "")

        return CrawlResult(
            url=url,
            title=metadata.get("title"),
            summary=trafilatura.extract(html) or "",
        )


firecrawl_client = FirecrawlClient()
