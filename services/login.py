from fastapi import HTTPException, status

from schemas.auth import LoginRequest, LoginResponse

# DB 연결 시 삭제 예정
DUMMY_USERS = {
    "test@example.com": "password123",
    "admin@example.com": "admin1234",
}


class LoginService:
    def login(self, login_request: LoginRequest) -> LoginResponse:
        # DB 연결 시 DUMMY_USERS를 DB에서 유저테이블로 변경, dict형태에서 table에 맞도록 수정
        stored_password = DUMMY_USERS.get(login_request.email)
        if stored_password is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if login_request.password != stored_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return LoginResponse(
            message="Login successful",
            user_email=login_request.email,
        )


login_service = LoginService()
