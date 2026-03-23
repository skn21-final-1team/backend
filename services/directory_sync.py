from datetime import UTC, datetime

from sqlalchemy.orm import Session

import crud.directory as directory_crud
import crud.extension_sync_key as extension_sync_key_crud
import crud.source as source_crud
from core.exceptions.auth import InvalidTokenException
from models.extension import ExtensionSyncKeyModel
from schemas.directory import BookmarkFromExtension

from schemas.crawl import CrawlSyncRequest
from services.crawl import crawl_service


class DirectorySyncService:
    def get_user_id_from_sync_key(self, sync_key: str, db: Session) -> ExtensionSyncKeyModel:
        sync_key = extension_sync_key_crud.get_sync_key(db, sync_key)
        if not sync_key:
            raise InvalidTokenException

        now = datetime.now(UTC)
        expires_at = sync_key.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < now:
            raise InvalidTokenException

        return sync_key

    def delete_sync_key(self, sync_key: str, db: Session) -> None:
        extension_sync_key_crud.delete_sync_key(db, sync_key)

    def save_directory_tree(
        self,
        db: Session,
        bookmarks: list[BookmarkFromExtension],
        notebook_id: int,
        parent_id: int | None = None,
        crawl_list: CrawlSyncRequest | None = None
    ) -> CrawlSyncRequest:
        if not crawl_list:
            crawl_list = CrawlSyncRequest(source_ids=[], notebook_id=notebook_id)

        for bookmark in bookmarks:
            if not bookmark.url:
                directory = directory_crud.create_directory(
                    db=db,
                    title=bookmark.title,
                    parent_id=parent_id,
                    notebook_id=notebook_id,
                )
                if bookmark.children:
                    self.save_directory_tree(
                        db, bookmark.children, notebook_id, directory.id, crawl_list
                        )
            else:
                source = source_crud.create_source(
                    db=db,
                    url=bookmark.url,
                    title=bookmark.title,
                    directory_id=parent_id,
                    notebook_id=notebook_id,
                )
                crawl_list.source_ids.append(source.id)
        return crawl_list

    def sync_bookmarks(self, sync_key: str, bookmarks: list[BookmarkFromExtension], db: Session) -> CrawlSyncRequest:
        target = self.get_user_id_from_sync_key(sync_key, db)
        crawl_request = self.save_directory_tree(db, bookmarks, target.notebook_id, None)
        self.delete_sync_key(sync_key, db)
        db.commit()
        return crawl_request

    async def _crawl_calling(self, body: CrawlSyncRequest) -> None:
        """crawl BE endpoint 비동기 크롤링 파이프라인 요청 전달"""
        return await crawl_service.request_sync_crawl(body)

directory_sync_service = DirectorySyncService()
