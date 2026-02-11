import hashlib
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from models.refresh_token import RefreshTokenModel


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(db: Session, user_id: int, token: str, expire_days: int) -> RefreshTokenModel:
    token_hash = hash_token(token)
    expires_at = datetime.now(UTC) + timedelta(days=expire_days)

    refresh_token = RefreshTokenModel(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_refresh_token(db: Session, token: str) -> RefreshTokenModel | None:
    token_hash = hash_token(token)
    return (
        db.query(RefreshTokenModel)
        .filter(
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.expires_at > datetime.now(UTC),
        )
        .first()
    )


def delete_refresh_token(db: Session, token: str) -> None:
    token_hash = hash_token(token)
    db.query(RefreshTokenModel).filter(RefreshTokenModel.token_hash == token_hash).delete()
    db.commit()


def delete_user_tokens(db: Session, user_id: int) -> None:
    db.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user_id).delete()
    db.commit()
