import json
from collections.abc import AsyncGenerator
from typing import Literal

from langgraph.types import Command, Interrupt
from sqlalchemy.orm import Session

from agent.model.llm_factory import DEFAULT_LLM_MODEL_NAME
from core.exceptions.notebook import NotebookNotFoundException
from crud.notebook import get_notebook
from crud.source import get_sources_by_notebook
from schemas.report_workflow import (
    ReportWorkflowRequest,
    ReportWorkflowSseMessageType,
    ReportWorkflowSsePayload,
    ReportWorkflowStateResponse,
    ReportWorkflowStepOutputs,
)
from schemas.report_workflow import (
    ReportWorkflowStep as ApiReportWorkflowStep,
)
from schemas.report_workflow import (
    WorkflowStatus as ApiWorkflowStatus,
)
from services.report_workflow_runtime import (
    ReviewInterruptPayload,
    WorkflowStateSnapshot,
    report_workflow_runtime,
)
from services.report_workflow_runtime import (
    WorkflowStatus as InternalWorkflowStatus,
)
from services.report_workflow_runtime import (
    WorkflowStep as InternalWorkflowStep,
)
from services.report_workflow_runtime import (
    WorkflowStepName as InternalWorkflowStepName,
)

_API_WORKFLOW_STATUS_BY_INTERNAL: dict[InternalWorkflowStatus, ApiWorkflowStatus] = {
    "idle": "idle",
    "in_progress": "in_progress",
    "awaiting_review": "awaiting_review",
    "completed": "completed",
}

_API_WORKFLOW_STEP_BY_INTERNAL: dict[InternalWorkflowStep, ApiReportWorkflowStep] = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
}

_STEP_EVENT_NAMES = report_workflow_runtime.step_event_names


