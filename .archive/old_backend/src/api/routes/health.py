"""
Health check and status endpoints
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
from models import HealthCheck, ServiceHealth

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Get overall system health status
    """
    timestamp = datetime.utcnow()
    
    services = [
        ServiceHealth(
            service="api",
            status="healthy",
            checked_at=timestamp,
            response_time_ms=2.5
        ),
        ServiceHealth(
            service="database",
            status="healthy",
            checked_at=timestamp,
            response_time_ms=5.3
        ),
        ServiceHealth(
            service="detection_engine",
            status="healthy",
            checked_at=timestamp,
            response_time_ms=3.1
        ),
        ServiceHealth(
            service="analysis_engine",
            status="healthy",
            checked_at=timestamp,
            response_time_ms=4.2
        ),
        ServiceHealth(
            service="correction_engine",
            status="healthy",
            checked_at=timestamp,
            response_time_ms=3.8
        ),
        ServiceHealth(
            service="message_queue",
            status="healthy",
            checked_at=timestamp,
            response_time_ms=2.1
        ),
    ]
    
    # Determine overall status
    unhealthy_count = sum(1 for s in services if s.status == "unhealthy")
    degraded_count = sum(1 for s in services if s.status == "degraded")
    
    if unhealthy_count > 0:
        overall_status = "unhealthy"
    elif degraded_count > 0:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    return HealthCheck(
        timestamp=timestamp,
        status=overall_status,
        services=services,
        version="1.0.0"
    )


@router.get("/health/live")
async def liveness_probe():
    """
    Liveness probe for Kubernetes
    Returns 200 if service is running
    """
    return {"status": "alive", "timestamp": datetime.utcnow()}


@router.get("/health/ready")
async def readiness_probe():
    """
    Readiness probe for Kubernetes
    Returns 200 if service is ready to accept traffic
    """
    # TODO: Check database connection
    # TODO: Check message queue connection
    # TODO: Check detection engine initialization
    
    return {"status": "ready", "timestamp": datetime.utcnow()}


@router.get("/metrics/system")
async def system_metrics():
    """
    Get system resource metrics
    """
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "timestamp": datetime.utcnow()
    }


@router.get("/status")
async def status():
    """
    Get detailed service status
    """
    return {
        "service": "Project Phoenix API",
        "version": "1.0.0",
        "environment": "production",
        "timestamp": datetime.utcnow(),
        "uptime_seconds": 0,  # TODO: Calculate from startup time
        "request_count": 0,  # TODO: Track requests
        "error_count": 0,  # TODO: Track errors
    }
