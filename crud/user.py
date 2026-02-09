from sqlalchemy.orm import Session

from models.user import UserModel


def get_user_by_email(db: Session, user_email: str):
    return db.query(UserModel).filter(UserModel.email == user_email).first()
