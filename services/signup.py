from sqlalchemy.orm import Session

from core.exceptions.user import UserAlreadyExistsException
from crud.user import create_user, get_user_by_email
from schemas.signup import SignupRequest


class SignupService:
    def signup(self, request: SignupRequest, db: Session) -> None:
        if get_user_by_email(db, request.email):
            raise UserAlreadyExistsException()
        create_user(db, request.email, request.password, request.name)


signup_service = SignupService()
