from langchain_core.messages import HumanMessage, SystemMessage

from agent.model.llm import llm
from agent.prompts.chat import (
    CASUAL_SYSTEM_PROMPT,
    QA_SYSTEM_PROMPT,
    QA_USER_PROMPT,
)
from agent.state import QAState


def format_chat_history(history: list[dict]) -> str:
    if not history:
        return "없음"
    return "\n".join(f"{chat['role']}: {chat['message']}" for chat in history)


def generate_answer(state: QAState) -> dict[str, str]:
    """소스 자료 기반으로 LLM 답변을 생성합니다.

    Args:
        state: sources, chat_history, question을 포함한 QAState
    Returns:
        answer 키를 포함한 딕셔너리
    """
    chat_history_text = format_chat_history(state.get("chat_history", []))

    sources_text = "\n\n---\n\n".join(state.get("sources", []))

    messages = [
        SystemMessage(content=QA_SYSTEM_PROMPT),
        HumanMessage(
            content=QA_USER_PROMPT.format(
                sources=sources_text,
                chat_history=chat_history_text,
                question=state["question"],
            )
        ),
    ]

    response = llm.invoke(messages)
    print(f"[generate_answer] 답변 생성 완료 (길이: {len(response.content)})")
    return {"answer": response.content}


def generate_casual_answer(state: QAState) -> dict[str, str]:
    """일상적인 대화에 대한 LLM 답변을 생성합니다.

    Args:
        state: question을 포함한 QAState
    Returns:
        answer 키를 포함한 딕셔너리
    """
    messages = [SystemMessage(content=CASUAL_SYSTEM_PROMPT.format(question=state["question"]))]

    response = await llm.ainvoke(messages)
    return {"answer": response.content}
