from sqlalchemy.orm import Session

from models.directory import DirectoryModel


def create_directory(db: Session, title: str, level: int, user_id: int, parent_id: int | None = None) -> DirectoryModel:
    db_dir = DirectoryModel(title=title, level=level, user_id=user_id, parent_id=parent_id)
    db.add(db_dir)
    return db_dir
