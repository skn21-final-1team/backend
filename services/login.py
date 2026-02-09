from sqlalchemy.orm import Session

from core.exceptions.user import UserNotFoundException, UserPasswordNotMatchException
from core.security import verify_password
from crud.user import get_user_by_email
from models.user import UserModel
from schemas.login import LoginRequest


class LoginService:
    def login(self, req: LoginRequest, db: Session) -> UserModel:
        user = get_user_by_email(db, req.email)

        if not user:
            raise UserNotFoundException()
        if not verify_password(req.password, user.password):
            raise UserPasswordNotMatchException()
        return user


login_service = LoginService()
