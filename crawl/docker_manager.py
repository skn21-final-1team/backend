import asyncio
import subprocess

import httpx

from core.exceptions.crawl import FirecrawlContainerException
from crawl.crawl import get_crawl_settings


class DockerComposeManager:
    def __init__(self) -> None:
        self._is_running: bool = False
        self._lock: asyncio.Lock = asyncio.Lock()
        self._active_requests: int = 0

    async def acquire(self) -> None:
        async with self._lock:
            self._active_requests += 1
            if not self._is_running:
                await self._compose("up", "-d")
                await self._wait_for_healthy()
                self._is_running = True

    async def release(self) -> None:
        async with self._lock:
            self._active_requests -= 1
            if self._active_requests == 0 and self._is_running:
                await self._compose("down")
                self._is_running = False

    async def _compose(self, *args: str) -> None:
        settings = get_crawl_settings()
        result = await asyncio.to_thread(
            subprocess.run,
            ["docker", "compose", "-f", settings.firecrawl_compose_path, "-p", "firecrawl", *args],
            capture_output=True,
        )
        if result.returncode != 0:
            raise FirecrawlContainerException

    async def _wait_for_healthy(self) -> None:
        settings = get_crawl_settings()
        async with httpx.AsyncClient() as client:
            for _ in range(settings.firecrawl_health_max_retries):
                try:
                    await client.get(f"{settings.firecrawl_base_url}/", timeout=5.0)
                    return
                except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError):
                    pass
                await asyncio.sleep(settings.firecrawl_health_retry_interval)
        raise FirecrawlContainerException


docker_manager = DockerComposeManager()
