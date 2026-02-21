"""
Advanced Monitoring & Observability Module
Provides comprehensive metrics, logging, tracing, and dashboards
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import logging
from enum import Enum


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"  # Total count
    GAUGE = "gauge"  # Current value
    HISTOGRAM = "histogram"  # Distribution
    TIMER = "timer"  # Duration


@dataclass
class Metric:
    """Represents a single metric"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


class MetricsCollector:
    """Collects and aggregates metrics"""
    
    def __init__(self, max_history: int = 10000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.aggregates: Dict[str, Dict[str, float]] = {}
        self.lock = __import__('threading').Lock()
    
    def record_metric(self, metric: Metric):
        """Record a metric"""
        with self.lock:
            self.metrics[metric.name].append(metric)
            self._update_aggregates(metric)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        metric = Metric(
            name=name,
            value=value,
            labels=labels or {},
            metric_type=MetricType.COUNTER
        )
        self.record_metric(metric)
    
    def record_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a gauge metric"""
        metric = Metric(
            name=name,
            value=value,
            labels=labels or {},
            metric_type=MetricType.GAUGE
        )
        self.record_metric(metric)
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram metric"""
        metric = Metric(
            name=name,
            value=value,
            labels=labels or {},
            metric_type=MetricType.HISTOGRAM
        )
        self.record_metric(metric)
    
    def record_timer(self, name: str, duration_ms: float, labels: Dict[str, str] = None):
        """Record a timer metric"""
        metric = Metric(
            name=name,
            value=duration_ms,
            labels=labels or {},
            metric_type=MetricType.TIMER
        )
        self.record_metric(metric)
    
    def _update_aggregates(self, metric: Metric):
        """Update aggregate statistics"""
        if metric.name not in self.aggregates:
            self.aggregates[metric.name] = {
                "min": metric.value,
                "max": metric.value,
                "sum": 0,
                "count": 0,
                "mean": 0,
            }
        
        agg = self.aggregates[metric.name]
        agg["min"] = min(agg["min"], metric.value)
        agg["max"] = max(agg["max"], metric.value)
        agg["sum"] += metric.value
        agg["count"] += 1
        agg["mean"] = agg["sum"] / agg["count"]
    
    def get_aggregates(self, name: str) -> Optional[Dict[str, float]]:
        """Get aggregate statistics for a metric"""
        with self.lock:
            return self.aggregates.get(name, {}).copy()
    
    def get_recent_metrics(self, name: str, limit: int = 100) -> List[Metric]:
        """Get recent metrics"""
        with self.lock:
            metrics = list(self.metrics.get(name, []))
            return metrics[-limit:]
    
    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        with self.lock:
            for name, metrics_list in self.metrics.items():
                if not metrics_list:
                    continue
                
                # Get latest value
                latest = metrics_list[-1]
                labels_str = ""
                if latest.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in latest.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                lines.append(f"{name}{labels_str} {latest.value}")
        
        return "\n".join(lines)


@dataclass
class LogEntry:
    """Represents a log entry"""
    timestamp: datetime
    level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    component: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)


