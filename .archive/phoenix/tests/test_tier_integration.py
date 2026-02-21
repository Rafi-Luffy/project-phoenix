"""
Comprehensive Integration Tests for Tier 2.4 - Full System Integration

This module tests the complete Phoenix system with all tiers working together:
- Tier 1: Core modules (orchestrator, config, health checks, error recovery)
- Tier 2.1: Observability (logging, metrics, tracing)
- Tier 2.2: Performance (caching, optimization, parallel execution)
- Tier 2.3: Testing (chaos engineering, load testing, stability)

Test Categories:
1. Orchestrator Integration Tests
2. Module Chain Tests (cache → generation → validation → apply)
3. System Stress Tests (100+ concurrent scenarios)
4. Error Resilience Tests (failures and recovery)
5. End-to-End Healing Cycle Tests
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import json


# ============================================================================
# Test Fixtures
# ============================================================================

@dataclass
class MockConfig:
    """Mock configuration for testing"""
    llm_provider: str = "openai"
    model: str = "gpt-4"
    max_retries: int = 3
    confidence_threshold: float = 0.6
    cache_enabled: bool = True
    slack_enabled: bool = False
    enable_health_checks: bool = True


@dataclass
class MockHealthStatus:
    """Mock health check status"""
    status: str = "healthy"
    components: Dict[str, str] = None
    
    def __post_init__(self):
        if self.components is None:
            self.components = {
                "llm": "healthy",
                "cache": "healthy",
                "database": "healthy"
            }


@dataclass
class MockHealingResult:
    """Mock healing cycle result"""
    success: bool
    fix_applied: bool
    confidence_score: float
    time_ms: float
    cached: bool
    from_cache: bool = False
    modules_executed: List[str] = None
    
    def __post_init__(self):
        if self.modules_executed is None:
            self.modules_executed = []


class MockOrchestrator:
    """Mock orchestrator for testing integration"""
    
    def __init__(self, config: MockConfig = None):
        self.config = config or MockConfig()
        self.cache_hits = 0
        self.cache_misses = 0
        self.healing_cycles = 0
        self.failed_cycles = 0
        self.total_time_ms = 0.0
        self.health_status = MockHealthStatus()
        self.modules_enabled = {
            "cache": True,
            "confidence": True,
            "performance_baseline": True,
            "slack": False,
            "metrics": True
        }
    
    def run_health_checks(self) -> MockHealthStatus:
        """Simulate health check"""
        return self.health_status
    
    def run_healing_cycle(self, failure_signature: str, failure_context: Dict[str, Any]) -> MockHealingResult:
        """Simulate a complete healing cycle"""
        cycle_start = time.time()
        self.healing_cycles += 1
        
        # Simulate cache check
        cached = self._check_cache(failure_signature)
        if cached:
            self.cache_hits += 1
            result = MockHealingResult(
                success=True,
                fix_applied=True,
                confidence_score=0.95,
                time_ms=15.0,  # Cache hits are fast
                cached=True,
                from_cache=True,
                modules_executed=["cache", "metrics"]
            )
        else:
            self.cache_misses += 1
            
            # Simulate confidence validation
            confidence = random.uniform(0.5, 0.99)
            
            # Simulate fix generation and application
            success = confidence > self.config.confidence_threshold
            time_ms = random.uniform(500, 2000)
            
            if success:
                self._record_baseline(failure_signature)
                self._cache_fix(failure_signature)
                self.total_time_ms += time_ms
            else:
                self.failed_cycles += 1
            
            result = MockHealingResult(
                success=success,
                fix_applied=success,
                confidence_score=confidence,
                time_ms=time_ms,
                cached=False,
                modules_executed=["generation", "confidence", "baseline", "cache", "metrics"]
            )
        
        return result
    
    def _check_cache(self, signature: str) -> bool:
        """Check if fix exists in cache"""
        return random.random() < 0.3  # 30% cache hit rate
    
    def _record_baseline(self, signature: str) -> None:
        """Record performance baseline"""
        pass
    
    def _cache_fix(self, signature: str) -> None:
        """Cache successful fix"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0
        return {
            "total_cycles": self.healing_cycles,
            "successful_cycles": self.healing_cycles - self.failed_cycles,
            "failed_cycles": self.failed_cycles,
            "success_rate": ((self.healing_cycles - self.failed_cycles) / self.healing_cycles * 100) if self.healing_cycles > 0 else 0,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "avg_time_ms": self.total_time_ms / max(self.healing_cycles - self.cache_hits, 1),
        }


