from fastapi import APIRouter

from db.database import DbSession
from schemas.crawl import CrawlRequest
from schemas.response import BaseResponse
from schemas.source import SourceResponse
from services.source import source_service

router = APIRouter()


@router.post(
    "",
    response_model=BaseResponse[list[SourceResponse]],
    responses={502: {"model": BaseResponse}, 503: {"model": BaseResponse}},
)
# url, bookmark 엔드포인트 구현 시 아래 패턴을 참고
# source_service.create_from_url(url, db) → 크롤링 + source 테이블 저장
async def crawl(request: CrawlRequest, db: DbSession) -> BaseResponse[list[SourceResponse]]:
    sources = []
    for url in request.urls:
        source = await source_service.create_from_url(str(url), db)
        sources.append(source)
    return BaseResponse.ok(data=sources)
