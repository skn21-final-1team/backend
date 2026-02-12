from sqlalchemy.orm import Session

from crud.directory import create_directory
from crud.source import create_source
from schemas.extension import BookmarkFolder


class ExtensionService:
    def process_bulk_import(self, db: Session, notebook_id: int, folders: list[BookmarkFolder]):
        for folder in folders:
            self._process_folder(db, notebook_id, folder, None)

    def _process_folder(self, db: Session, notebook_id: int, folder: BookmarkFolder, parent_id: int | None):
        db_directory = create_directory(db, notebook_id, folder.name, parent_id)
        
        for url_item in folder.urls:
            create_source(
                db, 
                url=url_item.url, 
                title=url_item.title, 
                summary=None,
                directory_id=db_directory.id,
                notebook_id=notebook_id
            )

        for sub_folder in folder.folders:
            self._process_folder(db, notebook_id, sub_folder, db_directory.id)


extension_service = ExtensionService()
