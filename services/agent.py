from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from agent.graph import graph
from crud.chat import get_chat_by_notebook_id
from schemas.chat import ChatHistoryForAgent, ChatRequest


class AgentService:
    def __sse_event(self, event_name: str, data: str) -> str:
        """Server-Sent Event 메시지 페이로드를 생성합니다."""
        return f"event: {event_name}\ndata: {data}\n\n"

    def __chat_history(self, notebook_id: int, db: Session) -> list[ChatHistoryForAgent]:
        """이전 채팅 이력을 role/message 형식으로 변환합니다."""
        chats = get_chat_by_notebook_id(db, notebook_id)
        return [ChatHistoryForAgent.model_validate(chat) for chat in chats]

    def __is_return_sse(self, mode: str, chunk: dict | tuple) -> bool:
        if mode != "messages":
            return False
        return_nodes = frozenset({"generate_answer", "casual_answer"})
        _, metadata = chunk
        return metadata.get("langgraph_node") in return_nodes

    async def stream_chat(self, req: ChatRequest, db: Session) -> AsyncGenerator[str, None]:
        """SSE 프레임반환, 마지막은 DONE 이벤트 반환"""
        chat_history = self.__chat_history(req.notebook_id, db)

        async for mode, chunk in graph.astream(
            {
                "notebook_id": req.notebook_id,
                "question": req.message,
                "chat_history": chat_history,
            },
            stream_mode=["updates", "messages"],
            version="v2",
        ):
            if not self.__is_return_sse(mode, chunk):
                continue

            message_chunk, _ = chunk
            yield self.__sse_event(mode, message_chunk.content)
        yield self.__sse_event("done", "[DONE]")


agent_service = AgentService()
