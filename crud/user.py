from sqlalchemy.orm import Session

from core.security import get_password_hash
from models.user import UserModel


def get_user_by_email(db: Session, user_email: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.email == user_email).first()


def create_user(db: Session, email: str, password: str, name: str) -> UserModel:
    hashed_password = get_password_hash(password)
    new_user = UserModel(email=email, password=hashed_password, name=name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
