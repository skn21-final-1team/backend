from sqlalchemy.orm import Session

from core.exceptions.chat import ChatNotFoundException
from models.chat import ChatModel
from models.notebook import NotebookModel

from crud.chat import get_chat_by_chat_id
from schemas.chat import ChatRequest

class ChatService:
    def get_chat(self, chat_id: int, db: Session) -> Chat:
        chat = get_chat_by_id(db, chat_id)
        if not chat:
            raise ChatNotFoundException()
        return chat


ChatService = ChatService()