import random, threading, time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Set, Callable

class FailureMode(Enum):
    TIMEOUT, EXCEPTION, PARTIAL_RESPONSE, CORRUPTED_DATA, MEMORY_LEAK, DEADLOCK, STALE_CACHE, CONNECTION_LOSS = range(8)

class CascadeType(Enum):
    LINEAR, EXPONENTIAL, CHAIN, CONVERGENT = range(4)

@dataclass
class FailureEvent:
    event_id: str
    failure_mode: FailureMode
    component: str
    triggered_at: Optional[float] = None
    resolved_at: Optional[float] = None
    duration_seconds: float = 5.0
    cascades_to: List[str] = field(default_factory=list)
    error_message: str = ""
    def is_active(self): return self.triggered_at and time.time() - self.triggered_at < self.duration_seconds
    def duration_ms(self): return (self.resolved_at - self.triggered_at) * 1000 if self.triggered_at and self.resolved_at else 0.0
    def to_dict(self): return {"event_id": self.event_id, "failure_mode": self.failure_mode.name, "component": self.component, "is_active": self.is_active(), "duration_ms": self.duration_ms(), "cascades_to": self.cascades_to, "error_message": self.error_message}

@dataclass
class CascadingFailure:
    cascade_id: str
    cascade_type: CascadeType
    root_cause: str
    root_failure: FailureEvent
    affected_components: Set[str] = field(default_factory=set)
    events: List[FailureEvent] = field(default_factory=list)
    started_at: Optional[float] = None
    contained_at: Optional[float] = None
    max_depth: int = 0
    def is_contained(self): return self.contained_at is not None
    def cascade_depth(self): return len(self.events)
    def duration_ms(self): return (self.contained_at - self.started_at) * 1000 if self.contained_at and self.started_at else 0.0
    def to_dict(self): return {"cascade_id": self.cascade_id, "cascade_type": self.cascade_type.name, "root_cause": self.root_cause, "affected_components": list(self.affected_components), "events": [e.to_dict() for e in self.events], "is_contained": self.is_contained(), "depth": self.cascade_depth(), "duration_ms": self.duration_ms()}

@dataclass
class FailureScenario:
    scenario_id: str
    name: str
    description: str
    failure_events: List[FailureEvent] = field(default_factory=list)
    cascades: List[CascadingFailure] = field(default_factory=list)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration_seconds: float = 120.0
    enable_cascade: bool = True
    def is_running(self): return self.started_at and time.time() - self.started_at < self.duration_seconds
    def total_failures(self): return len(self.failure_events) + sum(len(c.events) for c in self.cascades)
    def affected_components(self): return {e.component for e in self.failure_events} | {c for cascade in self.cascades for c in cascade.affected_components}
    def to_dict(self): return {"scenario_id": self.scenario_id, "name": self.name, "description": self.description, "is_running": self.is_running(), "total_failures": self.total_failures(), "affected_components": list(self.affected_components()), "cascades": [c.to_dict() for c in self.cascades]}

@dataclass
class FailureSimulationStats:
    total_scenarios: int = 0
    completed_scenarios: int = 0
    total_failures_injected: int = 0
    cascades_detected: int = 0
    max_cascade_depth: int = 0
    avg_cascade_duration_ms: float = 0.0
    total_cascading_failures: int = 0
    contained_cascades: int = 0
    mitigation_success_rate: float = 0.0
    def cascade_containment_rate(self): return (self.contained_cascades / self.cascades_detected * 100) if self.cascades_detected else 0.0
    def to_dict(self): return vars(self)

