import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일", examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=20, description="비밀번호")
    name: str = Field(..., min_length=2, max_length=20, description="사용자 이름")

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[a-z]", v):
            raise ValueError("비밀번호는 최소 하나의 소문자를 포함해야 합니다.")
        if not re.search(r"\d", v):
            raise ValueError("비밀번호는 최소 하나의 숫자를 포함해야 합니다.")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("비밀번호는 최소 하나의 특수문자(@$!%*?&)를 포함해야 합니다.")
        return v
