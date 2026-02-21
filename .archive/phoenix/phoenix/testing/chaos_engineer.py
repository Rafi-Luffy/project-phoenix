import threading, time, random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Callable

class FailureType(Enum):
    LLM_FAILURE, TIMEOUT, RESOURCE_EXHAUSTION, CASCADE_FAILURE, INTERMITTENT, PARTIAL, NETWORK, DATABASE = range(8)

class RecoveryStrategy(Enum):
    AUTO_RECOVERY, FALLBACK, RETRY, CIRCUIT_BREAK, MANUAL = range(5)

@dataclass
class FailureInjection:
    failure_type: FailureType
    component: str
    duration_seconds: float
    severity: float
    recovery_strategy: RecoveryStrategy
    created_at: float = field(default_factory=time.time)
    triggered_at: Optional[float] = None
    resolved_at: Optional[float] = None
    def is_active(self) -> bool:
        return self.triggered_at and time.time() - self.triggered_at < self.duration_seconds
    def duration_ms(self): return (self.resolved_at - self.triggered_at) * 1000 if self.triggered_at and self.resolved_at else 0
    def to_dict(self): return {"failure_type": self.failure_type.name, "component": self.component, "duration_seconds": self.duration_seconds, "severity": self.severity, "recovery_strategy": self.recovery_strategy.name, "is_active": self.is_active(), "duration_ms": self.duration_ms()}

@dataclass
class ChaosScenario:
    name: str
    description: str
    injections: List[FailureInjection] = field(default_factory=list)
    duration_seconds: float = 60.0
    concurrent_failures: int = 1
    expected_recovery_time_seconds: float = 30.0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    def total_injections(self): return len(self.injections)
    def active_failures(self): return sum(1 for inj in self.injections if inj.is_active())
    def is_running(self): return self.started_at and time.time() - self.started_at < self.duration_seconds
    def to_dict(self): return {"name": self.name, "description": self.description, "total_injections": self.total_injections(), "active_failures": self.active_failures(), "is_running": self.is_running(), "concurrent_limit": self.concurrent_failures}

@dataclass
class RecoveryResult:
    failure_injection: FailureInjection
    recovered: bool
    recovery_time_seconds: float
    recovery_strategy_used: RecoveryStrategy
    error: Optional[str] = None
    recovery_attempts: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return {"failure_type": self.failure_injection.failure_type.name, "component": self.failure_injection.component, "recovered": self.recovered, "recovery_time_seconds": self.recovery_time_seconds, "recovery_strategy": self.recovery_strategy_used.name}

@dataclass
class ChaosStats:
    total_scenarios: int = 0
    completed_scenarios: int = 0
    failures_injected: int = 0
    failures_recovered: int = 0
    recovery_failures: int = 0
    avg_recovery_time_seconds: float = 0.0
    def recovery_rate(self): return (self.failures_recovered / self.failures_injected * 100) if self.failures_injected else 0.0
    def to_dict(self): return vars(self)

class ChaosEngineer:
    def __init__(self):
        self.scenarios: Dict[str, ChaosScenario] = {}
        self.active_injections: Dict[str, FailureInjection] = {}
        self.recovery_results: List[RecoveryResult] = []
        self.stats = ChaosStats()
        self.lock = threading.RLock()
        self.failure_callbacks: Dict[FailureType, List[Callable]] = {}
    def register_failure_handler(self, failure_type: FailureType, callback: Callable) -> None:
        with self.lock:
            if failure_type not in self.failure_callbacks:
                self.failure_callbacks[failure_type] = []
            self.failure_callbacks[failure_type].append(callback)
    def create_scenario(self, name: str, description: str, duration_seconds: float = 60.0, concurrent_failures: int = 1) -> ChaosScenario:
        with self.lock:
            scenario = ChaosScenario(name=name, description=description, duration_seconds=duration_seconds, concurrent_failures=concurrent_failures)
            self.scenarios[name] = scenario
            return scenario
    def inject_failure(self, scenario_name: str, failure_type: FailureType, component: str, duration_seconds: float = 5.0, severity: float = 1.0, recovery_strategy: RecoveryStrategy = RecoveryStrategy.AUTO_RECOVERY) -> FailureInjection:
        with self.lock:
            if scenario_name not in self.scenarios:
                raise ValueError(f"Scenario {scenario_name} not found")
            scenario = self.scenarios[scenario_name]
            injection = FailureInjection(failure_type=failure_type, component=component, duration_seconds=duration_seconds, severity=severity, recovery_strategy=recovery_strategy)
            scenario.injections.append(injection)
            return injection
    def run_scenario(self, scenario_name: str, callback: Optional[Callable] = None) -> ChaosScenario:
        with self.lock:
            if scenario_name not in self.scenarios:
                raise ValueError(f"Scenario {scenario_name} not found")
            scenario = self.scenarios[scenario_name]
            scenario.started_at = time.time()
            self.stats.total_scenarios += 1
        threads = []
        for injection in scenario.injections:
            thread = threading.Thread(target=self._execute_injection, args=(injection, scenario, callback), daemon=True)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join(timeout=scenario.duration_seconds + 10)
        with self.lock:
            scenario.completed_at = time.time()
            self.stats.completed_scenarios += 1
        return scenario
    def _execute_injection(self, injection: FailureInjection, scenario: ChaosScenario, callback: Optional[Callable] = None) -> None:
        with self.lock:
            while len([i for i in self.active_injections.values() if i.is_active()]) >= scenario.concurrent_failures:
                time.sleep(0.1)
            self.active_injections[f"{injection.component}_{int(time.time() * 1000)}"] = injection
        injection.triggered_at = time.time()
        self.stats.failures_injected += 1
        for cb in self.failure_callbacks.get(injection.failure_type, []):
            try: cb(injection)
            except: pass
        time.sleep(min(injection.duration_seconds, 0.5))
        recovery_result = self._recover_from_failure(injection)
        self.recovery_results.append(recovery_result)
        if recovery_result.recovered:
            self.stats.failures_recovered += 1
        else:
            self.stats.recovery_failures += 1
        injection.resolved_at = time.time()
        if recovery_result.recovery_time_seconds > 0:
            total_time = sum(r.recovery_time_seconds for r in self.recovery_results if r.recovery_time_seconds > 0)
            count = sum(1 for r in self.recovery_results if r.recovery_time_seconds > 0)
            if count > 0:
                self.stats.avg_recovery_time_seconds = total_time / count
        if callback:
            callback(injection, recovery_result)
    def _recover_from_failure(self, injection: FailureInjection) -> RecoveryResult:
        recovery_start = time.time()
        recovered = random.random() < 0.8
        attempts = 1
        recovery_time = time.time() - recovery_start
        return RecoveryResult(failure_injection=injection, recovered=recovered, recovery_time_seconds=recovery_time, recovery_strategy_used=injection.recovery_strategy, error=None, recovery_attempts=attempts)
    def get_scenario_results(self, scenario_name: str) -> Dict[str, Any]:
        with self.lock:
            if scenario_name not in self.scenarios:
                return {}
            scenario = self.scenarios[scenario_name]
            relevant_results = [r for r in self.recovery_results if any(inj.component in r.failure_injection.component for inj in scenario.injections)]
            return {"scenario": scenario.to_dict(), "recovery_results": [r.to_dict() for r in relevant_results], "total_recovered": sum(1 for r in relevant_results if r.recovered), "total_failed": sum(1 for r in relevant_results if not r.recovered)}
    def get_stats(self) -> ChaosStats:
        return self.stats
