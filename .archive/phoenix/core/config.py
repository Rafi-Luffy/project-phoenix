"""
Configuration module for Phoenix system
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class Settings:
    """Core settings for Phoenix"""
    app_name: str = "Project Phoenix"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"


@dataclass
class PhoenixConfig:
    """Configuration for Phoenix system"""
    debug: bool = False
    log_level: str = "INFO"
    max_retries: int = 3
    timeout_seconds: int = 30
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    default_llm_provider: str = "openai"
    critic_model: str = "gpt-4"
    programmer_model: str = "gpt-4"
    observer_model: str = "gpt-3.5-turbo"
    validator_model: str = "gpt-3.5-turbo"
    settings: Optional[Settings] = field(default_factory=Settings)


# Global configuration instance
config = PhoenixConfig()
settings = Settings()
