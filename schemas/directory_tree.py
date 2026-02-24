from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceNode(BaseModel):
    id: int
    url: str
    title: str | None
    summary: str | None
    directory_id: int | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DirectoryNode(BaseModel):
    id: int
    title: str
    parent_id: int | None
    notebook_id: int
    children: list["DirectoryNode"] = []
    sources: list[SourceNode] = []

    model_config = ConfigDict(from_attributes=True)


class DirectoryTreeResponse(BaseModel):
    notebook_id: int
    directories: list[DirectoryNode]
    unassigned_sources: list[SourceNode]
