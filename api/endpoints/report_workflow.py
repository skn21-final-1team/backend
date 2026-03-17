from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from db.database import DbSession
from schemas.report_workflow import (
    ReportWorkflowResetResponse,
    ReportWorkflowResponse,
    ReportWorkflowStreamRequest,
)
from schemas.response import BaseResponse
from services.report_workflow import report_workflow_service

router = APIRouter()


@router.post(
    "/stream",
    summary="보고서 워크플로우 단계 스트리밍",
    description="에이전트의 최신 메시지를 워크플로우에 저장하고, 서버 전송 이벤트(SSE)를 스트리밍합니다.",
    responses={
        200: {
            "description": "저장된 상태와 생성된 콘텐츠 청크를 전달하는 서버 전송 이벤트 응답입니다.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def stream_report_workflow(req: ReportWorkflowStreamRequest, db: DbSession) -> StreamingResponse:
    """에이전트가 진행한 워크플로우 단계를 저장하고 완료될 때까지 서버 전송 이벤트를 스트리밍합니다."""
    return StreamingResponse(report_workflow_service.stream_workflow(req, db), media_type="text/event-stream")


@router.get(
    "/notebook/{notebook_id}",
    response_model=BaseResponse[ReportWorkflowResponse],
    summary="최신 보고서 워크플로우 조회",
    description="데이터를 생성하거나 변경하지 않고, 해당 노트북의 가장 최근 워크플로우 스냅샷을 반환합니다.",
    response_description="상태, 단계별 텍스트, 타임스탬프를 포함한 워크플로우 스냅샷 응답입니다.",
)
def get_report_workflow(notebook_id: int, db: DbSession) -> BaseResponse[ReportWorkflowResponse]:
    """데이터 변경 없이 노트북의 최신 워크플로우 상태를 반환합니다."""
    return BaseResponse.ok(report_workflow_service.get_workflow(notebook_id, db))


@router.post(
    "/notebook/{notebook_id}/reset",
    response_model=BaseResponse[ReportWorkflowResetResponse],
    summary="보고서 워크플로우 초기화",
    description="노트북 워크플로우를 강제로 취소 상태로 변경하고, 초기화 이력을 저장한 뒤 결과를 반환합니다.",
    response_description="워크플로우가 취소되었음을 나타내는 응답입니다.",
)
def reset_report_workflow(notebook_id: int, db: DbSession) -> BaseResponse[ReportWorkflowResetResponse]:
    """워크플로우를 강제로 취소 상태로 전환하고 초기화 이력을 저장합니다."""
    return BaseResponse.ok(report_workflow_service.reset_workflow(notebook_id, db))
