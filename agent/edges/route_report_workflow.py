import logging

from langgraph.graph import END

from agent.workflow_state import WorkflowState
from agent.workflow_types import FINAL_WORKFLOW_STEP, WORKFLOW_NAME_BY_STEP

logger = logging.getLogger(__name__)


def route_report_workflow(state: WorkflowState) -> str:
    action = state["action"].strip().lower()
    step = state["step"]

    if action == "reset":
        target = "filter_source"
    elif action == "revise":
        target = WORKFLOW_NAME_BY_STEP[step]
    elif action == "approve":
        target = END if step >= FINAL_WORKFLOW_STEP else WORKFLOW_NAME_BY_STEP[step + 1]
    elif action == "except":
        target = "await_user_review"
    else:
        target = WORKFLOW_NAME_BY_STEP[step]

    print(f"route_report_workflow resolved route action={action} step={step} target={target}")
    return target
