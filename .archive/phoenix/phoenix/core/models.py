"""Core data models for Phoenix framework."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class FailureType(str, Enum):
    """Types of failures Phoenix can detect."""
    
    TEST_FAILURE = "test_failure"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    ASSERTION_ERROR = "assertion_error"
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    UNKNOWN = "unknown"


class BugType(str, Enum):
    """Classification of bug types for diagnosis."""
    
    LOGIC_ERROR = "logic_error"
    BOUNDARY_CASE = "boundary_case"
    NULL_HANDLING = "null_handling"
    TYPE_MISMATCH = "type_mismatch"
    OFF_BY_ONE = "off_by_one"
    RACE_CONDITION = "race_condition"
    RESOURCE_LEAK = "resource_leak"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"


class RemediationStatus(str, Enum):
    """Status of a remediation attempt."""
    
    PENDING = "pending"
    DIAGNOSING = "diagnosing"
    GENERATING_PATCH = "generating_patch"
    VALIDATING = "validating"
    INTEGRATING = "integrating"
    SUCCESS = "success"
    FAILED = "failed"
    ABORTED = "aborted"


class ValidationStatus(str, Enum):
    """Result of patch validation."""
    
    SUCCESS = "success"
    PARTIAL = "partial"
    REGRESSION = "regression"
    CATASTROPHIC = "catastrophic"
    TIMEOUT = "timeout"


class FailureEvent(BaseModel):
    """Structured representation of a failure detected by Observer."""
    
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Failure classification
    failure_type: FailureType
    severity: int = Field(ge=1, le=10, default=5)
    
    # Test information
    test_name: Optional[str] = None
    test_file: Optional[str] = None
    test_inputs: Optional[Dict[str, Any]] = None
    
    # Error details
    error_message: str
    stack_trace: Optional[str] = None
    error_type: Optional[str] = None
    
    # Code context
    files_implicated: List[str] = Field(default_factory=list)
    lines_implicated: Dict[str, List[int]] = Field(default_factory=dict)
    
    # Environment context
    commit_hash: Optional[str] = None
    branch: Optional[str] = None
    environment: Dict[str, str] = Field(default_factory=dict)
    
    # Additional context
    logs: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class DiagnosticReport(BaseModel):
    """Output from Critic agent analyzing a failure."""
    
    id: UUID = Field(default_factory=uuid4)
    failure_event_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Diagnosis
    explanation: str
    bug_type: BugType
    root_cause: str
    
    # Localization
    suspected_files: List[str] = Field(default_factory=list)
    suspected_functions: List[str] = Field(default_factory=list)
    
    # Remediation guidance
    recommended_strategy: str
    constraints: List[str] = Field(default_factory=list)
    
    # Confidence
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Raw LLM output
    raw_response: Optional[str] = None


class Patch(BaseModel):
    """A code/config change proposed by Programmer agent."""
    
    id: UUID = Field(default_factory=uuid4)
    remediation_attempt_id: UUID
    iteration: int = 1
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Patch content
    patch_type: str = "code"  # code, config, prompt
    file_path: str
    original_content: Optional[str] = None
    patched_content: str
    diff: Optional[str] = None
    
    # Metadata
    description: str
    reasoning: Optional[str] = None
    
    # Validation
    is_validated: bool = False
    validation_result_id: Optional[UUID] = None


class ValidationResult(BaseModel):
    """Result of validating a patch in the sandbox."""
    
    id: UUID = Field(default_factory=uuid4)
    patch_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Overall status
    status: ValidationStatus
    
    # Test results
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    original_failures_fixed: int = 0
    new_failures_introduced: int = 0
    
    # Detailed results
    test_outputs: Dict[str, Any] = Field(default_factory=dict)
    logs: Optional[str] = None
    
    # Performance
    execution_time: float = 0.0
    timeout_occurred: bool = False
    
    # Errors
    errors: List[str] = Field(default_factory=list)


class RemediationAttempt(BaseModel):
    """A complete remediation cycle from failure to resolution."""
    
    id: UUID = Field(default_factory=uuid4)
    failure_event_id: UUID
    project_id: UUID
    
    # Status tracking
    status: RemediationStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Linked entities
    diagnostic_report_id: Optional[UUID] = None
    patch_ids: List[UUID] = Field(default_factory=list)
    successful_patch_id: Optional[UUID] = None
    
    # Metrics
    attempts_count: int = 0
    total_time_seconds: float = 0.0
    
    # Outcome
    is_successful: bool = False
    failure_reason: Optional[str] = None
    
    # Learning
    lessons_learned: Dict[str, Any] = Field(default_factory=dict)


class Project(BaseModel):
    """A registered project monitored by Phoenix."""
    
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    
    # Source
    repository_url: Optional[str] = None
    local_path: str
    branch: str = "main"
    
    # Configuration
    language: str = "python"
    test_command: str = "pytest"
    test_framework: str = "pytest"
    
    # Runtime
    python_version: Optional[str] = None
    dependencies_file: Optional[str] = None
    
    # Phoenix settings
    auto_remediation_enabled: bool = True
    max_attempts: int = 5
    validation_timeout: int = 300
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_run_at: Optional[datetime] = None
    
    # Health
    is_healthy: bool = True
    total_failures: int = 0
    total_remediations: int = 0
    success_rate: float = 0.0


class ExperienceRecord(BaseModel):
    """A learned pattern from past remediations."""
    
    id: UUID = Field(default_factory=uuid4)
    
    # Failure signature
    failure_signature: str
    failure_type: FailureType
    bug_type: BugType
    error_pattern: str
    
    # Context
    file_patterns: List[str] = Field(default_factory=list)
    test_patterns: List[str] = Field(default_factory=list)
    
    # Solution
    successful_patch_pattern: str
    remediation_strategy: str
    
    # Metrics
    times_encountered: int = 1
    times_successful: int = 0
    avg_attempts: float = 0.0
    avg_time_seconds: float = 0.0
    
    # Embeddings for similarity search
    failure_embedding: Optional[List[float]] = None
    patch_embedding: Optional[List[float]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
