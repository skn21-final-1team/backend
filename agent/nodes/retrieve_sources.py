from langchain_postgres.vectorstores import PGVector
from sqlalchemy.ext.asyncio import create_async_engine

from agent.model.embedding import embeddings
from agent.model.reranker import reranker
from agent.state import QAState
from core.config import get_settings
from crud.source import get_active_source_ids, get_source_ids_by_notebook
from db.database import get_db_context
from models.source import SourceModel

settings = get_settings()

async_engine = create_async_engine(settings.async_database_url)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="page_data",
    connection=async_engine,
    use_jsonb=True,
    create_extension=False,
)

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
    content_to_source_id: dict[str, int] = {}
    for query in queries:
        docs = await retriever.ainvoke(query)
        for doc in docs:
            all_contents.append(doc.page_content)
            if doc.page_content not in content_to_source_id:
                content_to_source_id[doc.page_content] = doc.metadata.get("source_id")

    unique_contents = list(dict.fromkeys(all_contents))

    if not unique_contents:
        return {"sources": [], "source_metadata": [], "retrieval_count": retrieval_count + 1}

    reranked = await reranker.rerank(state["question"], unique_contents)

    # rerank된 청크의 source_id로 URL/title 조회
    reranked_source_ids = {content_to_source_id[c] for c in reranked if c in content_to_source_id}
    source_info: dict[int, dict] = {}
    if reranked_source_ids:
        with get_db_context() as db:
            rows = db.query(SourceModel.id, SourceModel.url, SourceModel.title).filter(
                SourceModel.id.in_(reranked_source_ids)
            ).all()
            source_info = {r.id: {"url": r.url, "title": r.title} for r in rows}

    source_metadata = []
    for content in reranked:
        sid = content_to_source_id.get(content)
        info = source_info.get(sid, {})
        source_metadata.append({
            "content": content,
            "url": info.get("url", ""),
            "title": info.get("title", ""),
        })

    return {"sources": reranked, "source_metadata": source_metadata, "retrieval_count": retrieval_count + 1}
