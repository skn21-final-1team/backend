from typing import TypedDict


class QAState(TypedDict):
    notebook_id: int
    question: str
    search_queries: list[str]
    sources: list[str]
    source_metadata: list[dict]
    answer: str
    chat_history: list[dict]
    intent: str
    retrieval_count: int
