from collections.abc import AsyncGenerator
from typing import TypedDict

from langgraph.types import Command

from agent.report_graph import report_graph
from agent.workflow_types import (
    INITIAL_WORKFLOW_STEP,
    WORKFLOW_OUTPUT_FIELD_BY_STEP,
    WORKFLOW_STEP_BY_NAME,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepName,
)


class WorkflowStateSnapshot(TypedDict, total=False):
    status: WorkflowStatus
    step: WorkflowStep
    system_message: str
    requirements_text: str
    outline_text: str
    draft_text: str
    final_text: str


class ReviewInterruptPayload(TypedDict):
    system_message: str
    content: str
    step: WorkflowStep
    step_name: WorkflowStepName


class ReportWorkflowRuntime:
    initial_step = INITIAL_WORKFLOW_STEP
    step_by_name = WORKFLOW_STEP_BY_NAME
    output_field_by_step = WORKFLOW_OUTPUT_FIELD_BY_STEP
    step_event_names = tuple(WORKFLOW_STEP_BY_NAME)

    def get_state(self, config: dict[str, object]) -> object:
        return report_graph.get_state(config)

    def stream(
        self,
        graph_input: dict[str, object] | Command,
        config: dict[str, object],
    ) -> AsyncGenerator[tuple[str, dict[str, object]], None]:
        return report_graph.astream(
            graph_input,
            stream_mode=["updates", "values"],
            version="v2",
            config=config,
        )


report_workflow_runtime = ReportWorkflowRuntime()
