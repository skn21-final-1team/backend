from pydantic import BaseModel, Field, HttpUrl


class CrawlRequest(BaseModel):
    urls: list[HttpUrl] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="크롤링할 URL 목록",
        examples=[["https://example.com"]],
    )


class CrawlResult(BaseModel):
    url: str = Field(..., description="크롤링한 URL")
    title: str | None = Field(default=None, description="페이지 제목")
    summary: str = Field(..., description="추출된 본문 텍스트")
