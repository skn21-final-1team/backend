from pydantic import BaseModel


class CrawlRequestBody(BaseModel):
    urls: list[str]
    notebook_id: int
    directory_id: int | None = None
    source_id: int
