from sqlalchemy import func
from sqlalchemy.orm import Session

from models.notebook import NotebookModel
from schemas.notebook import NotebookSortType, NotebookUpdateBody


def get_notebook(db: Session, notebook_id: int) -> NotebookModel | None:
    return db.query(NotebookModel).filter(NotebookModel.id == notebook_id).first()


def get_notebooks_by_user_id(
    db: Session,
    user_id: int,
    sort_type: NotebookSortType = NotebookSortType.RECENT_CREATED,
) -> list[NotebookModel]:
    order_by_list = {
        NotebookSortType.RECENT_CREATED: (NotebookModel.created_at.desc().nullslast(), NotebookModel.id.desc()),
        NotebookSortType.CREATED_AT: (NotebookModel.created_at.asc().nullsfirst(), NotebookModel.id.asc()),
        NotebookSortType.NAME: (func.lower(NotebookModel.title).asc(), NotebookModel.id.asc()),
    }
    return db.query(NotebookModel).filter(NotebookModel.user_id == user_id).order_by(*order_by_list[sort_type]).all()


def create_notebook(db: Session, user_id: int, title: str = "Notebook-1") -> NotebookModel:
    new_notebook = NotebookModel(title=title, user_id=user_id)
    db.add(new_notebook)
    db.commit()
    db.refresh(new_notebook)
    return new_notebook


def update_notebook(db: Session, notebook_id: int, body: NotebookUpdateBody) -> NotebookModel | None:
    """요청에 포함된 필드만 노트북에 반영한다."""

    notebook = db.query(NotebookModel).filter(NotebookModel.id == notebook_id).first()
    if not notebook:
        return None

    for field_name in body.model_fields_set:
        setattr(notebook, field_name, getattr(body, field_name))

    db.commit()
    db.refresh(notebook)
    return notebook


def delete_notebook(db: Session, notebook_id: int) -> NotebookModel | None:
    notebook = db.query(NotebookModel).filter(NotebookModel.id == notebook_id).first()
    if not notebook:
        return None
    db.delete(notebook)
    db.commit()
    return notebook
