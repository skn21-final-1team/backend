from sqlalchemy.orm import Session

from models.directory import DirectoryModel


def create_directory(
    db: Session, title: str, user_id: int, notebook_id: int, parent_id: int | None = None
) -> DirectoryModel:
    db_dir = DirectoryModel(title=title, user_id=user_id, parent_id=parent_id, notebook_id=notebook_id)
    db.add(db_dir)
    db.flush()
    return db_dir
