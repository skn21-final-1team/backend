from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.prompts.report_workflow import SKELETON_SYSTEM_PROMPT, SKELETON_USER_PROMPT
from agent.workflow_state import WorkflowState


async def build_skeleton(state: WorkflowState, config: RunnableConfig) -> dict:
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=SKELETON_SYSTEM_PROMPT),
            HumanMessage(
                content=SKELETON_USER_PROMPT.format(
                    requirements_text=state["requirements_text"],
                )
            ),
        ]
    )

    outline_text = response.content
    return {
        "status": "in_progress",
        "step": 2,
        "outline_text": outline_text,
        "system_message": outline_text,
    }
