from typing import Literal, TypedDict

from schemas.report_workflow import AwaitingAction, WorkflowStatus

WorkflowAction = Literal["approve", "reset", "revise", "answer_clarification"]
WorkflowStep = Literal[1, 2, 3, 4]


class WorkflowState(TypedDict, total=False):
    # 그래프 실행에 필요한 입력 상태
    notebook_id: int
    message: str

    # 현재 워크플로우 진행 위치와 다음 행동을 결정하는 상태
    status: WorkflowStatus
    step: WorkflowStep
    awaiting_action: AwaitingAction
    action: WorkflowAction

    # 문서 생성의 근거가 되는 source
    source_snapshot: str

    # 단계별 산출물
    requirements_text: str
    outline_text: str
    draft_text: str
    final_text: str

    # 사용자 요청 흐름과 승인 이력을 유지하는 상태
    last_user_request: str
    last_revision_request: str
    last_approved_step: WorkflowStep

    # 추가 확인이 필요한 질문을 유지하는 상태
    clarification_questions: list[str]

    # 현재 작업 결과를 사용자에게 알리기 위한 상태
    system_message: str
