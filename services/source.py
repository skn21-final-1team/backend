from sqlalchemy.orm import Session

from crud.source import create_source
from models.source import SourceModel
from services.crawl import crawl_service


class SourceService:
    # url, bookmark 엔드포인트에서 이 메서드를 호출하여 크롤링 + DB 저장
    async def create_from_url(self, url: str, db: Session) -> SourceModel:
        result = await crawl_service.crawl(url)
        return create_source(db, url=result.url, title=result.title, summary=result.summary)


source_service = SourceService()
