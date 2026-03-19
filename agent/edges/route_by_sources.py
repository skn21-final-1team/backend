from agent.state import QAState

MAX_RETRIEVAL_RETRIES = 1


def route_by_sources(state: QAState) -> str:
    """검색 결과 유무에 따라 다음 노드를 결정합니다.

    Returns:
        "generate_answer": 소스 자료가 있거나 재시도 횟수를 초과한 경우
        "rewrite_query": 소스 자료가 없고 재시도 가능한 경우
    """
    sources = state.get("sources", [])
    retrieval_count = state.get("retrieval_count", 0)

    if not sources and retrieval_count <= MAX_RETRIEVAL_RETRIES:
        return "rewrite_query"
    return "generate_answer"
