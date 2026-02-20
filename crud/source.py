from sqlalchemy.orm import Session

from models.source import SourceModel


# notebook_id, directory_id 파라미터는 해당 테이블 생성 후 추가
def create_source(
    db: Session,
    url: str,
    title: str,
    summary: str,
    user_id: int,
    directory_id: int | None,
    is_active: bool,
    notebook_id: int,
) -> SourceModel:
    source = SourceModel(
        url=url,
        title=title,
        summary=summary,
        user_id=user_id,
        directory_id=directory_id,
        is_active=is_active,
        notebook_id=notebook_id,
    )
    db.add(source)
    db.flush()
    return source