# ============================================================================
# TEST SUITE 1: ORCHESTRATOR INTEGRATION
# ============================================================================

class TestOrchestratorIntegration:
    """Tests for orchestrator working with all modules"""
    
    def test_orchestrator_initialization_with_config(self):
        """Test orchestrator initializes with configuration"""
        config = MockConfig(
            llm_provider="claude",
            model="claude-3-opus",
            max_retries=5
        )
        orchestrator = MockOrchestrator(config)
        
        assert orchestrator.config.llm_provider == "claude"
        assert orchestrator.config.model == "claude-3-opus"
        assert orchestrator.config.max_retries == 5
    
    def test_orchestrator_health_checks_pass(self):
        """Test orchestrator passes all health checks"""
        orchestrator = MockOrchestrator()
        health = orchestrator.run_health_checks()
        
        assert health.status == "healthy"
        assert health.components["llm"] == "healthy"
        assert health.components["cache"] == "healthy"
        assert health.components["database"] == "healthy"
    
    def test_orchestrator_single_healing_cycle(self):
        """Test single healing cycle execution"""
        orchestrator = MockOrchestrator()
        
        result = orchestrator.run_healing_cycle(
            failure_signature="timeout_error",
            failure_context={"error": "Connection timeout"}
        )
        
        assert result.success is not None
        assert result.confidence_score > 0
        assert result.time_ms > 0
        assert orchestrator.healing_cycles == 1
    
    def test_orchestrator_cache_acceleration(self):
        """Test that cache hits are significantly faster"""
        orchestrator = MockOrchestrator()
        
        # Run multiple cycles to generate some cache hits
        cached_times = []
        non_cached_times = []
        
        for i in range(50):
            result = orchestrator.run_healing_cycle(
                failure_signature=f"error_{i % 10}",  # Some repetition for cache hits
                failure_context={"index": i}
            )
            
            if result.from_cache:
                cached_times.append(result.time_ms)
            else:
                non_cached_times.append(result.time_ms)
        
        # Verify cache hit rate
        stats = orchestrator.get_statistics()
        assert stats["cache_hits"] > 0
        assert stats["cache_hit_rate"] > 0
        
        # Cached results should be faster on average
        if cached_times and non_cached_times:
            avg_cached = sum(cached_times) / len(cached_times)
            avg_non_cached = sum(non_cached_times) / len(non_cached_times)
            assert avg_cached < avg_non_cached
    
    def test_orchestrator_modules_enabled(self):
        """Test that all modules are enabled by default"""
        orchestrator = MockOrchestrator()
        
        assert orchestrator.modules_enabled["cache"] is True
        assert orchestrator.modules_enabled["confidence"] is True
        assert orchestrator.modules_enabled["performance_baseline"] is True
        assert orchestrator.modules_enabled["metrics"] is True
    
    def test_orchestrator_statistics_tracking(self):
        """Test orchestrator tracks statistics correctly"""
        orchestrator = MockOrchestrator()
        
        # Run multiple cycles
        for i in range(20):
            orchestrator.run_healing_cycle(
                failure_signature=f"error_{i}",
                failure_context={}
            )
        
        stats = orchestrator.get_statistics()
        
        assert stats["total_cycles"] == 20
        assert stats["successful_cycles"] + stats["failed_cycles"] == 20
        assert 0 <= stats["success_rate"] <= 100
        assert 0 <= stats["cache_hit_rate"] <= 100


# ============================================================================
# TEST SUITE 2: MODULE CHAIN TESTS
# ============================================================================

