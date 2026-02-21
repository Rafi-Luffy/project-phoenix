"""Database models for Phoenix using SQLAlchemy."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ProjectDB(Base):
    """Database model for Project."""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    repository_url = Column(String(512), nullable=True)
    local_path = Column(String(512), nullable=False)
    branch = Column(String(255), default="main")
    language = Column(String(50), default="python")
    test_command = Column(String(255), default="pytest")
    test_framework = Column(String(50), default="pytest")
    python_version = Column(String(20), nullable=True)
    dependencies_file = Column(String(255), nullable=True)
    auto_remediation_enabled = Column(Boolean, default=True)
    max_attempts = Column(Integer, default=5)
    validation_timeout = Column(Integer, default=300)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run_at = Column(DateTime, nullable=True)
    is_healthy = Column(Boolean, default=True)
    total_failures = Column(Integer, default=0)
    total_remediations = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Relationships
    failure_events = relationship("FailureEventDB", back_populates="project")
    remediation_attempts = relationship("RemediationAttemptDB", back_populates="project")


class FailureEventDB(Base):
    """Database model for FailureEvent."""
    
    __tablename__ = "failure_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    failure_type = Column(String(50), nullable=False)
    severity = Column(Integer, default=5)
    test_name = Column(String(512), nullable=True)
    test_file = Column(String(512), nullable=True)
    test_inputs = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    error_type = Column(String(255), nullable=True)
    files_implicated = Column(JSON, default=list)
    lines_implicated = Column(JSON, default=dict)
    commit_hash = Column(String(40), nullable=True)
    branch = Column(String(255), nullable=True)
    environment = Column(JSON, default=dict)
    logs = Column(Text, nullable=True)
    metrics = Column(JSON, default=dict)
    
    # Relationships
    project = relationship("ProjectDB", back_populates="failure_events")
    remediation_attempts = relationship("RemediationAttemptDB", back_populates="failure_event")


class DiagnosticReportDB(Base):
    """Database model for DiagnosticReport."""
    
    __tablename__ = "diagnostic_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    failure_event_id = Column(UUID(as_uuid=True), ForeignKey("failure_events.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    explanation = Column(Text, nullable=False)
    bug_type = Column(String(50), nullable=False)
    root_cause = Column(Text, nullable=False)
    suspected_files = Column(JSON, default=list)
    suspected_functions = Column(JSON, default=list)
    recommended_strategy = Column(Text, nullable=False)
    constraints = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.7)
    raw_response = Column(Text, nullable=True)


class PatchDB(Base):
    """Database model for Patch."""
    
    __tablename__ = "patches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    remediation_attempt_id = Column(UUID(as_uuid=True), ForeignKey("remediation_attempts.id"))
    iteration = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow)
    patch_type = Column(String(50), default="code")
    file_path = Column(String(512), nullable=False)
    original_content = Column(Text, nullable=True)
    patched_content = Column(Text, nullable=False)
    diff = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)
    is_validated = Column(Boolean, default=False)
    validation_result_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    remediation_attempt = relationship("RemediationAttemptDB", back_populates="patches")


class ValidationResultDB(Base):
    """Database model for ValidationResult."""
    
    __tablename__ = "validation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patch_id = Column(UUID(as_uuid=True), ForeignKey("patches.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False)
    tests_run = Column(Integer, default=0)
    tests_passed = Column(Integer, default=0)
    tests_failed = Column(Integer, default=0)
    original_failures_fixed = Column(Integer, default=0)
    new_failures_introduced = Column(Integer, default=0)
    test_outputs = Column(JSON, default=dict)
    logs = Column(Text, nullable=True)
    execution_time = Column(Float, default=0.0)
    timeout_occurred = Column(Boolean, default=False)
    errors = Column(JSON, default=list)


class RemediationAttemptDB(Base):
    """Database model for RemediationAttempt."""
    
    __tablename__ = "remediation_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    failure_event_id = Column(UUID(as_uuid=True), ForeignKey("failure_events.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    diagnostic_report_id = Column(UUID(as_uuid=True), nullable=True)
    successful_patch_id = Column(UUID(as_uuid=True), nullable=True)
    attempts_count = Column(Integer, default=0)
    total_time_seconds = Column(Float, default=0.0)
    is_successful = Column(Boolean, default=False)
    failure_reason = Column(Text, nullable=True)
    lessons_learned = Column(JSON, default=dict)
    
    # Relationships
    project = relationship("ProjectDB", back_populates="remediation_attempts")
    failure_event = relationship("FailureEventDB", back_populates="remediation_attempts")
    patches = relationship("PatchDB", back_populates="remediation_attempt")


class ExperienceRecordDB(Base):
    """Database model for ExperienceRecord."""
    
    __tablename__ = "experience_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    failure_signature = Column(String(512), nullable=False, index=True)
    failure_type = Column(String(50), nullable=False)
    bug_type = Column(String(50), nullable=False)
    error_pattern = Column(Text, nullable=False)
    file_patterns = Column(JSON, default=list)
    test_patterns = Column(JSON, default=list)
    successful_patch_pattern = Column(Text, nullable=False)
    remediation_strategy = Column(Text, nullable=False)
    times_encountered = Column(Integer, default=1)
    times_successful = Column(Integer, default=0)
    avg_attempts = Column(Float, default=0.0)
    avg_time_seconds = Column(Float, default=0.0)
    failure_embedding = Column(JSON, nullable=True)  # Store as JSON array
    patch_embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
