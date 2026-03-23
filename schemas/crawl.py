from pydantic import BaseModel


class CrawlRequestBody(BaseModel):
    urls: list[str]
    notebook_id: int
    directory_id: int | None = None
    source_id: int


class CrawlSourceItem(BaseModel):
    source_id: int
    url: str


class CrawlNewRequest(BaseModel):
    sources: list[CrawlSourceItem]


class CrawlResponse(BaseModel):
    status: str
    accepted: list[int]
    not_found: list[int]


class CrawlCallbackEvent(BaseModel):
    source_id: int
    event: str
    stage: str | None = None
    error: str | None = None


class CrawlSyncRequest(BaseModel):
    source_ids: list[int]
    notebook_id: int


class CrawlSyncResponse(BaseModel):
    status: str
    accepted: list[int]
    not_found: list[int]
