import re

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from agent.model.llm_factory import llm_factory
from agent.prompts.classify import CLASSIFY_SYSTEM_PROMPT
from agent.state import QAState

VALID_INTENTS = {"simple", "complex", "casual"}


class RouteByIntent(BaseModel):
    """사용자의 의도와 복잡도를 구분합니다."""

    intent: str = Field(
        description="""
        - "simple": 단일 주제에 대한 직접적인 질문
        - "complex": 비교, 분석, 다단계 추론이 필요한 복합 질문
        - "casual": 인사, 잡담, 단순 대화
        """
    )


def _parse_intent_from_text(text: str) -> str:
    """LLM 텍스트 응답에서 intent를 추출합니다."""
    text_lower = text.strip().lower().strip('"\'')
    if text_lower in VALID_INTENTS:
        return text_lower
    json_match = re.search(r'"intent"\s*:\s*"(\w+)"', text)
    if json_match and json_match.group(1) in VALID_INTENTS:
        return json_match.group(1)
    for intent in VALID_INTENTS:
        if intent in text_lower:
            return intent
    return "simple"


def classify_intent(state: QAState, config: RunnableConfig) -> dict[str, str]:
    """사용자 메시지의 의도를 simple, complex, casual로 분류합니다."""
    try:
        messages = [SystemMessage(content=CLASSIFY_SYSTEM_PROMPT.format(question=state["question"]))]
        llm = llm_factory.get_llm(config)

        if llm_factory.supports_structured_output(config):
            response = llm.with_structured_output(RouteByIntent).invoke(messages)
            return {"intent": response.intent}
        else:
            response = llm.invoke(messages)
            return {"intent": _parse_intent_from_text(response.content)}
    except Exception as e:
        print("classify_intent error", e)
    return {"intent": "simple"}
