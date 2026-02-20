import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

import crud.notebook as notebook_crud
from core.exceptions.common import InvalidRequestException
from crud.extension_sync_key import create_sync_key, delete_sync_key


class ExtensionSyncKeyService:
    @staticmethod
    def generate_sync_key(user_id: int, db: Session, notebook_id: int) -> tuple[str, str]:
        notebook = notebook_crud.get_notebook(db, notebook_id)
        if not notebook:
            raise InvalidRequestException

        if notebook.user_id != user_id:
            raise InvalidRequestException

        delete_sync_key(db, user_id)

        sync_key = secrets.token_urlsafe(16)
        expires_at = datetime.now(UTC) + timedelta(minutes=15)

        create_sync_key(db=db, user_id=user_id, sync_key=sync_key, expires_at=expires_at, notebook_id=notebook_id)

        return sync_key, expires_at.isoformat()


extension_sync_key_service = ExtensionSyncKeyService()
