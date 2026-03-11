from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.source import SourceModel


def create_source(
    db: Session,
    url: str,
    title: str,
    directory_id: int | None,
    notebook_id: int,
) -> SourceModel:
    source = SourceModel(
        url=url,
        title=title,
        directory_id=directory_id,
        notebook_id=notebook_id,
    )
    db.add(source)
    db.flush()
    return source


def get_sources_by_notebook(db: Session, notebook_id: int) -> Sequence[SourceModel]:
    stmt = select(SourceModel).where(SourceModel.notebook_id == notebook_id)
    return db.scalars(stmt).all()


def delete_source_by_source_id(db: Session, source_id: int) -> SourceModel | None:
    source = db.query(SourceModel).filter(SourceModel.id == source_id).first()
    if not source:
        return None
    db.delete(source)
    db.commit()
    return source


def update_source_title(db: Session, source_id: int, title: str) -> SourceModel | None:
    source = db.query(SourceModel).filter(SourceModel.id == source_id).first()
    if not source:
        return None
    source.title = title
    db.commit()
    db.refresh(source)
    return source
