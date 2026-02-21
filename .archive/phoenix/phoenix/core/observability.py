"""
Observability System

Provides distributed tracing, metrics aggregation, and visibility into
the autonomous healing system's operation.
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class SpanKind(str, Enum):
    """Types of spans."""
    INTERNAL = "internal"  # Internal operation
    SERVER = "server"      # Received request
    CLIENT = "client"      # Made request
    PRODUCER = "producer"  # Produced message
    CONSUMER = "consumer"  # Consumed message


class SpanStatus(str, Enum):
    """Span completion status."""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class Span:
    """Represents a single trace span."""
    
    # Identifiers
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    
    # Metadata
    name: str = ""
    kind: SpanKind = SpanKind.INTERNAL
    
    # Timing
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Status
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""
    
    # Data
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    def finish(self, status: SpanStatus = SpanStatus.OK, message: str = ""):
        """Mark span as finished."""
        self.end_time = time.time()
        self.status = status
        self.status_message = message
    
    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if not self.end_time:
            return 0
        return (self.end_time - self.start_time) * 1000
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to span."""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "kind": self.kind.value,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": (
                datetime.fromtimestamp(self.end_time).isoformat()
                if self.end_time else None
            ),
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "status_message": self.status_message,
            "attributes": self.attributes,
            "events": self.events,
        }


@dataclass
class Metric:
    """Represents a single metric."""
    
    name: str
    description: str = ""
    unit: str = ""
    value: float = 0.0
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
            "value": self.value,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "labels": self.labels,
        }


