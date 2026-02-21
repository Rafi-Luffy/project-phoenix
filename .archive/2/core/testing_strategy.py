"""
Testing Strategy - Module 5.2

Comprehensive testing framework including unit testing,
integration testing, end-to-end testing, stress testing,
security testing, and chaos engineering.
"""

import time
import random
import threading
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Tuple
from collections import defaultdict
import traceback


class TestType(Enum):
    """Types of tests"""
    UNIT = "unit"
    INTEGRATION = "integration"
    END_TO_END = "end_to_end"
    STRESS = "stress"
    SECURITY = "security"
    CHAOS = "chaos"
    REGRESSION = "regression"
    SMOKE = "smoke"


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class SeverityLevel(Enum):
    """Severity level for failures"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class TestCase:
    """Individual test case"""
    test_id: str
    test_type: TestType
    name: str
    test_fn: Callable
    expected_result: Any
    timeout: float = 30.0
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)
    status: TestStatus = TestStatus.PENDING
    duration: float = 0.0
    error_message: Optional[str] = None


@dataclass
class TestResult:
    """Result of test execution"""
    test_id: str
    test_name: str
    status: TestStatus
    duration: float
    timestamp: float = field(default_factory=time.time)
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    assertions_passed: int = 0
    assertions_failed: int = 0


@dataclass
class TestSuite:
    """Collection of tests"""
    suite_id: str
    name: str
    tests: List[TestCase] = field(default_factory=list)
    setup_fn: Optional[Callable] = None
    teardown_fn: Optional[Callable] = None
    execution_order: str = "sequential"  # sequential, parallel
    tags: List[str] = field(default_factory=list)


@dataclass
class StressTestConfig:
    """Configuration for stress testing"""
    duration_seconds: int = 60
    request_rate: int = 100  # requests per second
    max_concurrent: int = 50
    ramp_up_time: int = 10  # seconds to reach max load
    payload_size_bytes: int = 1024
    failure_threshold: float = 0.05  # 5%


@dataclass
class ChaosTestConfig:
    """Configuration for chaos engineering"""
    failure_injection_rate: float = 0.1  # 10% of requests fail
    latency_injection_rate: float = 0.05  # 5% of requests get extra latency
    latency_range: Tuple[int, int] = (100, 5000)  # milliseconds
    partition_duration: int = 30  # seconds
    partition_probability: float = 0.01


class UnitTestSuite:
    """Framework for unit testing"""

    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
        self.lock = threading.RLock()

    def add_test(self, test_case: TestCase):
        """Add test case"""
        with self.lock:
            self.test_cases.append(test_case)

    def run_tests(self, filter_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run all test cases"""
        with self.lock:
            results_summary = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0.0,
                "results": []
            }

            start_time = time.time()

            tests_to_run = self.test_cases
            if filter_tags:
                tests_to_run = [
                    t for t in self.test_cases
                    if any(tag in t.tags for tag in filter_tags)
                ]

            for test_case in tests_to_run:
                result = self._run_single_test(test_case)
                results_summary["results"].append(result)

                results_summary["total"] += 1
                if result.status == TestStatus.PASSED:
                    results_summary["passed"] += 1
                elif result.status == TestStatus.FAILED:
                    results_summary["failed"] += 1
                elif result.status == TestStatus.SKIPPED:
                    results_summary["skipped"] += 1

            results_summary["duration"] = time.time() - start_time
            self.results.extend([r for r in results_summary["results"]])

            return results_summary

    def _run_single_test(self, test_case: TestCase) -> TestResult:
        """Run single test case with retry logic"""
        attempts = 0
        max_attempts = test_case.retry_count + 1

        while attempts < max_attempts:
            attempts += 1
            start = time.time()

            try:
                result = test_case.test_fn()
                duration = time.time() - start

                if result == test_case.expected_result:
                    return TestResult(
                        test_id=test_case.test_id,
                        test_name=test_case.name,
                        status=TestStatus.PASSED,
                        duration=duration
                    )
                else:
                    return TestResult(
                        test_id=test_case.test_id,
                        test_name=test_case.name,
                        status=TestStatus.FAILED,
                        duration=duration,
                        error_message=f"Expected {test_case.expected_result}, got {result}"
                    )

            except Exception as e:
                if attempts >= max_attempts:
                    return TestResult(
                        test_id=test_case.test_id,
                        test_name=test_case.name,
                        status=TestStatus.ERROR,
                        duration=time.time() - start,
                        error_message=str(e),
                        stack_trace=traceback.format_exc()
                    )

                time.sleep(0.5)

        return TestResult(
            test_id=test_case.test_id,
            test_name=test_case.name,
            status=TestStatus.FAILED,
            duration=0.0
        )

    def get_test_report(self) -> Dict[str, Any]:
        """Generate test report"""
        with self.lock:
            if not self.results:
                return {}

            passed = [r for r in self.results if r.status == TestStatus.PASSED]
            failed = [r for r in self.results if r.status == TestStatus.FAILED]
            errors = [r for r in self.results if r.status == TestStatus.ERROR]

            return {
                "total_tests": len(self.results),
                "passed": len(passed),
                "failed": len(failed),
                "errors": len(errors),
                "pass_rate": len(passed) / len(self.results) if self.results else 0.0,
                "total_duration": sum(r.duration for r in self.results),
                "failed_tests": [r.test_name for r in failed],
                "error_tests": [r.test_name for r in errors]
            }


