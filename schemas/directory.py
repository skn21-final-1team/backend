from pydantic import BaseModel, Field


class BookmarkFromExtension(BaseModel):
    id: int
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
