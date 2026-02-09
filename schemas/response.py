from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str
    data: T | None = None
    status: str = "success"

    # 단순화를 위한 헬퍼 메서드
    @classmethod
    def ok(cls, data: T | None = None, message: str = "Success"):
        return cls(status="success", code=0, data=data, message=message)

    @classmethod
    def error(cls, data: T | None = None, code: int = -1, message: str = "Error"):
        return cls(status="error", code=code, data=data, message=message)