class IntegrationTestSuite:
    """Framework for integration testing"""

    def __init__(self):
        self.test_suites: List[TestSuite] = []
        self.results: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()

    def add_test_suite(self, suite: TestSuite):
        """Add test suite"""
        with self.lock:
            self.test_suites.append(suite)

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run all integration test suites"""
        with self.lock:
            overall_results = {
                "suites_run": 0,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "duration": 0.0,
                "suite_results": {}
            }

            start_time = time.time()

            for suite in self.test_suites:
                suite_results = self._run_suite(suite)
                overall_results["suite_results"][suite.suite_id] = suite_results
                overall_results["suites_run"] += 1
                overall_results["total_tests"] += suite_results["total"]
                overall_results["passed"] += suite_results["passed"]
                overall_results["failed"] += suite_results["failed"]

            overall_results["duration"] = time.time() - start_time
            return overall_results

    def _run_suite(self, suite: TestSuite) -> Dict[str, Any]:
        """Run single test suite"""
        suite_results = {
            "suite_id": suite.suite_id,
            "name": suite.name,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "duration": 0.0,
            "test_results": []
        }

        start_time = time.time()

        # Setup
        if suite.setup_fn:
            try:
                suite.setup_fn()
            except Exception as e:
                suite_results["error"] = f"Setup failed: {str(e)}"
                return suite_results

        # Run tests
        for test_case in suite.tests:
            result = self._run_test(test_case)
            suite_results["test_results"].append(result)
            suite_results["total"] += 1

            if result.status == TestStatus.PASSED:
                suite_results["passed"] += 1
            else:
                suite_results["failed"] += 1

        # Teardown
        if suite.teardown_fn:
            try:
                suite.teardown_fn()
            except Exception as e:
                suite_results["teardown_error"] = str(e)

        suite_results["duration"] = time.time() - start_time
        self.results[suite.suite_id] = suite_results

        return suite_results

    def _run_test(self, test_case: TestCase) -> TestResult:
        """Run single test"""
        start = time.time()

        try:
            result = test_case.test_fn()
            duration = time.time() - start

            if result == test_case.expected_result:
                return TestResult(
                    test_id=test_case.test_id,
                    test_name=test_case.name,
                    status=TestStatus.PASSED,
                    duration=duration
                )
            else:
                return TestResult(
                    test_id=test_case.test_id,
                    test_name=test_case.name,
                    status=TestStatus.FAILED,
                    duration=duration,
                    error_message="Assertion failed"
                )

        except Exception as e:
            return TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                status=TestStatus.ERROR,
                duration=time.time() - start,
                error_message=str(e)
            )


class EndToEndTestSuite:
    """Framework for end-to-end testing"""

    def __init__(self):
        self.test_scenarios: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        self.lock = threading.RLock()

    def add_scenario(self, scenario_name: str, steps: List[Callable],
                    expected_outcomes: List[Any]):
        """Add end-to-end test scenario"""
        with self.lock:
            self.test_scenarios.append({
                "name": scenario_name,
                "steps": steps,
                "expected_outcomes": expected_outcomes,
                "status": "pending"
            })

    def run_scenarios(self) -> Dict[str, Any]:
        """Run all E2E scenarios"""
        with self.lock:
            results = {
                "total_scenarios": len(self.test_scenarios),
                "successful": 0,
                "failed": 0,
                "duration": 0.0,
                "scenario_results": []
            }

            start_time = time.time()

            for scenario in self.test_scenarios:
                scenario_result = self._run_scenario(scenario)
                results["scenario_results"].append(scenario_result)

                if scenario_result["status"] == "success":
                    results["successful"] += 1
                else:
                    results["failed"] += 1

            results["duration"] = time.time() - start_time
            self.results = results["scenario_results"]

            return results

    def _run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run single E2E scenario"""
        scenario_result = {
            "name": scenario["name"],
            "status": "success",
            "steps_executed": 0,
            "errors": []
        }

        start_time = time.time()

        for i, step in enumerate(scenario["steps"]):
            try:
                result = step()
                if i < len(scenario["expected_outcomes"]):
                    if result != scenario["expected_outcomes"][i]:
                        scenario_result["status"] = "failed"
                        scenario_result["errors"].append(
                            f"Step {i}: Expected {scenario['expected_outcomes'][i]}, got {result}"
                        )
                scenario_result["steps_executed"] += 1

            except Exception as e:
                scenario_result["status"] = "failed"
                scenario_result["errors"].append(f"Step {i}: {str(e)}")

        scenario_result["duration"] = time.time() - start_time
        return scenario_result


