import httpx
from sqlalchemy.orm import Session

from core.config import get_settings
from core.exceptions.auth import (
    GoogleClientIdMismatchException,
    InvalidGoogleTokenException,
    OAuthAccountConflictException,
)
from crud.user import create_oauth_user, get_user_by_email
from models.users import UserModel

settings = get_settings()

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class GoogleAuthService:
    def verify_and_login(self, id_token: str, db: Session) -> UserModel:
        user_info = self._verify_google_token(id_token)
        email = user_info["email"]
        name = user_info.get("name", email.split("@")[0])

        user = get_user_by_email(db, email)
        if not user:
            user = create_oauth_user(db, email, name, "google")

        if user.auth_provider != "google":
            raise OAuthAccountConflictException

        return user

    def _verify_google_token(self, id_token: str) -> dict[str, str]:
        response = httpx.get(GOOGLE_TOKENINFO_URL, params={"access_token": id_token})

        if not response.is_success:
            raise InvalidGoogleTokenException

        payload = response.json()

        if payload.get("aud") != settings.google_client_id:
            raise GoogleClientIdMismatchException

        return payload


google_auth_service = GoogleAuthService()
