from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from db.database import Base


class NotebookModel(Base):
    __tablename__ = "notebook"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="Notebook-1")
    is_active = Column(Boolean, nullable=False, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