class StressTestProtocol:
    """Protocol for stress testing"""

    def __init__(self, config: StressTestConfig):
        self.config = config
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_latency": 0.0,
            "max_latency": 0.0,
            "min_latency": float('inf'),
            "throughput": 0.0,
            "error_rate": 0.0
        }

    def run_stress_test(self, target_function: Callable,
                       test_data_generator: Callable) -> Dict[str, Any]:
        """Run stress test"""
        start_time = time.time()
        latencies = []
        failed_count = 0
        total_count = 0

        # Ramp up phase
        requests_per_second = 0
        ramp_up_step = self.config.request_rate / self.config.ramp_up_time

        elapsed = 0
        while elapsed < self.config.duration_seconds:
            # Increase load during ramp-up
            if elapsed < self.config.ramp_up_time:
                requests_per_second = int(ramp_up_step * elapsed)
            else:
                requests_per_second = self.config.request_rate

            # Make requests
            for _ in range(requests_per_second):
                test_data = test_data_generator()

                request_start = time.time()
                try:
                    target_function(test_data)
                    latency = time.time() - request_start
                    latencies.append(latency)
                    self.results["successful_requests"] += 1
                except Exception:
                    failed_count += 1
                    self.results["failed_requests"] += 1

                total_count += 1

            elapsed = time.time() - start_time
            time.sleep(1 / (requests_per_second + 1))

        # Calculate results
        self.results["total_requests"] = total_count
        self.results["error_rate"] = (failed_count / total_count
                                      if total_count > 0 else 0.0)

        if latencies:
            self.results["avg_latency"] = sum(latencies) / len(latencies)
            self.results["max_latency"] = max(latencies)
            self.results["min_latency"] = min(latencies)

        total_time = time.time() - start_time
        self.results["throughput"] = total_count / total_time if total_time > 0 else 0.0

        return self.results


