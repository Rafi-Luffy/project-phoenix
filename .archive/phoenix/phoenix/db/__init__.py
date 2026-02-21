"""Database initialization and session management."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from phoenix.core.config import get_config
from phoenix.db.models import Base

config = get_config()

# Create engine
engine = create_engine(
    config.database_url,
    pool_pre_ping=True,
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database (create tables)."""
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
