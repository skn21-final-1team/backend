from pydantic import BaseModel, Field

from datetime import datetime

class NotebookRequest(BaseModel):
    title: str = Field(..., description="노트북 제목", examples=["노트북 1"])

class NotebookResponse(BaseModel):
    id: int
    title: str