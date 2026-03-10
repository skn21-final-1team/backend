from fastapi import APIRouter

from db.database import DbSession

from schemas.services import service 
from schemas.response import SourceResponse, SourceRequest
from services.source import source_service

router = APIRouter()


@router.post("")
async def run_agent(req: ChatRequest, db: DbSession) -> StreamingResponse:
    """그래프 실행 과정과 모델 출력을 SSE 프레임으로 스트리밍합니다"""
    return StreamingResponse(agent_service.stream_chat(req, db), media_type="text/event-stream")


@router.get(
    "/{chat_id}",
    response_model=BaseResponse[ChatResponse],
    responses={404: {"model": BaseResponse}},
)
def get_chat(chat_id: int, db: DbSession) -> BaseResponse[ChatResponse]:
    """채팅 ID로 단일 채팅 항목을 조회합니다."""
    return BaseResponse.ok(chat_service.get_chat(chat_id, db))


@router.get(
    "/notebook/{notebook_id}",
    response_model=BaseResponse[list[ChatResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_chats_by_notebook(notebook_id: int, db: DbSession) -> BaseResponse[list[ChatResponse]]:
    """주어진 노트북 ID에 속한 모든 채팅을 조회합니다."""
    return BaseResponse.ok(chat_service.get_chats_by_notebook(notebook_id, db))
