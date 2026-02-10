from pydantic import BaseModel, ConfigDict, Field


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str = Field(..., description="크롤링한 URL")
    title: str | None = Field(default=None, description="페이지 제목")
    summary: str | None = Field(default=None, description="추출된 본문 텍스트")
