from sqlalchemy.orm import Session

from crud.directory import (
    create_directory,
    delete_directory,
    get_directories_by_notebook,
    get_directories_by_parent,
    get_directory,
    update_directory_title,
)
from models.directory import DirectoryModel


class DirectoryService:
    def get_directory(self, directory_id: int, db: Session) -> DirectoryModel | None:
        return get_directory(db, directory_id)

    def get_directories_by_notebook(self, notebook_id: int, db: Session) -> list[DirectoryModel]:
        return get_directories_by_notebook(db, notebook_id)

    def get_directories_by_parent(self, parent_id: int | None, notebook_id: int, db: Session) -> list[DirectoryModel]:
        return get_directories_by_parent(db, parent_id, notebook_id)

    def create_directory(self, notebook_id: int, title: str, parent_id: int | None, db: Session) -> DirectoryModel:
        return create_directory(db, notebook_id, title, parent_id)

    def update_directory_title(self, directory_id: int, title: str, db: Session) -> DirectoryModel | None:
        return update_directory_title(db, directory_id, title)

    def delete_directory(self, directory_id: int, db: Session) -> DirectoryModel | None:
        return delete_directory(db, directory_id)


directory_service = DirectoryService()
