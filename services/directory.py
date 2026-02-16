from sqlalchemy.orm import Session

from core.exceptions.directory import DirectoryNotFoundException
from crud.directory import (
    create_directory,
    delete_directory,
    get_directories_by_notebook,
    get_directories_by_parent,
    get_directory,
    update_directory,
)
from models.directory import DirectoryModel


class DirectoryService:
    def get_directory(self, directory_id: int, db: Session) -> DirectoryModel:
        directory = get_directory(db, directory_id)
        if not directory:
            raise DirectoryNotFoundException
        return directory

    def get_directories(
        self, notebook_id: int, parent_id: int | None | str = "unset", db: Session = None
    ) -> list[DirectoryModel]:
        # parent_id가 명시되지 않은 경우 (unset) - 노트북의 모든 디렉토리 반환
        if parent_id == "unset":
            return get_directories_by_notebook(db, notebook_id)
        # parent_id가 명시된 경우 - 특정 부모의 하위 디렉토리만 반환
        return get_directories_by_parent(db, notebook_id, parent_id if parent_id != "" else None)

    def create_directory(
        self, notebook_id: int, title: str, parent_id: int | None, db: Session
    ) -> DirectoryModel:
        return create_directory(db, notebook_id, title, parent_id)

    def update_directory(
        self, directory_id: int, title: str, parent_id: int | None, db: Session
    ) -> DirectoryModel:
        directory = update_directory(db, directory_id, title, parent_id)
        if not directory:
            raise DirectoryNotFoundException
        return directory

    def delete_directory(self, directory_id: int, db: Session) -> DirectoryModel:
        directory = delete_directory(db, directory_id)
        if not directory:
            raise DirectoryNotFoundException
        return directory


directory_service = DirectoryService()
