from sqlalchemy.orm import Session
from models.chat import ChatModel


def create_chat(db: Session, notebook_id: int, role: str, message: str) -> ChatModel:
    new_chat = ChatModel(role=role, message=message, notebook_id=notebook_id)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


def get_chat_by_notebook_id(db: Session, notebook_id: int) -> list[ChatModel]:
    return db.query(ChatModel).filter(ChatModel.notebook_id == notebook_id).all()


def get_chat_by_chat_id(db: Session, chat_id: int) -> ChatModel | None:
    return db.query(ChatModel).filter(ChatModel.id == chat_id).first()
