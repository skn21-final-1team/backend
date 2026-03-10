from sqlalchemy.orm import Session

from core.exceptions.source import SourceNotFoundException
from crud.source import create_source, get_sources_by_notebook, delete_source_by_source_id
from models.source import SourceModel


class SourceService:
    def get_sources(self, source_id: int, db: Session) -> SourceModel:
        pass
source_service = SourceService()