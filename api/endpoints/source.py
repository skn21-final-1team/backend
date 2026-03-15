from fastapi import APIRouter

from db.database import DbSession
from schemas.response import BaseResponse
from schemas.source import SourceResponse, SourceUpdateRequest, SourceAddRequest
from schemas.crawl import CrawlRequestBody

from services.source import source_service
from services.crawl import crawl_service

router = APIRouter()


@router.post(
    "/add",
    response_model=BaseResponse[SourceResponse],
    responses={404: {"model": BaseResponse}},
)
async def create_source(body: SourceAddRequest, db: DbSession) -> BaseResponse[SourceResponse]:
    """입력한 URL에 해당하는 소스를 추가합니다."""
    def create_source_with_url(body: SourceAddRequest, db: DbSession) -> BaseResponse[SourceResponse]:
        return BaseResponse.ok(source_service.create_source_by_url(body, db))
    @public
    async def crawl(body: CrawlRequestBody) -> BaseResponse[bool]:
        result = await crawl_service.crawl_and_save(body)
        return BaseResponse.ok(data=result)


@router.patch(
    "/{source_id}",
    response_model=BaseResponse[SourceResponse],
    responses={404: {"model": BaseResponse}},
)
def update_source(source_id: int, body: SourceUpdateRequest, db: DbSession) -> BaseResponse[SourceResponse]:
    """주어진 소스 ID에 해당하는 소스를 수정합니다."""
    print(source_id)
    return BaseResponse.ok(source_service.update_source_data(source_id, body, db))


@router.delete(
    "/{source_id}",
    response_model=BaseResponse[SourceResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_source(source_id: int, db: DbSession) -> BaseResponse[SourceResponse]:
    """주어진 소스 ID에 해당하는 소스를 삭제합니다."""
    return BaseResponse.ok(source_service.delete_source(source_id, db))
