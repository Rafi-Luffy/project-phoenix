"""
Database configuration and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator

# Configuration from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://phoenix:phoenix@localhost:5432/phoenix"
)

ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL", 
    "postgresql+asyncpg://phoenix:phoenix@localhost:5432/phoenix"
)

# SQLAlchemy synchronous engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

# SQLAlchemy synchronous session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# SQLAlchemy async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

# SQLAlchemy async session
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db() -> Session:
    """
    Dependency for synchronous database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for asynchronous database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Context manager for async database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    """
    from database import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    """
    await async_engine.dispose()
