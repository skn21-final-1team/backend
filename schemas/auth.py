from pydantic import BaseModel, EmailStr, Field


class GoogleLoginRequest(BaseModel):
    code: str = Field(..., description="Google Auth Code")


class TokenResponse(BaseModel):
    access_token: str


class LoginResponse(BaseModel):
    access_token: str
    user: "UserInfoResponse"


class UserInfoResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    auth_provider: str
