"""
Baseline 그래프 — requery 없이 직접 검색하는 기존 방식 재현.

비교 대상:
  - baseline: classify → retrieve → generate (requery 없음, 기존 프롬프트)
  - new:      classify → rewrite/decompose → retrieve → generate (requery + 개선 프롬프트)
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from agent.model.llm_factory import llm_factory
from agent.nodes.save_chat import save_chat
from agent.state import QAState

# --- Baseline 프롬프트 (수정 전 원본) ---

BASELINE_QA_SYSTEM_PROMPT = """당신은 사용자의 노트북에 저장된 소스 자료를 기반으로 질문에 답변하는 AI 어시스턴트입니다.

아래 규칙을 따르세요:
1. 제공된 소스 자료와 이전 대화 이력을 근거로 정확하게 답변하세요.
2. 소스 자료에 없는 내용은 추측하지 말고, 자료에 해당 내용이 없다고 안내하세요.
3. 답변은 한국어로 작성하세요.
4. 마크다운 형식을 사용하여 가독성 있게 답변하세요.
5. 제공된 소스 자료가 없다면, "해당 내용을 소스에서 찾을 수 없어요 :("라고 답변하세요."""

BASELINE_QA_USER_PROMPT = """## 소스 자료
{sources}

## 대화 이력
{chat_history}

## 질문
{question}"""

BASELINE_CLASSIFY_PROMPT = """당신은 사용자의 입력 의도를 분류하는 분류기입니다.
사용자의 메시지를 읽고 아래 두 가지 중 하나로 분류하세요.

- "question": 노트북 소스 자료를 기반으로 답변이 필요한 질문
- "casual": 일상적인 인사, 잡담, 단순 대화

반드시 "question" 또는 "casual" 중 하나만 출력하세요. 다른 텍스트는 포함하지 마세요.

사용자 메시지: {question}"""

BASELINE_CASUAL_PROMPT = """당신은 친절한 AI 어시스턴트입니다.
사용자와 자연스럽게 대화하세요. 답변은 한국어로 작성하세요.

## 사용자 메시지
{question}"""


# --- Baseline 노드 ---

from pydantic import BaseModel, Field  # noqa: E402


class BaselineIntent(BaseModel):
    intent: str = Field(description='"question" 또는 "casual"')


def _parse_baseline_intent(text: str) -> str:
    """텍스트 응답에서 intent를 추출합니다."""
    text_lower = text.strip().lower().strip('"\'')
    if text_lower in ("question", "casual"):
        return "simple" if text_lower == "question" else "casual"
    if "question" in text_lower:
        return "simple"
    if "casual" in text_lower:
        return "casual"
    return "simple"


def baseline_classify_intent(state: QAState, config: RunnableConfig) -> dict:
    try:
        messages = [SystemMessage(content=BASELINE_CLASSIFY_PROMPT.format(question=state["question"]))]
        llm = llm_factory.get_llm(config)

        if llm_factory.supports_structured_output(config):
            response = llm.with_structured_output(BaselineIntent).invoke(messages)
            intent = "simple" if response.intent == "question" else "casual"
            return {"intent": intent}
        else:
            response = llm.invoke(messages)
            return {"intent": _parse_baseline_intent(response.content)}
    except Exception:
        return {"intent": "simple"}


async def baseline_retrieve_sources(state: QAState) -> dict:
    """원본 question을 그대로 검색에 사용 (requery 없음)."""
    from agent.model.embedding import embeddings
    from agent.model.reranker import reranker
    from agent.nodes.retrieve_sources import async_engine, vector_store
    from core.config import get_settings
    from crud.source import get_active_source_ids, get_source_ids_by_notebook
    from db.database import get_db_context

    notebook_id = state["notebook_id"]
    question = state["question"]

    with get_db_context() as db:
        notebook_source_ids = get_source_ids_by_notebook(db, notebook_id)
        if not notebook_source_ids:
            return {"sources": []}
        active_source_ids = get_active_source_ids(db, notebook_source_ids)
        if not active_source_ids:
            return {"sources": []}

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 10,
            "filter": {"source_id": {"$in": active_source_ids}},
        }
    )

    docs = await retriever.ainvoke(question)
    contents = [doc.page_content for doc in docs]

    if not contents:
        return {"sources": []}

    reranked = await reranker.rerank(question, contents)
    return {"sources": reranked}


def baseline_format_chat_history(history: list[dict]) -> str:
    if not history:
        return "없음"
    return "\n".join(f"{chat.role}: {chat.message}" for chat in history)


async def baseline_generate_answer(state: QAState, config: RunnableConfig) -> dict:
    """기존 프롬프트로 답변 생성 (소스 번호 매기기 없음, --- 구분자)."""
    chat_history_text = baseline_format_chat_history(state.get("chat_history", []))
    sources_text = "\n\n---\n\n".join(state.get("sources", []))

    messages = [
        SystemMessage(content=BASELINE_QA_SYSTEM_PROMPT),
        HumanMessage(
            content=BASELINE_QA_USER_PROMPT.format(
                sources=sources_text,
                chat_history=chat_history_text,
                question=state["question"],
            )
        ),
    ]

    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(messages)
    return {"answer": response.content}


async def baseline_casual_answer(state: QAState, config: RunnableConfig) -> dict:
    messages = [SystemMessage(content=BASELINE_CASUAL_PROMPT.format(question=state["question"]))]
    llm = llm_factory.get_llm(config)
    response = await llm.ainvoke(messages)
    return {"answer": response.content}


def baseline_route_by_intent(state: QAState) -> str:
    if state.get("intent") == "casual":
        return "casual_answer"
    return "retrieve_sources"


# --- Baseline 그래프 조립 ---

baseline_workflow = StateGraph(QAState)

baseline_workflow.add_node("classify_intent", baseline_classify_intent)
baseline_workflow.add_node("retrieve_sources", baseline_retrieve_sources)
baseline_workflow.add_node("generate_answer", baseline_generate_answer)
baseline_workflow.add_node("casual_answer", baseline_casual_answer)
baseline_workflow.add_node("save_chat", save_chat)

baseline_workflow.add_edge(START, "classify_intent")
baseline_workflow.add_conditional_edges("classify_intent", baseline_route_by_intent)
baseline_workflow.add_edge("retrieve_sources", "generate_answer")
baseline_workflow.add_edge("generate_answer", "save_chat")
baseline_workflow.add_edge("casual_answer", "save_chat")
baseline_workflow.add_edge("save_chat", END)

baseline_graph = baseline_workflow.compile()
