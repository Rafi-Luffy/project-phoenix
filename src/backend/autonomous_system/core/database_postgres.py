"""
Production Database Manager for Project Phoenix
PostgreSQL with async support, connection pooling, and migrations
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration manager"""
    
    def __init__(self):
        # Get database URL from environment
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://phoenix_admin:secure_password@localhost:5432/project_phoenix'
        )
        
        # Convert to async URL if needed
        if self.database_url.startswith('postgresql://'):
            self.async_database_url = self.database_url.replace(
                'postgresql://',
                'postgresql+asyncpg://'
            )
        else:
            self.async_database_url = self.database_url
        
        # Pool settings
        self.pool_size = int(os.getenv('DATABASE_POOL_SIZE', '20'))
        self.max_overflow = int(os.getenv('DATABASE_MAX_OVERFLOW', '10'))
        self.pool_recycle = int(os.getenv('DATABASE_POOL_RECYCLE', '3600'))
        self.echo = os.getenv('DATABASE_ECHO', 'false').lower() == 'true'


class AsyncDatabaseManager:
    """Async database manager using PostgreSQL"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.engine = None
        self.async_session = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            logger.info("Initializing PostgreSQL connection pool...")
            
            self.engine = create_async_engine(
                self.config.async_database_url,
                echo=self.config.echo,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=True,  # Verify connections are alive
                connect_args={
                    "timeout": 10,
                    "command_timeout": 10,
                    "server_settings": {"jit": "off"}
                }
            )
            
            # Create async session factory
            self.async_session = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            logger.info(" PostgreSQL connection successful")
            return True
            
        except Exception as e:
            logger.error(f" Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")
    
    @asynccontextmanager
    async def get_session(self):
        """Get async database session"""
        if not self.async_session:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.async_session() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> dict:
        """Check database health"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                pool_size = self.engine.pool.size()
                pool_checked_out = self.engine.pool.checkedout()
                
                return {
                    "status": "healthy",
                    "database": "postgresql",
                    "pool_size": pool_size,
                    "connections_in_use": pool_checked_out,
                    "available_connections": pool_size - pool_checked_out
                }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "database": "postgresql",
                "error": str(e)
            }


# Global database instance
_db_manager: AsyncDatabaseManager = None


def get_database_manager() -> AsyncDatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = AsyncDatabaseManager()
    return _db_manager


async def initialize_database():
    """Initialize database on application startup"""
    db_manager = get_database_manager()
    await db_manager.initialize()


async def close_database():
    """Close database on application shutdown"""
    db_manager = get_database_manager()
    await db_manager.close()
