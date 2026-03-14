from pydantic import BaseModel, ConfigDict, Field


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str = Field(..., description="크롤링한 URL")
    title: str | None = Field(default=None, description="페이지 제목")
    summary: str | None = Field(default=None, description="추출된 본문 텍스트")
    is_active: bool = Field(..., description="소스 활성화 여부")


class SourceRequest(BaseModel):
    id: int
    title: str = Field(..., description="소스 이름", examples=["Kaggle: Your Home for Data Science"])


class SourceUpdateRequest(BaseModel):
    title: str | None = Field(default=None, description="소스 이름", examples=["Kaggle: Your Home for Data Science"])
    is_active: bool | None = Field(default=None, description="소스 활성화 여부")


class SourceAddRequest(BaseModel):
    title: str | None = Field(default=None, description="소스 이름", examples=["Kaggle: Your Home for Data Science"])
    url: str = Field(..., description="크롤링한 URL")
    is_active: bool | None = Field(default=None, description="소스 활성화 여부")
    directory_id: int | None = Field(default=None, description="소스의 부모 디렉토리 id")
    notebook_id: int = Field(..., description="크롤링한 URL")
