import httpx
from langchain_core.embeddings import Embeddings

from core.config import get_settings


class EmbeddingModel(Embeddings):
    """외부 임베딩 API 서버와 통신하는 클라이언트.

    POST /embed/query 엔드포인트를 호출하여 텍스트의 임베딩 벡터를 반환합니다.
    """

    def __init__(self) -> None:
        self._embedding_api_url = get_settings().embedding_api_url

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        pass

    async def embed_query(self, text: str) -> list[float]:
        pass

    async def aembed_query(self, text: str) -> list[float]:
        """텍스트를 임베딩 벡터로 변환합니다.

        Args:
            text: 임베딩할 텍스트 문자열

        Returns:
            임베딩 벡터 (float 리스트)

        Raises:
            httpx.HTTPStatusError: API 호출 실패 시
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._embedding_api_url}/embed/query",
                json={"query": text},
                timeout=30.0,
            )
            res_json = response.json()
            response.raise_for_status()
            return res_json.get("embedding")
