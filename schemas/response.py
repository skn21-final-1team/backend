from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str
    data: T | None = None

    @classmethod
    def ok(cls, data: T | None = None, message: str = "Success"):
        return cls(code=0, data=data, message=message)

    @classmethod
    def error(cls, message: str, code: int = 0, data: T | None = None):
        return cls(code=code, data=data, message=message)
