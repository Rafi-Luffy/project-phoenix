"""
Monitoring & Observability - Module 6.2

Metrics dashboards, distributed tracing, error tracking,
alerting systems, and SLA monitoring for production systems.
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from collections import defaultdict, deque
import statistics


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TraceSpanStatus(Enum):
    """Status of trace span"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class SLOMetricType(Enum):
    """Types of SLO metrics"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


@dataclass
class Metric:
    """Single metric data point"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class TraceSpan:
    """Single span in distributed trace"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: float = 0.0
    status: TraceSpanStatus = TraceSpanStatus.PENDING
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ErrorEvent:
    """Error event in system"""
    error_id: str
    timestamp: float
    error_type: str
    message: str
    service: str
    instance_id: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


@dataclass
class SLATarget:
    """Service Level Agreement target"""
    service_name: str
    metric_type: SLOMetricType
    target_value: float
    window: int  # seconds
    minimum_good_requests: int


@dataclass
class DashboardWidget:
    """Dashboard widget for visualization"""
    widget_id: str
    title: str
    metric_name: str
    metric_type: str  # gauge, counter, histogram
    refresh_interval: int = 60  # seconds
    time_range: int = 3600  # seconds


class MetricsDashboard:
    """Metrics dashboard and visualization"""

    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.widgets: Dict[str, DashboardWidget] = {}
        self.lock = threading.RLock()

    def record_metric(self, metric: Metric):
        """Record metric"""
        with self.lock:
            self.metrics[metric.name].append(metric)

    def record_metrics_batch(self, metrics: List[Metric]):
        """Record multiple metrics"""
        with self.lock:
            for metric in metrics:
                self.metrics[metric.name].append(metric)

    def add_widget(self, widget: DashboardWidget) -> bool:
        """Add dashboard widget"""
        with self.lock:
            if widget.widget_id in self.widgets:
                return False

            self.widgets[widget.widget_id] = widget
            return True

    def get_widget_data(self, widget_id: str,
                       time_range: int = 3600) -> Optional[Dict[str, Any]]:
        """Get data for widget"""
        with self.lock:
            if widget_id not in self.widgets:
                return None

            widget = self.widgets[widget_id]
            metric_name = widget.metric_name

            if metric_name not in self.metrics:
                return None

            current_time = time.time()
            recent_metrics = [
                m for m in self.metrics[metric_name]
                if current_time - m.timestamp <= time_range
            ]

            if not recent_metrics:
                return None

            values = [m.value for m in recent_metrics]

            return {
                "widget_id": widget_id,
                "title": widget.title,
                "metric_name": metric_name,
                "datapoints": len(recent_metrics),
                "current_value": values[-1] if values else 0,
                "min_value": min(values),
                "max_value": max(values),
                "avg_value": statistics.mean(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "timestamps": [m.timestamp for m in recent_metrics],
                "values": values
            }

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary of all dashboard data"""
        with self.lock:
            summary = {
                "total_widgets": len(self.widgets),
                "total_metrics": len(self.metrics),
                "widgets": {}
            }

            for widget_id, widget in self.widgets.items():
                widget_data = self.get_widget_data(widget_id)
                if widget_data:
                    summary["widgets"][widget_id] = widget_data

            return summary

    def export_dashboard_data(self, format_type: str = "json") -> Dict[str, Any]:
        """Export dashboard data"""
        with self.lock:
            export_data = {
                "timestamp": time.time(),
                "format": format_type,
                "metrics": {}
            }

            for metric_name, metric_deque in self.metrics.items():
                export_data["metrics"][metric_name] = [
                    {
                        "value": m.value,
                        "timestamp": m.timestamp,
                        "labels": m.labels
                    }
                    for m in list(metric_deque)[-100:]  # Last 100 for brevity
                ]

            return export_data


