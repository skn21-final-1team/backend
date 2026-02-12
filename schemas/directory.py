from pydantic import BaseModel, Field


class DirectoryRequest(BaseModel):
    title: str = Field(..., description="디렉토리 제목", examples=["폴더 1"])
    parent_id: int | None = Field(None, description="부모 디렉토리 ID (루트면 None)", examples=[1])


class DirectoryResponse(BaseModel):
    id: int
    title: str
    notebook_id: int
    parent_id: int | None
