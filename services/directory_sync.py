from datetime import UTC, datetime

from sqlalchemy.orm import Session

import crud.directory as directory_crud
import crud.extension_sync_key as extension_sync_key_crud
import crud.source as source_crud
from core.exceptions.auth import InvalidTokenException
from schemas.directory import BookmarkFromExtension

from schemas.crawl import CrawlSyncBody, CrawlSyncRequest
from services.crawl import crawl_service


class DirectorySyncService:
    def get_user_id_from_sync_key(self, sync_key: str, db: Session) -> bool:
        sync_key = extension_sync_key_crud.get_sync_key(db, sync_key)
        if not sync_key:
            raise InvalidTokenException

        if sync_key.expires_at < datetime.now(UTC):
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
            crawl_list = CrawlSyncRequest(sources=[], notebook_id=notebook_id)

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
                crawl_list.sources.append(
                    CrawlSyncBody(
                        url=source.url,
                        directory_id=source.directory_id,
                        source_id=source.id,
                    )
                )
        db.commit()
        return crawl_list

    def sync_bookmarks(self, sync_key: str, bookmarks: list[BookmarkFromExtension], db: Session) -> None:
        target = self.get_user_id_from_sync_key(sync_key, db)
        self.save_directory_tree(db, bookmarks, target.notebook_id, None)
        self.delete_sync_key(sync_key, db)

    async def __crawl_calling(self, body: CrawlSyncRequest) -> None:
        """crawl BE endpoint 비동기 크롤링 파이프라인 요청 전달"""
        return await crawl_service.request_sync_crawl(body)

directory_sync_service = DirectorySyncService()