class DistributedTracing:
    """Distributed tracing for request flows"""

    def __init__(self):
        self.traces: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.active_spans: Dict[str, TraceSpan] = {}
        self.lock = threading.RLock()

    def start_span(self, trace_id: str, span_id: str,
                   operation_name: str, service_name: str,
                   parent_span_id: Optional[str] = None) -> TraceSpan:
        """Start new trace span"""
        with self.lock:
            span = TraceSpan(
                span_id=span_id,
                trace_id=trace_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                service_name=service_name,
                start_time=time.time(),
                status=TraceSpanStatus.ACTIVE
            )

            self.active_spans[span_id] = span
            return span

    def end_span(self, span_id: str, status: TraceSpanStatus = TraceSpanStatus.COMPLETED):
        """End trace span"""
        with self.lock:
            if span_id not in self.active_spans:
                return

            span = self.active_spans.pop(span_id)
            span.end_time = time.time()
            span.duration = span.end_time - span.start_time
            span.status = status

            self.traces[span.trace_id].append(span)

    def add_span_tag(self, span_id: str, key: str, value: str):
        """Add tag to span"""
        with self.lock:
            if span_id in self.active_spans:
                self.active_spans[span_id].tags[key] = value

    def add_span_log(self, span_id: str, log_entry: Dict[str, Any]):
        """Add log entry to span"""
        with self.lock:
            if span_id in self.active_spans:
                self.active_spans[span_id].logs.append(log_entry)

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get complete trace"""
        with self.lock:
            if trace_id not in self.traces:
                return None

            spans = self.traces[trace_id]
            if not spans:
                return None

            # Sort spans by start time
            sorted_spans = sorted(spans, key=lambda s: s.start_time)

            return {
                "trace_id": trace_id,
                "start_time": sorted_spans[0].start_time,
                "end_time": sorted_spans[-1].end_time,
                "duration": sorted_spans[-1].end_time - sorted_spans[0].start_time,
                "span_count": len(spans),
                "spans": [
                    {
                        "span_id": s.span_id,
                        "operation": s.operation_name,
                        "service": s.service_name,
                        "duration": s.duration,
                        "status": s.status.value,
                        "tags": s.tags
                    }
                    for s in sorted_spans
                ]
            }

    def get_traces_by_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Get traces that touched a service"""
        with self.lock:
            service_traces = []

            for trace_id, spans in self.traces.items():
                if any(s.service_name == service_name for s in spans):
                    trace_data = self.get_trace(trace_id)
                    if trace_data:
                        service_traces.append(trace_data)

            return service_traces

    def get_critical_paths(self) -> List[Dict[str, Any]]:
        """Get critical paths (slowest traces)"""
        with self.lock:
            traces_with_duration = []

            for trace_id, spans in self.traces.items():
                if spans:
                    total_duration = max(s.end_time for s in spans) - min(s.start_time for s in spans)
                    traces_with_duration.append((trace_id, total_duration))

            # Return top 10 slowest
            slowest = sorted(traces_with_duration, key=lambda x: x[1], reverse=True)[:10]

            return [
                self.get_trace(trace_id)
                for trace_id, _ in slowest
                if self.get_trace(trace_id)
            ]


