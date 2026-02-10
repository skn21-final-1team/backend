from sqlalchemy.orm import Session

from models.notebook import NotebookModel

def get_notebook(notebook_id: int, db: Session) -> NotebookModel:
    return db.query(NotebookModel).filter(NotebookModel.id == notebook_id).first()

def get_notebooks(db: Session) -> list[NotebookModel]:
    return db.query(NotebookModel).all()

def create_notebook(notebook_id: int, db: Session) -> NotebookModel:
    db_notebook = NotebookModel(**notebook.dict())
    db.add(db_notebook)
    db.commit()
    db.refresh(db_notebook)
    return db_notebook

def update_notebook(notebook_id: int, notebook: NotebookRequest, db: Session) -> NotebookModel:
    db_notebook = get_notebook(notebook_id, db)
    if not db_notebook:
        raise NotebookNotFoundException()
    db_notebook.title = notebook.title
    db.commit()
    db.refresh(db_notebook)
    return db_notebook

def delete_notebook(notebook_id: int, db: Session) -> NotebookModel:
    db_notebook = get_notebook(notebook_id, db)
    if not db_notebook:
        raise NotebookNotFoundException()
    db.delete(db_notebook)
    db.commit()
    return db_notebook

NotebookCRUD = NotebookCRUD()