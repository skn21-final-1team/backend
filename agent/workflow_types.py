from typing import Literal

WorkflowStatus = Literal["idle", "in_progress", "awaiting_review", "completed"]
AwaitingAction = Literal["none", "approval"]
WorkflowAction = Literal["", "approve", "reset", "revise"]
WorkflowStep = Literal[1, 2, 3, 4]
WorkflowStepName = Literal["requirement", "skeleton", "prepared", "final"]

WORKFLOW_STEP_BY_NAME: dict[WorkflowStepName, WorkflowStep] = {
    "requirement": 1,
    "skeleton": 2,
    "prepared": 3,
    "final": 4,
}
WORKFLOW_NAME_BY_STEP: dict[WorkflowStep, WorkflowStepName] = {
    1: "requirement",
    2: "skeleton",
    3: "prepared",
    4: "final",
}
WORKFLOW_OUTPUT_FIELD_BY_STEP: dict[WorkflowStep, str] = {
    1: "requirements_text",
    2: "outline_text",
    3: "draft_text",
    4: "final_text",
}

FINAL_WORKFLOW_STEP: WorkflowStep = 4
INITIAL_WORKFLOW_STEP: WorkflowStep = 1
