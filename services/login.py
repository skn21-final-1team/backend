from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.auth import LoginRequest, LoginResponse

from fastapi import HTTPException, status

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


if __name__ == "__main__":
    print("=== Login Service Test ===")
    email = "admin@example.com"
    password = "admin1234"

    stored_password = DUMMY_USERS.get(email)
    if stored_password is None:
        print(f"[X] Login Failed: '{email}' user not found.")
    elif password != stored_password:
        print("[X] Login Failed: Password does not match.")
    else:
        print(f"[O] Login Success: {email}")