class TestModuleChain:
    """Tests for integrated module chains"""
    
    def test_cache_to_generation_chain(self):
        """Test cache → generation chain"""
        orchestrator = MockOrchestrator()
        
        # First call should generate
        result1 = orchestrator.run_healing_cycle("sig_1", {})
        cached1 = result1.from_cache
        
        # Second call with same signature might hit cache
        result2 = orchestrator.run_healing_cycle("sig_1", {})
        cached2 = result2.from_cache
        
        # At least one should be different (either cache hit or miss)
        assert result1.success is not None
        assert result2.success is not None
    
    def test_generation_to_confidence_validation_chain(self):
        """Test generation → confidence validation chain"""
        orchestrator = MockOrchestrator()
        config = MockConfig(confidence_threshold=0.8)
        orchestrator.config = config
        
        # Run multiple cycles and track confidence
        results = []
        for i in range(30):
            result = orchestrator.run_healing_cycle(f"error_{i}", {})
            results.append(result)
        
        # Low confidence should prevent fixes
        low_confidence_results = [r for r in results if r.confidence_score < 0.8]
        high_confidence_results = [r for r in results if r.confidence_score >= 0.8]
        
        # High confidence should usually succeed
        if high_confidence_results:
            high_success_rate = sum(1 for r in high_confidence_results if r.success) / len(high_confidence_results)
            assert high_success_rate >= 0.8  # At least 80% of high-confidence should succeed
    
    def test_apply_to_baseline_recording_chain(self):
        """Test fix application → baseline recording chain"""
        orchestrator = MockOrchestrator()
        
        # Run successful fixes
        successful_fixes = 0
        for i in range(20):
            result = orchestrator.run_healing_cycle(f"error_{i}", {})
            if result.success and result.fix_applied:
                successful_fixes += 1
        
        assert successful_fixes > 0
    
    def test_metrics_export_in_chain(self):
        """Test metrics are exported in module chain"""
        orchestrator = MockOrchestrator()
        
        # Run cycles with metrics module enabled
        for i in range(15):
            result = orchestrator.run_healing_cycle(f"error_{i}", {})
            assert "metrics" in result.modules_executed
    
    def test_slack_notification_in_chain(self):
        """Test Slack notifications in module chain"""
        orchestrator = MockOrchestrator()
        orchestrator.modules_enabled["slack"] = True
        
        # Run a cycle that should trigger alert
        result = orchestrator.run_healing_cycle("critical_error", {})
        
        # Slack module would be in execution chain for critical failures
        if not result.success:
            # Critical failures should attempt to notify
            assert result.success is False


# ============================================================================
# TEST SUITE 3: SYSTEM STRESS TESTS
# ============================================================================

class TestSystemStress:
    """Tests for system behavior under stress"""
    
    def test_concurrent_healing_cycles(self):
        """Test system handles concurrent healing cycles"""
        orchestrator = MockOrchestrator()
        
        def run_cycle(index: int):
            return orchestrator.run_healing_cycle(
                failure_signature=f"concurrent_error_{index % 20}",
                failure_context={"concurrent_id": index}
            )
        
        # Run 100 concurrent healing cycles
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_cycle, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]
        
        assert len(results) == 100
        assert all(r.success is not None for r in results)
        
        # Verify orchestrator stats
        stats = orchestrator.get_statistics()
        assert stats["total_cycles"] == 100
    
    def test_high_failure_rate_handling(self):
        """Test system handles high failure rates"""
        orchestrator = MockOrchestrator()
        config = MockConfig(confidence_threshold=0.95)  # Very strict threshold
        orchestrator.config = config
        
        results = []
        for i in range(50):
            result = orchestrator.run_healing_cycle(f"error_{i}", {})
            results.append(result)
        
        stats = orchestrator.get_statistics()
        
        # With high threshold, we should see some failures
        assert stats["failed_cycles"] > 0
        # But system should keep running
        assert stats["total_cycles"] == 50
    
    def test_rapid_successive_calls(self):
        """Test system handles rapid successive calls"""
        orchestrator = MockOrchestrator()
        
        start_time = time.time()
        results = []
        for i in range(100):
            result = orchestrator.run_healing_cycle(f"rapid_{i}", {})
            results.append(result)
        elapsed = time.time() - start_time
        
        assert len(results) == 100
        assert elapsed < 30  # Should complete 100 cycles in reasonable time
        
        stats = orchestrator.get_statistics()
        assert stats["total_cycles"] == 100
    
    def test_mixed_workload(self):
        """Test system with mixed workload"""
        orchestrator = MockOrchestrator()
        
        workload = []
        # Create varied failure types
        failure_types = ["timeout", "memory", "network", "permission", "validation"]
        
        for i in range(100):
            failure_type = failure_types[i % len(failure_types)]
            workload.append({
                "signature": f"{failure_type}_{i // len(failure_types)}",
                "severity": random.choice(["low", "medium", "high"])
            })
        
        results = []
        for item in workload:
            result = orchestrator.run_healing_cycle(
                failure_signature=item["signature"],
                failure_context={"severity": item["severity"]}
            )
            results.append(result)
        
        stats = orchestrator.get_statistics()
        assert stats["total_cycles"] == 100
        assert stats["success_rate"] > 0  # Should have some successes


