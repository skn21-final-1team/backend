import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
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

GOOGLE_OAUTH_URL = "https://oauth2.googleapis.com/token"


class GoogleAuthService:
    def verify_and_login(self, code: str, db: Session) -> UserModel:
        user_info = self._verify_google_token(code)
        email = user_info["email"]
        name = user_info.get("name", email.split("@")[0])

        user = get_user_by_email(db, email)
        if not user:
            user = create_oauth_user(db, email, name, "google")

        if user.auth_provider != "google":
            raise OAuthAccountConflictException

        return user

    def _verify_google_token(self, code: str) -> dict[str, str]:
        res = httpx.post(
            GOOGLE_OAUTH_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": "http://localhost:3000/auth/callback",
                "grant_type": "authorization_code",
            },
        )

        token = res.json().get("id_token")
        print("google login token", res.json())

        if not token:
            raise InvalidGoogleTokenException

        payload = id_token.verify_oauth2_token(token, google_requests.Request(), settings.google_client_id)

        if payload.get("aud") != settings.google_client_id:
            raise GoogleClientIdMismatchException

        return payload


google_auth_service = GoogleAuthService()