class FailureSimulator:
    def __init__(self):
        self.scenarios: Dict[str, FailureScenario] = {}
        self.stats = FailureSimulationStats()
        self.lock = threading.RLock()
        self.cascade_callbacks: Dict[CascadeType, List[Callable]] = {}
        self.event_counter = 0
    def register_cascade_handler(self, cascade_type: CascadeType, callback: Callable) -> None:
        with self.lock:
            if cascade_type not in self.cascade_callbacks:
                self.cascade_callbacks[cascade_type] = []
            self.cascade_callbacks[cascade_type].append(callback)
    def create_scenario(self, name: str, description: str, duration_seconds: float = 120.0, enable_cascade: bool = True) -> FailureScenario:
        with self.lock:
            scenario_id = f"scenario_{int(time.time() * 1000)}"
            scenario = FailureScenario(scenario_id=scenario_id, name=name, description=description, duration_seconds=duration_seconds, enable_cascade=enable_cascade)
            self.scenarios[scenario_id] = scenario
            return scenario
    def add_failure_event(self, scenario_id: str, failure_mode: FailureMode, component: str, duration_seconds: float = 5.0, error_message: str = "") -> FailureEvent:
        with self.lock:
            if scenario_id not in self.scenarios:
                raise ValueError(f"Scenario {scenario_id} not found")
            self.event_counter += 1
            event = FailureEvent(event_id=f"event_{self.event_counter}", failure_mode=failure_mode, component=component, duration_seconds=duration_seconds, error_message=error_message)
            self.scenarios[scenario_id].failure_events.append(event)
            return event
    def run_scenario(self, scenario_id: str, failure_callback: Optional[Callable] = None) -> FailureScenario:
        with self.lock:
            if scenario_id not in self.scenarios:
                raise ValueError(f"Scenario {scenario_id} not found")
            scenario = self.scenarios[scenario_id]
            scenario.started_at = time.time()
            self.stats.total_scenarios += 1
        threads = []
        for event in scenario.failure_events:
            thread = threading.Thread(target=self._execute_failure_event, args=(scenario, event, failure_callback), daemon=True)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join(timeout=scenario.duration_seconds + 10)
        with self.lock:
            scenario.completed_at = time.time()
            self.stats.completed_scenarios += 1
            self.stats.total_failures_injected += len(scenario.failure_events)
        return scenario
    def _execute_failure_event(self, scenario: FailureScenario, event: FailureEvent, failure_callback: Optional[Callable] = None) -> None:
        event.triggered_at = time.time()
        if failure_callback:
            try:
                failure_callback(event)
            except:
                pass
        time.sleep(min(event.duration_seconds, 0.5))
        if scenario.enable_cascade and random.random() < 0.3:
            self._create_cascade(scenario, event)
        event.resolved_at = time.time()
    def _create_cascade(self, scenario: FailureScenario, root_event: FailureEvent) -> None:
        with self.lock:
            cascade_type = random.choice(list(CascadeType))
            cascade_id = f"cascade_{int(time.time() * 1000)}"
            cascade = CascadingFailure(cascade_id=cascade_id, cascade_type=cascade_type, root_cause=root_event.component, root_failure=root_event, affected_components={root_event.component})
            cascade.started_at = time.time()
            cascade.max_depth = 3
        depth = 1
        affected = {root_event.component}
        while depth < cascade.max_depth and random.random() < 0.5:
            new_component = f"{root_event.component}_cascade_{depth}"
            affected.add(new_component)
            event = FailureEvent(event_id=f"event_{int(time.time() * 1000)}_{depth}", failure_mode=random.choice(list(FailureMode)), component=new_component, duration_seconds=2.0, error_message=f"Cascade from {root_event.component}")
            cascade.events.append(event)
            depth += 1
            time.sleep(0.2)
        cascade.contained_at = time.time()
        cascade.affected_components = affected
        with self.lock:
            scenario.cascades.append(cascade)
            self.stats.cascades_detected += 1
            self.stats.max_cascade_depth = max(self.stats.max_cascade_depth, depth)
            self.stats.contained_cascades += 1
        for cb in self.cascade_callbacks.get(cascade_type, []):
            try:
                cb(cascade)
            except:
                pass
    def get_scenario_results(self, scenario_id: str) -> Dict[str, Any]:
        with self.lock:
            if scenario_id not in self.scenarios:
                return {}
            scenario = self.scenarios[scenario_id]
            return {"scenario": scenario.to_dict(), "failure_events": [e.to_dict() for e in scenario.failure_events], "cascades": [c.to_dict() for c in scenario.cascades]}
    def get_stats(self) -> FailureSimulationStats:
        return self.stats
