from __future__ import annotations

from langgraph.types import interrupt

from agent.workflow_state import WorkflowState
from agent.workflow_types import WORKFLOW_NAME_BY_STEP, WORKFLOW_OUTPUT_FIELD_BY_STEP


def _get_current_output(state: WorkflowState) -> str:
    step = state["step"]
    field_name = WORKFLOW_OUTPUT_FIELD_BY_STEP[step]
    return state[field_name].strip() or "없음"


async def await_user_review(state: WorkflowState) -> dict[str, object]:
    step = state["step"]
    step_name = WORKFLOW_NAME_BY_STEP[step]
    current_output = _get_current_output(state)

    resume_value = interrupt(
        {
            "system_message": state["system_message"],
            "content": current_output,
            "step": step,
            "step_name": step_name,
        }
    )

    return {
        "message": resume_value["message"],
        "source_snapshot": resume_value["source_snapshot"],
    }
