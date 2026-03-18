from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import REQUIREMENT_SYSTEM_PROMPT, REQUIREMENT_USER_PROMPT
from agent.workflow_state import WorkflowState


def _revision_request_text(state: WorkflowState) -> str:
    revision_request = state.get("last_revision_request")
    if isinstance(revision_request, str) and revision_request.strip():
        return revision_request
    return "없음"


async def analyze_requirement(state: WorkflowState, config: RunnableConfig) -> dict:
    base_request = state.get("last_user_request") or state["message"]
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=REQUIREMENT_SYSTEM_PROMPT),
            HumanMessage(
                content=REQUIREMENT_USER_PROMPT.format(
                    base_request=base_request,
                    revision_request=_revision_request_text(state),
                    source_snapshot=state.get("source_snapshot", "참고 자료 없음"),
                )
            ),
        ]
    )

    requirements_text = response.content
    return {
        "status": "awaiting_review",
        "step": 1,
        "awaiting_action": "approval",
        "requirements_text": requirements_text,
        "outline_text": "",
        "draft_text": "",
        "final_text": "",
        "system_message": "요구사항 분석을 완료했습니다. 내용을 검토해 주세요.",
        "last_user_request": base_request,
    }
