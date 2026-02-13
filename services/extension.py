from sqlalchemy.orm import Session
from crud.source import create_source
from models.directory import DirectoryModel
from schemas.extension import ExtensionBookmarkNode


class ExtensionService:
    def process_extension_data(self, notebook_id: int, nodes: list[ExtensionBookmarkNode], db: Session):
        for node in nodes:
            self._save_node(notebook_id, node, None, db)

    def _save_node(self, notebook_id: int, node: ExtensionBookmarkNode, parent_id: int | None, db: Session):
        if not node.url:
            directory = DirectoryModel(name=node.title, notebook_id=notebook_id, parent_id=parent_id)
            db.add(directory)
            db.commit()
            db.refresh(directory)
            for child in node.children:
                self._save_node(notebook_id, child, directory.id, db)
        
        else:
            create_source(
                db, 
                url=node.url, 
                title=node.title, 
                notebook_id=notebook_id, 
                directory_id=parent_id
            )

extension_service = ExtensionService()