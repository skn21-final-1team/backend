from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import PREPARED_SYSTEM_PROMPT, PREPARED_USER_PROMPT
from agent.workflow_state import WorkflowState
from agent.workflow_types import WORKFLOW_STEP_BY_NAME


def _revision_request_text(state: WorkflowState) -> str:
    return state["last_revision_request"].strip() or "없음"


async def prepare_draft(state: WorkflowState, config: RunnableConfig) -> dict:
    base_request = state["last_user_request"] or state["message"]
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=PREPARED_SYSTEM_PROMPT),
            HumanMessage(
                content=PREPARED_USER_PROMPT.format(
                    base_request=base_request,
                    revision_request=_revision_request_text(state),
                    outline_text=state["outline_text"],
                    source_snapshot=state["source_snapshot"],
                )
            ),
        ]
    )

    draft_text = response.content
    return {
        "status": "awaiting_review",
        "step": WORKFLOW_STEP_BY_NAME["prepared"],
        "awaiting_action": "approval",
        "draft_text": draft_text,
        "final_text": "",
        "system_message": "초안 작성을 완료했습니다. 내용을 검토해 주세요.",
    }
