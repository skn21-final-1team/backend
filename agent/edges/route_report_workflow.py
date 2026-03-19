import logging

from langgraph.graph import END

from agent.workflow_state import WorkflowState

logger = logging.getLogger(__name__)


_STEP_NODE_BY_STEP = {
    1: "requirement",
    2: "skeleton",
    3: "prepared",
    4: "final",
}

_FINAL_STEP = 4


def route_report_workflow(state: WorkflowState) -> str:
    action = state["action"].strip().lower()
    step = state["step"]

    if action == "reset":
        target = "requirement"
    elif action == "revise":
        target = _STEP_NODE_BY_STEP[step]
    elif action == "approve":
        target = END if step >= _FINAL_STEP else _STEP_NODE_BY_STEP[step + 1]
    else:
        target = _STEP_NODE_BY_STEP[step]

    print(f"route_report_workflow resolved route action={action} step={step} target={target}")
    return target
