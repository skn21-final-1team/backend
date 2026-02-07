from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user_email: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class SignupResponse(BaseModel):
    message: str
    user_id: int
    user_email: str
