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


def get_source_ids_by_notebook(db: Session, notebook_id: int) -> list[int]:
    """노트북에 연결된 소스 ID 목록을 조회합니다."""
    stmt = select(SourceModel.id).where(SourceModel.notebook_id == notebook_id)
    return list(db.scalars(stmt).all())


def get_active_source_ids(db: Session, source_ids: Sequence[int]) -> list[int]:
    """주어진 소스 ID 중 활성화된 소스 ID만 조회합니다."""
    if not source_ids:
        return []

    stmt = select(SourceModel.id).where(
        SourceModel.id.in_(source_ids),
        SourceModel.is_active.is_(True),
    )
    return list(db.scalars(stmt).all())


def delete_source_by_source_id(db: Session, source_id: int) -> SourceModel | None:
    source = db.query(SourceModel).filter(SourceModel.id == source_id).first()
    if not source:
        return None
    db.delete(source)
    db.commit()
    return source


def update_source(
    db: Session, source_id: int, title: str | None = None, is_active: bool | None = None
) -> SourceModel | None:

    source = db.query(SourceModel).filter(SourceModel.id == source_id).first()
    if not source:
        return None
    if title is not None:
        source.title = title
    if is_active is not None:
        source.is_active = is_active
    db.commit()
    db.refresh(source)
    return source
