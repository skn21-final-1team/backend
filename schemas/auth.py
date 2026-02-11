from pydantic import BaseModel, EmailStr, Field


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google ID Token")


class TokenResponse(BaseModel):
    access_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh Token")


class LoginResponse(BaseModel):
    access_token: str
    user: "UserInfoResponse"


class UserInfoResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    auth_provider: str
