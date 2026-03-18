from typing import Literal

from pydantic import BaseModel, Field

WorkflowStatus = Literal["idle", "in_progress", "completed"]
AwaitingAction = Literal["none", "approval", "revision", "clarification"]


class ReportWorkflowRequest(BaseModel):
    notebook_id: int = Field(..., description="리포트 문서를 생성할 노트북 ID", examples=[1])
    message: str = Field(
        ...,
        description="사용자가 요청한 문서 작성 지시사항",
        examples=["시장 분석 보고서를 작성해줘. 임원 공유용으로 간결하게 정리해줘."],
    )
