from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import PREPARED_SYSTEM_PROMPT, PREPARED_USER_PROMPT
from agent.workflow_state import WorkflowState


async def prepare_draft(state: WorkflowState, config: RunnableConfig) -> dict:
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=PREPARED_SYSTEM_PROMPT),
            HumanMessage(
                content=PREPARED_USER_PROMPT.format(
                    outline_text=state["outline_text"],
                    source_snapshot=state.get("source_snapshot", "참고 자료 없음"),
                )
            ),
        ]
    )

    draft_text = response.content
    return {
        "status": "in_progress",
        "step": 3,
        "draft_text": draft_text,
        "system_message": "초안 작성 단계가 완료되었습니다. 다음 단계로 진행할지 결정해주세요.",
    }
