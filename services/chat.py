from sqlalchemy.orm import Session
from core.exceptions.chat import ChatNotFoundException
from crud.chat import create_chat, get_chat_by_chat_id, get_chat_by_notebook_id
from models.chat import ChatModel


class ChatService:
    def get_chat(self, chat_id: int, db: Session) -> ChatModel:
        chat = get_chat_by_chat_id(db, chat_id)
        if not chat:
            raise ChatNotFoundException()
        return chat

    def get_chats_by_notebook(self, notebook_id: int, db: Session) -> list[ChatModel]:
        return get_chat_by_notebook_id(db, notebook_id)

    def create_chat(self, notebook_id: int, role: str, message: str, db: Session) -> ChatModel:
        return create_chat(db, notebook_id, role, message)


chat_service = ChatService()
