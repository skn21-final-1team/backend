from typing import TypedDict


class QAState(TypedDict):
    notebook_id: int
    question: str
    sources: list[str]
    answer: str
    chat_history: list[dict]
    intent: str
