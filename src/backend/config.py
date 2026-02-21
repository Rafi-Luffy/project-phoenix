"""
System Configuration
Environment-based settings for the autonomous system
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # System
    SYSTEM_NAME: str = "Autonomous Self-Healing System"
    SYSTEM_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/autonomous_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_WORKERS: int = 4
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    TOKEN_EXPIRATION_HOURS: int = 24
    JWT_ALGORITHM: str = "HS256"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # Monitoring
    METRICS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    # Agent System
    MAX_AGENTS: int = 1000
    AGENT_TIMEOUT_SECONDS: int = 300
    AGENT_RETRY_ATTEMPTS: int = 3
    
    # Memory
    SHORT_TERM_MEMORY_SIZE: int = 1000
    LONG_TERM_MEMORY_RETENTION_DAYS: int = 30
    MEMORY_CLEANUP_INTERVAL_HOURS: int = 24
    
    # Message Bus
    MESSAGE_QUEUE_MAX_SIZE: int = 50000
    MESSAGE_HISTORY_RETENTION: int = 50000
    
    # Performance
    PERFORMANCE_MONITORING_ENABLED: bool = True
    PERFORMANCE_METRICS_INTERVAL_SECONDS: int = 60
    
    # Caching
    REDIS_URL: Optional[str] = None
    CACHE_ENABLED: bool = False
    CACHE_TTL_SECONDS: int = 3600
    
    # API
    API_TITLE: str = "Autonomous Self-Healing System API"
    API_VERSION: str = "0.1.0"
    API_DOCS_URL: str = "/docs"
    API_REDOC_URL: str = "/redoc"
    
    # Security
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Error Handling
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    FAILED_LOGIN_LOCKOUT_MINUTES: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
