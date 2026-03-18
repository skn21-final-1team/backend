from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from db.database import DbSession
from schemas.report_workflow import ReportWorkflowRequest
from services.report import report_service

router = APIRouter()


@router.post(
    "/stream",
    summary="리포트 문서 작성 워크플로우 실행",
    description="새 워크플로우를 시작하거나 기존 thread를 resume하여, LangGraph interrupt 기반 사용자 검토 루프와 함께 현재 차례의 마크다운 결과를 SSE로 스트리밍합니다.",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "각 워크플로우 노드가 생성한 마크다운 결과를 SSE로 전달합니다.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def run_report_workflow(req: ReportWorkflowRequest, db: DbSession) -> StreamingResponse:
    return StreamingResponse(report_service.stream_report(req, db), media_type="text/event-stream")
