from datetime import UTC, datetime

from sqlalchemy.orm import Session

import crud.directory as directory_crud
import crud.extension_sync_key as extension_sync_key_crud
import crud.source as source_crud
from core.exceptions.auth import InvalidTokenException
from schemas.directory import BookmarkFromExtension


class DirectorySyncService:
    def get_user_id_from_sync_key(self, sync_key: str, db: Session) -> bool:
        sync_key = extension_sync_key_crud.get_sync_key(db, sync_key)
        if not sync_key:
            raise InvalidTokenException

        if sync_key.expires_at < datetime.now(UTC):
            raise InvalidTokenException

        return sync_key.user_id

    def delete_sync_key(self, sync_key: str, db: Session) -> None:
        extension_sync_key_crud.delete_sync_key(db, sync_key)

    def save_directory_tree(
        self, db: Session, user_id: int, bookmarks: list[BookmarkFromExtension], parent_id: int | None = None
    ):

        for bookmark in bookmarks:
            if not bookmark.url:
                directory = directory_crud.create_directory(
                    db=db,
                    title=bookmark.title,
                    user_id=user_id,
                    parent_id=parent_id,
                )
                db.flush()

                if bookmark.children:
                    self.save_directory_tree(db, user_id, bookmark.children, directory.id)
            else:
                source_crud.create_source_sync(
                    db=db,
                    url=bookmark.url,
                    title=bookmark.title,
                    summary="",
                    user_id=user_id,
                    directory_id=parent_id,
                    is_active=True,
                )

        db.commit()

    def sync_bookmarks(self, sync_key: str, bookmarks: list[BookmarkFromExtension], db: Session) -> None:
        user_id = self.get_user_id_from_sync_key(sync_key, db)

        if user_id:
            self.delete_sync_key(sync_key, db)

        self.save_directory_tree(db, user_id, bookmarks)


directory_sync_service = DirectorySyncService()
