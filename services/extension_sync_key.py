import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from crud.extension_sync_key import create_directory_key, delete_directory_key_by_user


class ExtensionSyncKeyService:
    @staticmethod
    def generate_sync_key(user_id: int, db: Session) -> tuple[str, str]:
        delete_directory_key_by_user(db, user_id)

        sync_key = secrets.token_urlsafe(16)
        expires_at = datetime.now(UTC) + timedelta(minutes=15)

        create_directory_key(db=db, user_id=user_id, sync_key=sync_key, expires_at=expires_at)

        return sync_key, expires_at.isoformat()


extension_sync_key_service = ExtensionSyncKeyService()
