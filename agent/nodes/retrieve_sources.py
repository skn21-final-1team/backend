from langchain_postgres.vectorstores import PGVector
from sqlalchemy.ext.asyncio import create_async_engine

from agent.model.embedding import embeddings
from agent.model.reranker import reranker
from agent.state import QAState
from core.config import get_settings

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
        question = state["question"]
        retriever = vector_store.as_retriever(search_kwargs={"k": 10})

        docs = await retriever.ainvoke(question)
        contents = [doc.page_content for doc in docs]

        reranked = await reranker.rerank(question, contents)
        return {"sources": reranked}
    except Exception as e:
        print("Error in retrieve_sources:", e)
        return {"sources": []}
