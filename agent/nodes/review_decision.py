from __future__ import annotations

from typing import cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from agent.model.llm_factory import llm_factory
from agent.prompts.report_review import REVIEW_DECISION_SYSTEM_PROMPT, REVIEW_DECISION_USER_PROMPT
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

_FINAL_STEP = 4


class ReviewDecisionPayload(BaseModel):
    action: str = Field(description="approve, revise, reset 중 하나")
    reason: str = Field(description="판정 근거")
    next_step: int = Field(description="권장 다음 단계 번호")


def _normalize_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return "\n".join(str(item) for item in content).strip()
    return str(content).strip()


def _build_current_output(state: WorkflowState) -> str:
    step = int(state.get("step") or 1)
    field_name = cast(str, _CURRENT_OUTPUT_FIELD_BY_STEP.get(step, "requirements_text"))
    current_output = state.get(field_name)
    if isinstance(current_output, str) and current_output.strip():
        return current_output.strip()
    return "없음"


def _build_snapshot_text(state: WorkflowState) -> str:
    fields = [
        ("status", state.get("status")),
        ("step", state.get("step")),
        ("awaiting_action", state.get("awaiting_action")),
        ("last_user_request", state.get("last_user_request")),
        ("last_revision_request", state.get("last_revision_request")),
        ("last_approved_step", state.get("last_approved_step")),
        ("source_snapshot", state.get("source_snapshot")),
        ("requirements_text", state.get("requirements_text")),
        ("outline_text", state.get("outline_text")),
        ("draft_text", state.get("draft_text")),
        ("final_text", state.get("final_text")),
    ]
    lines = ["# Workflow Snapshot"]
    for key, value in fields:
        if value is None or value == "":
            continue
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


async def review_decision(state: WorkflowState, config: RunnableConfig) -> dict[str, object]:
    step = int(state.get("step") or 1)
    step_name = _STEP_NAME_BY_STEP.get(step, "requirement")
    current_output = _build_current_output(state)
    workflow_snapshot = _build_snapshot_text(state)

    llm = llm_factory.get_llm(config).with_structured_output(
        ReviewDecisionPayload,
        method="json_schema",
        strict=True,
    )
    payload = await llm.ainvoke(
        [
            SystemMessage(content=REVIEW_DECISION_SYSTEM_PROMPT),
            HumanMessage(
                content=REVIEW_DECISION_USER_PROMPT.format(
                    message=state.get("message", ""),
                    step=step,
                    step_name=step_name,
                    current_output=current_output,
                    workflow_snapshot=workflow_snapshot,
                )
            ),
        ]
    )

    action = payload.action.strip().lower()
    if action not in {"approve", "revise", "reset"}:
        error_message = f"review_decision returned unsupported action: {payload.action}"
        raise ValueError(error_message)

    reason = _normalize_text(payload.reason)
    next_step = int(payload.next_step)

    summary = "\n".join(
        [
            "## Review Decision",
            f"- action: `{action}`",
            f"- step: `{step}`",
            f"- reason: {reason}",
            f"- next_step: `{next_step}`",
        ]
    )

    updates: dict[str, object] = {
        "action": action,
        "status": "completed" if action == "approve" and step >= _FINAL_STEP else "in_progress",
        "awaiting_action": "none",
        "system_message": summary,
    }
    if action == "approve":
        updates["last_approved_step"] = step
    elif action == "reset":
        updates["step"] = 1
        updates["last_user_request"] = state.get("message", "")
        updates["last_revision_request"] = ""
    else:
        updates["last_revision_request"] = state.get("message", "")
    return updates
