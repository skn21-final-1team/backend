from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.directory import DirectoryModel


def create_directory(db: Session, title: str, notebook_id: int, parent_id: int | None = None) -> DirectoryModel:
    db_dir = DirectoryModel(title=title, parent_id=parent_id, notebook_id=notebook_id)
    db.add(db_dir)
    db.flush()
    return db_dir


def get_directories_by_notebook(db: Session, notebook_id: int) -> Sequence[DirectoryModel]:
    stmt = select(DirectoryModel).where(DirectoryModel.notebook_id == notebook_id)
    return db.scalars(stmt).all()


def update_directory(db: Session, directory_id: int, title: str) -> DirectoryModel | None:
    stmt = select(DirectoryModel).where(DirectoryModel.id == directory_id)
    directory = db.scalars(stmt).first()
    if not directory:
        return None
    directory.title = title
    db.commit()
    db.refresh(directory)
    return directory


def delete_directory(db: Session, directory_id: int) -> DirectoryModel | None:
    stmt = select(DirectoryModel).where(DirectoryModel.id == directory_id)
    directory = db.scalars(stmt).first()
    if not directory:
        return None
    db.delete(directory)
    db.commit()
    return directory
