from pydantic import BaseModel, Field


class BookmarkFromExtension(BaseModel):
    id: int
    url: str | None = None
    title: str
    children: list["BookmarkFromExtension"]


class ExtensionSyncRequest(BaseModel):
    sync_key: str = Field(..., description="외부 확장 프로그램에 사용되는 동기화 키")
    bookmarks: list[BookmarkFromExtension]
