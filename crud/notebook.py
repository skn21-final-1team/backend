from sqlalchemy.orm import Session
from models.notebook import NotebookModel

def get_notebook(db: Session, notebook_id: int) -> NotebookModel | None:
    return db.query(NotebookModel).filter(NotebookModel.id == notebook_id).first()

def get_notebooks_by_user_id(db: Session, user_id: int) -> list[NotebookModel]:
    return db.query(NotebookModel).filter(NotebookModel.user_id == user_id).all()

def create_notebook(db: Session, user_id: int, title: str = "Notebook-1") -> NotebookModel:
    new_notebook = NotebookModel(title=title, user_id=user_id)
    db.add(new_notebook)
    db.commit()
    db.refresh(new_notebook)
    return new_notebook

def update_notebook_title(db: Session, notebook_id: int, title: str) -> NotebookModel | None:
    notebook = db.query(NotebookModel).filter(NotebookModel.id == notebook_id).first()
    if not notebook:
        return None
    notebook.title = title
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
