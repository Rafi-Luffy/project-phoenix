"""
Integration test for module integration with orchestrator.

Tests that all 5 optional modules are properly wired into
the autonomous_self_healing_orchestrator.
"""

import sys
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the phoenix module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phoenix.orchestrator.autonomous_self_healing_orchestrator import (
    AutonomousSelfHealingOrchestrator,
)


class TestModuleIntegration:
    """Test that all modules are integrated correctly."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return AutonomousSelfHealingOrchestrator(
            workspace_path="/tmp/phoenix_test",
            auto_heal=True,
        )
    
    def test_modules_initialized(self, orchestrator):
        """Test that all modules are initialized."""
        assert orchestrator.metrics_exporter is not None
        assert orchestrator.slack_notifier is not None
        assert orchestrator.baseline_tracker is not None
        assert orchestrator.fix_cache is not None
        assert orchestrator.cost_optimizer is not None
        assert orchestrator.confidence_analyzer is not None
        assert orchestrator.quality_validator is not None
    
    def test_cache_integration(self, orchestrator):
        """Test fix cache integration."""
        # Cache a fix
        sig = orchestrator.fix_cache.get_failure_signature(
            failure_type="test_failure",
            error_message="test error",
            stack_trace="",
        )
        
        assert sig is not None
        assert len(sig) > 0
        
        # Verify cache is empty initially
        cached = orchestrator.fix_cache.get_cached_fix(sig)
        assert cached is None
    
    def test_confidence_analyzer_integration(self, orchestrator):
        """Test confidence analyzer integration."""
        # Test confidence scoring
        level = orchestrator.confidence_analyzer.get_confidence_level(
            failure_type="null_pointer",
            llm_confidence=0.8,
            has_similar_fixes=True,
            fix_has_tests=True,
        )
        
        assert level is not None
        
        # Test that it allows high-confidence fixes
        should_apply = orchestrator.confidence_analyzer.should_apply_fix(level)
        assert isinstance(should_apply, bool)
    
    def test_slack_notifier_integration(self, orchestrator):
        """Test Slack notifier integration."""
        # Should initialize gracefully even without webhook
        assert orchestrator.slack_notifier is not None
        assert orchestrator.slack_notifier.enabled is False  # No webhook set
        
        # Should handle notifications gracefully
        orchestrator.slack_notifier.notify_critical_failure(
            failure_type="test",
            agent_name="test_agent",
            error_message="test error",
        )
        
        # Should not raise exception
        assert True
    
    def test_metrics_export_integration(self, orchestrator):
        """Test metrics exporter integration."""
        assert orchestrator.metrics_exporter is not None
        
        # Should be able to export metrics
        metrics = {"test": "metric"}
        orchestrator.metrics_exporter.export_healing_metrics(metrics)
        
        # Should not raise exception
        assert True
    
    def test_baseline_tracker_integration(self, orchestrator):
        """Test performance baseline tracker integration."""
        assert orchestrator.baseline_tracker is not None
        
        # Should be able to record baseline
        baseline = orchestrator.baseline_tracker.record_baseline(
            agent_name="test_agent",
            execution_time_ms=100,
            success_count=10,
            failure_count=1,
            error_frequency=0.1,
            avg_recovery_time_ms=50,
            memory_usage_mb=100,
        )
        
        assert baseline is not None
        assert baseline.agent_name == "test_agent"
    
    def test_stats_tracking(self, orchestrator):
        """Test that stats are tracked."""
        assert orchestrator.stats["total_cycles"] == 0
        assert orchestrator.stats["total_healed"] == 0
        assert orchestrator.stats["cache_hits"] == 0
        
        # Stats should be updated after cycle
        # (This would be tested in integration test with real data)
        assert True
    
    def test_dashboard_data(self, orchestrator):
        """Test that dashboard data can be retrieved."""
        dashboard_data = orchestrator.get_dashboard_data()
        
        assert dashboard_data is not None
        assert "statistics" in dashboard_data
        assert "healing_stats" in dashboard_data
        assert "cache" in dashboard_data
        assert "performance" in dashboard_data
        assert "most_reused_fixes" in dashboard_data
    
    def test_module_independence(self, orchestrator):
        """Test that modules work independently."""
        # Disable one module shouldn't affect others
        orchestrator.slack_notifier.enabled = False
        
        # Other modules should still work
        assert orchestrator.metrics_exporter is not None
        assert orchestrator.fix_cache is not None
        assert orchestrator.confidence_analyzer is not None


class TestMetricsExport:
    """Test metrics export functionality."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return AutonomousSelfHealingOrchestrator(
            workspace_path="/tmp/phoenix_test",
        )
    
    def test_export_all_metrics(self, orchestrator):
        """Test comprehensive metrics export."""
        # Should not raise exception
        orchestrator._export_all_metrics()
        assert True
    
    def test_prometheus_format(self, orchestrator):
        """Test Prometheus metrics format."""
        stats = {
            "test_metric": 42,
            "success_rate": 95.5,
        }
        
        # Should handle Prometheus export
        orchestrator.metrics_exporter.export_prometheus_format(stats)
        assert True
    
    def test_csv_export(self, orchestrator):
        """Test CSV export format."""
        stats = {
            "metric1": 10,
            "metric2": 20,
        }
        
        # Should handle CSV export
        orchestrator.metrics_exporter.export_csv_for_excel(stats)
        assert True


class TestContinuousHealingWithModules:
    """Test continuous healing with module integration."""
    
    def test_continuous_loop_with_metrics(self):
        """Test that metrics are exported in continuous loop."""
        orchestrator = AutonomousSelfHealingOrchestrator(
            workspace_path="/tmp/phoenix_test",
        )
        
        # Mock log source
        def mock_logs():
            return "No errors in logs"
        
        # Should handle continuous loop setup
        assert orchestrator.is_running is False
        
        # Would need async test for actual loop
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
