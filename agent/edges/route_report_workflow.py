from langgraph.graph import END

from agent.workflow_state import WorkflowState


_STEP_NODE_BY_STEP = {
    1: "requirement",
    2: "skeleton",
    3: "prepared",
    4: "final",
}

_NEXT_NODE_BY_STEP = {
    1: "skeleton",
    2: "prepared",
    3: "final",
}


def route_report_workflow(state: WorkflowState) -> str:
    action = str(state.get("action", "")).strip().lower()
    step = int(state.get("step") or 1)

    if action == "reset":
        return "requirement"

    if action == "revise":
        return _STEP_NODE_BY_STEP.get(step, "requirement")

    if action == "approve":
        if step >= 4:
            return END
        return _NEXT_NODE_BY_STEP.get(step, "requirement")

    return _STEP_NODE_BY_STEP.get(step, "requirement")
