from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

WorkflowStatus = Literal["idle", "in_progress", "awaiting_review", "completed"]
AwaitingAction = Literal["none", "approval"]
ReportWorkflowSseMessageType = Literal["thread", "step", "review", "done"]


class ReportWorkflowRequest(BaseModel):
    notebook_id: int = Field(..., description="리포트 문서를 생성할 노트북 ID", examples=[1])
    message: str = Field(
        ...,
        description=(
            "새 워크플로우에서는 최초 문서 요청, "
            "진행 중인 워크플로우에서는 현재 단계에 대한 사용자 검토 피드백"
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
    step: int | None = Field(
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
