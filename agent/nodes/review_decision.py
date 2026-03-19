from __future__ import annotations

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


def _build_current_output(state: WorkflowState) -> str:
    step = state["step"]
    field_name = _CURRENT_OUTPUT_FIELD_BY_STEP[step]
    current_output = state[field_name].strip()
    if current_output:
        return current_output
    return "없음"


def _build_snapshot_text(state: WorkflowState) -> str:
    fields = [
        ("status", state["status"]),
        ("step", state["step"]),
        ("awaiting_action", state["awaiting_action"]),
        ("last_user_request", state["last_user_request"]),
        ("last_revision_request", state["last_revision_request"]),
        ("last_approved_step", state["last_approved_step"]),
        ("source_snapshot", state["source_snapshot"]),
        ("requirements_text", state["requirements_text"]),
        ("outline_text", state["outline_text"]),
        ("draft_text", state["draft_text"]),
        ("final_text", state["final_text"]),
    ]
    lines = ["# Workflow Snapshot"]
    for key, value in fields:
        if value is None or value == "":
            continue
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


async def review_decision(state: WorkflowState, config: RunnableConfig) -> dict[str, object]:
    step = state["step"]
    step_name = _STEP_NAME_BY_STEP[step]
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
                    message=state["message"],
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

    reason = payload.reason
    next_step = int(payload.next_step)

    print(
        f"review decision resolved: step={step}, step_name={step_name}, "
        f"action={action}, next_step={next_step}, reason={reason}"
    )

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
        updates["last_user_request"] = state["message"]
        updates["last_revision_request"] = ""
    else:
        updates["last_revision_request"] = state["message"]
    return updates
