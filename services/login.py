from core.exceptions.user import UserNotFoundException, UserPasswordNotMatchException
from schemas.auth import LoginRequest, LoginResponse

# DB 연결 시 삭제 예정
DUMMY_USERS = {
    "id": 1,
    "email": "test@example.com",
    "password": "password123",
    "name": "test",
    "created_at": "2022-01-01",
}


class LoginService:
    def login(self, req: LoginRequest) -> LoginResponse:
        # DB 연결 시 DUMMY_USERS를 DB에서 유저테이블로 변경, dict형태에서 table에 맞도록 수정
        stored_password = DUMMY_USERS.get(req.email)

        if stored_password is None:
            raise UserNotFoundException
        if req.password != stored_password:
            raise UserPasswordNotMatchException
        return DUMMY_USERS


login_service = LoginService()
