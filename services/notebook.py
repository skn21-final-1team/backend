from collections.abc import Sequence

from sqlalchemy.orm import Session

from core.exceptions.notebook import NotebookNotFoundException
from crud.notebook import (
    create_notebook,
    delete_notebook,
    get_notebook,
    get_notebooks_by_user_id,
    update_notebook,
)
from models.notebook import NotebookModel
from models.source import SourceModel
from schemas.notebook import NotebookSortType, NotebookUpdateBody
from schemas.source import SourceUpdateBatchRequest
from services.source import source_service


class NotebookService:
    def get_notebook(self, notebook_id: int, db: Session) -> NotebookModel:
        notebook = get_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException
        return notebook

    def get_notebooks_by_user(
        self,
        user_id: int,
        db: Session,
        sort_type: NotebookSortType = NotebookSortType.RECENT_CREATED,
    ) -> list[NotebookModel]:
        return get_notebooks_by_user_id(db, user_id, sort_type)

    def create_notebook(self, user_id: int, title: str, db: Session) -> NotebookModel:
        return create_notebook(db, user_id, title)

    def update_notebook(self, notebook_id: int, body: NotebookUpdateBody, db: Session) -> NotebookModel:
        notebook = update_notebook(db, notebook_id, body)
        if not notebook:
            raise NotebookNotFoundException
        return notebook

    def delete_notebook(self, notebook_id: int, db: Session) -> NotebookModel:
        notebook = delete_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException
        return notebook

    def active_all_sources(
        self, notebook_id: int, body: SourceUpdateBatchRequest, db: Session
    ) -> Sequence[SourceModel]:
        notebook = get_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException
        return source_service.active_all_sources(notebook_id, body, db)


notebook_service = NotebookService()
