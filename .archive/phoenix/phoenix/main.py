"""Main entry point for Phoenix runtime."""

import sys
from pathlib import Path

from phoenix.core.config import ensure_directories, get_config
from phoenix.core.logging import setup_logging, get_logger
from phoenix.db import init_db

setup_logging()
logger = get_logger(__name__)


def main():
    """Main entry point."""
    logger.info("phoenix_starting")
    
    # Ensure directories exist
    ensure_directories()
    
    # Initialize database
    try:
        init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        sys.exit(1)
    
    # Start API server
    import uvicorn
    from phoenix.api.main import app
    
    config = get_config()
    
    logger.info(
        "starting_api_server",
        host=config.api_host,
        port=config.api_port,
    )
    
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
