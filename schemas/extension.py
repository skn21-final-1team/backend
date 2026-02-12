from __future__ import annotations

from pydantic import BaseModel, Field


class BookmarkUrl(BaseModel):
    title: str
    url: str


class BookmarkFolder(BaseModel):
    name: str = Field(alias="title")
    folders: list[BookmarkFolder] = []
    urls: list[BookmarkUrl] = []


class ExtensionBulkRequest(BaseModel):
    folders: list[BookmarkFolder]
