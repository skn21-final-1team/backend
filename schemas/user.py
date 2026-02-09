import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일", examples=["dev_gemini@openai.com"])
    password: str = Field(..., min_length=8, max_length=20)

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


class UserInfo(BaseModel):
    name: str
    email: EmailStr
