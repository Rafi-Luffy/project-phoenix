"""
System metrics and performance monitoring endpoints
"""

from fastapi import APIRouter, Query
from typing import List
from datetime import datetime
from models import MetricsSnapshot, PerformanceMetrics, SystemMetrics

router = APIRouter()

# In-memory storage for demo (TODO: Replace with time-series database like InfluxDB)
metrics_db: dict = {}


@router.post("/snapshot")
async def record_metrics(metrics: MetricsSnapshot):
    """
    Record a metrics snapshot
    """
    # Store metrics (TODO: Use proper time-series database)
    key = f"{metrics.system_id}_{metrics.timestamp.isoformat()}"
    metrics_db[key] = metrics.model_dump()
    
    return {
        "message": "Metrics recorded",
        "timestamp": datetime.utcnow()
    }


@router.get("/system/{system_id}/current", response_model=MetricsSnapshot)
async def get_current_metrics(system_id: str):
    """
    Get current metrics for a system
    """
    # Find the most recent metric for this system
    system_metrics = [
        m for k, m in metrics_db.items()
        if m["system_id"] == system_id
    ]
    
    if not system_metrics:
        # Return default healthy metrics
        return MetricsSnapshot(
            timestamp=datetime.utcnow(),
            system_id=system_id,
            metrics=SystemMetrics(
                cpu_usage=45.2,
                memory_usage=62.1,
                disk_usage=78.5,
                network_latency=23.4,
                error_rate=0.3,
                request_rate=1250
            ),
            anomaly_detected=False,
            anomaly_score=0.05
        )
    
    # Return the most recent
    latest = sorted(system_metrics, key=lambda m: m["timestamp"], reverse=True)[0]
    return MetricsSnapshot(**latest)


@router.get("/system/{system_id}/history")
async def get_metrics_history(
    system_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get historical metrics for a system
    """
    system_metrics = [
        m for k, m in metrics_db.items()
        if m["system_id"] == system_id
    ]
    
    # Sort by timestamp descending
    system_metrics = sorted(system_metrics, key=lambda m: m["timestamp"], reverse=True)
    
    # Apply pagination
    system_metrics = system_metrics[offset:offset + limit]
    
    return [MetricsSnapshot(**m) for m in system_metrics]


@router.get("/performance/summary", response_model=PerformanceMetrics)
async def get_performance_summary():
    """
    Get overall performance metrics
    """
    # TODO: Calculate from actual data
    return PerformanceMetrics(
        detection_latency_ms=45.3,
        analysis_latency_ms=67.2,
        correction_latency_ms=123.5,
        total_events_detected=15247,
        auto_resolved_count=14353,
        auto_resolution_rate=94.1,
        system_uptime_percentage=99.95,
        cost_savings=145320.50
    )


@router.get("/system/{system_id}/anomalies")
async def get_system_anomalies(system_id: str, limit: int = Query(50, ge=1, le=500)):
    """
    Get detected anomalies for a system
    """
    system_metrics = [
        m for k, m in metrics_db.items()
        if m["system_id"] == system_id and m.get("anomaly_detected")
    ]
    
    # Sort by timestamp descending
    system_metrics = sorted(system_metrics, key=lambda m: m["timestamp"], reverse=True)[:limit]
    
    return [
        {
            "timestamp": m["timestamp"],
            "anomaly_score": m.get("anomaly_score"),
            "metrics": m["metrics"]
        }
        for m in system_metrics
    ]


@router.get("/trends")
async def get_trends(
    system_id: str = Query(None),
    metric_type: str = Query("all")
):
    """
    Get trends in key metrics
    """
    # TODO: Calculate actual trends from historical data
    return {
        "timestamp": datetime.utcnow(),
        "cpu_trend": -2.3,  # Decreasing
        "memory_trend": 1.5,  # Increasing
        "error_rate_trend": -0.8,  # Decreasing (good)
        "latency_trend": 0.2,
        "period_hours": 24
    }


@router.get("/alerts/active")
async def get_active_alerts(system_id: str = Query(None)):
    """
    Get currently active alerts
    """
    return {
        "timestamp": datetime.utcnow(),
        "total_alerts": 3,
        "critical": 1,
        "warning": 2,
        "alerts": [
            {
                "id": "alert_001",
                "system_id": "system_123",
                "metric": "cpu_usage",
                "threshold": 85,
                "current_value": 92,
                "severity": "critical",
                "triggered_at": datetime.utcnow()
            },
            {
                "id": "alert_002",
                "system_id": "system_123",
                "metric": "error_rate",
                "threshold": 5,
                "current_value": 7.2,
                "severity": "warning",
                "triggered_at": datetime.utcnow()
            },
            {
                "id": "alert_003",
                "system_id": "system_456",
                "metric": "disk_usage",
                "threshold": 90,
                "current_value": 92.5,
                "severity": "warning",
                "triggered_at": datetime.utcnow()
            }
        ]
    }
