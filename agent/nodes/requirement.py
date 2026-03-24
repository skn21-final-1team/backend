from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import REQUIREMENT_SYSTEM_PROMPT, REQUIREMENT_USER_PROMPT
from agent.workflow_state import WorkflowState
from agent.workflow_types import INITIAL_WORKFLOW_STEP


def _revision_request_text(state: WorkflowState) -> str:
    return state["last_revision_request"].strip() or "없음"


async def analyze_requirement(state: WorkflowState, config: RunnableConfig) -> dict:
    base_request = state["last_user_request"] or state["message"]
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=REQUIREMENT_SYSTEM_PROMPT),
            HumanMessage(
                content=REQUIREMENT_USER_PROMPT.format(
                    base_request=base_request,
                    revision_request=_revision_request_text(state),
                    source_snapshot=state["source_snapshot"],
                )
            ),
        ]
    )

    requirements_text = response.content
    return {
        "status": "awaiting_review",
        "step": INITIAL_WORKFLOW_STEP,
        "awaiting_action": "approval",
        "requirements_text": requirements_text,
        "outline_text": "",
        "draft_text": "",
        "final_text": "",
        "system_message": "요구사항 분석을 완료했습니다. **승인** 또는 **수정** 요청을 할 수 있습니다. \
            \n - 예: 다음으로 진행해줘, 완료, 승인 \
            \n - 예: 이런 부분 수정해줘. (수정 사항을 구체적으로 작성해주세요.)",
        "last_user_request": base_request,
    }
