from fastapi import APIRouter

from db.database import DbSession

from schemas.source import SourceResponse, SourceUpdateRequest
from schemas.response import BaseResponse
from services.source import source_service

router = APIRouter()

@router.get(
    "/{notebook_id}",
    response_model=BaseResponse[list[SourceResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_sources_by_notebook(notebook_id: int, db: DbSession) -> BaseResponse[SourceResponse]:
    """notebook id로 모든 소스를 조회합니다."""
    return BaseResponse.ok(source_service.get_sources_by_notebook(notebook_id, db))


@router.patch(
    "/{source_id}",
    response_model=BaseResponse[SourceResponse],
    responses={404: {"model": BaseResponse}},
)
def update_source(source_id: int, body: SourceUpdateRequest, db: DbSession) -> BaseResponse[SourceResponse]:
    """주어진 소스 ID에 해당하는 소스의 타이틀을 수정합니다."""
    return BaseResponse.ok(source_service.update_source_title(source_id, body.title, db))

@router.delete(
    "/{source_id}",
    response_model=BaseResponse[SourceResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_source(source_id: int, db: DbSession) -> BaseResponse[SourceResponse]:
    """주어진 소스 ID에 해당하는 소스를 삭제합니다."""
    return BaseResponse.ok(source_service.delete_source(source_id, db))