class ReportService:
    def __sse_event(self, event_name: str, payload: dict[str, object]) -> str:
        data = json.dumps(payload, ensure_ascii=False)
        body = "\n".join(f"data: {line}" for line in data.splitlines()) or "data: "
        return f"event: {event_name}\n{body}\n\n"

    def __build_payload(
        self,
        *,
        message_type: ReportWorkflowSseMessageType,
        event_name: str,
        system_message: str | None,
        content: str | None,
        step: ApiReportWorkflowStep | None,
        step_name: str | None,
        mode: Literal["start", "resume"] | None,
    ) -> dict[str, object]:
        return ReportWorkflowSsePayload(
            message_type=message_type,
            event_name=event_name,
            system_message=system_message,
            content=content,
            step=step,
            step_name=step_name,
            mode=mode,
        ).model_dump(mode="json", exclude_none=False)

    def __build_thread_payload(self, mode: Literal["start", "resume"]) -> dict[str, object]:
        system_message = "리포트 워크플로우를 재개합니다." if mode == "resume" else "리포트 워크플로우를 시작합니다."
        return self.__build_payload(
            message_type="thread",
            event_name="thread",
            system_message=system_message,
            content=None,
            step=None,
            step_name=None,
            mode=mode,
        )

    def __build_done_payload(self) -> dict[str, object]:
        return self.__build_payload(
            message_type="done",
            event_name="done",
            system_message="리포트 워크플로우가 완료되었습니다.",
            content=None,
            step=None,
            step_name=None,
            mode=None,
        )

    def __build_step_payload(
        self,
        event_name: InternalWorkflowStepName,
        node_update: WorkflowStateSnapshot,
    ) -> dict[str, object]:
        step_number = report_workflow_runtime.step_by_name[event_name]
        content_field = report_workflow_runtime.output_field_by_step[step_number]
        return self.__build_payload(
            message_type="step",
            event_name=event_name,
            system_message=node_update["system_message"],
            content=node_update[content_field],
            step=self.__to_api_workflow_step(step_number),
            step_name=event_name,
            mode=None,
        )

    def __build_review_payload(self, interrupt_value: Interrupt) -> dict[str, object]:
        review_payload: ReviewInterruptPayload = interrupt_value.value
        return self.__build_payload(
            message_type="review",
            event_name="await_user_review",
            system_message=review_payload["system_message"],
            content=review_payload["content"],
            step=self.__to_api_workflow_step(review_payload["step"]),
            step_name=review_payload["step_name"],
            mode=None,
        )

    def __extract_interrupt_payloads(self, interrupts: tuple[Interrupt, ...]) -> list[dict[str, object]]:
        return [self.__build_review_payload(interrupt) for interrupt in interrupts]

    def __build_source_snapshot(self, notebook_id: int, db: Session) -> str:
        notebook = get_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException

        sources = get_sources_by_notebook(db, notebook_id)
        if not sources:
            return f"# Source Snapshot\n\n노트북 `{notebook.title}`에 연결된 source가 없습니다."

        sections: list[str] = [f"# Source Snapshot\n\n노트북 `{notebook.title}` 기준 source 정리"]
        for index, source in enumerate(sources, start=1):
            content = source.summary or source.refined or source.raw or "내용 없음"
            sections.append(
                "\n".join(
                    [
                        f"## Source {index}",
                        f"- title: {source.title or '제목 없음'}",
                        f"- url: {source.url}",
                        f"- status: {source.status}",
                        f"- content: {content.strip()}",
                    ]
                )
            )
        return "\n\n---\n\n".join(sections)

    def __build_step_outputs(self, values: WorkflowStateSnapshot) -> ReportWorkflowStepOutputs:
        return ReportWorkflowStepOutputs(
            requirements_text=values.get("requirements_text", ""),
            outline_text=values.get("outline_text", ""),
            draft_text=values.get("draft_text", ""),
            final_text=values.get("final_text", ""),
        )

    def __to_api_workflow_status(self, status: InternalWorkflowStatus) -> ApiWorkflowStatus:
        return _API_WORKFLOW_STATUS_BY_INTERNAL[status]

    def __to_api_workflow_step(self, step: InternalWorkflowStep) -> ApiReportWorkflowStep:
        return _API_WORKFLOW_STEP_BY_INTERNAL[step]

    def __resolve_workflow_status(
        self,
        values: WorkflowStateSnapshot,
        next_nodes: tuple[str, ...],
        interrupts: tuple[Interrupt, ...],
    ) -> InternalWorkflowStatus:
        if not values:
            return "idle"
        if interrupts:
            return "awaiting_review"
        if next_nodes:
            return "in_progress"
        return values["status"]

    def __resolve_current_step_number(self, values: WorkflowStateSnapshot) -> InternalWorkflowStep | None:
        if not values:
            return None
        return values["step"]

    def __resolve_workflow_state(
        self,
        state_snapshot: object,
    ) -> tuple[ApiWorkflowStatus, ApiReportWorkflowStep | None, ReportWorkflowStepOutputs]:
        values: WorkflowStateSnapshot = getattr(state_snapshot, "values", {})
        next_nodes: tuple[str, ...] = getattr(state_snapshot, "next", ())
        interrupts: tuple[Interrupt, ...] = getattr(state_snapshot, "interrupts", ())
        workflow_status = self.__resolve_workflow_status(values, next_nodes, interrupts)
        current_step = self.__resolve_current_step_number(values)

        return (
            self.__to_api_workflow_status(workflow_status),
            None if current_step is None else self.__to_api_workflow_step(current_step),
            self.__build_step_outputs(values),
        )

    def get_report_workflow_state(self, notebook_id: int, db: Session) -> ReportWorkflowStateResponse:
        notebook = get_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException

        workflow_status, current_step, step_outputs = self.__resolve_workflow_state(
            report_workflow_runtime.get_state(self.__build_config(notebook_id))
        )

        return ReportWorkflowStateResponse(
            workflow_status=workflow_status,
            current_step=current_step,
            step_outputs=step_outputs,
        )

    def reset_report_workflow(self, notebook_id: int, db: Session) -> ReportWorkflowStateResponse:
        notebook = get_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException

        report_workflow_runtime.reset_thread(str(notebook_id))
        return self.get_report_workflow_state(notebook_id, db)

    def __build_initial_state(self, req: ReportWorkflowRequest, source_snapshot: str) -> dict[str, object]:
        return {
            "notebook_id": req.notebook_id,
            "message": req.message,
            "source_snapshot": source_snapshot,
            "status": "in_progress",
            "step": report_workflow_runtime.initial_step,
            "awaiting_action": "none",
            "action": "",
            "last_user_request": req.message,
            "last_revision_request": "",
            "last_approved_step": None,
            "requirements_text": "",
            "outline_text": "",
            "draft_text": "",
            "final_text": "",
            "system_message": "해당 요구사항으로 문서를 작성했어요. 결과물을 검토해 주세요.",
            "clarification_questions": [],
        }

    def __build_stream_input(
        self,
        req: ReportWorkflowRequest,
        source_snapshot: str,
        has_pending_work: bool,
    ) -> dict[str, object] | Command:
        if has_pending_work:
            return Command(
                resume={
                    "message": req.message,
                    "source_snapshot": source_snapshot,
                }
            )
        return self.__build_initial_state(req, source_snapshot)

    def __build_config(
        self,
        notebook_id: int,
        model_name: str = DEFAULT_LLM_MODEL_NAME,
    ) -> dict[str, object]:
        print("model_name in config:", model_name)  # 디버깅용 출력
        return {
            "configurable": {
                "model_name": model_name,
                "thread_id": str(notebook_id),
            }
        }

    async def stream_report(self, req: ReportWorkflowRequest, db: Session) -> AsyncGenerator[str, None]:
        source_snapshot = self.__build_source_snapshot(req.notebook_id, db)
        config = self.__build_config(req.notebook_id, req.model_name)
        state_snapshot = report_workflow_runtime.get_state(config)
        has_pending_work = bool(state_snapshot.next)
        graph_input = self.__build_stream_input(req, source_snapshot, has_pending_work)
        last_interrupt_signature: tuple[str | None, str | None] | None = None

        yield self.__sse_event(
            "thread",
            self.__build_thread_payload("resume" if has_pending_work else "start"),
        )

        async for chunk_type, chunk_data in report_workflow_runtime.stream(graph_input, config):
            if chunk_type == "updates":
                interrupts = chunk_data.get("__interrupt__", ())
                if interrupts:
                    for payload in self.__extract_interrupt_payloads(interrupts):
                        signature = (payload["system_message"], payload["content"])
                        if signature == last_interrupt_signature:
                            continue
                        last_interrupt_signature = signature
                        yield self.__sse_event("await_user_review", payload)
                    continue

                for node_name, node_update in chunk_data.items():
                    if node_name not in _STEP_EVENT_NAMES:
                        continue
                    payload = self.__build_step_payload(node_name, node_update)
                    last_interrupt_signature = None
                    yield self.__sse_event(node_name, payload)
                continue

            if chunk_type == "values":
                interrupts = chunk_data.get("__interrupt__", ())
                for payload in self.__extract_interrupt_payloads(interrupts):
                    signature = (payload["system_message"], payload["content"])
                    if signature == last_interrupt_signature:
                        continue
                    last_interrupt_signature = signature
                    yield self.__sse_event("await_user_review", payload)

        yield self.__sse_event("done", self.__build_done_payload())


report_service = ReportService()
