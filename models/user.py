from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from db.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    name = Column(String, nullable=False)
    auth_provider = Column(String, nullable=False, default="local")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
