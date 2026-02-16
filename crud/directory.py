from sqlalchemy.orm import Session

from models.directory import DirectoryModel


def get_directory(db: Session, directory_id: int) -> DirectoryModel | None:
    return db.query(DirectoryModel).filter(DirectoryModel.id == directory_id).first()


def get_directories_by_notebook(db: Session, notebook_id: int) -> list[DirectoryModel]:
    return db.query(DirectoryModel).filter(DirectoryModel.notebook_id == notebook_id).all()


def get_directories_by_parent(db: Session, notebook_id: int, parent_id: int | None) -> list[DirectoryModel]:
    return (
        db.query(DirectoryModel)
        .filter(DirectoryModel.notebook_id == notebook_id, DirectoryModel.parent_id == parent_id)
        .all()
    )


def create_directory(
    db: Session, notebook_id: int, title: str, parent_id: int | None = None
) -> DirectoryModel:
    new_directory = DirectoryModel(name=title, notebook_id=notebook_id, parent_id=parent_id)
    db.add(new_directory)
    db.commit()
    db.refresh(new_directory)
    return new_directory


def update_directory(
    db: Session, directory_id: int, title: str, parent_id: int | None
) -> DirectoryModel | None:
    directory = db.query(DirectoryModel).filter(DirectoryModel.id == directory_id).first()
    if not directory:
        return None
    directory.name = title
    directory.parent_id = parent_id
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
