from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import FINAL_SYSTEM_PROMPT, FINAL_USER_PROMPT
from agent.workflow_state import WorkflowState


def _revision_request_text(state: WorkflowState) -> str:
    revision_request = state.get("last_revision_request")
    if isinstance(revision_request, str) and revision_request.strip():
        return revision_request
    return "없음"


async def finalize_report(state: WorkflowState, config: RunnableConfig) -> dict:
    base_request = state.get("last_user_request") or state["message"]
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=FINAL_SYSTEM_PROMPT),
            HumanMessage(
                content=FINAL_USER_PROMPT.format(
                    base_request=base_request,
                    revision_request=_revision_request_text(state),
                    requirements_text=state.get("requirements_text", "없음"),
                    outline_text=state.get("outline_text", "없음"),
                    draft_text=state.get("draft_text", "없음"),
                )
            ),
        ]
    )

    final_text = response.content
    return {
        "status": "awaiting_review",
        "step": 4,
        "awaiting_action": "approval",
        "final_text": final_text,
        "system_message": final_text,
    }
