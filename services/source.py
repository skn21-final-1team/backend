from collections.abc import Sequence

from sqlalchemy.orm import Session

from core.exceptions.source import SourceNotFoundException
from crud.source import (
    get_sources_by_notebook,
    delete_source_by_source_id,
    update_source_title,
)
from models.source import SourceModel


class SourceService:
    def get_sources_by_notebook(self, notebook_id: int, db: Session) -> Sequence[SourceModel]:
        return get_sources_by_notebook(db, notebook_id)

    def delete_source(self, source_id: int, db: Session) -> SourceModel:
        source = delete_source_by_source_id(db, source_id)
        if not source:
            raise SourceNotFoundException
        return source

    def update_source_title(self, source_id: int, title: str, db: Session) -> SourceModel:
        source = update_source_title(db, source_id, title)
        if not source:
            raise SourceNotFoundException
        return source


source_service = SourceService()
