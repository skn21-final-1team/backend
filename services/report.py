import json
from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from agent.report_graph import report_graph
from core.exceptions.notebook import NotebookNotFoundException
from crud.notebook import get_notebook
from crud.source import get_sources_by_notebook
from langgraph.types import Command
from schemas.report_workflow import ReportWorkflowRequest


class ReportService:
    def __sse_event(self, event_name: str, data: str) -> str:
        payload = "\n".join(f"data: {line}" for line in data.splitlines()) or "data: "
        return f"event: {event_name}\n{payload}\n\n"

    def __json_sse_event(self, event_name: str, payload: dict[str, object]) -> str:
        return self.__sse_event(event_name, json.dumps(payload, ensure_ascii=False))

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
                        f"- content: {content.strip() if isinstance(content, str) else content}",
                    ]
                )
            )
        return "\n\n---\n\n".join(sections)

    def __extract_markdown(self, node_update: object) -> str | None:
        if isinstance(node_update, dict):
            markdown = node_update.get("system_message")
            if isinstance(markdown, str) and markdown.strip():
                return markdown.strip()
        if isinstance(node_update, str) and node_update.strip():
            return node_update.strip()
        return None

    def __iter_updates(self, chunk: object) -> list[tuple[str, object]]:
        if isinstance(chunk, dict):
            return list(chunk.items())
        if isinstance(chunk, tuple) and len(chunk) == 2 and isinstance(chunk[1], dict):
            return list(chunk[1].items())
        return []

    def __build_initial_state(self, req: ReportWorkflowRequest, source_snapshot: str) -> dict[str, object]:
        return {
            "notebook_id": req.notebook_id,
            "message": req.message,
            "source_snapshot": source_snapshot,
            "status": "in_progress",
            "step": 1,
            "awaiting_action": "none",
            "last_user_request": req.message,
            "last_revision_request": "",
            "last_approved_step": None,
            "requirements_text": "",
            "outline_text": "",
            "draft_text": "",
            "final_text": "",
            "system_message": "",
            "clarification_questions": [],
        }

    def __thread_id(self, notebook_id: int) -> str:
        return f"report:{notebook_id}"

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

    def __build_config(self, thread_id: str) -> dict[str, object]:
        return {
            "configurable": {
                "model_name": "gpt-4o-mini",
                "thread_id": thread_id,
            }
        }

    def __extract_interrupt_markdown(self, interrupts: object) -> list[str]:
        if not interrupts:
            return []

        values = interrupts if isinstance(interrupts, (list, tuple)) else [interrupts]
        markdowns: list[str] = []
        for interrupt in values:
            payload = getattr(interrupt, "value", interrupt)
            if not isinstance(payload, dict):
                continue
            markdown = payload.get("markdown")
            if isinstance(markdown, str) and markdown.strip():
                markdowns.append(markdown.strip())
        return markdowns

    async def stream_report(self, req: ReportWorkflowRequest, db: Session) -> AsyncGenerator[str, None]:
        source_snapshot = self.__build_source_snapshot(req.notebook_id, db)
        thread_id = self.__thread_id(req.notebook_id)
        config = self.__build_config(thread_id)
        try:
            state_snapshot = report_graph.get_state(config)
        except Exception:
            state_snapshot = None
        has_pending_work = bool(getattr(state_snapshot, "next", ()))
        graph_input = self.__build_stream_input(req, source_snapshot, has_pending_work)
        last_interrupt_markdown: str | None = None

        yield self.__json_sse_event(
            "thread",
            {
                "thread_id": thread_id,
                "mode": "resume" if has_pending_work else "start",
            },
        )

        async for chunk in report_graph.astream(
            graph_input,
            stream_mode=["updates", "values"],
            version="v2",
            config=config,
        ):
            chunk_type = chunk.get("type")
            chunk_data = chunk.get("data")

            if chunk_type == "updates":
                if isinstance(chunk_data, dict):
                    interrupts = chunk_data.get("__interrupt__")
                    for markdown in self.__extract_interrupt_markdown(interrupts):
                        if markdown == last_interrupt_markdown:
                            continue
                        last_interrupt_markdown = markdown
                        yield self.__sse_event("await_user_review", markdown)
                for node_name, node_update in self.__iter_updates(chunk_data):
                    markdown = self.__extract_markdown(node_update)
                    if markdown:
                        last_interrupt_markdown = None
                        yield self.__sse_event(node_name, markdown)
                continue

            if chunk_type == "values" and isinstance(chunk_data, dict):
                interrupts = chunk_data.get("interrupts") or chunk_data.get("__interrupt__")
                for markdown in self.__extract_interrupt_markdown(interrupts):
                    if markdown == last_interrupt_markdown:
                        continue
                    last_interrupt_markdown = markdown
                    yield self.__sse_event("await_user_review", markdown)

        yield self.__sse_event("done", "[DONE]")


report_service = ReportService()
