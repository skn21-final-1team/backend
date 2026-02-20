from sqlalchemy import Column, ForeignKey, Integer, String

from db.database import Base


class DirectoryModel(Base):
    __tablename__ = "directory"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("directory.id", ondelete="CASCADE"), nullable=True)
    notebook_id = Column(Integer, ForeignKey("notebook.id", ondelete="CASCADE"), nullable=False)
