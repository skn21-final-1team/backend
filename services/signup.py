from datetime import UTC, datetime

from fastapi import HTTPException, status

from schemas.auth import SignupRequest, SignupResponse

DUMMY_USERS: dict[int, dict[str, str | int]] = {
    1: {
        "id": 1,
        "email": "test@example.com",
        "password": "password123",
        "name": "테스트유저",
        "created_at": "2026-01-01T00:00:00",
    },
    2: {
        "id": 2,
        "email": "admin@example.com",
        "password": "admin1234",
        "name": "관리자",
        "created_at": "2026-01-01T00:00:00",
    },
}


def get_next_user_id() -> int:
    if not DUMMY_USERS:
        return 1
    return max(DUMMY_USERS.keys()) + 1


def get_user_by_email(email: str) -> dict[str, str | int] | None:
    for user in DUMMY_USERS.values():
        if user["email"] == email:
            return user
    return None


class SignupService:
    def signup(self, request: SignupRequest) -> SignupResponse:
        existing_user = get_user_by_email(request.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        new_user_id = get_next_user_id()
        new_user = {
            "id": new_user_id,
            "email": request.email,
            "password": request.password,
            "name": request.name,
            "created_at": datetime.now(UTC).isoformat(),
        }
        DUMMY_USERS[new_user_id] = new_user

        return SignupResponse(
            message="Signup successful",
            user_id=new_user_id,
            user_email=request.email,
        )


signup_service = SignupService()
