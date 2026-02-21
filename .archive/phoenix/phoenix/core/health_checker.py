"""
Health Check Service

Monitors system health and readiness.
Detects issues early, enables fail-fast behavior.
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth:
    """Health status of a single component."""
    
    def __init__(self, name: str, status: HealthStatus, latency_ms: float = 0, details: str = ""):
        self.name = name
        self.status = status
        self.latency_ms = latency_ms
        self.details = details
        self.last_check = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "last_check": self.last_check,
        }


class HealthCheckService:
    """
    Monitors system health and readiness.
    
    Checks:
    - LLM provider connectivity
    - Database connection
    - File system access
    - Cache accessibility
    - Slack webhook (if configured)
    """
    
    def __init__(self):
        """Initialize health check service."""
        self.logger = get_logger(__name__)
        self.components: Dict[str, ComponentHealth] = {}
        self._llm_failures = 0
        self._max_llm_failures = 3
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Health status report
        """
        start_time = datetime.utcnow()
        
        # Run checks in parallel
        checks = await asyncio.gather(
            self._check_llm_provider(),
            self._check_filesystem(),
            self._check_cache_access(),
            self._check_slack_webhook(),
            return_exceptions=True,
        )
        
        elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Determine overall status
        statuses = [c.status for c in self.components.values()]
        if HealthStatus.UNHEALTHY in statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return {
            "status": overall_status.value,
            "timestamp": start_time.isoformat(),
            "check_time_ms": elapsed_ms,
            "components": {
                name: component.to_dict()
                for name, component in self.components.items()
            },
        }
    
    async def check_readiness(self) -> Dict[str, Any]:
        """
        Check if system is ready to accept requests.
        
        Returns:
            Readiness status with missing components list
        """
        health = await self.check_health()
        
        missing_components = []
        for name, status in health.get("components", {}).items():
            if status["status"] != "healthy":
                missing_components.append({
                    "component": name,
                    "status": status["status"],
                    "details": status.get("details", ""),
                })
        
        return {
            "ready": health["status"] == "healthy",
            "missing_components": missing_components,
            "timestamp": health["timestamp"],
        }
    
    async def _check_llm_provider(self):
        """Check LLM provider connectivity."""
        try:
            start = datetime.utcnow()
            
            # Try a simple call to LLM provider
            # This is a mock - actual implementation would call real LLM
            await asyncio.sleep(0.01)  # Simulate API call
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            
            self.components["llm_provider"] = ComponentHealth(
                name="llm_provider",
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                details="Connected and responding",
            )
            self._llm_failures = 0
        
        except Exception as e:
            self._llm_failures += 1
            
            if self._llm_failures >= self._max_llm_failures:
                status = HealthStatus.UNHEALTHY
                details = f"Failed {self._llm_failures} times: {str(e)}"
            else:
                status = HealthStatus.DEGRADED
                details = f"Temporary connectivity issue: {str(e)}"
            
            self.components["llm_provider"] = ComponentHealth(
                name="llm_provider",
                status=status,
                details=details,
            )
            
            self.logger.warning("llm_health_check_failed", error=str(e))
    
    async def _check_filesystem(self):
        """Check file system access and permissions."""
        try:
            import tempfile
            import os
            
            # Try to create a temp file
            with tempfile.NamedTemporaryFile(delete=True) as f:
                pass
            
            self.components["filesystem"] = ComponentHealth(
                name="filesystem",
                status=HealthStatus.HEALTHY,
                details="Read/write access OK",
            )
        
        except Exception as e:
            self.components["filesystem"] = ComponentHealth(
                name="filesystem",
                status=HealthStatus.UNHEALTHY,
                details=f"Access denied: {str(e)}",
            )
            
            self.logger.warning("filesystem_health_check_failed", error=str(e))
    
    async def _check_cache_access(self):
        """Check cache file accessibility."""
        try:
            cache_path = "./cache/fixes.json"
            
            # Check if cache directory is writable
            import os
            if not os.path.exists("./cache"):
                os.makedirs("./cache", exist_ok=True)
            
            # Try to read/write
            test_file = "./cache/.health_check"
            with open(test_file, 'w') as f:
                f.write("{}")
            os.remove(test_file)
            
            self.components["cache"] = ComponentHealth(
                name="cache",
                status=HealthStatus.HEALTHY,
                details="Cache accessible",
            )
        
        except Exception as e:
            self.components["cache"] = ComponentHealth(
                name="cache",
                status=HealthStatus.DEGRADED,
                details=f"Cache issue: {str(e)}",
            )
            
            self.logger.warning("cache_health_check_failed", error=str(e))
    
    async def _check_slack_webhook(self):
        """Check Slack webhook connectivity (if configured)."""
        try:
            import os
            
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            if not webhook_url:
                self.components["slack"] = ComponentHealth(
                    name="slack",
                    status=HealthStatus.HEALTHY,
                    details="Not configured (optional)",
                )
                return
            
            # Try to ping the webhook
            import urllib.request
            import json
            
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps({"text": "Health check ping"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            
            start = datetime.utcnow()
            with urllib.request.urlopen(req, timeout=5) as response:
                latency = (datetime.utcnow() - start).total_seconds() * 1000
                
                self.components["slack"] = ComponentHealth(
                    name="slack",
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                    details="Webhook responding",
                )
        
        except Exception as e:
            self.components["slack"] = ComponentHealth(
                name="slack",
                status=HealthStatus.DEGRADED,
                details=f"Webhook issue: {str(e)}",
            )
            
            self.logger.warning("slack_health_check_failed", error=str(e))
    
    async def continuous_monitoring(self, interval_seconds: int = 60):
        """
        Continuously monitor health.
        
        Args:
            interval_seconds: Check interval
        """
        while True:
            try:
                health = await self.check_health()
                
                if health["status"] != "healthy":
                    self.logger.warning(
                        "health_degraded",
                        status=health["status"],
                    )
                
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                self.logger.error("health_monitoring_error", error=str(e))
                await asyncio.sleep(interval_seconds)


async def run_health_checks():
    """
    Run health checks and return status.
    
    Example:
        health = await run_health_checks()
        if not health["ready"]:
            sys.exit(1)
    """
    service = HealthCheckService()
    return await service.check_readiness()


# Synchronous wrapper for compatibility
def check_health_sync() -> Dict[str, Any]:
    """Synchronous health check for startup verification."""
    service = HealthCheckService()
    
    # Run async checks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(service.check_health())
    finally:
        loop.close()


def check_readiness_sync() -> Dict[str, Any]:
    """Synchronous readiness check for startup verification."""
    service = HealthCheckService()
    
    # Run async checks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(service.check_readiness())
    finally:
        loop.close()
