from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from core import settings


_engine = create_engine(settings.get().DATABASE_URL)
SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False, class_=Session)

def create_all(base_class: Type[DeclarativeBase]):
    """
    Create all tables in the database.
    """
    base_class.metadata.create_all(bind=_engine)
