from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field

from agent.model.llm import llm
from agent.prompts.classify import CLASSIFY_SYSTEM_PROMPT
from agent.state import QAState


class RouteByIntent(BaseModel):
    """사용자의 의도를 구분합니다."""

    intent: str = Field(
        description="""
        - "question": 노트북 소스 자료를 기반으로 답변이 필요한 질문
        - "casual": 일상적인 인사, 잡담, 단순 대화
        """
    )


def classify_intent(state: QAState) -> dict[str, str]:
    """사용자 메시지의 의도를 question 또는 casual로 분류합니다.

    Args:
        state: question을 포함한 QAState
    Returns:
        intent 키를 포함한 딕셔너리
    """
    print(f"[classify_intent] 입력 질문: {state['question']}")
    messages = [SystemMessage(content=CLASSIFY_SYSTEM_PROMPT.format(question=state["question"]))]
    response = llm.with_structured_output(RouteByIntent).invoke(messages)

    print(f"[classify_intent] 분류 결과: {response.intent}")
    return {"intent": response.intent}
