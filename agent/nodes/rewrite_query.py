import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.rewrite import REWRITE_SYSTEM_PROMPT, REWRITE_USER_PROMPT
from agent.state import QAState

logger = logging.getLogger(__name__)


def format_chat_history_for_rewrite(history: list[dict]) -> str:
    if not history:
        return "없음"
    recent = history[-6:]
    return "\n".join(f"{chat.role}: {chat.message}" for chat in recent)


async def rewrite_query(state: QAState, config: RunnableConfig) -> dict:
    """사용자 질문을 벡터 검색에 최적화된 형태로 재작성합니다."""
    question = state["question"]
    chat_history_text = format_chat_history_for_rewrite(state.get("chat_history", []))
    retrieval_count = state.get("retrieval_count", 0)
    previous_queries = state.get("search_queries", [])

    is_retry = retrieval_count > 0
    user_content = REWRITE_USER_PROMPT.format(
        question=question,
        chat_history=chat_history_text,
        is_retry=is_retry,
        previous_queries=", ".join(previous_queries) if previous_queries else "없음",
    )

    messages = [
        SystemMessage(content=REWRITE_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    try:
        llm = llm_factory.get_llm(config)
        response = await llm.ainvoke(messages)
        return {"search_queries": [response.content.strip()]}
    except Exception as e:
        logger.warning("rewrite_query failed, falling back to original question: %s", e)
        return {"search_queries": [question]}
