from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import FINAL_SYSTEM_PROMPT, FINAL_USER_PROMPT
from agent.workflow_state import WorkflowState


async def finalize_report(state: WorkflowState, config: RunnableConfig) -> dict:
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=FINAL_SYSTEM_PROMPT),
            HumanMessage(
                content=FINAL_USER_PROMPT.format(
                    message=state["message"],
                    requirements_text=state["requirements_text"],
                    outline_text=state["outline_text"],
                    draft_text=state["draft_text"],
                )
            ),
        ]
    )

    final_text = response.content
    return {
        "status": "completed",
        "step": 4,
        "final_text": final_text,
        "system_message": "최종안 작성 단계가 완료되었습니다. 에이전트를 종료할까요?",
        "last_approved_step": 4,
    }
