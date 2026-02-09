from crud.user import create_user, get_user_by_email
from schemas.auth import SignupRequest


class SignupService:
    def signup(self, request: SignupRequest) -> dict[str, str | int] | None:
        existing_user = get_user_by_email(request.email)
        if existing_user is not None:
            return None

        new_user = create_user(
            email=request.email,
            password=request.password,
            name=request.name,
        )
        return new_user


signup_service = SignupService()
