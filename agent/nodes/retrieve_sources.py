from langchain_postgres.vectorstores import PGVector
from sqlalchemy.ext.asyncio import create_async_engine

from agent.model.embedding import embeddings
from agent.model.reranker import reranker
from agent.state import QAState
from core.config import get_settings
from crud.source import get_active_source_ids, get_source_ids_by_notebook
from db.database import get_db_context

settings = get_settings()

async_engine = create_async_engine(settings.async_database_url)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="page_data",
    connection=async_engine,
    use_jsonb=True,
    create_extension=False,
)


MAX_SOURCES = 5


async def retrieve_sources(state: QAState) -> dict:
    notebook_id = state["notebook_id"]
    queries = state.get("search_queries", [state["question"]])
    retrieval_count = state.get("retrieval_count", 0)

    with get_db_context() as db:
        notebook_source_ids = get_source_ids_by_notebook(db, notebook_id)
        if not notebook_source_ids:
            return {"sources": [], "retrieval_count": retrieval_count + 1}

        active_source_ids = get_active_source_ids(db, notebook_source_ids)
        if not active_source_ids:
            return {"sources": [], "retrieval_count": retrieval_count + 1}

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 10,
            "filter": {
                "source_id": {
                    "$in": active_source_ids,
                }
            },
        }
    )

    all_contents = []
    for query in queries:
        docs = await retriever.ainvoke(query)
        all_contents.extend([doc.page_content for doc in docs])

    unique_contents = list(dict.fromkeys(all_contents))

    if not unique_contents:
        return {"sources": [], "retrieval_count": retrieval_count + 1}

    if len(queries) > 1:
        # 복합 질문: sub-query별로 개별 rerank 후 합침
        # 원본 질문으로 rerank하면 각 주제 문서가 min_score 미만으로 탈락할 수 있음
        all_reranked = []
        for query in queries:
            reranked = await reranker.rerank(query, unique_contents)
            all_reranked.extend(reranked)
        # 중복 제거 (순서 유지)
        reranked = list(dict.fromkeys(all_reranked))
    else:
        reranked = await reranker.rerank(state["question"], unique_contents)

    return {"sources": reranked[:MAX_SOURCES], "retrieval_count": retrieval_count + 1}
