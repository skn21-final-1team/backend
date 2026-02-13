from pydantic import BaseModel


class ExtensionBookmarkNode(BaseModel):
    id: str
    title: str
    url: str | None = None
    children: list["ExtensionBookmarkNode"] = []


class ExtensionUploadRequest(BaseModel):
    bookmarks: list[ExtensionBookmarkNode]