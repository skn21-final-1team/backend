from collections.abc import Generator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings

setting = get_settings()

engine = create_engine(setting.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_db_context() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator[Session]:
    with get_db_context() as db:
        yield db


DbSession = Annotated[Session, Depends(get_db)]
