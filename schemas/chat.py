from pydantic import BaseModel, Field

from datetime import datetime

class NotebookRequest(BaseModel):
    title: str = Field(..., description="노트북 제목", examples=["노트북 1"])

class NotebookResponse(BaseModel):
    id: int
    title: str 

class ChatRequest(BaseModel):
    role: str = Field(..., description="채팅 역할", examples=["user"])
    message: str = Field(..., description="채팅 메시지", examples=["안녕하세요"])
    notebook_id: int = Field(..., description="노트북 ID", examples=[1])

class ChatResponse(BaseModel):
    id: int
    role: str
    message: str
    created_at: datetime
    notebook_id: int