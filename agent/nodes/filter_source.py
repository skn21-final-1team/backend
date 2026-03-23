import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from agent.model.llm_factory import llm_factory
from agent.workflow_state import WorkflowState
from crud.source import get_active_source_ids, get_source_ids_by_notebook, get_sources_by_ids
from db.database import get_db_context
from models.source import SourceModel

_MAX_SELECTED_SOURCE_COUNT = 10

_FILTER_SOURCE_SYSTEM_PROMPT = """
당신은 사용자 요청과 관련된 source만 골라내는 편집자다.
주어진 source 후보의 id와 summary를 읽고, 사용자 요청과 직접적으로 관련된 source id만 선택한다.
응답은 반드시 숫자 id만 쉼표로 구분해서 출력한다.
관련된 source가 없으면 빈 문자열을 출력한다.
"""


def _build_source_candidates_text(sources: list[SourceModel]) -> str:
    candidate_lines: list[str] = []
    for source in sources:
        if not source.summary:
            continue
        candidate_lines.append(
            "\n".join(
                [
                    f"id: {source.id}",
                    f"title: {source.title or '제목 없음'}",
                    f"summary: {source.summary.strip()}",
                ]
            )
        )
    return "\n\n".join(candidate_lines)


def _parse_selected_source_ids(response_text: str, valid_source_ids: set[int]) -> list[int]:
    selected_source_ids: list[int] = []
    for token in re.findall(r"\d+", response_text):
        source_id = int(token)
        if source_id not in valid_source_ids or source_id in selected_source_ids:
            continue
        selected_source_ids.append(source_id)
        if len(selected_source_ids) >= _MAX_SELECTED_SOURCE_COUNT:
            break
    return selected_source_ids


def _build_source_snapshot(sources: list[SourceModel]) -> str:
    snapshot_sections: list[str] = []
    for source in sources:
        if not source:
            continue

        content = (source.raw or source.refined or source.summary or "").strip()
        if not content:
            continue

        snapshot_sections.append(
            "\n".join(
                [
                    f"## Source File {source.id}",
                    f"- source_file_id: {source.id}",
                    f"- title: {source.title or '제목 없음'}",
                    f"- url: {source.url}",
                    "",
                    content,
                ]
            )
        )

    return "\n\n".join(snapshot_sections)


async def filter_source(state: WorkflowState, config: RunnableConfig) -> dict[str, object]:
    query = state["message"]
    if not query:
        return {"source_snapshot": ""}

    with get_db_context() as db:
        notebook_source_ids = get_source_ids_by_notebook(db, state["notebook_id"])
        if not notebook_source_ids:
            return {"source_snapshot": ""}

        active_source_ids = get_active_source_ids(db, notebook_source_ids)
        if not active_source_ids:
            return {"source_snapshot": ""}

    active_sources = get_sources_by_ids(db, active_source_ids)
    candidate_text = _build_source_candidates_text(active_sources)

    if not candidate_text:
        return {"source_snapshot": ""}

    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(
        [
            SystemMessage(content=_FILTER_SOURCE_SYSTEM_PROMPT),
            HumanMessage(
                content="\n\n".join(
                    [
                        f"## 사용자 요청\n{query}",
                        "## source 후보",
                        candidate_text,
                        (
                            "출력 규칙:\n"
                            "- 관련된 source id만 선택\n"
                            "- 숫자 id만 쉼표로 구분해서 출력\n"
                            "- 설명, 이유, JSON, 마크다운 금지"
                        ),
                    ]
                )
            ),
        ]
    )

    selected_source_ids = _parse_selected_source_ids(response.content, set(active_source_ids))
    sources = get_sources_by_ids(db, selected_source_ids)
    print("selected_source_ids", selected_source_ids)
    source_snapshot = _build_source_snapshot(sources)
    return {"source_snapshot": source_snapshot}
