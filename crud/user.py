from datetime import UTC, datetime

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


def create_user(email: str, password: str, name: str) -> dict[str, str | int]:
    new_user_id = get_next_user_id()
    new_user: dict[str, str | int] = {
        "id": new_user_id,
        "email": email,
        "password": password,
        "name": name,
        "created_at": datetime.now(UTC).isoformat(),
    }
    DUMMY_USERS[new_user_id] = new_user
    return new_user
