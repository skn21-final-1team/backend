from fastapi import HTTPException, status

from core.security import create_access_token
from schemas.auth import LoginRequest, LoginResponse
from services.signup import get_user_by_email


class LoginService:
    def login(self, login_request: LoginRequest) -> LoginResponse:
        user = get_user_by_email(login_request.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if login_request.password != user["password"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = create_access_token(data={"user_id": user["id"], "email": str(user["email"])})

        return LoginResponse(
            message="Login successful",
            user_email=login_request.email,
            access_token=access_token,
        )


login_service = LoginService()
