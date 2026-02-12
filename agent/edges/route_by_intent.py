from agent.state import QAState


def route_by_intent(state: QAState) -> str:
    """사용자 의도 분석
    Args:
        state: QAState
    Returns:
        "retrieve_sources": 노트북 소스 자료를 기반으로 답변이 필요한 질문
        "casual_answer": 일상적인 인사, 잡담, 단순 대화
    """
    if state.get("intent") == "question":
        print("[route_by_intent] → retrieve_sources")
        return "retrieve_sources"
    print("[route_by_intent] → casual_answer")
    return "casual_answer"
