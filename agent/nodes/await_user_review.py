from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from agent.workflow_state import WorkflowState


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

_ALLOWED_ACTIONS = ["approve", "revise", "reset"]


def _format_current_output(state: WorkflowState) -> str:
    step = int(state.get("step") or 1)
    field_name = _CURRENT_OUTPUT_FIELD_BY_STEP.get(step, "requirements_text")
    current_output = state.get(field_name)
    if isinstance(current_output, str) and current_output.strip():
        return current_output.strip()
    return "없음"


def _build_review_markdown(state: WorkflowState) -> tuple[dict[str, Any], str]:
    step = int(state.get("step") or 1)
    step_name = _STEP_NAME_BY_STEP.get(step, "requirement")
    current_output = _format_current_output(state)

    markdown = "\n".join(
        [
            "## Review Needed",
            f"- step: `{step}`",
            f"- step_name: `{step_name}`",
            "",
            "### Current Output",
            current_output,
            "",
            "### Available Actions",
            "- `approve`: 다음 단계로 진행",
            "- `revise`: 현재 단계 재생성",
            "- `reset`: 1단계부터 다시 시작",
        ]
    )

    payload = {
        "markdown": markdown,
        "step": step,
        "step_name": step_name,
        "allowed_actions": list(_ALLOWED_ACTIONS),
    }
    return payload, markdown


def _extract_resume_message(resume_value: Any) -> str:
    if isinstance(resume_value, str):
        return resume_value.strip()

    if isinstance(resume_value, dict):
        for key in ("message", "feedback", "response", "text"):
            value = resume_value.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return str(resume_value).strip()


async def await_user_review(state: WorkflowState, config: RunnableConfig) -> dict[str, object]:
    review_payload, _ = _build_review_markdown(state)
    resume_value = interrupt(review_payload)
    user_feedback = _extract_resume_message(resume_value)

    updates: dict[str, object] = {"message": user_feedback}
    if isinstance(resume_value, dict):
        source_snapshot = resume_value.get("source_snapshot")
        if isinstance(source_snapshot, str) and source_snapshot.strip():
            updates["source_snapshot"] = source_snapshot
    return updates
