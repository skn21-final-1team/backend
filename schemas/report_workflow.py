from typing import Literal

from pydantic import BaseModel, Field

WorkflowStatus = Literal["idle", "in_progress", "awaiting_review", "completed"]
AwaitingAction = Literal["none", "approval"]


class ReportWorkflowRequest(BaseModel):
    notebook_id: int = Field(..., description="리포트 문서를 생성할 노트북 ID", examples=[1])
    message: str = Field(
        ...,
        description="새 워크플로우에서는 최초 문서 요청, 진행 중인 워크플로우에서는 현재 단계에 대한 사용자 검토 피드백",
        examples=["시장 분석 보고서를 작성해줘. 임원 공유용으로 간결하게 정리해줘."],
    )
