import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from db.database import DbSession
from schemas.report_workflow import (
    ReportWorkflowRequest,
    ReportWorkflowSsePayload,
    ReportWorkflowStepOutputs,
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

_REPORT_WORKFLOW_RESET_RESPONSE_EXAMPLE = BaseResponse.ok(
    data=ReportWorkflowStateResponse(
        workflow_status="idle",
        current_step=None,
        step_outputs=ReportWorkflowStepOutputs(
            requirements_text="",
            outline_text="",
            draft_text="",
            final_text="",
        ),
    ).model_dump(mode="json"),
    message="리포트 워크플로우 상태를 초기화했습니다.",
).model_dump(mode="json")


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
        },
        409: {"description": "해당 노트북의 리포트 워크플로우가 이미 실행 중인 경우"},
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


@router.delete(
    "/{notebook_id}/state",
    summary="리포트 워크플로우 상태 초기화",
    description=(
        "노트북 ID 기준으로 report-workflow의 체크포인트와 모든 상태를 삭제한다. "
        "초기화가 끝나면 `workflow_status`는 `idle`, `current_step`은 `null`, "
        "단계별 산출물은 모두 빈 문자열로 복원되며, 응답 구조는 상태조회 GET과 동일한 "
        "`ReportWorkflowStateResponse`를 사용한다."
    ),
    response_model=BaseResponse[ReportWorkflowStateResponse],
    responses={
        200: {
            "description": (
                "워크플로우 상태를 초기화한 뒤, 상태조회 GET과 동일한 "
                "`ReportWorkflowStateResponse` 구조를 반환한다. "
                "`data`는 `workflow_status=idle`, `current_step=null`, "
                "`step_outputs`의 모든 필드가 빈 문자열인 상태다."
            ),
            "content": {
                "application/json": {
                    "example": _REPORT_WORKFLOW_RESET_RESPONSE_EXAMPLE,
                }
            },
        },
        404: {"description": "존재하지 않는 노트북이거나 상태를 초기화할 수 없는 경우"},
    },
)
def reset_report_workflow(notebook_id: int, db: DbSession) -> BaseResponse[ReportWorkflowStateResponse]:
    return BaseResponse.ok(
        report_service.reset_report_workflow(notebook_id, db),
        message="리포트 워크플로우 상태를 초기화했습니다.",
    )
