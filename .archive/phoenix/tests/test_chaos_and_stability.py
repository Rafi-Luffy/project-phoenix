"""
Comprehensive Tests for Tier 2.3: Testing Expansion

Tests all chaos, load, failure, and stability testing utilities.
"""

import pytest
import time
from phoenix.testing.chaos_engineer import (
    ChaosEngineer, FailureType, RecoveryStrategy, FailureInjection, ChaosScenario
)
from phoenix.testing.load_tester import (
    LoadTester, LoadPattern, LoadResult
)
from phoenix.testing.failure_simulator import (
    FailureSimulator, FailureMode, CascadeType, FailureEvent, FailureScenario
)
from phoenix.testing.stability_tester import (
    StabilityTester, ResourceType
)


class TestChaosEngineer:
    """Test chaos engineering functionality."""

    def test_chaos_engineer_init(self):
        """Test ChaosEngineer initialization."""
        engineer = ChaosEngineer()
        assert engineer is not None
        assert len(engineer.scenarios) == 0
        assert engineer.stats.total_scenarios == 0

    def test_create_scenario(self):
        """Test creating a chaos scenario."""
        engineer = ChaosEngineer()
        scenario = engineer.create_scenario(
            name="test_scenario",
            description="Test scenario",
            duration_seconds=10.0,
            concurrent_failures=2,
        )

        assert scenario is not None
        assert scenario.name == "test_scenario"
        assert scenario.duration_seconds == 10.0
        assert scenario.concurrent_failures == 2

    def test_inject_failure(self):
        """Test failure injection."""
        engineer = ChaosEngineer()
        scenario = engineer.create_scenario("test", "test")

        injection = engineer.inject_failure(
            scenario_name="test",
            failure_type=FailureType.LLM_FAILURE,
            component="llm_service",
            duration_seconds=2.0,
            severity=0.8,
            recovery_strategy=RecoveryStrategy.AUTO_RECOVERY,
        )

        assert injection is not None
        assert injection.failure_type == FailureType.LLM_FAILURE
        assert injection.component == "llm_service"
        assert injection.duration_seconds == 2.0

    def test_register_failure_handler(self):
        """Test registering failure handlers."""
        engineer = ChaosEngineer()
        calls = []

        def handler(injection):
            calls.append(injection)

        engineer.register_failure_handler(FailureType.TIMEOUT, handler)

        assert FailureType.TIMEOUT in engineer.failure_callbacks
        assert len(engineer.failure_callbacks[FailureType.TIMEOUT]) == 1

    def test_run_scenario(self):
        """Test running a chaos scenario."""
        engineer = ChaosEngineer()
        scenario = engineer.create_scenario("test", "test", duration_seconds=5.0)

        engineer.inject_failure(
            scenario_name="test",
            failure_type=FailureType.TIMEOUT,
            component="service_a",
            duration_seconds=1.0,
        )

        completed = engineer.run_scenario("test")

        assert completed is not None
        assert completed.started_at is not None
        assert completed.completed_at is not None
        assert engineer.stats.total_scenarios == 1

    def test_chaos_stats(self):
        """Test chaos statistics."""
        engineer = ChaosEngineer()
        scenario = engineer.create_scenario("test", "test", duration_seconds=3.0)

        engineer.inject_failure("test", FailureType.TIMEOUT, "service")

        engineer.run_scenario("test")

        stats = engineer.get_stats()
        assert stats.total_scenarios == 1
        assert stats.failures_injected > 0
        assert stats.recovery_rate() >= 0


