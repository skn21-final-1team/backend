from sqlalchemy.orm import Session

from models.source import SourceModel


# notebook_id, directory_id 파라미터는 해당 테이블 생성 후 추가
def create_source(db: Session, url: str, title: str | None, summary: str) -> SourceModel:
    source = SourceModel(url=url, title=title, summary=summary)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
