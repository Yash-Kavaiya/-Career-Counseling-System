"""SQLAlchemy engine, session factory, and Base. SQLite for zero-infra dev."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Create tables. Imports models so they register on Base.metadata."""
    from . import models  # noqa: F401  (side-effect: register mappers)

    Base.metadata.create_all(bind=engine)
