from core.database import Base  # DB 연결 설정에서 만든 Base 클래스
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
