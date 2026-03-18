from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from agent.report_graph import report_graph
from core.exceptions.notebook import NotebookNotFoundException
from crud.notebook import get_notebook
from crud.source import get_sources_by_notebook
from schemas.report_workflow import ReportWorkflowRequest


class ReportService:
    def __sse_event(self, event_name: str, data: str) -> str:
        payload = "\n".join(f"data: {line}" for line in data.splitlines()) or "data: "
        return f"event: {event_name}\n{payload}\n\n"

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

    async def stream_report(self, req: ReportWorkflowRequest, db: Session) -> AsyncGenerator[str, None]:
        source_snapshot = self.__build_source_snapshot(req.notebook_id, db)
        initial_state = {
            "notebook_id": req.notebook_id,
            "message": req.message,
            "source_snapshot": source_snapshot,
            "last_user_request": req.message,
        }

        async for mode, chunk in report_graph.astream(
            initial_state,
            stream_mode=["updates"],
            version="v2",
            config={
                "configurable": {
                    "model_name": "gpt-4o-mini",
                }
            },
        ):
            if mode != "updates":
                continue

            for node_name, node_update in self.__iter_updates(chunk):
                markdown = self.__extract_markdown(node_update)
                if markdown:
                    yield self.__sse_event(node_name, markdown)

        yield self.__sse_event("done", "[DONE]")


report_service = ReportService()
