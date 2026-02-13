from sqlalchemy.orm import Session

from models.source import SourceModel


def create_source(db: Session, url: str, title: str | None = None, summary: str | None = None, notebook_id: int | None = None, directory_id: int | None = None) -> SourceModel:
    db_source = SourceModel(url=url, title=title, summary=summary, notebook_id=notebook_id, directory_id=directory_id)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source
