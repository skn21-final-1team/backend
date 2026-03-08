from langchain_openai import OpenAIEmbeddings

from core.config import get_settings

settings = get_settings()

embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",
    base_url=f"{settings.embedding_url}/openai/v1",
    api_key=settings.runpod_api_key,
    check_embedding_ctx_length=False,
)
