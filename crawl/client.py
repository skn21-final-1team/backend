from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from trafilatura import extract, extract_metadata

from core.exceptions.crawl import CrawlFailedException
from crawl.crawl import get_crawl_settings
from schemas.crawl import CrawlResult

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
_HEADERS = {
    "User-Agent": _USER_AGENT,
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def _parse_html(html: str) -> tuple[str | None, str]:
    meta = extract_metadata(html)
    title = meta.title if meta else None
    content = extract(html, include_comments=False, include_tables=True, output_format="markdown") or ""
    return title, content


def _parse_duckduckgo_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for result in soup.select(".result"):
        title_el = result.select_one(".result__title a")
        snippet_el = result.select_one(".result__snippet")
        url_el = result.select_one(".result__url")
        if not title_el or not snippet_el:
            continue
        title = title_el.get_text(strip=True)
        snippet = snippet_el.get_text(strip=True)
        url = url_el.get_text(strip=True) if url_el else ""
        results.append(f"## {title}\n{url}\n{snippet}")
    return "\n\n".join(results)


def _to_duckduckgo(url: str) -> str:
    parsed = urlparse(url)
    if "google" not in parsed.netloc:
        return url
    query = parse_qs(parsed.query).get("q", [""])[0]
    if not query:
        return url
    return f"https://html.duckduckgo.com/html/?{urlencode({'q': query})}"


def _to_mobile_naver(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc == "blog.naver.com":
        return url.replace("blog.naver.com", "m.blog.naver.com", 1)
    return url


class HybridClient:
    async def scrape(self, url: str) -> CrawlResult:
        url = _to_duckduckgo(url)
        url = _to_mobile_naver(url)
        settings = get_crawl_settings()
        try:
            title, content = await self._scrape_static(url)
            if len(content) < settings.static_fallback_threshold:
                title, content = await self._scrape_dynamic(url)
        except CrawlFailedException:
            raise
        except Exception as e:
            raise CrawlFailedException from e

        return CrawlResult(url=url, title=title or None, summary=content)

    async def _scrape_static(self, url: str) -> tuple[str | None, str]:
        async with httpx.AsyncClient(headers=_HEADERS, timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
        html = response.text
        if "duckduckgo.com" in url:
            return "DuckDuckGo 검색 결과", _parse_duckduckgo_html(html)
        return _parse_html(html)

    async def _scrape_dynamic(self, url: str) -> tuple[str | None, str]:
        settings = get_crawl_settings()
        stealth = Stealth(navigator_languages_override=("ko-KR", "ko"))
        async with stealth.use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=settings.playwright_headless)
            context = await browser.new_context(
                locale="ko-KR",
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=settings.playwright_timeout)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            html = await page.content()
            title = await page.title()
            await browser.close()

        _, content = _parse_html(html)
        return title or None, content


hybrid_client = HybridClient()
