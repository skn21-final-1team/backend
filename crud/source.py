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
