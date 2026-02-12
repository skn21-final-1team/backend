from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from db.database import Base


class SourceModel(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    notebook_id = Column(Integer, ForeignKey("notebook.id"), nullable=True)
    directory_id = Column(Integer, ForeignKey("directory.id"), nullable=True)
    is_active = Column(Boolean, default=False)
