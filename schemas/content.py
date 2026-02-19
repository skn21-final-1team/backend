from pydantic import BaseModel

class SourceNode(BaseModel):
    id: int
    title: str | None
    url: str
    type: str

class ContentNode(BaseModel):
    id: int
    title: str
    parent_id: int | None
    is_expanded: bool = False
    sources: list[SourceNode] = []
    children: list["ContentNode"] = []