from sqlalchemy.orm import Session
from core.exceptions.notebook import NotebookNotFoundException
from crud.notebook import (
    create_notebook,
    delete_notebook,
    get_notebook,
    get_notebooks_by_user_id,
    update_notebook_title,
)
from models.notebook import NotebookModel

class NotebookService:
    def get_notebook(self, notebook_id: int, db: Session) -> NotebookModel:
        notebook = get_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException()
        return notebook

    def get_notebooks_by_user(self, user_id: int, db: Session) -> list[NotebookModel]:
        return get_notebooks_by_user_id(db, user_id)

    def create_notebook(self, user_id: int, title: str, db: Session) -> NotebookModel:
        return create_notebook(db, user_id, title) 

    def update_notebook_title(self, notebook_id: int, title: str, db: Session) -> NotebookModel:
        notebook = update_notebook_title(db, notebook_id, title)
        if not notebook:
            raise NotebookNotFoundException()
        return notebook

    def delete_notebook(self, notebook_id: int, db: Session) -> NotebookModel:
        notebook = delete_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException()
        return notebook

notebook_service = NotebookService()
