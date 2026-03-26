from collections.abc import AsyncGenerator
from typing import Literal, TypedDict

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


WorkflowResumeMode = Literal["start", "continue", "review"]


class WorkflowCheckpointSnapshot(TypedDict):
    values: WorkflowStateSnapshot
    workflow_status: WorkflowStatus
    current_step: WorkflowStep | None
    resume_mode: WorkflowResumeMode


class ReportWorkflowRuntime:
    initial_step = INITIAL_WORKFLOW_STEP
    step_by_name = WORKFLOW_STEP_BY_NAME
    output_field_by_step = WORKFLOW_OUTPUT_FIELD_BY_STEP
    step_event_names = tuple(WORKFLOW_STEP_BY_NAME)
    _review_wait_node_name = "await_user_review"
    _review_decision_node_name = "review_decision"
    _source_filter_node_name = "filter_source"

    def _get_pending_node_name(self, next_nodes: tuple[str, ...]) -> str | None:
        return next_nodes[0] if next_nodes else None

    def _resolve_checkpoint_status(
        self,
        values: WorkflowStateSnapshot,
        next_nodes: tuple[str, ...],
        interrupts: tuple[Interrupt, ...],
    ) -> WorkflowStatus:
        if interrupts:
            return "awaiting_review"
        pending_node_name = self._get_pending_node_name(next_nodes)
        if pending_node_name == self._review_wait_node_name:
            return "awaiting_review"
        if next_nodes:
            return "in_progress"
        if values:
            return values.get("status", "in_progress")
        return "idle"

    def _resolve_current_step(
        self,
        values: WorkflowStateSnapshot,
        next_nodes: tuple[str, ...],
        interrupts: tuple[Interrupt, ...],
    ) -> WorkflowStep | None:
        saved_step = values.get("step")
        if interrupts:
            return saved_step

        pending_node_name = self._get_pending_node_name(next_nodes)
        if pending_node_name is None:
            return saved_step
        if pending_node_name in self.step_by_name:
            return self.step_by_name[pending_node_name]
        if pending_node_name in {self._review_wait_node_name, self._review_decision_node_name}:
            return saved_step
        if pending_node_name == self._source_filter_node_name:
            return saved_step or self.initial_step
        return saved_step

    def _resolve_resume_mode(
        self,
        next_nodes: tuple[str, ...],
        interrupts: tuple[Interrupt, ...],
    ) -> WorkflowResumeMode:
        if interrupts:
            return "review"
        pending_node_name = self._get_pending_node_name(next_nodes)
        if pending_node_name == self._review_wait_node_name:
            return "review"
        if next_nodes:
            return "continue"
        return "start"

    def get_checkpoint_snapshot(self, config: dict[str, object]) -> WorkflowCheckpointSnapshot:
        state_snapshot = report_graph.get_state(config)
        values: WorkflowStateSnapshot = getattr(state_snapshot, "values", {})
        next_nodes: tuple[str, ...] = tuple(getattr(state_snapshot, "next", ()))
        interrupts: tuple[Interrupt, ...] = tuple(getattr(state_snapshot, "interrupts", ()))

        return WorkflowCheckpointSnapshot(
            values=values,
            workflow_status=self._resolve_checkpoint_status(values, next_nodes, interrupts),
            current_step=self._resolve_current_step(values, next_nodes, interrupts),
            resume_mode=self._resolve_resume_mode(next_nodes, interrupts),
        )

    def reset_thread(self, thread_id: str) -> None:
        report_graph.checkpointer.delete_thread(thread_id)

    def stream(
        self,
        graph_input: dict[str, object] | Command | None,
        config: dict[str, object],
    ) -> AsyncGenerator[tuple[str, dict[str, object]], None]:
        return report_graph.astream(
            graph_input,
            stream_mode=["updates", "values"],
            version="v2",
            config=config,
        )


report_workflow_runtime = ReportWorkflowRuntime()
