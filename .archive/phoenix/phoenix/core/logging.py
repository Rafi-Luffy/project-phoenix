"""Logging configuration for Phoenix."""

import logging
import sys
from pathlib import Path

import structlog

from phoenix.core.config import get_config


def setup_logging() -> None:
    """Configure structured logging for Phoenix."""
    config = get_config()
    
    # Ensure logs directory exists
    config.logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if config.log_format == "json"
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(config.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(config.log_level),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance for a module."""
    return structlog.get_logger(name)
