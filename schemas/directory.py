from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookmarkFromExtension(BaseModel):
    id: str | int
    url: str | None = None
    title: str
    children: list["BookmarkFromExtension"]


class DirectorySyncRequest(BaseModel):
    sync_key: str = Field(..., description="외부 확장 프로그램에 사용되는 동기화 키")
    bookmarks: list[BookmarkFromExtension]


class DirectorySyncKeyRequest(BaseModel):
    notebook_id: int = Field(..., description="북마크 저장할 노트북 아이디")


class DirectorySyncKeyResponse(BaseModel):
    sync_key: str = Field(..., description="외부 확장 프로그램에 사용되는 동기화 키")
    expires_at: str = Field(..., description="동기화 키 만료 시간")


class SourceResponse(BaseModel):
    id: int
    url: str
    title: str | None
    summary: str | None
    directory_id: int | None
    is_active: bool
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class DirectoryUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, description="변경할 디렉토리 이름")


class DirectoryResponse(BaseModel):
    id: int
    title: str
    url: None = None
    parent_id: int | None
    notebook_id: int
    children: list["DirectoryResponse"] = []
    sources: list[SourceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DirectoryTreeResponse(BaseModel):
    directories: list[DirectoryResponse]
    sources: list[SourceResponse]
