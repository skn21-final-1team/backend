from pydantic import BaseModel, Field


class DirectoryKeyResponse(BaseModel):
    bookmark_sync_key: str = Field(..., description="외부 확장 프로그램에 사용되는 북마크 동기화 키")
    expires_at: str = Field(..., description="북마크 동기화 키의 만료 시간")
