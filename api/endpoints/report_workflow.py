import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from db.database import DbSession
from schemas.report_workflow import (
    ReportWorkflowRequest,
    ReportWorkflowSsePayload,
    ReportWorkflowStateResponse,
)
from schemas.response import BaseResponse
from services.report import report_service

router = APIRouter()

_REPORT_WORKFLOW_STEP_EVENT_EXAMPLE = ReportWorkflowSsePayload(
    message_type="step",
    event_name="requirement",
    system_message="요구사항 분석을 완료했습니다. 내용을 검토해 주세요.",
    content="# 요구사항\n\n- 시장 분석 보고서 작성\n- 임원 공유용 간결한 톤 유지",
    step=1,
    step_name="requirement",
    mode=None,
).model_dump(mode="json", exclude_none=False)

_REPORT_WORKFLOW_STEP_STREAM_EXAMPLE = (
    f"event: requirement\ndata: {json.dumps(_REPORT_WORKFLOW_STEP_EVENT_EXAMPLE, ensure_ascii=False)}\n\n"
)


@router.post(
    "/stream",
    summary="리포트 문서 작성 워크플로우 실행",
    description=(
        "새 워크플로우를 시작하거나 기존 thread를 resume하여, "
        "LangGraph interrupt 기반 사용자 검토 루프와 함께 구조화된 JSON SSE payload를 스트리밍합니다. "
        "각 payload는 `system_message`와 `content`를 분리해서 전달합니다."
    ),
    response_class=StreamingResponse,
    responses={
        200: {
            "description": (
                "각 워크플로우 노드가 생성한 구조화 payload를 `text/event-stream` 형식으로 전달합니다. "
                "각 SSE 이벤트의 `data:` 라인은 `ReportWorkflowSsePayload` 구조의 JSON 문자열입니다."
            ),
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "description": (
                            "SSE 스트림 본문. 각 `data:` 라인은 "
                            "`ReportWorkflowSsePayload` JSON payload를 담습니다."
                        ),
                    },
                    "example": _REPORT_WORKFLOW_STEP_STREAM_EXAMPLE,
                }
            },
        }
    },
)
async def run_report_workflow(req: ReportWorkflowRequest, db: DbSession) -> StreamingResponse:
    return StreamingResponse(report_service.stream_report(req, db), media_type="text/event-stream")


@router.get(
    "/{notebook_id}",
    summary="리포트 워크플로우 현재 상태 조회",
    description=(
        "노트북 ID 기준으로 현재 report-workflow 상태를 조회한다. "
        "프론트엔드는 이 응답의 최소 필드만 사용해 새로고침 이후 현재 단계와 단계별 산출물을 복원할 수 있다."
    ),
    response_model=BaseResponse[ReportWorkflowStateResponse],
    responses={
        200: {
            "description": (
                "현재 워크플로우 스냅샷을 반환한다. "
                "`data`에는 `workflow_status`, `current_step`, `step_outputs`만 포함된다."
            )
        },
        404: {"description": "존재하지 않는 노트북이거나 상태를 조회할 수 없는 경우"},
    },
)
def get_report_workflow_state(notebook_id: int, db: DbSession) -> BaseResponse[ReportWorkflowStateResponse]:
    return BaseResponse.ok(report_service.get_report_workflow_state(notebook_id, db))
