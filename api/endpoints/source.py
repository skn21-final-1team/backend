from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from core.auth_guard import public
from db.database import DbSession
from schemas.crawl import CrawlCallbackEvent
from schemas.response import BaseResponse
from schemas.source import SourceResponse, SourceUpdateRequest, SourceAddRequest, SourceUpdateBatchRequest
from services.event_broker import event_broker
from services.source import source_service

router = APIRouter()


@router.post(
    "/add",
    response_model=BaseResponse[SourceResponse],
    responses={404: {"model": BaseResponse}},
)
async def create_source(body: SourceAddRequest, db: DbSession) -> BaseResponse[SourceResponse]:
    """입력한 URL에 해당하는 소스를 추가합니다."""
    return BaseResponse.ok(await source_service.create_source_by_url(body, db))


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


@router.post("/callback")
@public
async def crawl_callback(body: CrawlCallbackEvent) -> dict:
    """Crawl 서버에서 호출하는 webhook 콜백. 이벤트를 SSE 구독자에게 전달합니다."""
    await event_broker.publish(body.model_dump())
    return {"status": "ok"}


@router.get("/stream")
async def source_stream() -> StreamingResponse:
    """SSE 스트림. 프론트엔드가 crawl 이벤트를 실시간으로 수신합니다."""
    return StreamingResponse(event_broker.subscribe(), media_type="text/event-stream")


@router.patch(
    "/{notebook_id}/active",
    response_model=BaseResponse[list[SourceResponse]],
    responses={404: {"model": BaseResponse}},
)
def active_all_sources(
    notebook_id: int, body: SourceUpdateBatchRequest, db: DbSession
) -> BaseResponse[list[SourceResponse]]:
    """주어진 notebook ID에 속한 모든 소스의 활성화 상태를 일괄 변경합니다."""
    return BaseResponse.ok(source_service.active_all_sources(notebook_id, body, db))
