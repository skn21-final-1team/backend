from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from agent.model.llm_factory import DEFAULT_LLM_MODEL_NAME


class ChatRequest(BaseModel):
    message: str = Field(..., description="채팅 메시지", examples=["안녕하세요"])
    notebook_id: int = Field(..., description="노트북 ID", examples=[1])
    model_name: str = Field(
        default=DEFAULT_LLM_MODEL_NAME,
        description="채팅 응답 생성에 사용할 LLM 모델 이름",
        examples=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1", "exaone"],
    )


class ChatResponse(BaseModel):
    id: int
    role: str
    message: str
    created_at: datetime
    notebook_id: int


class ChatHistoryForAgent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    message: str
