from sqlalchemy.orm import Session
from models.chat import NotebookModel, ChatModel

def create_notebook(db: Session, notebook_id: int) -> NotebookModel:
    new_notebook = NotebookModel(id=notebook_id)
    db.add(new_notebook)
    db.commit()
    db.refresh(new_notebook)
    return new_notebook

def update_notebook_title(db: Session, notebook_id: int, title: str) -> NotebookModel:
    notebook = db.query(NotebookModel).filter(NotebookModel.id == notebook_id).first()
    if not notebook:
        raise NotebookNotFoundException()
    notebook.title = title
    db.commit()
    db.refresh(notebook)
    return notebook

def create_chat(db: Session, notebook_id: int, role: str, message:str) -> ChatModel:
    new_chat = ChatModel(role=role, message=message, notebook_id=notebook_id)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

def get_chat_by_notebook_id(db: Session, notebook_id: int) -> List[ChatModel]:
    return [chat for chat in db.query(ChatModel).filter(ChatModel.notebook_id == notebook_id).all()]

def get_chat_by_chat_id(db: Session, chat_id: int) -> ChatModel:
    return db.query(ChatModel).filter(ChatModel.id == chat_id).first()