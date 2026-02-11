from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.sql import func

from db.database import Base

class ChatModel(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notebook_id = Column(Integer, ForeignKey("notebook.id"), nullable=False)