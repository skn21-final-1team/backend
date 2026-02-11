from sqlalchemy.orm import Session

from core.config import get_settings
from core.exceptions.auth import ExpiredRefreshTokenException, InvalidRefreshTokenException
from core.security import create_access_token, create_refresh_token, decode_token
from crud.refresh_token import (
    create_refresh_token as save_refresh_token,
)
from crud.refresh_token import (
    delete_refresh_token,
    get_refresh_token,
)

settings = get_settings()


class AuthService:
    def create_tokens(self, user_id: int, db: Session) -> tuple[str, str]:
        token_data = {"sub": str(user_id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        save_refresh_token(db, user_id, refresh_token, settings.refresh_token_expire_days)

        return access_token, refresh_token

    def refresh_access_token(self, refresh_token_str: str, db: Session) -> tuple[str, str]:
        stored_token = get_refresh_token(db, refresh_token_str)
        if not stored_token:
            raise ExpiredRefreshTokenException

        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise InvalidRefreshTokenException

        delete_refresh_token(db, refresh_token_str)

        token_data = {"sub": str(stored_token.user_id)}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        save_refresh_token(db, stored_token.user_id, new_refresh_token, settings.refresh_token_expire_days)

        return new_access_token, new_refresh_token


auth_service = AuthService()
