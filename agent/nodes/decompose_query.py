import json
import re

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


def _parse_queries_from_text(text: str, fallback_question: str) -> list[str]:
    """LLM 텍스트 응답에서 쿼리 목록을 추출합니다."""
    # JSON 배열 형태
    json_match = re.search(r'\[([^\]]+)\]', text)
    if json_match:
        try:
            queries = json.loads(f"[{json_match.group(1)}]")
            if queries and all(isinstance(q, str) for q in queries):
                return queries
        except json.JSONDecodeError:
            pass
    # 번호 목록 형태 (1. xxx, 2. xxx)
    numbered = re.findall(r'\d+[.)]\s*(.+)', text)
    if len(numbered) >= 2:
        return [q.strip().strip('"\'') for q in numbered]
    # 줄바꿈으로 구분된 형태
    lines = [line.strip().strip('-•').strip() for line in text.strip().split('\n') if line.strip()]
    if len(lines) >= 2:
        return lines[:3]
    return [fallback_question]


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
        if llm_factory.supports_structured_output(config):
            response = await llm.with_structured_output(DecomposedQueries).ainvoke(messages)
            return {"search_queries": response.queries}
        else:
            response = await llm.ainvoke(messages)
            return {"search_queries": _parse_queries_from_text(response.content, state["question"])}
    except Exception:
        return {"search_queries": [state["question"]]}
