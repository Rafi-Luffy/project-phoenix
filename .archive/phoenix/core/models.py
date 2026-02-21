"""
Core Data Models - Foundation for Autonomous Self-Healing System
Module 1.1: Foundation Setup - Database schema design
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
import json
from abc import ABC, abstractmethod


class ComponentState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    RECOVERING = "recovering"
    RECOVERED = "recovered"
    UNKNOWN = "unknown"


class ActionType(Enum):
    RESTART = "restart"
    FAILOVER = "failover"
    REBALANCE = "rebalance"
    CIRCUIT_BREAK = "circuit_break"
    REDUCE_LOAD = "reduce_load"
    ROLLBACK = "rollback"
    ISOLATE = "isolate"
    HEAL = "heal"
    MONITOR = "monitor"


class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


@dataclass
class Component:
    """Represents a system component being monitored"""
    name: str
    component_type: str
    state: ComponentState = ComponentState.UNKNOWN
    last_checked: datetime = field(default_factory=datetime.now)
    health_score: float = 1.0
    error_count: int = 0
    recovery_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'type': self.component_type,
            'state': self.state.value,
            'last_checked': self.last_checked.isoformat(),
            'health_score': self.health_score,
            'error_count': self.error_count,
            'recovery_count': self.recovery_count,
            'metadata': self.metadata
        }


@dataclass
class HealthMetric:
    """Represents a single health measurement"""
    component_name: str
    metric_name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    threshold_warning: float = 0.7
    threshold_critical: float = 0.3

    def is_healthy(self) -> bool:
        return self.value >= self.threshold_warning

    def is_critical(self) -> bool:
        return self.value < self.threshold_critical

    def to_dict(self) -> Dict:
        return {
            'component': self.component_name,
            'metric': self.metric_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'status': 'healthy' if self.is_healthy() else 'critical' if self.is_critical() else 'warning'
        }


@dataclass
class Failure:
    """Represents a detected failure event"""
    failure_id: str
    component_name: str
    failure_type: str
    severity: int  # 1-10
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    root_cause: Optional[str] = None
    related_metrics: List[str] = field(default_factory=list)
    detected_by: str = "anomaly_detector"

    def to_dict(self) -> Dict:
        return {
            'failure_id': self.failure_id,
            'component': self.component_name,
            'type': self.failure_type,
            'severity': self.severity,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'root_cause': self.root_cause,
            'related_metrics': self.related_metrics,
            'detected_by': self.detected_by
        }


@dataclass
class RecoveryAction:
    """Represents an automated recovery action"""
    action_id: str
    failure_id: str
    action_type: ActionType
    target_component: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    executed: bool = False
    execution_time: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    decision_rationale: str = ""

    def to_dict(self) -> Dict:
        return {
            'action_id': self.action_id,
            'failure_id': self.failure_id,
            'action_type': self.action_type.value,
            'target': self.target_component,
            'parameters': self.parameters,
            'timestamp': self.timestamp.isoformat(),
            'executed': self.executed,
            'execution_time': self.execution_time,
            'success': self.success,
            'error': self.error_message,
            'rationale': self.decision_rationale
        }


@dataclass
class Memory:
    """Represents stored memory in the system"""
    memory_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'memory_id': self.memory_id,
            'type': self.memory_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'relevance': self.relevance_score,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat(),
            'tags': self.tags
        }


@dataclass
class DecisionContext:
    """Context for decision making"""
    failure: Failure
    component_state: Component
    historical_actions: List[RecoveryAction]
    similar_past_failures: List[Failure]
    available_actions: List[ActionType]
    system_load: float
    confidence_threshold: float = 0.75

    def to_dict(self) -> Dict:
        return {
            'failure': self.failure.to_dict(),
            'component': self.component_state.to_dict(),
            'history_size': len(self.historical_actions),
            'similar_failures': len(self.similar_past_failures),
            'available_actions': [a.value for a in self.available_actions],
            'system_load': self.system_load
        }


@dataclass
class Correction:
    """Represents a correction/refinement action"""
    correction_id: str
    related_action_id: str
    correction_type: str  # "rule_based", "ml_based", "hybrid"
    original_decision: str
    corrected_decision: str
    confidence: float
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    applied: bool = False

    def to_dict(self) -> Dict:
        return {
            'correction_id': self.correction_id,
            'action_id': self.related_action_id,
            'type': self.correction_type,
            'original': self.original_decision,
            'corrected': self.corrected_decision,
            'confidence': self.confidence,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'applied': self.applied
        }


@dataclass
class LearningRecord:
    """Records learned pattern for future use"""
    record_id: str
    pattern_type: str  # "failure_pattern", "recovery_pattern", "causality"
    pattern_description: str
    effectiveness_score: float  # 0-1, how effective this pattern was
    applications: int = 0
    success_count: int = 0
    failure_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0

    def to_dict(self) -> Dict:
        return {
            'record_id': self.record_id,
            'pattern_type': self.pattern_type,
            'description': self.pattern_description,
            'effectiveness': self.effectiveness_score,
            'success_rate': self.success_rate(),
            'applications': self.applications,
            'metadata': self.metadata
        }


@dataclass
class AgentMessage:
    """Message passed between agents"""
    message_id: str
    sender_agent: str
    recipient_agent: str
    message_type: str  # "request", "response", "notification", "consensus"
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 5  # 1-10, higher is more urgent
    requires_response: bool = False
    response_deadline: Optional[float] = None  # seconds
    retry_count: int = 0

    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'from': self.sender_agent,
            'to': self.recipient_agent,
            'type': self.message_type,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority
        }


@dataclass
class CollaborationSession:
    """Represents a multi-agent collaboration session"""
    session_id: str
    agents_involved: List[str]
    task: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "active"  # "active", "completed", "failed"
    messages: List[AgentMessage] = field(default_factory=list)
    consensus_reached: bool = False
    result: Optional[Dict[str, Any]] = None

    def duration_seconds(self) -> float:
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def to_dict(self) -> Dict:
        return {
            'session_id': self.session_id,
            'agents': self.agents_involved,
            'task': self.task,
            'status': self.status,
            'duration': self.duration_seconds(),
            'consensus': self.consensus_reached,
            'message_count': len(self.messages)
        }


class PersistentStore(ABC):
    """Abstract interface for persistent storage"""

    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        pass

    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def list_keys(self, pattern: str = "*") -> List[str]:
        pass

    @abstractmethod
    def query(self, query: str) -> List[Any]:
        pass


# Test-Compatible Models (dataclass-based for Python 3.13 compatibility)


class FailureType(str, Enum):
    TEST_FAILURE = "test_failure"
    ASSERTION_ERROR = "assertion_error"
    EXCEPTION = "exception"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    UNKNOWN = "unknown"


class BugType(str, Enum):
    LOGIC_ERROR = "logic_error"
    OFF_BY_ONE = "off_by_one"
    NULL_POINTER = "null_pointer"
    TYPE_ERROR = "type_error"
    CONCURRENCY_BUG = "concurrency_bug"
    MEMORY_LEAK = "memory_leak"
    UNKNOWN = "unknown"


class ValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    PENDING = "pending"
    FIXED = "fixed"
    SUCCESS = "success"


class RemediationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class FailureEvent:
    project_id: UUID
    test_name: str
    failure_type: FailureType
    error_message: str
    stack_trace: str
    files_implicated: List[str] = field(default_factory=list)
    lines_implicated: Dict[str, List[int]] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    severity: int = 5


@dataclass
class DiagnosticReport:
    report_id: UUID = field(default_factory=lambda: UUID(int=0))
    failure_event_id: UUID = field(default_factory=lambda: UUID(int=0))
    explanation: str = ""
    bug_type: Optional[BugType] = None
    suspected_cause: str = ""
    confidence_score: float = 0.5
    recommendation: str = ""
    root_cause: str = ""
    recommended_strategy: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Patch:
    patch_id: UUID = field(default_factory=lambda: UUID(int=0))
    remediation_attempt_id: UUID = field(default_factory=lambda: UUID(int=0))
    file_path: str = ""
    target_lines: List[int] = field(default_factory=list)
    original_code: str = ""
    original_content: str = ""
    patched_code: str = ""
    patched_content: str = ""
    diff: str = ""
    description: str = ""
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    result_id: UUID = field(default_factory=lambda: UUID(int=0))
    patch_id: UUID = field(default_factory=lambda: UUID(int=0))
    validation_status: ValidationStatus = ValidationStatus.UNKNOWN
    status: ValidationStatus = ValidationStatus.UNKNOWN
    test_results: Dict[str, bool] = field(default_factory=dict)
    coverage: float = 0.0
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class RemediationAttempt:
    attempt_id: UUID = field(default_factory=lambda: UUID(int=0))
    failure_event: Optional[FailureEvent] = None
    diagnostic_report: Optional[DiagnosticReport] = None
    patch: Optional[Patch] = None
    validation_result: Optional[ValidationResult] = None
    status: RemediationStatus = RemediationStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Project:
    project_id: UUID = field(default_factory=lambda: UUID(int=0))
    name: str = ""
    description: str = ""
    local_path: str = ""
    repository_url: str = ""
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperienceRecord:
    record_id: UUID = field(default_factory=lambda: UUID(int=0))
    failure_type: Optional[FailureType] = None
    bug_type: Optional[BugType] = None
    remediation: Optional[RemediationAttempt] = None
    success: bool = False
    lessons_learned: str = ""
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PhoenixConfig:
    """Configuration for Phoenix system"""
    debug: bool = False
    log_level: str = "INFO"
    max_retries: int = 3
    timeout_seconds: int = 30
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    default_llm_provider: str = "openai"
    critic_model: str = "gpt-4"
    programmer_model: str = "gpt-4"
    observer_model: str = "gpt-3.5-turbo"
    validator_model: str = "gpt-3.5-turbo"


@dataclass
class Settings:
    """Settings for Phoenix"""
    app_name: str = "Project Phoenix"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
