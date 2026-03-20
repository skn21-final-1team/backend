from agent.state import QAState


def route_by_intent(state: QAState) -> str:
    """사용자 의도와 복잡도에 따라 다음 노드를 결정합니다.

    Returns:
        "retrieve_sources": 단순 질문 → 원본 쿼리로 바로 검색
        "decompose_query": 복합 질문 → 질문 분해
        "casual_answer": 일상 대화
    """
    intent = state.get("intent", "simple")
    if intent == "complex":
        return "decompose_query"
    if intent == "casual":
        return "casual_answer"
    return "retrieve_sources"
