from pydantic import BaseModel, EmailStr

from crud.user import create_user, get_user_by_email


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class SignupService:
    def signup(self, request: SignupRequest) -> bool:
        existing_user = get_user_by_email(request.email)
        if existing_user is not None:
            return False

        create_user(
            email=request.email,
            password=request.password,
            name=request.name,
        )
        return True


signup_service = SignupService()
