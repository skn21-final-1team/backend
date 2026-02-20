from sqlalchemy.orm import Session

from models.extension import ExtensionSyncKeyModel


def delete_sync_key(db: Session, sync_key: str) -> None:
    db.query(ExtensionSyncKeyModel).filter(ExtensionSyncKeyModel.sync_key == sync_key).delete(synchronize_session=False)
    db.commit()


def create_sync_key(
    db: Session,
    user_id: int,
    sync_key: str,
    notebook_id: int,
    expires_at: str | None = None,
) -> ExtensionSyncKeyModel:
    db_key = ExtensionSyncKeyModel(user_id=user_id, sync_key=sync_key, notebook_id=notebook_id, expires_at=expires_at)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


def get_sync_key(db: Session, sync_key: str) -> ExtensionSyncKeyModel | None:
    return db.query(ExtensionSyncKeyModel).filter(ExtensionSyncKeyModel.sync_key == sync_key).first()
