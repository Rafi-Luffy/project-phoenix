"""
Monitoring and Logging Infrastructure
Structured logging, metrics collection, event tracking, performance monitoring
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
import json
import time


class EventType(Enum):
    """System event types"""
    AGENT_CREATED = "agent_created"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    INCIDENT_DETECTED = "incident_detected"
    INCIDENT_RESOLVED = "incident_resolved"
    ERROR_DETECTED = "error_detected"
    CORRECTION_APPLIED = "correction_applied"
    LEARNING_EVENT = "learning_event"
    FEEDBACK_RECEIVED = "feedback_received"
    SYSTEM_HEALTH_CHECK = "system_health_check"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class SeverityLevel(Enum):
    """Severity levels for alerts"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


class MetricType(Enum):
    """System metric types"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    ACTIVE_AGENTS = "active_agents"
    ACTIVE_TASKS = "active_tasks"
    INCIDENTS_TOTAL = "incidents_total"


class LogRecord:
    """Structured log record"""
    
    def __init__(self, level: str, message: str, timestamp: datetime = None, context: Dict[str, Any] = None):
        self.level = level
        self.message = message
        self.timestamp = timestamp or datetime.now()
        self.context = context or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context
        }


class Event:
    """System event"""
    
    def __init__(self, event_type: EventType, details: Dict[str, Any], timestamp: datetime = None):
        self.event_type = event_type
        self.details = details
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'event_type': self.event_type.value,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class MetricRecord:
    """Performance metric record"""
    
    def __init__(self, metric_type: MetricType, value: float, timestamp: datetime = None, tags: Dict[str, str] = None):
        self.metric_type = metric_type
        self.value = value
        self.timestamp = timestamp or datetime.now()
        self.tags = tags or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


class Alert:
    """System alert"""
    
    def __init__(self, severity: SeverityLevel, title: str, description: str, metric: Optional[MetricRecord] = None):
        self.severity = severity
        self.title = title
        self.description = description
        self.metric = metric
        self.timestamp = datetime.now()
        self.acknowledged = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'severity': self.severity.name,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'metric': self.metric.to_dict() if self.metric else None
        }


class StructuredLogger:
    """Structured logging with context"""
    
    def __init__(self, name: str = "autonomous_system"):
        self.logger = logging.getLogger(name)
        self.logs: List[LogRecord] = []
        self.max_logs = 10000
        
        # Configure logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log(self, level: str, message: str, context: Dict[str, Any] = None):
        """Log with structured context"""
        record = LogRecord(level, message, context=context)
        self.logs.append(record)
        
        # Trim logs if exceeding max
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Also log to standard logger
        if level.upper() == 'DEBUG':
            self.logger.debug(f"{message} | {json.dumps(context or {})}")
        elif level.upper() == 'INFO':
            self.logger.info(f"{message} | {json.dumps(context or {})}")
        elif level.upper() == 'WARNING':
            self.logger.warning(f"{message} | {json.dumps(context or {})}")
        elif level.upper() == 'ERROR':
            self.logger.error(f"{message} | {json.dumps(context or {})}")
        elif level.upper() == 'CRITICAL':
            self.logger.critical(f"{message} | {json.dumps(context or {})}")
    
    def info(self, message: str, context: Dict[str, Any] = None):
        """Log info level"""
        self.log('INFO', message, context)
    
    def warning(self, message: str, context: Dict[str, Any] = None):
        """Log warning level"""
        self.log('WARNING', message, context)
    
    def error(self, message: str, context: Dict[str, Any] = None):
        """Log error level"""
        self.log('ERROR', message, context)
    
    def debug(self, message: str, context: Dict[str, Any] = None):
        """Log debug level"""
        self.log('DEBUG', message, context)
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        return [log.to_dict() for log in self.logs[-limit:]]


class EventTracker:
    """Track system events"""
    
    def __init__(self):
        self.events: List[Event] = []
        self.max_events = 50000
        self.event_listeners: Dict[EventType, List[callable]] = {}
    
    def track_event(self, event_type: EventType, details: Dict[str, Any] = None):
        """Track an event"""
        event = Event(event_type, details or {})
        self.events.append(event)
        
        # Trim events if exceeding max
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Notify listeners
        self._notify_listeners(event)
    
    def subscribe(self, event_type: EventType, callback: callable):
        """Subscribe to events"""
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(callback)
    
    def _notify_listeners(self, event: Event):
        """Notify registered listeners"""
        if event.event_type in self.event_listeners:
            for callback in self.event_listeners[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logging.error(f"Event listener error: {e}")
    
    def get_events(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Dict]:
        """Get events, optionally filtered by type"""
        if event_type:
            filtered = [e for e in self.events if e.event_type == event_type]
        else:
            filtered = self.events
        
        return [e.to_dict() for e in filtered[-limit:]]


class MetricsCollector:
    """Collect and manage system metrics"""
    
    def __init__(self):
        self.metrics: List[MetricRecord] = []
        self.max_metrics = 100000
        self.thresholds: Dict[MetricType, float] = {
            MetricType.LATENCY: 5000,  # ms
            MetricType.ERROR_RATE: 0.1,  # 10%
            MetricType.CPU_USAGE: 80,  # %
            MetricType.MEMORY_USAGE: 85,  # %
        }
    
    def record_metric(self, metric_type: MetricType, value: float, tags: Dict[str, str] = None):
        """Record a metric"""
        metric = MetricRecord(metric_type, value, tags=tags)
        self.metrics.append(metric)
        
        # Trim metrics if exceeding max
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
    
    def get_metric_average(self, metric_type: MetricType, time_window_seconds: int = 300) -> float:
        """Get average metric value over time window"""
        cutoff_time = datetime.now() - timedelta(seconds=time_window_seconds)
        relevant_metrics = [
            m.value for m in self.metrics 
            if m.metric_type == metric_type and m.timestamp > cutoff_time
        ]
        
        if not relevant_metrics:
            return 0.0
        return sum(relevant_metrics) / len(relevant_metrics)
    
    def get_metrics(self, metric_type: Optional[MetricType] = None, limit: int = 100) -> List[Dict]:
        """Get metrics, optionally filtered by type"""
        if metric_type:
            filtered = [m for m in self.metrics if m.metric_type == metric_type]
        else:
            filtered = self.metrics
        
        return [m.to_dict() for m in filtered[-limit:]]
    
    def set_threshold(self, metric_type: MetricType, threshold: float):
        """Set alert threshold for metric"""
        self.thresholds[metric_type] = threshold


class AlertManager:
    """Manage system alerts"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.max_alerts = 10000
        self.alert_history: List[Alert] = []
    
    def create_alert(self, severity: SeverityLevel, title: str, description: str, metric: Optional[MetricRecord] = None) -> Alert:
        """Create an alert"""
        alert = Alert(severity, title, description, metric)
        self.alerts.append(alert)
        
        # Trim alerts if exceeding max
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        return alert
    
    def acknowledge_alert(self, alert_index: int) -> bool:
        """Acknowledge an alert"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].acknowledged = True
            self.alert_history.append(self.alerts[alert_index])
            return True
        return False
    
    def get_active_alerts(self, severity: Optional[SeverityLevel] = None) -> List[Dict]:
        """Get active alerts, optionally filtered by severity"""
        filtered = [a for a in self.alerts if not a.acknowledged]
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        
        return [a.to_dict() for a in filtered]
    
    def get_all_alerts(self, limit: int = 100) -> List[Dict]:
        """Get all alerts"""
        return [a.to_dict() for a in self.alerts[-limit:]]


class PerformanceMonitor:
    """Monitor system performance"""
    
    def __init__(self):
        self.start_times: Dict[str, float] = {}
        self.metrics_collector = MetricsCollector()
    
    def start_timer(self, operation_id: str):
        """Start timing an operation"""
        self.start_times[operation_id] = time.time()
    
    def end_timer(self, operation_id: str, metric_type: MetricType = MetricType.LATENCY, tags: Dict[str, str] = None) -> float:
        """End timing and record metric"""
        if operation_id not in self.start_times:
            return 0.0
        
        elapsed_ms = (time.time() - self.start_times[operation_id]) * 1000
        self.metrics_collector.record_metric(metric_type, elapsed_ms, tags)
        del self.start_times[operation_id]
        
        return elapsed_ms


from datetime import timedelta
