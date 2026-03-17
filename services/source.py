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
from schemas.crawl import CrawlRequestBody
from services.crawl import crawl_service

from core.config import get_settings

settings = get_settings()


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

    def crawl_endpoint(self, body: CrawlRequestBody, settings):
        pass

    async def create_source_by_url(
        self,
        body: SourceAddRequest,
        db: Session
    ) -> SourceModel:
        source = create_source(db, body.url, body.title, body.directory_id, body.notebook_id)
        if not body.notebook_id:
            raise NotebookNotFoundException
        db.commit()

        crawl_body = CrawlRequestBody(
            urls=[body.url],
            notebook_id=body.notebook_id,
            directory_id=body.directory_id,
        )
        await crawl_service.crawl_and_save(crawl_body)

        return source


source_service = SourceService()
