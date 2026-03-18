from __future__ import annotations

from typing import TypedDict, cast

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from agent.workflow_state import WorkflowState


class ReviewResumePayload(TypedDict):
    message: str
    source_snapshot: str


_STEP_NAME_BY_STEP = {
    1: "requirement",
    2: "skeleton",
    3: "prepared",
    4: "final",
}

_CURRENT_OUTPUT_FIELD_BY_STEP = {
    1: "requirements_text",
    2: "outline_text",
    3: "draft_text",
    4: "final_text",
}


def _get_current_output(state: WorkflowState) -> str:
    step = cast(int, state.get("step", 1))
    field_name = _CURRENT_OUTPUT_FIELD_BY_STEP[step]
    current_output = cast(str, state.get(field_name, ""))
    return current_output.strip()


async def await_user_review(state: WorkflowState, config: RunnableConfig) -> dict[str, object]:
    step = cast(int, state.get("step", 1))
    step_name = _STEP_NAME_BY_STEP[step]
    current_output = _get_current_output(state)

    resume_value = cast(ReviewResumePayload, interrupt(
        {
            "system_message": "현재 단계 결과를 검토해 주세요.",
            "content": current_output,
            "step": step,
            "step_name": step_name,
        }
    ))

    return {
        "message": resume_value["message"],
        "source_snapshot": resume_value["source_snapshot"],
    }