class ChaosEngineer:
    """Chaos engineering for resilience testing"""

    def __init__(self, config: ChaosTestConfig):
        self.config = config
        self.active_failures: List[str] = []
        self.results = {
            "total_injections": 0,
            "total_recoveries": 0,
            "mean_recovery_time": 0.0,
            "failure_events": [],
            "recovery_events": []
        }

    def inject_failure(self, failure_type: str) -> bool:
        """Inject failure into system"""
        if random.random() > self.config.failure_injection_rate:
            return False

        failure_id = f"{failure_type}_{time.time()}"
        self.active_failures.append(failure_id)
        self.results["failure_events"].append({
            "failure_id": failure_id,
            "type": failure_type,
            "timestamp": time.time()
        })
        self.results["total_injections"] += 1

        return True

    def inject_latency(self) -> Optional[float]:
        """Inject latency into request"""
        if random.random() > self.config.latency_injection_rate:
            return None

        latency = random.uniform(
            self.config.latency_range[0],
            self.config.latency_range[1]
        ) / 1000.0  # Convert to seconds

        return latency

    def simulate_network_partition(self) -> bool:
        """Simulate network partition"""
        if random.random() > self.config.partition_probability:
            return False

        return True

    def recover_from_failure(self, failure_id: str) -> float:
        """Recover from failure and measure recovery time"""
        if failure_id in self.active_failures:
            self.active_failures.remove(failure_id)
            self.results["total_recoveries"] += 1

            recovery_event = {
                "failure_id": failure_id,
                "recovery_timestamp": time.time()
            }
            self.results["recovery_events"].append(recovery_event)

            return time.time() - float(failure_id.split("_")[1])

        return 0.0

    def get_chaos_report(self) -> Dict[str, Any]:
        """Get chaos testing report"""
        recovery_times = []
        for recovery_event in self.results["recovery_events"]:
            for failure_event in self.results["failure_events"]:
                if failure_event["failure_id"] == recovery_event["failure_id"]:
                    recovery_time = (recovery_event["recovery_timestamp"] -
                                   failure_event["timestamp"])
                    recovery_times.append(recovery_time)

        if recovery_times:
            self.results["mean_recovery_time"] = sum(recovery_times) / len(recovery_times)

        return self.results


class SecurityTestProcedures:
    """Security testing procedures"""

    def __init__(self):
        self.vulnerabilities_found: List[Dict[str, Any]] = []
        self.security_checks: List[Dict[str, Any]] = []
        self.lock = threading.RLock()

    def test_authentication(self, auth_fn: Callable) -> Dict[str, Any]:
        """Test authentication mechanism"""
        with self.lock:
            results = {
                "test_name": "Authentication",
                "checks": [],
                "vulnerabilities": []
            }

            # Test valid credentials
            try:
                valid = auth_fn("valid_user", "correct_password")
                results["checks"].append({
                    "check": "Valid credentials",
                    "passed": valid
                })
            except Exception as e:
                results["vulnerabilities"].append(f"Auth error: {str(e)}")

            # Test invalid credentials
            try:
                invalid = not auth_fn("invalid_user", "wrong_password")
                results["checks"].append({
                    "check": "Invalid credentials rejected",
                    "passed": invalid
                })
            except Exception as e:
                results["vulnerabilities"].append(f"Auth bypass vulnerability: {str(e)}")

            return results

    def test_injection_attacks(self, function_under_test: Callable) -> Dict[str, Any]:
        """Test for injection vulnerabilities"""
        with self.lock:
            results = {
                "test_name": "Injection Attacks",
                "vulnerabilities": []
            }

            injection_payloads = [
                "'; DROP TABLE users; --",
                "<script>alert('XSS')</script>",
                "${7*7}",
                "$(whoami)"
            ]

            for payload in injection_payloads:
                try:
                    function_under_test(payload)
                    results["vulnerabilities"].append({
                        "type": "Injection Vulnerability",
                        "payload": payload
                    })
                except Exception:
                    pass  # Expected behavior

            return results

    def test_access_control(self, access_fn: Callable,
                           user_roles: Dict[str, List[str]]) -> Dict[str, Any]:
        """Test access control"""
        with self.lock:
            results = {
                "test_name": "Access Control",
                "checks": [],
                "violations": []
            }

            for user, allowed_resources in user_roles.items():
                for resource in allowed_resources:
                    try:
                        can_access = access_fn(user, resource)
                        if not can_access:
                            results["violations"].append(
                                f"User {user} denied access to allowed resource {resource}"
                            )
                    except Exception as e:
                        results["violations"].append(str(e))

            return results
