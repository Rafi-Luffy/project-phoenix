"""
AUTONOMOUS SELF-HEALING SYSTEM - Project Phoenix
Continuously monitors, detects failures, and autonomously heals the system
"""

import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Tuple, Callable, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json


class HealthStatus(Enum):
    """Component health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class SystemState(Enum):
    """Overall system states"""
    HEALTHY = "healthy"
    DETECTING_FAILURE = "detecting_failure"
    HEALING_IN_PROGRESS = "healing_in_progress"
    RECOVERED = "recovered"
    CRITICAL = "critical"


@dataclass
class HealthMetric:
    """Single health metric"""
    name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    timestamp: float = field(default_factory=time.time)
    
    def get_status(self) -> HealthStatus:
        if self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        elif self.value >= self.threshold_warning:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY


@dataclass
class ComponentHealth:
    """Health status of a single component"""
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    metrics: Dict[str, HealthMetric] = field(default_factory=dict)
    last_check: float = field(default_factory=time.time)
    failure_count: int = 0
    recovery_count: int = 0
    last_failure_time: Optional[float] = None
    last_recovery_time: Optional[float] = None
    
    def update_metric(self, metric: HealthMetric):
        self.metrics[metric.name] = metric
        # Update overall status based on metrics
        statuses = [m.get_status() for m in self.metrics.values()]
        if HealthStatus.CRITICAL in statuses:
            self.status = HealthStatus.CRITICAL
        elif HealthStatus.DEGRADED in statuses:
            self.status = HealthStatus.DEGRADED
        else:
            self.status = HealthStatus.HEALTHY
    
    def mark_failed(self):
        self.status = HealthStatus.CRITICAL
        self.failure_count += 1
        self.last_failure_time = time.time()
    
    def mark_recovered(self):
        self.status = HealthStatus.HEALTHY
        self.recovery_count += 1
        self.last_recovery_time = time.time()


class HealthMonitor:
    """Continuously monitors component health"""
    
    def __init__(self, check_interval_ms: int = 100):
        self.check_interval = check_interval_ms / 1000.0
        self.components: Dict[str, ComponentHealth] = {}
        self.health_checks: Dict[str, Callable] = {}
        self.last_check_time = 0
        self.check_history: Dict[str, List[Tuple[float, HealthStatus]]] = defaultdict(list)
    
    def register_component(self, name: str, health_check: Callable):
        """Register a component with its health check function"""
        self.components[name] = ComponentHealth(name=name)
        self.health_checks[name] = health_check
    
    def check_health(self) -> Dict[str, ComponentHealth]:
        """Run all health checks"""
        current_time = time.time()
        
        # Only check if interval passed
        if current_time - self.last_check_time < self.check_interval:
            return self.components
        
        self.last_check_time = current_time
        
        for component_name, health_check_fn in self.health_checks.items():
            try:
                metrics = health_check_fn()  # Returns dict of HealthMetric
                component = self.components[component_name]
                
                for metric_name, metric in metrics.items():
                    component.update_metric(metric)
                
                component.last_check = current_time
                
                # Track history
                self.check_history[component_name].append(
                    (current_time, component.status)
                )
                # Keep last 100 checks
                if len(self.check_history[component_name]) > 100:
                    self.check_history[component_name].pop(0)
                    
            except Exception as e:
                self.components[component_name].mark_failed()
        
        return self.components
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        health = self.check_health()
        
        statuses = [c.status for c in health.values()]
        
        if HealthStatus.CRITICAL in statuses:
            system_status = HealthStatus.CRITICAL
        elif HealthStatus.DEGRADED in statuses:
            system_status = HealthStatus.DEGRADED
        else:
            system_status = HealthStatus.HEALTHY
        
        return {
            "system_status": system_status,
            "components": {
                name: {
                    "status": comp.status.value,
                    "failure_count": comp.failure_count,
                    "recovery_count": comp.recovery_count,
                    "metrics": {
                        mname: {
                            "value": m.value,
                            "status": m.get_status().value
                        }
                        for mname, m in comp.metrics.items()
                    }
                }
                for name, comp in health.items()
            }
        }


class FailureDetector:
    """Detects failures with confidence scoring"""
    
    def __init__(self, consecutive_failures_threshold: int = 3):
        self.threshold = consecutive_failures_threshold
        self.failure_streak: Dict[str, int] = defaultdict(int)
        self.detected_failures: List[Dict[str, Any]] = []
        self.last_detection_time: Dict[str, float] = {}
    
    def detect_failures(self, health: Dict[str, ComponentHealth]) -> List[Dict[str, Any]]:
        """Detect failures from health checks"""
        failures = []
        current_time = time.time()
        
        for component_name, component_health in health.items():
            if component_health.status == HealthStatus.CRITICAL:
                self.failure_streak[component_name] += 1
                
                # Only report after threshold
                if self.failure_streak[component_name] >= self.threshold:
                    time_since_last = current_time - self.last_detection_time.get(component_name, 0)
                    
                    # Only report if sufficient time passed (avoid duplicate reports)
                    if time_since_last > 0.5:  # 500ms minimum
                        failure = {
                            "component": component_name,
                            "severity": "critical",
                            "confidence": min(
                                1.0,
                                self.failure_streak[component_name] / self.threshold
                            ),
                            "detected_at": current_time,
                            "metrics": {
                                name: {
                                    "value": metric.value,
                                    "threshold": metric.threshold_critical
                                }
                                for name, metric in component_health.metrics.items()
                            }
                        }
                        failures.append(failure)
                        self.detected_failures.append(failure)
                        self.last_detection_time[component_name] = current_time
            else:
                # Reset streak if healthy
                self.failure_streak[component_name] = 0
        
        return failures


class RecoveryAction:
    """Represents a recovery action"""
    
    def __init__(self, name: str, description: str, executor: Callable, timeout_sec: float = 5.0):
        self.name = name
        self.description = description
        self.executor = executor
        self.timeout_sec = timeout_sec
        self.execution_time: Optional[float] = None
        self.success: Optional[bool] = None
        self.error_message: Optional[str] = None
    
    def execute(self) -> bool:
        """Execute the recovery action"""
        start_time = time.time()
        try:
            result = self.executor()
            self.execution_time = time.time() - start_time
            self.success = result if isinstance(result, bool) else True
            return self.success
        except Exception as e:
            self.execution_time = time.time() - start_time
            self.success = False
            self.error_message = str(e)
            return False


class DecisionEngine:
    """Decides which recovery actions to take"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, List[RecoveryAction]] = {}
        self.action_history: List[Dict[str, Any]] = []
        self.recovery_success_rate: Dict[str, float] = {}
    
    def register_strategy(self, component_name: str, actions: List[RecoveryAction]):
        """Register recovery strategy for a component"""
        self.recovery_strategies[component_name] = actions
    
    def decide_recovery(self, failure: Dict[str, Any]) -> List[RecoveryAction]:
        """Decide which recovery actions to execute"""
        component = failure["component"]
        
        if component not in self.recovery_strategies:
            return []
        
        # Return all registered actions for this component
        return self.recovery_strategies[component]
    
    def track_action_execution(self, component: str, action: RecoveryAction, success: bool):
        """Track action execution for learning"""
        self.action_history.append({
            "component": component,
            "action": action.name,
            "success": success,
            "execution_time": action.execution_time,
            "timestamp": time.time()
        })
        
        # Update success rate
        key = f"{component}:{action.name}"
        recent_actions = [a for a in self.action_history 
                         if a["component"] == component and a["action"] == action.name]
        
        if recent_actions:
            success_count = sum(1 for a in recent_actions if a["success"])
            self.recovery_success_rate[key] = success_count / len(recent_actions)


