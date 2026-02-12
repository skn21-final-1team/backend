from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from db.database import Base


class DirectoryModel(Base):
    __tablename__ = "directory"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebook.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("directory.id"), nullable=True)  # 자기 참조: 폴더 안의 폴더
    created_at = Column(DateTime(timezone=True), server_default=func.now())
