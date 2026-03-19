from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from agent.model.llm_factory import llm_factory
from agent.prompts.rewrite import DECOMPOSE_SYSTEM_PROMPT, DECOMPOSE_USER_PROMPT
from agent.state import QAState


class DecomposedQueries(BaseModel):
    """복합 질문을 분해한 하위 질문 목록"""

    queries: list[str] = Field(
        description="검색에 최적화된 2-3개의 하위 질문 목록"
    )


def format_chat_history_for_decompose(history: list[dict]) -> str:
    if not history:
        return "없음"
    recent = history[-6:]
    return "\n".join(f"{chat.role}: {chat.message}" for chat in recent)


async def decompose_query(state: QAState, config: RunnableConfig) -> dict:
    """복합 질문을 2-3개의 하위 질문으로 분해합니다."""
    chat_history_text = format_chat_history_for_decompose(state.get("chat_history", []))

    user_content = DECOMPOSE_USER_PROMPT.format(
        question=state["question"],
        chat_history=chat_history_text,
    )

    messages = [
        SystemMessage(content=DECOMPOSE_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    llm = llm_factory.get_llm(config)

    try:
        response = await llm.with_structured_output(DecomposedQueries).ainvoke(messages)
        return {"search_queries": response.queries}
    except Exception:
        return {"search_queries": [state["question"]]}
