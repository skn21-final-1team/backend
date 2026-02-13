from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base


class DirectoryModel(Base):
    __tablename__ = "directory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("directory.id"), nullable=True)
    notebook_id = Column(Integer, ForeignKey("notebook.id"), nullable=False)

    parent = relationship("DirectoryModel", remote_side=[id], backref="children")
    notebook = relationship("NotebookModel", back_populates="directories")
    sources = relationship("SourceModel", back_populates="directory")