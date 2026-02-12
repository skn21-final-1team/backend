from sqlalchemy.orm import Session

from models.directory import DirectoryModel


def get_directory(db: Session, directory_id: int) -> DirectoryModel | None:
    return db.query(DirectoryModel).filter(DirectoryModel.id == directory_id).first()


def get_directories_by_notebook(db: Session, notebook_id: int) -> list[DirectoryModel]:
    return db.query(DirectoryModel).filter(DirectoryModel.notebook_id == notebook_id).all()


def get_directories_by_parent(db: Session, parent_id: int | None, notebook_id: int) -> list[DirectoryModel]:
    return db.query(DirectoryModel).filter(
        DirectoryModel.parent_id == parent_id,
        DirectoryModel.notebook_id == notebook_id
    ).all()


def create_directory(db: Session, notebook_id: int, title: str, parent_id: int | None = None) -> DirectoryModel:
    new_directory = DirectoryModel(title=title, notebook_id=notebook_id, parent_id=parent_id)
    db.add(new_directory)
    db.commit()
    db.refresh(new_directory)
    return new_directory


def update_directory_title(db: Session, directory_id: int, title: str) -> DirectoryModel | None:
    directory = db.query(DirectoryModel).filter(DirectoryModel.id == directory_id).first()
    if not directory:
        return None
    directory.title = title
    db.commit()
    db.refresh(directory)
    return directory


def delete_directory(db: Session, directory_id: int) -> DirectoryModel | None:
    directory = db.query(DirectoryModel).filter(DirectoryModel.id == directory_id).first()
    if not directory:
        return None
    db.delete(directory)
    db.commit()
    return directory
