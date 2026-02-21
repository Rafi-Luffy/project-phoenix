"""
Observability Integration Tests

Tests observability system integrated with orchestrator.
"""

import pytest
from phoenix.orchestrator.autonomous_self_healing_orchestrator import (
    AutonomousSelfHealingOrchestrator,
)
from phoenix.core.observability import ObservabilityOrchestrator


class TestObservabilityOrchestratorIntegration:
    """Test observability integration with main orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with observability."""
        return AutonomousSelfHealingOrchestrator(
            workspace_path="./test_workspace"
        )
    
    def test_orchestrator_has_observability(self, orchestrator):
        """Test orchestrator has observability component."""
        assert hasattr(orchestrator, "observability")
        assert isinstance(orchestrator.observability, ObservabilityOrchestrator)
    
    def test_get_observability_dashboard(self, orchestrator):
        """Test getting observability dashboard."""
        dashboard = orchestrator.get_observability_dashboard()
        
        assert isinstance(dashboard, dict)
        assert "timestamp" in dashboard
        assert "metrics" in dashboard
        assert "recent_traces" in dashboard
        assert "system_status" in dashboard
    
    def test_dashboard_includes_system_status(self, orchestrator):
        """Test dashboard includes system status."""
        dashboard = orchestrator.get_observability_dashboard()
        
        # Should have system status
        system_status = dashboard["system_status"]
        assert "health" in system_status
        assert "error_recovery" in system_status
        assert "operational_stats" in system_status
    
    def test_tracing_available(self, orchestrator):
        """Test tracing service is available."""
        tracing = orchestrator.observability.tracing
        
        span = tracing.start_span("test_operation")
        assert span is not None
        assert span.span_id is not None
    
    def test_metrics_recording_available(self, orchestrator):
        """Test metrics recording is available."""
        obs = orchestrator.observability
        
        obs.record_healing_metric("test_metric", 42.5)
        
        metrics = obs.metrics.get_all_metrics()
        assert "phoenix.healing.test_metric" in metrics
    
    def test_start_healing_trace(self, orchestrator):
        """Test starting healing trace."""
        obs = orchestrator.observability
        
        span = obs.start_healing_trace(
            log_source="test",
            agent_type="test_agent",
        )
        
        assert span.name == "healing_cycle"
        assert span.attributes["log_source"] == "test"
        assert span.attributes["agent_type"] == "test_agent"


class TestObservabilityWorkflow:
    """Test complete observability workflow."""
    
    def test_tracing_healing_cycle(self):
        """Test tracing a healing cycle."""
        orch = AutonomousSelfHealingOrchestrator(
            workspace_path="./test"
        )
        obs = orch.observability
        
        # Start healing trace
        root = obs.start_healing_trace("logs", "pipeline")
        
        # Simulate detection
        detection = obs.start_child_span(root, "failure_detection")
        obs.record_healing_metric("failures_detected", 5)
        obs.tracing.finish_span(detection.span_id)
        
        # Simulate fix generation
        generation = obs.start_child_span(root, "fix_generation")
        obs.record_healing_metric("latency_ms", 2500)
        obs.tracing.finish_span(generation.span_id)
        
        # Finish root span
        obs.tracing.finish_span(root.span_id)
        
        # Get dashboard
        dashboard = orch.get_observability_dashboard()
        
        assert "recent_traces" in dashboard
        assert len(dashboard["recent_traces"]) > 0
    
    def test_metrics_aggregation(self):
        """Test metrics aggregation in dashboard."""
        orch = AutonomousSelfHealingOrchestrator(
            workspace_path="./test"
        )
        obs = orch.observability
        
        # Record multiple metrics
        for i in range(10):
            obs.record_healing_metric("latency_ms", 100 + i * 10)
            obs.record_healing_metric("success_rate", 0.9 + (i * 0.01))
        
        # Get dashboard
        dashboard = orch.get_observability_dashboard()
        
        # Should have metric summaries
        assert "summaries" in dashboard["metrics"]
        assert len(dashboard["metrics"]["summaries"]) > 0


class TestDashboardContent:
    """Test dashboard content and structure."""
    
    def test_empty_dashboard(self):
        """Test dashboard with no data."""
        orch = AutonomousSelfHealingOrchestrator(
            workspace_path="./test"
        )
        
        dashboard = orch.get_observability_dashboard()
        
        assert "timestamp" in dashboard
        assert "metrics" in dashboard
        assert "recent_traces" in dashboard
    
    def test_dashboard_with_data(self):
        """Test dashboard populated with data."""
        orch = AutonomousSelfHealingOrchestrator(
            workspace_path="./test"
        )
        obs = orch.observability
        
        # Add data
        span = obs.start_healing_trace("test")
        obs.record_healing_metric("latency", 100)
        obs.tracing.finish_span(span.span_id)
        
        # Get dashboard
        dashboard = orch.get_observability_dashboard()
        
        # Should have data
        assert len(dashboard["recent_traces"]) > 0
        assert len(dashboard["metrics"]["all_metrics"]) > 0
    
    def test_dashboard_format(self):
        """Test dashboard follows correct format."""
        orch = AutonomousSelfHealingOrchestrator(
            workspace_path="./test"
        )
        
        dashboard = orch.get_observability_dashboard()
        
        # Check structure
        assert isinstance(dashboard, dict)
        assert isinstance(dashboard["timestamp"], str)
        assert isinstance(dashboard["metrics"], dict)
        assert isinstance(dashboard["recent_traces"], list)
        assert isinstance(dashboard["system_status"], dict)