class ErrorTracking:
    """Track and aggregate errors"""

    def __init__(self):
        self.errors: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.lock = threading.RLock()

    def record_error(self, error: ErrorEvent):
        """Record error event"""
        with self.lock:
            self.errors[error.error_type].append(error)
            self.error_patterns[error.error_type] += 1

    def get_errors_by_type(self, error_type: str,
                          time_window: int = 3600) -> List[ErrorEvent]:
        """Get errors of specific type"""
        with self.lock:
            if error_type not in self.errors:
                return []

            current_time = time.time()
            return [
                e for e in self.errors[error_type]
                if current_time - e.timestamp <= time_window
            ]

    def get_error_rate(self, time_window: int = 300) -> Dict[str, float]:
        """Calculate error rate by type"""
        with self.lock:
            current_time = time.time()
            error_rates = {}

            for error_type, error_deque in self.errors.items():
                recent_errors = [
                    e for e in error_deque
                    if current_time - e.timestamp <= time_window
                ]
                error_rates[error_type] = len(recent_errors) / (time_window / 60)  # errors per minute

            return error_rates

    def get_top_errors(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top error types"""
        with self.lock:
            sorted_errors = sorted(
                self.error_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_errors[:limit]

    def mark_error_resolved(self, error_id: str) -> bool:
        """Mark error as resolved"""
        with self.lock:
            for error_type in self.errors:
                for error in self.errors[error_type]:
                    if error.error_id == error_id:
                        error.resolved = True
                        return True

            return False

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        with self.lock:
            total_errors = sum(len(e) for e in self.errors.values())
            unresolved_errors = sum(
                1 for error_type in self.errors
                for error in self.errors[error_type]
                if not error.resolved
            )

            return {
                "total_errors": total_errors,
                "unresolved_errors": unresolved_errors,
                "error_types": len(self.errors),
                "top_errors": self.get_top_errors(5)
            }


class AlertingSystem:
    """Alert management and notification"""

    def __init__(self):
        self.alerts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_handlers: List[Callable] = []
        self.lock = threading.RLock()

    def add_alert_rule(self, rule_name: str,
                       condition_fn: Callable,
                       severity: AlertSeverity) -> bool:
        """Add alert rule"""
        with self.lock:
            self.alert_rules.append({
                "name": rule_name,
                "condition": condition_fn,
                "severity": severity,
                "created_at": time.time()
            })
            return True

    def check_alerts(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check all alert rules"""
        triggered_alerts = []

        with self.lock:
            for rule in self.alert_rules:
                try:
                    if rule["condition"](current_metrics):
                        alert = {
                            "rule_name": rule["name"],
                            "severity": rule["severity"].value,
                            "timestamp": time.time(),
                            "metrics": current_metrics
                        }
                        triggered_alerts.append(alert)
                        self.alerts[rule["name"]].append(alert)

                        # Notify
                        for handler in self.notification_handlers:
                            handler(alert)

                except Exception:
                    pass

        return triggered_alerts

    def register_notification_handler(self, handler: Callable):
        """Register notification handler"""
        with self.lock:
            self.notification_handlers.append(handler)

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Get active alerts"""
        with self.lock:
            active_alerts = []

            for rule_name, alert_deque in self.alerts.items():
                for alert in alert_deque:
                    if severity is None or alert["severity"] == severity.value:
                        if time.time() - alert["timestamp"] < 3600:  # Last hour
                            active_alerts.append(alert)

            return sorted(active_alerts, key=lambda a: a["timestamp"], reverse=True)

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        with self.lock:
            active = self.get_active_alerts()
            critical_alerts = [a for a in active if a["severity"] == "critical"]

            return {
                "total_active_alerts": len(active),
                "critical_alerts": len(critical_alerts),
                "alert_rules_count": len(self.alert_rules),
                "critical_rules_triggered": len(set(a["rule_name"] for a in critical_alerts))
            }


class SLAMonitoring:
    """Monitor Service Level Agreements"""

    def __init__(self):
        self.sla_targets: Dict[str, SLATarget] = {}
        self.slo_measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.lock = threading.RLock()

    def register_sla_target(self, target: SLATarget) -> bool:
        """Register SLA target"""
        with self.lock:
            sla_key = f"{target.service_name}_{target.metric_type.value}"

            if sla_key in self.sla_targets:
                return False

            self.sla_targets[sla_key] = target
            return True

    def record_slo_measurement(self, service_name: str,
                              metric_type: SLOMetricType,
                              is_good: bool):
        """Record SLO measurement (good or bad)"""
        with self.lock:
            sla_key = f"{service_name}_{metric_type.value}"
            self.slo_measurements[sla_key].append({
                "timestamp": time.time(),
                "is_good": is_good
            })

    def check_sla_compliance(self, service_name: str,
                            metric_type: SLOMetricType) -> Optional[Dict[str, Any]]:
        """Check if SLA is being met"""
        with self.lock:
            sla_key = f"{service_name}_{metric_type.value}"

            if sla_key not in self.sla_targets:
                return None

            target = self.sla_targets[sla_key]
            measurements = self.slo_measurements[sla_key]

            if not measurements:
                return None

            current_time = time.time()
            recent_measurements = [
                m for m in measurements
                if current_time - m["timestamp"] <= target.window
            ]

            if len(recent_measurements) < target.minimum_good_requests:
                return None

            good_count = sum(1 for m in recent_measurements if m["is_good"])
            good_ratio = good_count / len(recent_measurements)

            met = good_ratio >= target.target_value

            return {
                "service": service_name,
                "metric": metric_type.value,
                "target": target.target_value,
                "actual": good_ratio,
                "met": met,
                "measurements": len(recent_measurements),
                "good_count": good_count
            }

    def get_sla_report(self) -> Dict[str, Any]:
        """Get SLA compliance report"""
        with self.lock:
            compliance_results = []

            for sla_key, target in self.sla_targets.items():
                compliance = self.check_sla_compliance(target.service_name, target.metric_type)
                if compliance:
                    compliance_results.append(compliance)

            met_count = sum(1 for c in compliance_results if c["met"])
            total_count = len(compliance_results)

            return {
                "total_slas": total_count,
                "slas_met": met_count,
                "compliance_percentage": (met_count / total_count * 100) if total_count > 0 else 0,
                "sla_details": compliance_results
            }
