from agent.state import QAState
from crud.chat import create_chat
from db.database import SessionLocal


def save_chat(state: QAState) -> dict[str, str]:
    """유저 질문과 AI 답변을 DB에 저장합니다.

    Args:
        state: notebook_id, question, answer를 포함한 QAState
    Returns:
        answer 키를 포함한 딕셔너리
    """
    db = SessionLocal()
    try:
        create_chat(db, notebook_id=state["notebook_id"], role="user", message=state["question"])
        create_chat(db, notebook_id=state["notebook_id"], role="assistant", message=state["answer"])
        return {"answer": state["answer"]}
    finally:
        db.close()
