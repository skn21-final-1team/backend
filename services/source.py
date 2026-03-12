from collections.abc import Sequence

from sqlalchemy.orm import Session

from core.exceptions.source import SourceNotFoundException
from core.exceptions.notebook import NotebookNotFoundException

from crud.source import (
    delete_source_by_source_id,
    get_sources_by_notebook,
    update_source,
    create_source
)
from models.source import SourceModel
from schemas.source import SourceUpdateRequest, SourceAddRequest


class SourceService:
    def get_sources_by_notebook(self, notebook_id: int, db: Session) -> Sequence[SourceModel]:
        return get_sources_by_notebook(db, notebook_id)

    def delete_source(self, source_id: int, db: Session) -> SourceModel:
        source = delete_source_by_source_id(db, source_id)
        if not source:
            raise SourceNotFoundException
        return source

    def update_source_data(
        self,
        source_id: int,
        body: SourceUpdateRequest,
        db: Session,
    ) -> SourceModel:
        source = update_source(db, source_id, body.title, body.is_active)
        if not source:
            raise SourceNotFoundException
        return source

    def create_source_by_url(
        self,
        notebook_id: int,
        body: SourceAddRequest,
        db: Session
    ) -> SourceModel:
        source = create_source(db, body.url, body.title, body.directory_id, notebook_id)
        if not notebook_id:
            raise NotebookNotFoundException
        db.commit()
        return source


source_service = SourceService()
