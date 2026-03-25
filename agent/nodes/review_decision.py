from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from agent.model.llm_factory import llm_factory
from agent.prompts.report_review import REVIEW_DECISION_SYSTEM_PROMPT, REVIEW_DECISION_USER_PROMPT
from agent.workflow_state import WorkflowState
from agent.workflow_types import (
    FINAL_WORKFLOW_STEP,
    INITIAL_WORKFLOW_STEP,
    WORKFLOW_NAME_BY_STEP,
    WORKFLOW_OUTPUT_FIELD_BY_STEP,
)


class ReviewDecisionPayload(BaseModel):
    action: str = Field(description="approve, revise, reset, except 중 하나")
    reason: str = Field(description="판정 근거")
    next_step: int = Field(description="권장 다음 단계 번호")


_VALID_ACTIONS = {"approve", "revise", "reset", "except"}


def _parse_review_decision_from_text(text: str) -> ReviewDecisionPayload:
    """structured output 미지원 모델용: 텍스트 응답에서 JSON을 파싱합니다."""
    json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if not json_match:
        return ReviewDecisionPayload(action="except", reason="응답 파싱 실패", next_step=1)

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        return ReviewDecisionPayload(action="except", reason="JSON 파싱 실패", next_step=1)

    action = str(data.get("action", "except")).strip().lower()
    if action not in _VALID_ACTIONS:
        action = "except"

    return ReviewDecisionPayload(
        action=action,
        reason=str(data.get("reason", "")),
        next_step=int(data.get("next_step", 1)),
    )


def _build_current_output(state: WorkflowState) -> str:
    step = state["step"]
    field_name = WORKFLOW_OUTPUT_FIELD_BY_STEP[step]
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
    step_name = WORKFLOW_NAME_BY_STEP[step]
    current_output = _build_current_output(state)
    workflow_snapshot = _build_snapshot_text(state)

    messages = [
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

    llm = llm_factory.get_llm(config)
    if llm_factory.supports_structured_output(config):
        payload = await llm.with_structured_output(
            ReviewDecisionPayload,
            method="json_schema",
            strict=True,
        ).ainvoke(messages)
    else:
        response = await llm.ainvoke(messages)
        payload = _parse_review_decision_from_text(response.content)

    action = payload.action.strip().lower()

    if action == "except":
        return {
            "action": "except",
            "system_message": "무슨말씀인지 잘 모르겠어요. 추가 피드백을 작성해주세요.",
        }

    if action not in {"approve", "revise", "reset", "except"}:
        error_message = f"review_decision returned unsupported action: {payload.action}"
        raise ValueError(error_message)

    reason = payload.reason
    next_step = int(payload.next_step)

    print(
        f"review decision resolved: step={step}, step_name={step_name}, query={state['message']}"
        f"action={action}, next_step={next_step}, reason={reason}",
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
        "status": "completed" if action == "approve" and step >= FINAL_WORKFLOW_STEP else "in_progress",
        "awaiting_action": "none",
        "system_message": summary,
    }
    if action == "approve":
        updates["last_approved_step"] = step
    elif action == "reset":
        updates["step"] = INITIAL_WORKFLOW_STEP
        updates["last_user_request"] = state["message"]
        updates["last_revision_request"] = ""
    else:
        updates["last_revision_request"] = state["message"]
    return updates
