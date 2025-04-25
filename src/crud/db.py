import logging
from typing import Type

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from core import settings


_engine = create_engine(str(settings.get().DATABASE_URL))
SessionLocal = sessionmaker(
    bind=_engine, autocommit=False, autoflush=False, class_=Session
)


def create_all(base_class: Type[DeclarativeBase]):
    """
    Create all tables in the database.
    """
    inspector = inspect(_engine)
    existing_tables = set(inspector.get_table_names())
    model_tables = set(base_class.metadata.tables.keys())
    if not existing_tables & model_tables:
        # If there are no existing tables, create all tables
        logging.info("Creating all tables in the database.")
        base_class.metadata.create_all(bind=_engine)
        return
    logging.info("Tables already exist in the database. Skipping creation.")
