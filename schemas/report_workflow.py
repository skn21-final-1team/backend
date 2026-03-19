from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

WorkflowStatus = Literal["idle", "in_progress", "awaiting_review", "completed"]
AwaitingAction = Literal["none", "approval"]
ReportWorkflowSseMessageType = Literal["thread", "step", "review", "done"]
ReportWorkflowStep = Literal[1, 2, 3, 4]


class ReportWorkflowRequest(BaseModel):
    notebook_id: int = Field(..., description="리포트 문서를 생성할 노트북 ID", examples=[1])
    message: str = Field(
        ...,
        description=(
            "새 워크플로우에서는 최초 문서 요청, 진행 중인 워크플로우에서는 현재 단계에 대한 사용자 검토 피드백"
        ),
        examples=["시장 분석 보고서를 작성해줘. 임원 공유용으로 간결하게 정리해줘."],
    )


class ReportWorkflowSsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_type: ReportWorkflowSseMessageType = Field(
        ...,
        description="SSE data payload의 분류값",
        examples=["step"],
    )
    event_name: str = Field(
        ...,
        description="SSE 이벤트 이름",
        examples=["requirement"],
    )
    system_message: str | None = Field(
        ...,
        description="LLM 또는 워크플로우가 전달하는 안내 문구",
        examples=["요구사항을 정리했습니다."],
    )
    content: str | None = Field(
        ...,
        description="실제 LLM 생성 내용",
        examples=["# 요구사항\n\n- ..."],
    )
    step: ReportWorkflowStep | None = Field(
        ...,
        description="리포트 워크플로우 단계 번호",
        examples=[1],
    )
    step_name: str | None = Field(
        ...,
        description="리포트 워크플로우 단계 이름",
        examples=["requirement"],
    )
    mode: Literal["start", "resume"] | None = Field(
        ...,
        description="thread 이벤트의 시작/재개 여부",
        examples=["start"],
    )


class ReportWorkflowStepOutputs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirements_text: str = Field(
        ...,
        description="요구사항 분석 단계의 산출물",
        examples=["# 요구사항\n\n- 시장 분석 보고서 작성\n- 임원 공유용으로 간결한 톤 유지"],
    )
    outline_text: str = Field(
        ...,
        description="문서 구조 초안 단계의 산출물",
        examples=["# 개요\n\n1. 시장 현황\n2. 핵심 인사이트\n3. 실행 제안"],
    )
    draft_text: str = Field(
        ...,
        description="초안 작성 단계의 산출물",
        examples=["# 초안\n\n시장 분석 결과, 올해의 주요 변화는 ..."],
    )
    final_text: str = Field(
        ...,
        description="최종 작성 단계의 산출물",
        examples=["# 최종본\n\n시장 분석 보고서"],
    )


class ReportWorkflowStateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_status: WorkflowStatus = Field(
        ...,
        description="현재 워크플로우의 진행 상태. `idle`이면 아직 시작되지 않았거나 복원할 진행 정보가 없는 상태를 의미한다.",
        examples=["idle", "awaiting_review"],
    )
    current_step: ReportWorkflowStep | None = Field(
        ...,
        description="현재 워크플로우 단계 번호. 값이 없으면 아직 시작되지 않은 상태를 의미한다.",
        examples=[None, 2],
    )
    step_outputs: ReportWorkflowStepOutputs = Field(
        ...,
        description="단계별 산출물 스냅샷. 프론트는 이 값으로 새로고침 후 각 단계 내용을 복원한다.",
    )
