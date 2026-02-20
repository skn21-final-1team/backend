from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from db.database import Base


class SourceModel(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    notebook_id = Column(Integer, ForeignKey("notebook.id", ondelete="CASCADE"), nullable=False)
    directory_id = Column(Integer, ForeignKey("directory.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=False)
