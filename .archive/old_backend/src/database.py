"""
SQLAlchemy ORM Models for Project Phoenix
Database schema for core entities
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class System(Base):
    """Monitored system entity"""
    __tablename__ = "systems"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # kubernetes, microservice, database, etc
    endpoint = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    status = Column(String, default="unknown")  # healthy, warning, critical, unknown
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship("Event", back_populates="system", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="system", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="system", cascade="all, delete-orphan")
    corrections = relationship("Correction", back_populates="system", cascade="all, delete-orphan")


class Event(Base):
    """Detected event in monitored system"""
    __tablename__ = "events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String, ForeignKey("systems.id"), nullable=False)
    event_type = Column(String, nullable=False)  # metric_anomaly, log_error, etc
    severity = Column(String, nullable=False)  # low, medium, high, critical
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    metrics = Column(JSON, default=dict)
    context = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    detected_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    system = relationship("System", back_populates="events")
    corrections = relationship("Correction", back_populates="event", cascade="all, delete-orphan")


class Policy(Base):
    """Correction policy for automated response"""
    __tablename__ = "policies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String, ForeignKey("systems.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=5)  # 1-10, higher = more important
    conditions = Column(JSON, nullable=False)  # List of conditions
    actions = Column(JSON, nullable=False)  # List of actions
    executions = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    system = relationship("System", back_populates="policies")
    corrections = relationship("Correction", back_populates="policy")


class Correction(Base):
    """Correction execution record"""
    __tablename__ = "corrections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    policy_id = Column(String, ForeignKey("policies.id"), nullable=False)
    system_id = Column(String, ForeignKey("systems.id"), nullable=False)
    action_type = Column(String, nullable=False)
    target = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False)
    dry_run = Column(Boolean, default=False)
    status = Column(String, nullable=False)  # pending, in_progress, successful, failed, rolled_back
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Relationships
    event = relationship("Event", back_populates="corrections")
    policy = relationship("Policy", back_populates="corrections")
    system = relationship("System", back_populates="corrections")


class Metric(Base):
    """System metrics snapshot"""
    __tablename__ = "metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    system_id = Column(String, ForeignKey("systems.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Metrics
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    disk_usage = Column(Float, nullable=False)
    network_latency = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    request_rate = Column(Integer, nullable=False)
    
    # Anomaly Detection
    anomaly_detected = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    system = relationship("System", back_populates="metrics")


class LearningRecord(Base):
    """Learning outcome from corrections"""
    __tablename__ = "learning_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False)
    root_cause = Column(String, nullable=False)
    correction_strategy = Column(String, nullable=False)
    success_rate = Column(Float, nullable=False)
    average_duration_ms = Column(Integer, nullable=False)
    sample_size = Column(Integer, default=1)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit log for compliance and debugging"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String, nullable=False)  # create, update, delete, execute, rollback, etc
    resource_type = Column(String, nullable=False)  # system, event, policy, correction, etc
    resource_id = Column(String, nullable=False)
    user = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    status = Column(String, nullable=False)  # success, failure
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
