from datetime import datetime

from pydantic import BaseModel, Field


class NotebookRequest(BaseModel):
    title: str = Field(..., description="노트북 제목", examples=["노트북 1"])


class NotebookResponse(BaseModel):
    id: int
    title: str
    pinned: bool
    created_at: datetime = Field(..., description="노트북 생성 시간", examples=["2024-01-01T12:00:00Z"])


class NotebookUpdateRequest(BaseModel):
    title: str