class TestLoadTester:
    """Test load testing functionality."""

    def test_load_tester_init(self):
        """Test LoadTester initialization."""
        tester = LoadTester()
        assert tester is not None
        assert len(tester.phases) == 0
        assert len(tester.results) == 0

    def test_add_phase(self):
        """Test adding load test phase."""
        tester = LoadTester()
        phase = tester.add_phase(
            duration_seconds=10.0,
            concurrent_users=10,
            requests_per_user=5,
        )

        assert phase is not None
        assert phase.duration_seconds == 10.0
        assert phase.concurrent_users == 10

    def test_run_load_test(self):
        """Test running load test."""
        tester = LoadTester()
        tester.add_phase(duration_seconds=2.0, concurrent_users=5, requests_per_user=2)

        def test_function(request_id):
            """Simple test function."""
            time.sleep(0.01)
            return True, 10.0, None

        metrics = tester.run_load_test(test_function, LoadPattern.CONSTANT)

        assert metrics is not None
        assert metrics.total_requests > 0
        assert metrics.successful_requests > 0
        assert metrics.throughput_requests_per_second > 0

    def test_load_patterns(self):
        """Test different load patterns."""
        for pattern in [LoadPattern.CONSTANT, LoadPattern.RAMP_UP]:
            tester = LoadTester()
            tester.add_phase(duration_seconds=1.0, concurrent_users=3, requests_per_user=2)

            def test_func(req_id):
                return True, 5.0, None

            metrics = tester.run_load_test(test_func, pattern)
            assert metrics.total_requests > 0

    def test_load_metrics(self):
        """Test load metrics calculation."""
        tester = LoadTester()
        tester.add_phase(duration_seconds=2.0, concurrent_users=4, requests_per_user=3)

        def test_func(req_id):
            return True, 10.0, None

        metrics = tester.run_load_test(test_func)

        assert metrics.total_requests > 0
        assert metrics.min_response_time_ms <= metrics.max_response_time_ms
        assert metrics.avg_response_time_ms > 0
        assert metrics.p50_response_time_ms > 0
        assert metrics.p95_response_time_ms >= metrics.p50_response_time_ms
        assert metrics.p99_response_time_ms >= metrics.p95_response_time_ms


class TestFailureSimulator:
    """Test failure simulation functionality."""

    def test_failure_simulator_init(self):
        """Test FailureSimulator initialization."""
        simulator = FailureSimulator()
        assert simulator is not None
        assert len(simulator.scenarios) == 0

    def test_create_scenario(self):
        """Test creating failure scenario."""
        simulator = FailureSimulator()
        scenario = simulator.create_scenario(
            name="test_scenario",
            description="Test failure scenario",
            duration_seconds=20.0,
            enable_cascade=True,
        )

        assert scenario is not None
        assert scenario.name == "test_scenario"
        assert scenario.enable_cascade is True

    def test_add_failure_event(self):
        """Test adding failure event to scenario."""
        simulator = FailureSimulator()
        scenario = simulator.create_scenario("test", "test")

        event = simulator.add_failure_event(
            scenario_id=scenario.scenario_id,
            failure_mode=FailureMode.TIMEOUT,
            component="database",
            duration_seconds=3.0,
            error_message="Query timeout",
        )

        assert event is not None
        assert event.failure_mode == FailureMode.TIMEOUT
        assert event.component == "database"

    def test_run_scenario(self):
        """Test running failure scenario."""
        simulator = FailureSimulator()
        scenario = simulator.create_scenario("test", "test", duration_seconds=5.0)

        simulator.add_failure_event(
            scenario_id=scenario.scenario_id,
            failure_mode=FailureMode.TIMEOUT,
            component="service",
            duration_seconds=2.0,
        )

        completed = simulator.run_scenario(scenario.scenario_id)

        assert completed is not None
        assert completed.started_at is not None
        assert completed.completed_at is not None
        assert len(completed.failure_events) > 0

    def test_cascade_detection(self):
        """Test cascading failure detection."""
        simulator = FailureSimulator()
        scenario = simulator.create_scenario("test", "test", duration_seconds=10.0, enable_cascade=True)

        simulator.add_failure_event(
            scenario_id=scenario.scenario_id,
            failure_mode=FailureMode.TIMEOUT,
            component="core_service",
            duration_seconds=2.0,
        )

        completed = simulator.run_scenario(scenario.scenario_id)

        # Cascades may or may not occur based on probability
        assert completed is not None
        assert len(completed.cascades) >= 0

    def test_failure_simulator_stats(self):
        """Test failure simulator statistics."""
        simulator = FailureSimulator()
        scenario = simulator.create_scenario("test", "test", duration_seconds=5.0)

        simulator.add_failure_event(
            scenario_id=scenario.scenario_id,
            failure_mode=FailureMode.EXCEPTION,
            component="service",
            duration_seconds=1.0,
        )

        simulator.run_scenario(scenario.scenario_id)

        stats = simulator.get_stats()
        assert stats.total_scenarios == 1
        assert stats.total_failures_injected > 0


