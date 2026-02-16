from pydantic import BaseModel, Field


class DirectoryRequest(BaseModel):
    title: str = Field(..., description="디렉토리 제목", examples=["폴더 1"])
    parent_id: int | None = Field(None, description="부모 디렉토리 ID", examples=[1])
    notebook_id: int = Field(..., description="노트북 ID", examples=[1])


class DirectoryResponse(BaseModel):
    id: int
    title: str
    notebook_id: int
    parent_id: int | None

    @staticmethod
    def from_model(directory):
        return DirectoryResponse(
            id=directory.id,
            title=directory.name,
            notebook_id=directory.notebook_id,
            parent_id=directory.parent_id,
        )
