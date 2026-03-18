from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import REQUIREMENT_SYSTEM_PROMPT, REQUIREMENT_USER_PROMPT
from agent.workflow_state import WorkflowState


async def analyze_requirement(state: WorkflowState, config: RunnableConfig) -> dict:
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=REQUIREMENT_SYSTEM_PROMPT),
            HumanMessage(
                content=REQUIREMENT_USER_PROMPT.format(
                    message=state["message"],
                    source_snapshot=state.get("source_snapshot", "참고 자료 없음"),
                )
            ),
        ]
    )

    requirements_text = response.content
    return {
        "status": "in_progress",
        "step": 1,
        "awaiting_action": "none",
        "requirements_text": requirements_text,
        "system_message": "요구 사항 분석 단계가 완료되었습니다. 다음 단계로 진행할지 결정해주세요.",
        "last_user_request": state["message"],
    }
