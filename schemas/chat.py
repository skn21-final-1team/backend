from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="채팅 메시지", examples=["안녕하세요"])
    notebook_id: int = Field(..., description="노트북 ID", examples=[1])


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
