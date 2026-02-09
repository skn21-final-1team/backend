from core.exceptions.user import UserAlreadyExistsException
from crud.user import create_user, get_user_by_email
from schemas.signup import SignupRequest


class SignupService:
    def signup(self, request: SignupRequest) -> None:
        existing_user = get_user_by_email(request.email)
        if existing_user is not None:
            raise UserAlreadyExistsException

        create_user(
            email=request.email,
            password=request.password,
            name=request.name,
        )


signup_service = SignupService()