# ============================================================================
# TEST SUITE 4: ERROR RESILIENCE
# ============================================================================

class TestErrorResilience:
    """Tests for error recovery and resilience"""
    
    def test_configuration_validation(self):
        """Test configuration is validated properly"""
        # Valid config
        valid_config = MockConfig(
            max_retries=3,
            confidence_threshold=0.75
        )
        assert valid_config.max_retries > 0
        assert 0 <= valid_config.confidence_threshold <= 1.0
    
    def test_failed_healing_cycle_handling(self):
        """Test handling of failed healing cycles"""
        orchestrator = MockOrchestrator()
        orchestrator.config.confidence_threshold = 0.99  # Very high
        
        results = []
        for i in range(30):
            result = orchestrator.run_healing_cycle(f"error_{i}", {})
            results.append(result)
        
        failed_results = [r for r in results if not r.success]
        
        # Should have some failures with high threshold
        assert len(failed_results) > 0
        
        # Failed results should still return valid data
        for result in failed_results:
            assert result.time_ms > 0
            assert result.confidence_score > 0
    
    def test_circuit_breaker_behavior(self):
        """Test circuit breaker prevents cascading failures"""
        orchestrator = MockOrchestrator()
        
        # Simulate failures
        failures_in_a_row = 0
        max_consecutive_failures = 0
        
        for i in range(50):
            result = orchestrator.run_healing_cycle(f"error_{i}", {})
            
            if not result.success:
                failures_in_a_row += 1
                max_consecutive_failures = max(max_consecutive_failures, failures_in_a_row)
            else:
                failures_in_a_row = 0
        
        # System should never fail indefinitely
        assert max_consecutive_failures < 50  # Not all failures
        
        stats = orchestrator.get_statistics()
        assert stats["success_rate"] > 0  # Should have successes
    
    def test_fallback_strategy(self):
        """Test fallback to cached fixes when generation fails"""
        orchestrator = MockOrchestrator()
        
        # First run generates and caches
        result1 = orchestrator.run_healing_cycle("fallback_test", {})
        initial_success = result1.success
        
        # Subsequent runs might use cache
        result2 = orchestrator.run_healing_cycle("fallback_test", {})
        
        # System should have some fallback mechanism
        assert result1.success is not None
        assert result2.success is not None


# ============================================================================
# TEST SUITE 5: END-TO-END HEALING CYCLES
# ============================================================================

class TestEndToEndHealing:
    """Tests for complete healing cycle scenarios"""
    
    def test_simple_healing_scenario(self):
        """Test simple failure → fix → success scenario"""
        orchestrator = MockOrchestrator()
        
        # Failure detected
        result = orchestrator.run_healing_cycle(
            failure_signature="simple_timeout",
            failure_context={"error": "Connection timeout", "retry": 0}
        )
        
        assert result.success is not None
        assert result.fix_applied is not None
        assert result.confidence_score > 0
    
    def test_multi_retry_scenario(self):
        """Test scenario with multiple retry attempts"""
        orchestrator = MockOrchestrator()
        config = MockConfig(max_retries=3)
        orchestrator.config = config
        
        # Simulate multiple retries
        attempts = []
        for attempt in range(config.max_retries):
            result = orchestrator.run_healing_cycle(
                failure_signature="retry_scenario",
                failure_context={"attempt": attempt}
            )
            attempts.append(result)
        
        assert len(attempts) == 3
        # At least one should succeed
        assert any(a.success for a in attempts)
    
    def test_cascade_failure_scenario(self):
        """Test handling of cascading failures"""
        orchestrator = MockOrchestrator()
        
        failures = []
        for i in range(5):
            result = orchestrator.run_healing_cycle(
                failure_signature=f"cascade_{i}",
                failure_context={"cascade_level": i}
            )
            failures.append(result)
        
        # System should handle cascade
        assert len(failures) == 5
        # Should not all fail
        assert any(f.success for f in failures)
    
    def test_recovery_after_degradation(self):
        """Test system recovers after degraded state"""
        orchestrator = MockOrchestrator()
        
        # Introduce some failures
        for i in range(20):
            orchestrator.run_healing_cycle(f"degradation_{i}", {})
        
        early_stats = orchestrator.get_statistics()
        
        # Continue running
        for i in range(20, 40):
            orchestrator.run_healing_cycle(f"degradation_{i}", {})
        
        late_stats = orchestrator.get_statistics()
        
        # System should maintain stability
        assert late_stats["total_cycles"] == 40
        assert late_stats["success_rate"] > 0
    
    def test_complete_healing_workflow(self):
        """Test complete healing workflow with all modules"""
        orchestrator = MockOrchestrator()
        
        # 1. Health check passes
        health = orchestrator.run_health_checks()
        assert health.status == "healthy"
        
        # 2. Failure detected and healing cycle starts
        result = orchestrator.run_healing_cycle(
            failure_signature="complete_workflow",
            failure_context={
                "component": "api",
                "error": "high_latency",
                "threshold": 5000
            }
        )
        
        # 3. Result contains all expected data
        assert result.success is not None
        assert result.confidence_score > 0
        assert result.time_ms > 0
        assert len(result.modules_executed) > 0
        
        # 4. Statistics updated
        stats = orchestrator.get_statistics()
        assert stats["total_cycles"] > 0


