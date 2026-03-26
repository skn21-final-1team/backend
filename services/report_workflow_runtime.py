from collections.abc import AsyncGenerator
from typing import TypedDict

from langgraph.types import Command, Interrupt

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
    source_snapshot: str
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


class WorkflowCheckpointSnapshot(TypedDict):
    values: WorkflowStateSnapshot
    next_nodes: tuple[str, ...]
    interrupts: tuple[Interrupt, ...]
    status: WorkflowStatus
    current_step: WorkflowStep | None
    has_checkpoint: bool
    is_resumable: bool


class ReportWorkflowRuntime:
    initial_step = INITIAL_WORKFLOW_STEP
    step_by_name = WORKFLOW_STEP_BY_NAME
    output_field_by_step = WORKFLOW_OUTPUT_FIELD_BY_STEP
    step_event_names = tuple(WORKFLOW_STEP_BY_NAME)

    def _resolve_checkpoint_status(
        self,
        values: WorkflowStateSnapshot,
        next_nodes: tuple[str, ...],
        interrupts: tuple[Interrupt, ...],
    ) -> WorkflowStatus:
        if interrupts:
            return "awaiting_review"
        if next_nodes:
            return "in_progress"
        if values:
            return values.get("status", "in_progress")
        return "idle"

    def get_checkpoint_snapshot(self, config: dict[str, object]) -> WorkflowCheckpointSnapshot:
        state_snapshot = report_graph.get_state(config)
        values: WorkflowStateSnapshot = getattr(state_snapshot, "values", {})
        next_nodes: tuple[str, ...] = tuple(getattr(state_snapshot, "next", ()))
        interrupts: tuple[Interrupt, ...] = tuple(getattr(state_snapshot, "interrupts", ()))
        has_checkpoint = bool(values or next_nodes or interrupts)

        return WorkflowCheckpointSnapshot(
            values=values,
            next_nodes=next_nodes,
            interrupts=interrupts,
            status=self._resolve_checkpoint_status(values, next_nodes, interrupts),
            current_step=values.get("step"),
            has_checkpoint=has_checkpoint,
            is_resumable=bool(next_nodes or interrupts),
        )

    def get_state(self, config: dict[str, object]) -> object:
        return report_graph.get_state(config)

    def reset_thread(self, thread_id: str) -> None:
        report_graph.checkpointer.delete_thread(thread_id)

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