class TracingService:
    """
    Distributed tracing for healing operations.
    
    Tracks spans across the entire healing cycle:
    - Failure detection
    - Fix generation
    - Fix application
    - Validation
    """
    
    def __init__(self):
        """Initialize tracing service."""
        self.logger = get_logger(__name__)
        self.spans: Dict[str, List[Span]] = defaultdict(list)
        self.active_spans: Dict[str, Span] = {}
        self._lock = threading.Lock()
        self._span_counter = 0
    
    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """
        Start a new span.
        
        Args:
            name: Span name
            trace_id: Trace identifier (generates if None)
            parent_span_id: Parent span ID
            kind: Type of span
            attributes: Initial attributes
            
        Returns:
            New span
        """
        with self._lock:
            if not trace_id:
                trace_id = f"trace_{int(time.time() * 1000000)}"
            
            self._span_counter += 1
            span_id = f"span_{self._span_counter}"
            
            span = Span(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                kind=kind,
                attributes=attributes or {},
            )
            
            self.spans[trace_id].append(span)
            self.active_spans[span_id] = span
            
            self.logger.debug(
                "span_started",
                trace_id=trace_id,
                span_id=span_id,
                name=name,
            )
        
        return span
    
    def finish_span(
        self,
        span_id: str,
        status: SpanStatus = SpanStatus.OK,
        message: str = "",
    ):
        """
        Finish a span.
        
        Args:
            span_id: Span to finish
            status: Completion status
            message: Status message
        """
        with self._lock:
            if span_id in self.active_spans:
                span = self.active_spans[span_id]
                span.finish(status, message)
                
                self.logger.debug(
                    "span_finished",
                    span_id=span_id,
                    duration_ms=span.duration_ms,
                    status=status.value,
                )
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace."""
        with self._lock:
            return self.spans.get(trace_id, [])
    
    def export_trace(self, trace_id: str) -> Dict[str, Any]:
        """Export trace as dictionary."""
        spans = self.get_trace(trace_id)
        return {
            "trace_id": trace_id,
            "span_count": len(spans),
            "spans": [span.to_dict() for span in spans],
            "exported_at": datetime.utcnow().isoformat(),
        }


class MetricsCollector:
    """
    Collects and aggregates metrics about healing operations.
    
    Metrics:
    - Failure detection rate
    - Fix generation latency
    - Fix application success rate
    - Cache hit rate
    - System health score
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.logger = get_logger(__name__)
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def record_metric(
        self,
        name: str,
        value: float,
        description: str = "",
        unit: str = "",
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Record a metric value.
        
        Args:
            name: Metric name
            value: Metric value
            description: Metric description
            unit: Unit of measurement
            labels: Metric labels
        """
        with self._lock:
            metric = Metric(
                name=name,
                description=description,
                unit=unit,
                value=value,
                labels=labels or {},
            )
            self.metrics[name].append(metric)
            
            self.logger.debug(
                "metric_recorded",
                name=name,
                value=value,
                unit=unit,
            )
    
    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        with self._lock:
            values = self.metrics.get(name, [])
        
        if not values:
            return {}
        
        nums = [m.value for m in values]
        
        return {
            "name": name,
            "count": len(values),
            "latest": nums[-1],
            "min": min(nums),
            "max": max(nums),
            "avg": sum(nums) / len(nums),
            "sum": sum(nums),
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics."""
        with self._lock:
            return {
                name: [m.to_dict() for m in metrics]
                for name, metrics in self.metrics.items()
            }
    
    def clear_metrics(self, older_than_seconds: int = 3600):
        """Clear old metrics."""
        cutoff_time = time.time() - older_than_seconds
        
        with self._lock:
            for name in self.metrics:
                self.metrics[name] = [
                    m for m in self.metrics[name]
                    if m.timestamp > cutoff_time
                ]


class DashboardService:
    """
    Provides dashboard-ready data about system status.
    
    Aggregates health, metrics, and trace information into
    a format suitable for real-time dashboards.
    """
    
    def __init__(
        self,
        tracing: TracingService,
        metrics: MetricsCollector,
    ):
        """
        Initialize dashboard service.
        
        Args:
            tracing: TracingService instance
            metrics: MetricsCollector instance
        """
        self.tracing = tracing
        self.metrics = metrics
        self.logger = get_logger(__name__)
    
    def get_dashboard_data(
        self,
        include_traces: bool = True,
        include_metrics: bool = True,
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.
        
        Args:
            include_traces: Include trace data
            include_metrics: Include metrics data
            
        Returns:
            Dashboard-ready data
        """
        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_time": time.time(),
        }
        
        if include_metrics:
            dashboard["metrics"] = self._get_metrics_dashboard()
        
        if include_traces:
            dashboard["recent_traces"] = self._get_recent_traces()
        
        return dashboard
    
    def _get_metrics_dashboard(self) -> Dict[str, Any]:
        """Get metrics dashboard data."""
        return {
            "all_metrics": self.metrics.get_all_metrics(),
            "summaries": self._get_metric_summaries(),
        }
    
    def _get_metric_summaries(self) -> Dict[str, Any]:
        """Get summary statistics for all metrics."""
        summaries = {}
        
        for name in list(self.metrics.metrics.keys()):
            summary = self.metrics.get_metric_summary(name)
            if summary:
                summaries[name] = summary
        
        return summaries
    
    def _get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trace summaries."""
        all_trace_ids = set()
        for traces in self.tracing.spans.values():
            for span in traces:
                all_trace_ids.add(span.trace_id)
        
        # Get recent traces
        trace_ids = sorted(list(all_trace_ids))[-limit:]
        
        return [
            self._summarize_trace(trace_id)
            for trace_id in trace_ids
        ]
    
    def _summarize_trace(self, trace_id: str) -> Dict[str, Any]:
        """Summarize a trace."""
        spans = self.tracing.get_trace(trace_id)
        
        if not spans:
            return {"trace_id": trace_id, "error": "trace not found"}
        
        durations = [s.duration_ms for s in spans if s.duration_ms > 0]
        
        return {
            "trace_id": trace_id,
            "span_count": len(spans),
            "total_duration_ms": sum(durations),
            "avg_span_duration_ms": (
                sum(durations) / len(durations) if durations else 0
            ),
            "statuses": [s.status.value for s in spans],
            "status": "success" if all(s.status == SpanStatus.OK for s in spans) else "error",
        }


class ObservabilityOrchestrator:
    """
    Coordinates tracing, metrics, and dashboard services.
    
    Provides unified interface for observability across
    the entire autonomous healing system.
    """
    
    def __init__(self):
        """Initialize observability orchestrator."""
        self.tracing = TracingService()
        self.metrics = MetricsCollector()
        self.dashboard = DashboardService(self.tracing, self.metrics)
        self.logger = get_logger(__name__)
    
    def start_healing_trace(
        self,
        log_source: str,
        agent_type: str = "unknown",
    ) -> Span:
        """
        Start trace for a healing cycle.
        
        Args:
            log_source: Source of logs being analyzed
            agent_type: Type of agent being healed
            
        Returns:
            Root span for healing cycle
        """
        return self.tracing.start_span(
            name="healing_cycle",
            kind=SpanKind.SERVER,
            attributes={
                "log_source": log_source,
                "agent_type": agent_type,
            },
        )
    
    def start_child_span(
        self,
        parent_span: Span,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
    ) -> Span:
        """
        Start a child span.
        
        Args:
            parent_span: Parent span
            name: Child span name
            kind: Span kind
            
        Returns:
            New child span
        """
        return self.tracing.start_span(
            name=name,
            trace_id=parent_span.trace_id,
            parent_span_id=parent_span.span_id,
            kind=kind,
        )
    
    def record_healing_metric(
        self,
        metric_type: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Record a healing-related metric.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            labels: Metric labels
        """
        metric_name = f"phoenix.healing.{metric_type}"
        
        self.metrics.record_metric(
            name=metric_name,
            value=value,
            labels=labels or {},
        )
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard data."""
        return self.dashboard.get_dashboard_data()
    
    def export_trace(self, trace_id: str) -> Dict[str, Any]:
        """Export a trace."""
        return self.tracing.export_trace(trace_id)
