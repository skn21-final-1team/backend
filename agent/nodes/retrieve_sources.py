import random

from agent.state import QAState
from db.database import SessionLocal


def retrieve_sources(_: QAState) -> dict[str, list[str]]:
    """노트북에 연결된 소스 자료를 조회합니다.

    Args:
        _: QAState (현재 미사용)
    Returns:
        sources 키를 포함한 딕셔너리
    """
    print("[retrieve_sources] 소스 조회 시작")
    db = SessionLocal()
    try:
        temp_sources = """
        LangGraph overview
Gain control with LangGraph to design agents that reliably handle complex tasks
Trusted by companies shaping the future of agents— including Klarna, Replit, Elastic, and more— LangGraph is a low-level
orchestration framework and runtime for building, managing, and deploying long-running, stateful agents.
LangGraph is very low-level,and focused entirely on agent orchestration. Before using LangGraph,
we recommend you familiarize yourself with some of the components used to build agents, starting with models and tools.
We will commonly use LangChain components throughout the documentation to integrate models and tools,
but you don\'t need to use LangChain to use LangGraph.
        """

        # TODO: 리트리버 구현 후 대체
        num = random.randint(1, 10)  # noqa: S311
        limit = 8
        if num < limit:
            return {"sources": [temp_sources]}
        return {"sources": []}
    finally:
        db.close()
