import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from crud.directory_key import create_directory_key, delete_directory_key_by_user


class DirectoryKeyService:
    @staticmethod
    def generate_directory_key(user_id: int, db: Session) -> tuple[str, str]:
        delete_directory_key_by_user(db, user_id)

        bookmark_sync_key = secrets.token_urlsafe(16)
        expires_at = datetime.now(UTC) + timedelta(minutes=15)

        create_directory_key(db=db, user_id=user_id, bookmark_sync_key=bookmark_sync_key, expires_at=expires_at)

        return bookmark_sync_key, expires_at


directory_key_service = DirectoryKeyService()