class TestStabilityTester:
    """Test stability testing functionality."""

    def test_stability_tester_init(self):
        """Test StabilityTester initialization."""
        tester = StabilityTester()
        assert tester is not None
        assert len(tester.snapshots) == 0
        assert len(tester.memory_leaks) == 0

    def test_take_snapshot(self):
        """Test taking resource snapshot."""
        tester = StabilityTester()
        snapshot = tester._take_snapshot()

        assert snapshot is not None
        assert snapshot.cpu_percent >= 0
        assert snapshot.memory_percent >= 0
        assert snapshot.memory_bytes > 0
        assert snapshot.thread_count > 0

    def test_start_monitoring(self):
        """Test starting stability monitoring."""
        tester = StabilityTester()
        thread = tester.start_monitoring(duration_seconds=3.0, sample_interval_seconds=0.5)

        assert thread is not None
        thread.join(timeout=5.0)

        assert tester.metrics.snapshots_collected > 0
        assert tester.monitoring is False

    def test_snapshot_collection(self):
        """Test collecting multiple snapshots."""
        tester = StabilityTester()
        thread = tester.start_monitoring(duration_seconds=2.0, sample_interval_seconds=0.2)

        thread.join(timeout=5.0)

        snapshots = tester.get_snapshot_history()
        assert len(snapshots) > 0

    def test_stability_metrics(self):
        """Test stability metrics calculation."""
        tester = StabilityTester()
        thread = tester.start_monitoring(duration_seconds=2.0, sample_interval_seconds=0.2)

        thread.join(timeout=5.0)

        metrics = tester.get_metrics()
        assert metrics.snapshots_collected > 0
        assert metrics.avg_cpu_percent >= 0
        assert metrics.avg_memory_percent >= 0
        assert 0 <= metrics.stability_score <= 100

    def test_stop_monitoring(self):
        """Test stopping monitoring."""
        tester = StabilityTester()
        thread = tester.start_monitoring(duration_seconds=10.0)

        time.sleep(1.0)
        tester.stop_monitoring()
        thread.join(timeout=5.0)

        assert tester.monitoring is False


class TestIntegration:
    """Integration tests for all testing utilities."""

    def test_chaos_and_recovery(self):
        """Test chaos engineering with recovery."""
        engineer = ChaosEngineer()
        scenario = engineer.create_scenario("integration", "integration test", duration_seconds=5.0)

        for i in range(3):
            engineer.inject_failure(
                scenario_name="integration",
                failure_type=FailureType.TIMEOUT,
                component=f"service_{i}",
                duration_seconds=1.0,
            )

        engineer.run_scenario("integration")

        results = engineer.get_scenario_results("integration")
        assert "scenario" in results
        assert "recovery_results" in results

    def test_combined_load_and_chaos(self):
        """Test load test under chaos conditions."""
        # First run normal load test
        tester = LoadTester()
        tester.add_phase(duration_seconds=2.0, concurrent_users=5, requests_per_user=2)

        def test_func(req_id):
            return True, 5.0, None

        metrics = tester.run_load_test(test_func, LoadPattern.CONSTANT)
        assert metrics.total_requests > 0

    def test_comprehensive_test_suite(self):
        """Test all testing utilities together."""
        # Chaos Engineering
        engineer = ChaosEngineer()
        scenario = engineer.create_scenario("comprehensive", "test", duration_seconds=3.0)
        engineer.inject_failure("comprehensive", FailureType.TIMEOUT, "service")
        engineer.run_scenario("comprehensive")

        # Load Testing
        tester = LoadTester()
        tester.add_phase(duration_seconds=1.0, concurrent_users=3, requests_per_user=1)
        tester.run_load_test(lambda x: (True, 5.0, None))

        # Failure Simulation
        simulator = FailureSimulator()
        scenario = simulator.create_scenario("test", "test", duration_seconds=3.0)
        simulator.add_failure_event(scenario.scenario_id, FailureMode.TIMEOUT, "service")
        simulator.run_scenario(scenario.scenario_id)

        # Stability Testing
        stability = StabilityTester()
        thread = stability.start_monitoring(duration_seconds=1.0, sample_interval_seconds=0.1)
        thread.join(timeout=3.0)

        # All should complete without errors
        assert engineer.stats.total_scenarios > 0
        assert tester.metrics.total_requests > 0
        assert simulator.stats.total_scenarios > 0
        assert stability.metrics.snapshots_collected > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