class StateManager:
    """Tracks system state transitions"""
    
    def __init__(self):
        self.current_state = SystemState.HEALTHY
        self.state_history: List[Tuple[float, SystemState]] = []
        self.transition_count: Dict[Tuple[SystemState, SystemState], int] = defaultdict(int)
        self.state_entry_time = time.time()
    
    def transition_to(self, new_state: SystemState) -> bool:
        """Transition to new state"""
        if new_state == self.current_state:
            return False
        
        current_time = time.time()
        time_in_state = current_time - self.state_entry_time
        
        self.state_history.append((current_time, new_state))
        self.transition_count[(self.current_state, new_state)] += 1
        
        self.current_state = new_state
        self.state_entry_time = current_time
        
        return True
    
    def get_state_timeline(self, last_n: int = 50) -> List[Dict[str, Any]]:
        """Get state transition history"""
        return [
            {
                "timestamp": ts,
                "state": state.value,
                "unix_time": ts
            }
            for ts, state in self.state_history[-last_n:]
        ]


class MetricsCollector:
    """Collects recovery metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "total_failures_detected": 0,
            "total_healings_attempted": 0,
            "total_healings_successful": 0,
            "total_healings_failed": 0,
            "average_detection_time": 0,
            "average_recovery_time": 0,
            "mttr": 0,  # Mean Time To Recovery
            "component_metrics": defaultdict(dict)
        }
        self.detection_times: List[float] = []
        self.recovery_times: List[float] = []
    
    def record_failure_detected(self, detection_time: float):
        self.metrics["total_failures_detected"] += 1
        self.detection_times.append(detection_time)
        
        if self.detection_times:
            self.metrics["average_detection_time"] = sum(self.detection_times) / len(self.detection_times)
    
    def record_healing_attempt(self, component: str, success: bool, recovery_time: float):
        self.metrics["total_healings_attempted"] += 1
        
        if success:
            self.metrics["total_healings_successful"] += 1
        else:
            self.metrics["total_healings_failed"] += 1
        
        self.recovery_times.append(recovery_time)
        
        if self.recovery_times:
            self.metrics["average_recovery_time"] = sum(self.recovery_times) / len(self.recovery_times)
            self.metrics["mttr"] = sum(self.recovery_times) / len(self.recovery_times)
        
        # Per-component metrics
        if component not in self.metrics["component_metrics"]:
            self.metrics["component_metrics"][component] = {
                "attempts": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0
            }
        
        comp_metric = self.metrics["component_metrics"][component]
        comp_metric["attempts"] += 1
        
        if success:
            comp_metric["successful"] += 1
        else:
            comp_metric["failed"] += 1
        
        comp_metric["success_rate"] = comp_metric["successful"] / comp_metric["attempts"]
    
    def get_metrics(self) -> Dict[str, Any]:
        return dict(self.metrics)


class AutoHealer:
    """Main autonomous self-healing orchestrator"""
    
    def __init__(self, check_interval_ms: int = 100):
        self.monitor = HealthMonitor(check_interval_ms)
        self.failure_detector = FailureDetector()
        self.decision_engine = DecisionEngine()
        self.state_manager = StateManager()
        self.metrics_collector = MetricsCollector()
        
        self.healing_in_progress: Dict[str, bool] = {}
        self.active = False
        self.healing_log: List[Dict[str, Any]] = []
    
    def register_component(self, name: str, health_check: Callable):
        """Register a component to monitor"""
        self.monitor.register_component(name, health_check)
        self.healing_in_progress[name] = False
    
    def register_recovery_strategy(self, component_name: str, actions: List[RecoveryAction]):
        """Register recovery strategy for a component"""
        self.decision_engine.register_strategy(component_name, actions)
    
    def start(self):
        """Start autonomous healing"""
        self.active = True
        self.state_manager.transition_to(SystemState.HEALTHY)
    
    def stop(self):
        """Stop autonomous healing"""
        self.active = False
    
    def run_one_cycle(self) -> Dict[str, Any]:
        """Run one healing cycle"""
        if not self.active:
            return {"status": "inactive"}
        
        cycle_start = time.time()
        cycle_log = {
            "timestamp": cycle_start,
            "failures_detected": 0,
            "healing_actions": [],
            "state_transitions": [],
            "system_health": None
        }
        
        # Phase 1: Check health
        health = self.monitor.check_health()
        cycle_log["system_health"] = self.monitor.get_system_health()
        
        # Phase 2: Detect failures
        failures = self.failure_detector.detect_failures(health)
        cycle_log["failures_detected"] = len(failures)
        
        if failures:
            self.state_manager.transition_to(SystemState.DETECTING_FAILURE)
            cycle_log["state_transitions"].append(SystemState.DETECTING_FAILURE.value)
            
            for failure in failures:
                # Phase 3: Decide recovery
                detection_time = failure["detected_at"]
                self.metrics_collector.record_failure_detected(detection_time)
                
                # Phase 4: Execute recovery
                actions = self.decision_engine.decide_recovery(failure)
                component = failure["component"]
                
                if actions and not self.healing_in_progress[component]:
                    self.healing_in_progress[component] = True
                    self.state_manager.transition_to(SystemState.HEALING_IN_PROGRESS)
                    cycle_log["state_transitions"].append(SystemState.HEALING_IN_PROGRESS.value)
                    
                    healing_start = time.time()
                    
                    for action in actions:
                        action_result = {
                            "component": component,
                            "action": action.name,
                            "description": action.description,
                            "executed": action.execute(),
                            "execution_time": action.execution_time,
                            "error": action.error_message
                        }
                        
                        cycle_log["healing_actions"].append(action_result)
                        
                        # Track in decision engine
                        self.decision_engine.track_action_execution(
                            component,
                            action,
                            action_result["executed"]
                        )
                        
                        # Track in metrics
                        healing_time = time.time() - healing_start
                        self.metrics_collector.record_healing_attempt(
                            component,
                            action_result["executed"],
                            healing_time
                        )
                    
                    self.healing_in_progress[component] = False
                    
                    # Check if recovered
                    health = self.monitor.check_health()
                    if health[component].status == HealthStatus.HEALTHY:
                        self.state_manager.transition_to(SystemState.RECOVERED)
                        cycle_log["state_transitions"].append(SystemState.RECOVERED.value)
                        health[component].mark_recovered()
        else:
            # No failures
            if self.state_manager.current_state != SystemState.HEALTHY:
                self.state_manager.transition_to(SystemState.HEALTHY)
                cycle_log["state_transitions"].append(SystemState.HEALTHY.value)
        
        cycle_log["execution_time"] = time.time() - cycle_start
        self.healing_log.append(cycle_log)
        
        # Keep last 1000 cycles
        if len(self.healing_log) > 1000:
            self.healing_log.pop(0)
        
        return cycle_log
    
    def run_continuous(self, duration_seconds: float = 10):
        """Run healing for specified duration"""
        self.start()
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            self.run_one_cycle()
            time.sleep(0.01)  # Small sleep to avoid busy-waiting
        
        self.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "state": self.state_manager.current_state.value,
            "health": self.monitor.get_system_health(),
            "metrics": self.metrics_collector.get_metrics(),
            "state_history": self.state_manager.get_state_timeline(20),
            "recent_logs": self.healing_log[-10:]
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Get comprehensive system report"""
        return {
            "current_state": self.state_manager.current_state.value,
            "system_health": self.monitor.get_system_health(),
            "metrics": self.metrics_collector.get_metrics(),
            "total_cycles": len(self.healing_log),
            "state_transitions": self.state_manager.get_state_timeline(),
            "recovery_strategies": {
                comp: [action.name for action in actions]
                for comp, actions in self.decision_engine.recovery_strategies.items()
            },
            "action_success_rates": self.decision_engine.recovery_success_rate,
            "recent_healing_log": self.healing_log[-20:]
        }


# Example usage functions
def create_auto_healer() -> AutoHealer:
    """Create and configure an AutoHealer instance"""
    healer = AutoHealer(check_interval_ms=100)
    return healer
