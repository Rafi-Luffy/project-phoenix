"""
Core data models for Project Phoenix
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# ============= Enums =============

class SystemStatus(str, Enum):
    """System health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class EventType(str, Enum):
    """Types of detected events"""
    METRIC_ANOMALY = "metric_anomaly"
    LOG_ERROR = "log_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    AVAILABILITY_LOSS = "availability_loss"
    SECURITY_THREAT = "security_threat"
    CUSTOM = "custom"


class EventSeverity(str, Enum):
    """Event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CorrectionStatus(str, Enum):
    """Status of correction attempts"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


# ============= System Models =============

class SystemMetrics(BaseModel):
    """System performance metrics"""
    cpu_usage: float = Field(..., ge=0, le=100)
    memory_usage: float = Field(..., ge=0, le=100)
    disk_usage: float = Field(..., ge=0, le=100)
    network_latency: float = Field(..., ge=0)
    error_rate: float = Field(..., ge=0, le=100)
    request_rate: int = Field(..., ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "cpu_usage": 45.5,
                "memory_usage": 62.3,
                "disk_usage": 78.9,
                "network_latency": 25.4,
                "error_rate": 0.5,
                "request_rate": 1500
            }
        }


class SystemRegister(BaseModel):
    """Register a new system to monitor"""
    name: str = Field(..., min_length=1)
    type: str = Field(..., description="System type: kubernetes, microservice, database, etc")
    endpoint: str = Field(..., description="API endpoint or connection string")
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)


class SystemResponse(SystemRegister):
    """System response with ID and metadata"""
    id: str
    status: SystemStatus = SystemStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ============= Event Models =============

class EventDetected(BaseModel):
    """Event detected by monitoring system"""
    system_id: str
    event_type: EventType
    severity: EventSeverity
    title: str
    description: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class EventResponse(EventDetected):
    """Event response with ID and timestamps"""
    id: str
    detected_at: datetime
    created_at: datetime


# ============= Policy Models =============

class PolicyCondition(BaseModel):
    """Condition for policy trigger"""
    metric: str = Field(..., description="Metric name to evaluate")
    operator: str = Field(..., description="Comparison operator: >, <, >=, <=, ==, !=")
    threshold: float = Field(...)
    duration: int = Field(..., description="Duration in seconds condition must be true")


class PolicyAction(BaseModel):
    """Action to execute when policy is triggered"""
    type: str = Field(..., description="Action type: restart, scale, rollback, webhook, etc")
    target: str = Field(..., description="Target resource or service")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = Field(default=False, description="Execute in dry-run mode first")


class PolicyCreate(BaseModel):
    """Create a new correction policy"""
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    system_id: str
    enabled: bool = Field(default=True)
    conditions: List[PolicyCondition] = Field(...)
    actions: List[PolicyAction] = Field(...)
    priority: int = Field(default=5, ge=1, le=10)


class PolicyResponse(PolicyCreate):
    """Policy response with ID and metadata"""
    id: str
    created_at: datetime
    updated_at: datetime
    executions: int = Field(default=0)


# ============= Correction Models =============

class CorrectionAttempt(BaseModel):
    """Correction attempt log"""
    event_id: str
    policy_id: str
    system_id: str
    action_type: str
    target: str
    parameters: Dict[str, Any]
    dry_run: bool = False
    status: CorrectionStatus = CorrectionStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CorrectionResponse(CorrectionAttempt):
    """Correction response with ID and timestamps"""
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


# ============= Learning Models =============

class LearningOutcome(BaseModel):
    """Learning outcome from correction"""
    event_type: EventType
    root_cause: str
    correction_strategy: str
    success_rate: float = Field(..., ge=0, le=100)
    average_duration_ms: int
    last_updated: datetime


class PatternMatch(BaseModel):
    """Similar pattern match from historical data"""
    pattern_id: str
    similarity_score: float = Field(..., ge=0, le=100)
    recommended_action: str
    historical_success_rate: float = Field(..., ge=0, le=100)


# ============= Metrics Models =============

class MetricsSnapshot(BaseModel):
    """Snapshot of system metrics"""
    timestamp: datetime
    system_id: str
    metrics: SystemMetrics
    anomaly_detected: bool = False
    anomaly_score: Optional[float] = None


class PerformanceMetrics(BaseModel):
    """System-wide performance metrics"""
    detection_latency_ms: float
    analysis_latency_ms: float
    correction_latency_ms: float
    total_events_detected: int
    auto_resolved_count: int
    auto_resolution_rate: float = Field(..., ge=0, le=100)
    system_uptime_percentage: float = Field(..., ge=0, le=100)
    cost_savings: float = Field(..., description="Cost savings in USD")


# ============= Health Models =============

class ServiceHealth(BaseModel):
    """Health status of a service"""
    service: str
    status: str = Field(..., description="healthy, degraded, unhealthy")
    message: Optional[str] = None
    checked_at: datetime
    response_time_ms: float


class HealthCheck(BaseModel):
    """Overall system health"""
    timestamp: datetime
    status: str = Field(..., description="healthy, degraded, unhealthy")
    services: List[ServiceHealth]
    version: str
