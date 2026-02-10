from sqlalchemy.orm import Session

from core.exceptions.chat import ChatNotFoundException
from crud.chat import get_chat_by_id
from models.chat import Chat
from schemas.chat import ChatRequest

class ChatService:
    def get_chat(self, chat_id: int, db: Session) -> Chat:
        chat = get_chat_by_id(db, chat_id)
        if not chat:
            raise ChatNotFoundException()
        return chat


ChatService = ChatService()