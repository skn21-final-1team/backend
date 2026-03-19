from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from agent.model.llm_factory import llm_factory
from agent.prompts.classify import CLASSIFY_SYSTEM_PROMPT
from agent.state import QAState


class RouteByIntent(BaseModel):
    """사용자의 의도와 복잡도를 구분합니다."""

    intent: str = Field(
        description="""
        - "simple": 단일 주제에 대한 직접적인 질문
        - "complex": 비교, 분석, 다단계 추론이 필요한 복합 질문
        - "casual": 인사, 잡담, 단순 대화
        """
    )


def classify_intent(state: QAState, config: RunnableConfig) -> dict[str, str]:
    try:
        """사용자 메시지의 의도를 question 또는 casual로 분류합니다."""
        messages = [SystemMessage(content=CLASSIFY_SYSTEM_PROMPT.format(question=state["question"]))]

        llm = llm_factory.get_llm(config)

        response = llm.with_structured_output(RouteByIntent).invoke(messages)
        return {"intent": response.intent}
    except Exception as e:
        print("classify_intent error", e)
    return {"intent": "simple"}
