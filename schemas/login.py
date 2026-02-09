from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일", examples=["dev_gemini@openai.com"])
    password: str = Field(..., max_length=20)


class UserInfo(BaseModel):
    name: str
    email: EmailStr
