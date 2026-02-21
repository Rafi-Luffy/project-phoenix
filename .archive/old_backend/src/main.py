"""
Project Phoenix - FastAPI Backend Application
Autonomous Self-Healing System for Infrastructure
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

# Import routers
from api.routes import systems, events, policies, corrections, health, metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Manage application startup and shutdown
    """
    # Startup
    logger.info("Starting Project Phoenix Backend")
    
    # Initialize services
    logger.info("Initializing core services...")
    # TODO: Initialize detection engine
    # TODO: Initialize analysis engine
    # TODO: Initialize correction engine
    # TODO: Initialize learning engine
    # TODO: Connect to PostgreSQL
    # TODO: Connect to Redis
    
    yield
    
    # Shutdown
    logger.info("Shutting down Project Phoenix Backend")
    # TODO: Cleanup connections
    # TODO: Flush pending events
    # TODO: Save state


# Create FastAPI app
app = FastAPI(
    title="Project Phoenix API",
    description="Autonomous Self-Healing System for Modern Infrastructure",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(systems.router, prefix="/api/v1/systems", tags=["Systems"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
app.include_router(corrections.router, prefix="/api/v1/corrections", tags=["Corrections"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Project Phoenix API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