class StructuredLogger:
    """Structured logging with context"""
    
    def __init__(self, component: str, max_history: int = 1000):
        self.component = component
        self.logs: deque = deque(maxlen=max_history)
        self.lock = __import__('threading').Lock()
        self.logger = logging.getLogger(component)
    
    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a message with context"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            component=self.component,
            message=message,
            context=context or {}
        )
        
        with self.lock:
            self.logs.append(entry)
        
        # Also log to standard logger
        getattr(self.logger, level.lower(), self.logger.info)(
            f"{message} | context={entry.context}"
        )
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log("DEBUG", message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log("INFO", message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log("WARNING", message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log("ERROR", message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log("CRITICAL", message, context)
    
    def get_recent_logs(self, level: Optional[str] = None, limit: int = 100) -> List[LogEntry]:
        """Get recent logs, optionally filtered by level"""
        with self.lock:
            logs = list(self.logs)
        
        if level:
            logs = [log for log in logs if log.level == level]
        
        return logs[-limit:]


@dataclass
class TraceSpan:
    """Represents a distributed trace span"""
    trace_id: str
    span_id: str
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    status: str = "active"  # active, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)


class DistributedTracer:
    """Distributed tracing for request correlation"""
    
    def __init__(self):
        self.spans: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.active_spans: Dict[str, TraceSpan] = {}
        self.lock = __import__('threading').Lock()
    
    def start_span(self, trace_id: str, operation: str, metadata: Dict[str, Any] = None) -> TraceSpan:
        """Start a new trace span"""
        import uuid
        span_id = str(uuid.uuid4())
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            operation=operation,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        with self.lock:
            self.spans[trace_id].append(span)
            self.active_spans[span_id] = span
        
        return span
    
    def end_span(self, span_id: str, status: str = "completed"):
        """End a trace span"""
        with self.lock:
            if span_id in self.active_spans:
                span = self.active_spans.pop(span_id)
                span.end_time = datetime.now()
                span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
                span.status = status
    
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace"""
        with self.lock:
            return self.spans.get(trace_id, [])


class AlertManager:
    """Manages alerts and thresholds"""
    
    def __init__(self):
        self.alerts: deque = deque(maxlen=1000)
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.callbacks: List[Callable] = []
        self.lock = __import__('threading').Lock()
    
    def set_threshold(self, metric: str, alert_type: str, threshold: float):
        """Set alert threshold for a metric"""
        if metric not in self.thresholds:
            self.thresholds[metric] = {}
        self.thresholds[metric][alert_type] = threshold
    
    def check_and_alert(self, metric_name: str, value: float) -> Optional[Dict[str, Any]]:
        """Check metric against thresholds and create alert if needed"""
        if metric_name not in self.thresholds:
            return None
        
        thresholds = self.thresholds[metric_name]
        
        alert = None
        if "max" in thresholds and value > thresholds["max"]:
            alert = {
                "metric": metric_name,
                "value": value,
                "threshold": thresholds["max"],
                "type": "max_exceeded",
                "timestamp": datetime.now(),
                "severity": "warning"
            }
        elif "min" in thresholds and value < thresholds["min"]:
            alert = {
                "metric": metric_name,
                "value": value,
                "threshold": thresholds["min"],
                "type": "min_exceeded",
                "timestamp": datetime.now(),
                "severity": "warning"
            }
        
        if alert:
            with self.lock:
                self.alerts.append(alert)
            self._notify_callbacks(alert)
        
        return alert
    
    def register_callback(self, callback: Callable):
        """Register callback for alerts"""
        with self.lock:
            self.callbacks.append(callback)
    
    def _notify_callbacks(self, alert: Dict[str, Any]):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {str(e)}")
    
    def get_recent_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        with self.lock:
            return list(self.alerts)[-limit:]


class ObservabilityManager:
    """Centralized observability management"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.loggers: Dict[str, StructuredLogger] = {}
        self.tracer = DistributedTracer()
        self.alerts = AlertManager()
        self.lock = __import__('threading').Lock()
    
    def get_or_create_logger(self, component: str) -> StructuredLogger:
        """Get or create logger for component"""
        with self.lock:
            if component not in self.loggers:
                self.loggers[component] = StructuredLogger(component)
            return self.loggers[component]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics_summary": {
                name: self.metrics.get_aggregates(name)
                for name in self.metrics.aggregates.keys()
            },
            "recent_logs": {
                name: [
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "level": log.level,
                        "message": log.message,
                        "context": log.context
                    }
                    for log in logger_obj.get_recent_logs(limit=10)
                ]
                for name, logger_obj in self.loggers.items()
            },
            "active_traces": len(self.tracer.active_spans),
            "recent_alerts": self.alerts.get_recent_alerts(limit=20),
        }
    
    def export_all_metrics(self) -> str:
        """Export all metrics in Prometheus format"""
        return self.metrics.export_prometheus_format()
