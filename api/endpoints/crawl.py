from fastapi import APIRouter

from core.security import CurrentUser
from db.database import DbSession
from schemas.crawl import CrawlRequest
from schemas.response import BaseResponse
from schemas.source import SourceResponse
from services.source import source_service

router = APIRouter()


@router.post(
    "/",
    response_model=BaseResponse[list[SourceResponse]],
    responses={502: {"model": BaseResponse}, 503: {"model": BaseResponse}, 401: {"model": BaseResponse}},
)
async def crawl(request: CrawlRequest, db: DbSession, user: CurrentUser) -> BaseResponse[list[SourceResponse]]:
    sources = []
    for url in request.urls:
        source = await source_service.create_from_url(str(url), db)
        sources.append(source)
    return BaseResponse.ok(data=sources)
