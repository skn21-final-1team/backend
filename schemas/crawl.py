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


class CrawlSyncBody(BaseModel):
    url: str
    directory_id: int
    source_id: int


class CrawlSyncRequest(BaseModel):
    sources: list[CrawlSyncBody]
    notebook_id: int


class CrawlSyncResponse(BaseModel):
    source_id: list[int]
    status_list: list[str]
