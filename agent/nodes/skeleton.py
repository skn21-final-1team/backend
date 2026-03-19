from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import SKELETON_SYSTEM_PROMPT, SKELETON_USER_PROMPT
from agent.workflow_state import WorkflowState
from agent.workflow_types import WORKFLOW_STEP_BY_NAME


def _revision_request_text(state: WorkflowState) -> str:
    return state["last_revision_request"].strip() or "없음"


async def build_skeleton(state: WorkflowState, config: RunnableConfig) -> dict:
    base_request = state["last_user_request"] or state["message"]
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=SKELETON_SYSTEM_PROMPT),
            HumanMessage(
                content=SKELETON_USER_PROMPT.format(
                    base_request=base_request,
                    revision_request=_revision_request_text(state),
                    requirements_text=state["requirements_text"],
                )
            ),
        ]
    )

    outline_text = response.content
    return {
        "status": "awaiting_review",
        "step": WORKFLOW_STEP_BY_NAME["skeleton"],
        "awaiting_action": "approval",
        "outline_text": outline_text,
        "draft_text": "",
        "final_text": "",
        "system_message": "문서 개요 생성을 완료했습니다. 내용을 검토해 주세요.",
    }
