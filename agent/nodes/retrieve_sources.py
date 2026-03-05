from langchain_postgres.vectorstores import PGVector
from sqlalchemy.ext.asyncio import create_async_engine

from agent.model.embedding import EmbeddingModel
from agent.state import QAState
from core.config import get_settings

embeddings = EmbeddingModel()
settings = get_settings()

async_engine = create_async_engine(settings.async_database_url)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="page_data",
    connection=async_engine,
    use_jsonb=True,
    create_extension=False,
)


async def retrieve_sources(state: QAState) -> dict[str, list[str]]:
    try:
        print("retriver query start")
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        docs = await retriever.ainvoke(state["question"])
        print(docs)
        return {"sources": [doc.page_content for doc in docs]}
    except Exception as e:
        print(e)
        return {"sources": []}
