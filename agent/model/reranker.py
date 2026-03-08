import httpx

from core.config import get_settings

settings = get_settings()


class Reranker:
    CONFIG = {
        "model": "BAAI/bge-reranker-v2-m3",
        "top_k": 3,
        "api_key": settings.runpod_api_key,
        "headers": {"Authorization": f"Bearer {settings.runpod_api_key}", "Content-Type": "application/json"},
        "url": f"{settings.reranker_url}/runsync",
    }

    async def rerank(self, query: str, documents: list[str]) -> list[str]:
        """query 관련성 기준으로 documents를 재정렬하여 top_k개 반환.

        Args:
            query: 사용자 질문 문자열.
            documents: 재정렬할 문서 목록.

        Returns:
            관련성 높은 순으로 정렬된 상위 top_k개 문서 텍스트.

        Raises:
            httpx.HTTPStatusError: 서버 응답이 4xx/5xx인 경우.
        """

        payload = {"query": query, "documents": documents, "top_k": self.CONFIG["top_k"]}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.CONFIG["url"], json={"input": payload}, headers=self.CONFIG["headers"])
            response.raise_for_status()
            data = response.json()
            output = data.get("output", [])
            return [v.get("document", "") for v in output]


reranker = Reranker()
