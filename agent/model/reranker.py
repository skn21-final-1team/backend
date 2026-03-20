import httpx

from core.config import get_settings

settings = get_settings()


class Reranker:
    CONFIG = {
        "model": "BAAI/bge-reranker-v2-m3",
        "top_k": 3,
        "min_score": 0.05,
        "api_key": settings.runpod_api_key,
        "headers": {"Authorization": f"Bearer {settings.runpod_api_key}", "Content-Type": "application/json"},
        "url": f"{settings.reranker_url}/runsync",
    }

    async def rerank(self, query: str, documents: list[str], top_k: int | None = None) -> list[str]:
        """query 관련성 기준으로 documents를 재정렬하여 top_k개 반환.

        min_score 미만인 문서는 제외합니다.

        Args:
            query: 사용자 질문 문자열.
            documents: 재정렬할 문서 목록.
            top_k: 반환할 문서 수. None이면 CONFIG 기본값 사용.

        Returns:
            관련성 높은 순으로 정렬된 상위 top_k개 문서 텍스트.

        Raises:
            httpx.HTTPStatusError: 서버 응답이 4xx/5xx인 경우.
        """

        try:
            payload = {"query": query, "documents": documents, "top_k": top_k or self.CONFIG["top_k"]}

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.CONFIG["url"], json={"input": payload}, headers=self.CONFIG["headers"]
                )
                response.raise_for_status()
                data = response.json()
                output = data.get("output", [])
                # min_score 미만 필터링
                filtered = [v for v in output if v.get("score", 0) >= self.CONFIG["min_score"]]
                print(f"Reranker: {len(output)}건 → {len(filtered)}건 (min_score={self.CONFIG['min_score']})")
                return [v.get("document", "") for v in filtered]
        except httpx.HTTPStatusError as e:
            print(f"Reranker API error: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.ReadTimeout:
            print("Reranker timeout: 응답 대기 시간 초과")
            return []


reranker = Reranker()
