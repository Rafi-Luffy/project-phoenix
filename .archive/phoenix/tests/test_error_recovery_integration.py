"""
Error Recovery Orchestrator Integration Tests

Tests error recovery integration with the main orchestrator.
"""

import pytest
from unittest.mock import Mock, patch

from phoenix.orchestrator.autonomous_self_healing_orchestrator import (
    AutonomousSelfHealingOrchestrator,
)
from phoenix.core.error_recovery import CircuitBreaker, RetryStrategy


class TestErrorRecoveryOrchestratorIntegration:
    """Test error recovery integration with orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with error recovery."""
        return AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
    
    def test_orchestrator_has_error_recovery(self, orchestrator):
        """Test orchestrator has error recovery component."""
        assert hasattr(orchestrator, "error_recovery")
        assert hasattr(orchestrator, "llm_circuit_breaker")
        assert hasattr(orchestrator, "fix_generator_retry")
        assert hasattr(orchestrator, "fix_applier_retry")
    
    def test_circuit_breaker_initialized(self, orchestrator):
        """Test circuit breaker is properly initialized."""
        assert isinstance(orchestrator.llm_circuit_breaker, CircuitBreaker)
        assert orchestrator.llm_circuit_breaker.name == "llm_provider"
    
    def test_retry_strategies_initialized(self, orchestrator):
        """Test retry strategies are initialized."""
        assert isinstance(orchestrator.fix_generator_retry, RetryStrategy)
        assert isinstance(orchestrator.fix_applier_retry, RetryStrategy)
    
    def test_get_error_recovery_stats(self, orchestrator):
        """Test getting error recovery statistics."""
        stats = orchestrator.get_error_recovery_stats()
        
        assert isinstance(stats, dict)
        assert "circuit_breakers" in stats
        assert "fallback_providers" in stats
        assert "llm_provider" in stats["circuit_breakers"]
    
    def test_get_system_status(self, orchestrator):
        """Test getting comprehensive system status."""
        status = orchestrator.get_system_status()
        
        assert isinstance(status, dict)
        assert "health" in status
        assert "error_recovery" in status
        assert "operational_stats" in status
        assert "timestamp" in status
    
    def test_llm_circuit_breaker_tracks_failures(self, orchestrator):
        """Test circuit breaker tracks LLM failures."""
        breaker = orchestrator.llm_circuit_breaker
        
        # Simulate failures
        func = Mock(side_effect=Exception("timeout"))
        
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(func)
        
        assert breaker.failure_count == 3
    
    def test_fix_generator_retry_retries(self, orchestrator):
        """Test fix generator retry strategy."""
        strategy = orchestrator.fix_generator_retry
        
        # Simulate transient failure then success
        func = Mock(side_effect=[
            TimeoutError("timeout"),
            "success",
        ])
        
        result = strategy.execute(func)
        
        assert result == "success"
        assert func.call_count == 2
    
    def test_recovery_stats_show_breaker_status(self, orchestrator):
        """Test recovery stats show circuit breaker status."""
        # Trigger some failures
        breaker = orchestrator.llm_circuit_breaker
        func = Mock(side_effect=Exception("error"))
        
        for _ in range(2):
            with pytest.raises(Exception):
                breaker.call(func)
        
        # Check stats
        stats = orchestrator.get_error_recovery_stats()
        breaker_status = stats["circuit_breakers"]["llm_provider"]
        
        assert breaker_status["failures"] == 2
        assert breaker_status["state"] == "closed"


class TestErrorRecoveryWorkflow:
    """Test complete error recovery workflow."""
    
    def test_graceful_failure_handling(self):
        """Test system handles failures gracefully."""
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
        
        # Ensure system is still operational even with failures
        status = orchestrator.get_system_status()
        
        assert status is not None
        assert "health" in status
    
    def test_circuit_breaker_fast_fail(self):
        """Test circuit breaker enables fast-fail on repeated failures."""
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
        
        breaker = orchestrator.llm_circuit_breaker
        
        # Open circuit
        func = Mock(side_effect=Exception("error"))
        for _ in range(5):
            with pytest.raises(Exception):
                breaker.call(func)
        
        # Circuit should be open
        from phoenix.core.error_recovery import CircuitBreakerError
        
        with pytest.raises(CircuitBreakerError):
            breaker.call(func)
        
        # Should fail fast (no sleep in test)
        assert breaker.state.value == "open"


class TestErrorRecoveryWithHealthCheck:
    """Test error recovery with health checks."""
    
    def test_orchestrator_combines_health_and_recovery(self):
        """Test orchestrator uses both health checks and recovery."""
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
        
        # Get comprehensive status
        status = orchestrator.get_system_status()
        
        # Should have both health and recovery info
        assert status["health"]["status"] is not None
        assert status["error_recovery"] is not None
        assert status["operational_stats"] is not None
    
    def test_health_check_informs_recovery_decisions(self):
        """Test system makes decisions based on health."""
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
        
        # Startup health check
        ready = orchestrator.startup_health_check()
        
        # Should have made health determination
        assert isinstance(ready, bool)
        
        # Get detailed status
        status = orchestrator.get_system_status()
        
        # If health is bad, recovery should be engaged
        health_status = status["health"]["status"]
        assert health_status in ["healthy", "degraded", "unhealthy"]