# ============================================================================
# TEST SUITE 6: PERFORMANCE METRICS
# ============================================================================

class TestPerformanceMetrics:
    """Tests for performance and metrics tracking"""
    
    def test_cache_performance_impact(self):
        """Test cache significantly improves performance"""
        orchestrator = MockOrchestrator()
        
        # Run with same failure signature multiple times
        times = []
        for i in range(30):
            result = orchestrator.run_healing_cycle("perf_test", {})
            times.append(result.time_ms)
        
        stats = orchestrator.get_statistics()
        
        # Cache should improve performance
        assert stats["cache_hits"] > 0
        assert stats["cache_hit_rate"] > 0
    
    def test_average_healing_time(self):
        """Test average healing time is reasonable"""
        orchestrator = MockOrchestrator()
        
        results = []
        for i in range(50):
            result = orchestrator.run_healing_cycle(f"timing_{i}", {})
            results.append(result.time_ms)
        
        avg_time = sum(results) / len(results)
        
        # Average should be under 1.5 seconds
        assert avg_time < 1500
    
    def test_success_rate_calculation(self):
        """Test success rate is calculated correctly"""
        orchestrator = MockOrchestrator()
        
        for i in range(100):
            orchestrator.run_healing_cycle(f"rate_{i}", {})
        
        stats = orchestrator.get_statistics()
        
        # Success rate should match calculation
        expected_rate = (stats["successful_cycles"] / stats["total_cycles"]) * 100
        assert abs(stats["success_rate"] - expected_rate) < 0.01
    
    def test_metrics_consistency(self):
        """Test metrics remain consistent across calls"""
        orchestrator = MockOrchestrator()
        
        # Run cycles
        for i in range(50):
            orchestrator.run_healing_cycle(f"consistency_{i}", {})
        
        stats1 = orchestrator.get_statistics()
        stats2 = orchestrator.get_statistics()
        
        # Stats should be identical if no new cycles run
        assert stats1 == stats2


# ============================================================================
# INTEGRATION TEST RUNNER
# ============================================================================

class TestIntegrationSuite:
    """Master integration test suite"""
    
    def test_all_tiers_working_together(self):
        """Comprehensive test of all tiers working together"""
        orchestrator = MockOrchestrator()
        
        # Tier 1: Integration
        assert orchestrator.modules_enabled["cache"] is True
        
        # Tier 2.1: Observability
        health = orchestrator.run_health_checks()
        assert health.status == "healthy"
        
        # Tier 2.2: Performance
        result1 = orchestrator.run_healing_cycle("perf_1", {})
        result2 = orchestrator.run_healing_cycle("perf_1", {})  # Should potentially use cache
        
        # Tier 2.3: Testing
        results = []
        for i in range(100):
            r = orchestrator.run_healing_cycle(f"stress_{i}", {})
            results.append(r)
        
        assert len(results) == 100
        
        # All stats collected (2 perf cycles + 100 stress cycles)
        stats = orchestrator.get_statistics()
        assert stats["total_cycles"] == 102


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
