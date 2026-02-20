from sqlalchemy.orm import Session

from models.directory_key import DirectoryKeyModel


def delete_directory_key_by_user(db: Session, user_id: int) -> None:
    db.query(DirectoryKeyModel).filter(DirectoryKeyModel.user_id == user_id).delete(synchronize_session=False)
    db.commit()


def create_directory_key(
    db: Session, user_id: int, bookmark_sync_key: str, expires_at: str | None = None
) -> DirectoryKeyModel:
    db_key = DirectoryKeyModel(user_id=user_id, bookmark_sync_key=bookmark_sync_key, expires_at=expires_at)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key
