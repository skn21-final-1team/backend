from sqlalchemy.orm import Session

from core.exceptions.notebook import NotebookNotFoundException
from crud.notebook import (
    create_notebook,
    delete_notebook,
    get_notebook,
    get_notebooks_by_user_id,
    update_notebook_title,
)
from models.notebook import NotebookModel
from models.directory import DirectoryModel
from models.source import SourceModel
from schemas.content import ContentNode, SourceNode

class NotebookService:
    def get_notebook(self, notebook_id: int, db: Session) -> NotebookModel:
        notebook = get_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException
        return notebook

    def get_notebooks_by_user(self, user_id: int, db: Session) -> list[NotebookModel]:
        return get_notebooks_by_user_id(db, user_id)

    def create_notebook(self, user_id: int, title: str, db: Session) -> NotebookModel:
        return create_notebook(db, user_id, title)

    def update_notebook_title(self, notebook_id: int, title: str, db: Session) -> NotebookModel:
        notebook = update_notebook_title(db, notebook_id, title)
        if not notebook:
            raise NotebookNotFoundException
        return notebook

    def delete_notebook(self, notebook_id: int, db: Session) -> NotebookModel:
        notebook = delete_notebook(db, notebook_id)
        if not notebook:
            raise NotebookNotFoundException
        return notebook

    def get_notebook_content(self, notebook_id: int, db: Session) -> list[ContentNode]:
        root_directories = db.query(DirectoryModel).filter(
            DirectoryModel.notebook_id == notebook_id,
            DirectoryModel.parent_id.is_(None)
        ).all()
        return [self._build_directory_node(d, db) for d in root_directories]

    def _build_directory_node(self, directory: DirectoryModel, db: Session) -> ContentNode:
        sources = db.query(SourceModel).filter(
            SourceModel.directory_id == directory.id
        ).all()
        source_nodes = [
            SourceNode(id=s.id, title=s.title, url=s.url, type="url")
            for s in sources
        ]
        children = db.query(DirectoryModel).filter(
            DirectoryModel.parent_id == directory.id
        ).all()
        child_nodes = [self._build_directory_node(c, db) for c in children]
        return ContentNode(
            id=directory.id,
            title=directory.name,
            parent_id=directory.parent_id,
            sources=source_nodes,
            children=child_nodes,
        )

notebook_service = NotebookService()
