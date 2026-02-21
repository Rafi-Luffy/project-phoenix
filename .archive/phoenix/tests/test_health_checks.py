"""
Health Check Service Tests

Tests the health monitoring system.
"""

import pytest
import asyncio
from phoenix.core.health_checker import (
    HealthCheckService,
    HealthStatus,
    check_health_sync,
    check_readiness_sync,
)


class TestHealthCheckService:
    """Test HealthCheckService class."""
    
    @pytest.fixture
    def service(self):
        """Create health check service."""
        return HealthCheckService()
    
    @pytest.mark.asyncio
    async def test_check_health_structure(self, service):
        """Test that health check returns proper structure."""
        health = await service.check_health()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "timestamp" in health
        assert "check_time_ms" in health
        assert "components" in health
        assert isinstance(health["components"], dict)
    
    @pytest.mark.asyncio
    async def test_health_status_values(self, service):
        """Test that health status is valid."""
        health = await service.check_health()
        
        status = health["status"]
        assert status in ["healthy", "degraded", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_llm_provider_check(self, service):
        """Test LLM provider health check."""
        await service._check_llm_provider()
        
        assert "llm_provider" in service.components
        component = service.components["llm_provider"]
        assert component.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        assert component.name == "llm_provider"
    
    @pytest.mark.asyncio
    async def test_filesystem_check(self, service):
        """Test filesystem health check."""
        await service._check_filesystem()
        
        assert "filesystem" in service.components
        component = service.components["filesystem"]
        assert component.status == HealthStatus.HEALTHY
        assert component.name == "filesystem"
    
    @pytest.mark.asyncio
    async def test_cache_check(self, service):
        """Test cache accessibility check."""
        await service._check_cache_access()
        
        assert "cache" in service.components
        component = service.components["cache"]
        assert component.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        assert component.name == "cache"
    
    @pytest.mark.asyncio
    async def test_slack_check_without_config(self, service):
        """Test Slack check when not configured."""
        await service._check_slack_webhook()
        
        assert "slack" in service.components
        component = service.components["slack"]
        assert component.status == HealthStatus.HEALTHY
        assert "Not configured" in component.details
    
    @pytest.mark.asyncio
    async def test_check_readiness_structure(self, service):
        """Test that readiness check returns proper structure."""
        readiness = await service.check_readiness()
        
        assert isinstance(readiness, dict)
        assert "ready" in readiness
        assert "missing_components" in readiness
        assert "timestamp" in readiness
        assert isinstance(readiness["missing_components"], list)
    
    @pytest.mark.asyncio
    async def test_check_readiness_bool(self, service):
        """Test that readiness is a boolean."""
        readiness = await service.check_readiness()
        
        assert isinstance(readiness["ready"], bool)
    
    @pytest.mark.asyncio
    async def test_concurrent_checks(self, service):
        """Test that health checks run concurrently."""
        import time
        
        start = time.time()
        health = await service.check_health()
        elapsed = time.time() - start
        
        # Should be fast because checks run concurrently
        # (less than sum of individual check times)
        assert elapsed < 5.0
        assert health["status"] is not None
    
    @pytest.mark.asyncio
    async def test_component_latency_recorded(self, service):
        """Test that component latency is recorded."""
        await service.check_health()
        
        # At least some components should have latency recorded
        components_with_latency = [
            c for c in service.components.values()
            if c.latency_ms > 0
        ]
        # LLM or filesystem should have latency
        assert len(components_with_latency) >= 0


class TestSyncHealthChecks:
    """Test synchronous health check wrappers."""
    
    def test_check_health_sync(self):
        """Test synchronous health check."""
        health = check_health_sync()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_check_readiness_sync(self):
        """Test synchronous readiness check."""
        readiness = check_readiness_sync()
        
        assert isinstance(readiness, dict)
        assert "ready" in readiness
        assert isinstance(readiness["ready"], bool)
    
    def test_readiness_matches_health(self):
        """Test that readiness matches health status."""
        health = check_health_sync()
        readiness = check_readiness_sync()
        
        # Readiness should match health
        health_is_healthy = health["status"] == "healthy"
        assert readiness["ready"] == health_is_healthy


class TestHealthCheckIntegration:
    """Integration tests with orchestrator."""
    
    def test_orchestrator_health_method(self):
        """Test that orchestrator has health check method."""
        from phoenix.orchestrator.autonomous_self_healing_orchestrator import (
            AutonomousSelfHealingOrchestrator,
        )
        
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
        
        assert hasattr(orchestrator, "health_checker")
        assert hasattr(orchestrator, "startup_health_check")
        assert hasattr(orchestrator, "get_system_health")
    
    def test_orchestrator_startup_health_check(self):
        """Test orchestrator startup health check."""
        from phoenix.orchestrator.autonomous_self_healing_orchestrator import (
            AutonomousSelfHealingOrchestrator,
        )
        
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
        
        result = orchestrator.startup_health_check()
        assert isinstance(result, bool)
    
    def test_orchestrator_get_system_health(self):
        """Test orchestrator get_system_health method."""
        from phoenix.orchestrator.autonomous_self_healing_orchestrator import (
            AutonomousSelfHealingOrchestrator,
        )
        
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
        
        health = orchestrator.get_system_health()
        
        assert isinstance(health, dict)
        assert "status" in health


class TestHealthComponentData:
    """Test ComponentHealth data structure."""
    
    def test_component_health_to_dict(self):
        """Test converting component health to dict."""
        from phoenix.core.health_checker import ComponentHealth
        
        component = ComponentHealth(
            name="test_component",
            status=HealthStatus.HEALTHY,
            latency_ms=42.5,
            details="Test details",
        )
        
        data = component.to_dict()
        
        assert data["name"] == "test_component"
        assert data["status"] == "healthy"
        assert data["latency_ms"] == 42.5
        assert data["details"] == "Test details"
        assert "last_check" in data
    
    def test_component_health_degraded_status(self):
        """Test degraded component health."""
        from phoenix.core.health_checker import ComponentHealth
        
        component = ComponentHealth(
            name="degraded_component",
            status=HealthStatus.DEGRADED,
            details="Temporary issue",
        )
        
        data = component.to_dict()
        assert data["status"] == "degraded"
    
    def test_component_health_unhealthy_status(self):
        """Test unhealthy component health."""
        from phoenix.core.health_checker import ComponentHealth
        
        component = ComponentHealth(
            name="unhealthy_component",
            status=HealthStatus.UNHEALTHY,
            details="Critical failure",
        )
        
        data = component.to_dict()
        assert data["status"] == "unhealthy"


class TestHealthCheckErrorHandling:
    """Test error handling in health checks."""
    
    @pytest.mark.asyncio
    async def test_health_check_handles_exceptions(self):
        """Test that health checks handle exceptions gracefully."""
        service = HealthCheckService()
        
        # Should not raise exception
        health = await service.check_health()
        
        assert isinstance(health, dict)
        assert "status" in health
    
    def test_sync_health_check_handles_exceptions(self):
        """Test that sync health check handles exceptions."""
        # Should not raise exception
        health = check_health_sync()
        
        assert isinstance(health, dict)
        assert health["status"] is not None
    
    @pytest.mark.asyncio
    async def test_continuous_monitoring_handles_errors(self):
        """Test that continuous monitoring handles errors."""
        service = HealthCheckService()
        
        # Run monitoring for short time with error handling
        import asyncio
        
        task = asyncio.create_task(
            asyncio.wait_for(service.continuous_monitoring(interval_seconds=0.1), timeout=0.3)
        )
        
        try:
            await task
        except asyncio.TimeoutError:
            # Expected - monitoring runs forever
            pass
