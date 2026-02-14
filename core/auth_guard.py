from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import get_settings
from core.exceptions.user import InvalidUserException, UserNotFoundException
from core.security import decode_token
from db.database import DbSession
from models.users import UserModel

settings = get_settings()
security_scheme = HTTPBearer()
optional_security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: DbSession,
) -> UserModel:
    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise InvalidUserException

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidUserException

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if user is None:
        raise UserNotFoundException

    return user


def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_security_scheme)],
    db: DbSession,
) -> UserModel | None:
    if credentials is None:
        return None

    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        return None

    if payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
OptionalUser = Annotated[UserModel | None, Depends(get_optional_user)]
