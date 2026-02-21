"""
Observability System Tests

Tests distributed tracing, metrics collection, and dashboards.
"""

import pytest
import time
from phoenix.core.observability import (
    TracingService,
    MetricsCollector,
    DashboardService,
    ObservabilityOrchestrator,
    Span,
    Metric,
    SpanKind,
    SpanStatus,
)


# ============ Span Tests ============

class TestSpan:
    """Test Span class."""
    
    def test_span_creation(self):
        """Test creating a span."""
        span = Span(
            trace_id="trace_123",
            span_id="span_456",
            name="test_operation",
        )
        
        assert span.trace_id == "trace_123"
        assert span.span_id == "span_456"
        assert span.name == "test_operation"
        assert span.status == SpanStatus.UNSET
    
    def test_span_finish(self):
        """Test finishing a span."""
        span = Span(trace_id="t1", span_id="s1", name="test")
        
        time.sleep(0.01)
        span.finish(SpanStatus.OK, "completed")
        
        assert span.status == SpanStatus.OK
        assert span.status_message == "completed"
        assert span.end_time is not None
    
    def test_span_duration(self):
        """Test span duration calculation."""
        span = Span(trace_id="t1", span_id="s1", name="test")
        
        time.sleep(0.05)
        span.finish()
        
        assert span.duration_ms >= 50
    
    def test_span_add_event(self):
        """Test adding events to span."""
        span = Span(trace_id="t1", span_id="s1", name="test")
        
        span.add_event("started")
        span.add_event("processing", {"items": 10})
        span.add_event("finished")
        
        assert len(span.events) == 3
        assert span.events[0]["name"] == "started"
        assert span.events[1]["attributes"]["items"] == 10
    
    def test_span_attributes(self):
        """Test span attributes."""
        span = Span(
            trace_id="t1",
            span_id="s1",
            name="test",
            attributes={"user_id": "123", "action": "heal"},
        )
        
        assert span.attributes["user_id"] == "123"
        assert span.attributes["action"] == "heal"
    
    def test_span_to_dict(self):
        """Test converting span to dictionary."""
        span = Span(
            trace_id="t1",
            span_id="s1",
            name="test",
            kind=SpanKind.SERVER,
        )
        
        span.finish(SpanStatus.OK)
        
        data = span.to_dict()
        
        assert data["trace_id"] == "t1"
        assert data["span_id"] == "s1"
        assert data["name"] == "test"
        assert data["kind"] == "server"
        assert data["status"] == "ok"
        assert "duration_ms" in data


# ============ Metric Tests ============

class TestMetric:
    """Test Metric class."""
    
    def test_metric_creation(self):
        """Test creating a metric."""
        metric = Metric(
            name="healing_latency",
            description="Time to heal",
            unit="ms",
            value=42.5,
        )
        
        assert metric.name == "healing_latency"
        assert metric.value == 42.5
        assert metric.unit == "ms"
    
    def test_metric_labels(self):
        """Test metric labels."""
        metric = Metric(
            name="failures",
            value=5,
            labels={"agent_type": "data_pipeline", "status": "resolved"},
        )
        
        assert metric.labels["agent_type"] == "data_pipeline"
        assert metric.labels["status"] == "resolved"
    
    def test_metric_to_dict(self):
        """Test converting metric to dictionary."""
        metric = Metric(
            name="test_metric",
            value=123.45,
            unit="ms",
        )
        
        data = metric.to_dict()
        
        assert data["name"] == "test_metric"
        assert data["value"] == 123.45
        assert data["unit"] == "ms"
        assert "timestamp" in data


# ============ TracingService Tests ============

class TestTracingService:
    """Test TracingService class."""
    
    @pytest.fixture
    def tracing(self):
        """Create tracing service."""
        return TracingService()
    
    def test_start_span(self, tracing):
        """Test starting a span."""
        span = tracing.start_span(
            name="test_operation",
            kind=SpanKind.INTERNAL,
        )
        
        assert span.name == "test_operation"
        assert span.kind == SpanKind.INTERNAL
        assert span.trace_id is not None
        assert span.span_id is not None
    
    def test_finish_span(self, tracing):
        """Test finishing a span."""
        span = tracing.start_span("test")
        
        tracing.finish_span(span.span_id, SpanStatus.OK)
        
        assert span.status == SpanStatus.OK
        assert span.end_time is not None
    
    def test_parent_child_spans(self, tracing):
        """Test parent-child span relationships."""
        parent = tracing.start_span("parent")
        
        child = tracing.start_span(
            "child",
            trace_id=parent.trace_id,
            parent_span_id=parent.span_id,
        )
        
        assert child.trace_id == parent.trace_id
        assert child.parent_span_id == parent.span_id
    
    def test_get_trace(self, tracing):
        """Test retrieving trace spans."""
        span1 = tracing.start_span("operation_1")
        span2 = tracing.start_span(
            "operation_2",
            trace_id=span1.trace_id,
        )
        
        spans = tracing.get_trace(span1.trace_id)
        
        assert len(spans) == 2
        assert spans[0].span_id == span1.span_id
        assert spans[1].span_id == span2.span_id
    
    def test_export_trace(self, tracing):
        """Test exporting a trace."""
        span = tracing.start_span("test")
        span.add_event("progress")
        tracing.finish_span(span.span_id)
        
        exported = tracing.export_trace(span.trace_id)
        
        assert exported["trace_id"] == span.trace_id
        assert exported["span_count"] == 1
        assert len(exported["spans"]) == 1


# ============ MetricsCollector Tests ============

class TestMetricsCollector:
    """Test MetricsCollector class."""
    
    @pytest.fixture
    def collector(self):
        """Create metrics collector."""
        return MetricsCollector()
    
    def test_record_metric(self, collector):
        """Test recording a metric."""
        collector.record_metric(
            "response_time",
            42.5,
            unit="ms",
            labels={"endpoint": "/heal"},
        )
        
        metrics = collector.get_all_metrics()
        
        assert "response_time" in metrics
        assert len(metrics["response_time"]) == 1
        assert metrics["response_time"][0]["value"] == 42.5
    
    def test_get_metric_summary(self, collector):
        """Test getting metric summary."""
        for i in range(5):
            collector.record_metric("latency", 10 + i)
        
        summary = collector.get_metric_summary("latency")
        
        assert summary["count"] == 5
        assert summary["min"] == 10
        assert summary["max"] == 14
        assert summary["avg"] == 12
    
    def test_multiple_metrics(self, collector):
        """Test recording multiple different metrics."""
        collector.record_metric("requests", 100)
        collector.record_metric("errors", 5)
        collector.record_metric("latency", 42.5)
        
        all_metrics = collector.get_all_metrics()
        
        assert len(all_metrics) == 3
    
    def test_metric_labels(self, collector):
        """Test metrics with labels."""
        collector.record_metric(
            "failures",
            3,
            labels={"agent": "pipeline_1", "type": "timeout"},
        )
        
        metrics = collector.get_all_metrics()
        
        recorded_metric = metrics["failures"][0]
        assert recorded_metric["labels"]["agent"] == "pipeline_1"


# ============ DashboardService Tests ============

class TestDashboardService:
    """Test DashboardService class."""
    
    @pytest.fixture
    def dashboard(self):
        """Create dashboard service."""
        tracing = TracingService()
        metrics = MetricsCollector()
        return DashboardService(tracing, metrics)
    
    def test_get_dashboard_data(self, dashboard):
        """Test getting dashboard data."""
        data = dashboard.get_dashboard_data()
        
        assert "timestamp" in data
        assert "metrics" in data
        assert "recent_traces" in data
    
    def test_dashboard_with_metrics(self, dashboard):
        """Test dashboard with metrics data."""
        dashboard.metrics.record_metric("test_metric", 42)
        
        data = dashboard.get_dashboard_data(include_traces=False)
        
        assert "metrics" in data
        assert len(data["metrics"]["all_metrics"]) > 0
    
    def test_dashboard_with_traces(self, dashboard):
        """Test dashboard with trace data."""
        span = dashboard.tracing.start_span("test")
        dashboard.tracing.finish_span(span.span_id)
        
        data = dashboard.get_dashboard_data(include_metrics=False)
        
        assert "recent_traces" in data
        assert len(data["recent_traces"]) > 0


# ============ ObservabilityOrchestrator Tests ============

class TestObservabilityOrchestrator:
    """Test ObservabilityOrchestrator class."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create observability orchestrator."""
        return ObservabilityOrchestrator()
    
    def test_orchestrator_components(self, orchestrator):
        """Test orchestrator has all components."""
        assert isinstance(orchestrator.tracing, TracingService)
        assert isinstance(orchestrator.metrics, MetricsCollector)
        assert isinstance(orchestrator.dashboard, DashboardService)
    
    def test_start_healing_trace(self, orchestrator):
        """Test starting healing trace."""
        span = orchestrator.start_healing_trace(
            log_source="stdout",
            agent_type="data_processor",
        )
        
        assert span.name == "healing_cycle"
        assert span.kind == SpanKind.SERVER
        assert span.attributes["log_source"] == "stdout"
        assert span.attributes["agent_type"] == "data_processor"
    
    def test_child_span(self, orchestrator):
        """Test creating child span."""
        parent = orchestrator.start_healing_trace("test")
        child = orchestrator.start_child_span(
            parent,
            name="fix_generation",
        )
        
        assert child.parent_span_id == parent.span_id
        assert child.trace_id == parent.trace_id
    
    def test_record_healing_metric(self, orchestrator):
        """Test recording healing metric."""
        orchestrator.record_healing_metric(
            "fixes_applied",
            5,
            labels={"status": "success"},
        )
        
        metrics = orchestrator.metrics.get_all_metrics()
        
        assert "phoenix.healing.fixes_applied" in metrics
    
    def test_get_dashboard(self, orchestrator):
        """Test getting dashboard data."""
        # Create some data
        span = orchestrator.start_healing_trace("test")
        orchestrator.record_healing_metric("latency", 42)
        orchestrator.tracing.finish_span(span.span_id)
        
        data = orchestrator.get_dashboard()
        
        assert "timestamp" in data
        assert "metrics" in data
        assert "recent_traces" in data
    
    def test_export_trace(self, orchestrator):
        """Test exporting trace."""
        span = orchestrator.start_healing_trace("test")
        orchestrator.tracing.finish_span(span.span_id)
        
        exported = orchestrator.export_trace(span.trace_id)
        
        assert exported["trace_id"] == span.trace_id
        assert exported["span_count"] == 1


# ============ Integration Tests ============

class TestObservabilityIntegration:
    """Integration tests for observability system."""
    
    def test_complete_healing_trace(self):
        """Test tracing a complete healing cycle."""
        obs = ObservabilityOrchestrator()
        
        # Start healing trace
        root = obs.start_healing_trace("logs", "pipeline")
        
        # Detection phase
        detection = obs.start_child_span(root, "failure_detection")
        obs.record_healing_metric("failures_detected", 3)
        obs.tracing.finish_span(detection.span_id)
        
        # Fix generation phase
        generation = obs.start_child_span(root, "fix_generation")
        obs.record_healing_metric("fix_latency_ms", 2500)
        obs.tracing.finish_span(generation.span_id)
        
        # Application phase
        application = obs.start_child_span(root, "fix_application")
        obs.record_healing_metric("fixes_applied", 3)
        obs.record_healing_metric("fixes_successful", 2)
        obs.tracing.finish_span(application.span_id)
        
        # Finish root
        obs.tracing.finish_span(root.span_id)
        
        # Export and verify
        exported = obs.export_trace(root.trace_id)
        
        assert exported["span_count"] == 4  # root + 3 children
        assert len(exported["spans"]) == 4
    
    def test_dashboard_with_multiple_metrics(self):
        """Test dashboard aggregating multiple metrics."""
        obs = ObservabilityOrchestrator()
        
        # Record various metrics
        for i in range(10):
            obs.record_healing_metric("latency_ms", 100 + i * 10)
            obs.record_healing_metric("success_rate", 0.8 + (i * 0.01))
        
        # Get dashboard
        data = obs.get_dashboard()
        
        # Check summaries
        assert "metrics" in data
        assert len(data["metrics"]["summaries"]) > 0


# ============ Performance Tests ============

class TestObservabilityPerformance:
    """Test performance of observability system."""
    
    def test_span_creation_performance(self):
        """Test span creation is fast."""
        tracing = TracingService()
        
        start = time.time()
        for i in range(100):
            tracing.start_span(f"span_{i}")
        elapsed = time.time() - start
        
        # Should be very fast (under 100ms for 100 spans)
        assert elapsed < 0.1
    
    def test_metric_recording_performance(self):
        """Test metric recording is fast."""
        collector = MetricsCollector()
        
        start = time.time()
        for i in range(1000):
            collector.record_metric("test", float(i))
        elapsed = time.time() - start
        
        # Should be very fast (under 100ms for 1000 metrics)
        assert elapsed < 0.1
    
    def test_dashboard_generation_performance(self):
        """Test dashboard generation is fast."""
        obs = ObservabilityOrchestrator()
        
        # Add some data
        for i in range(50):
            span = obs.start_healing_trace(f"trace_{i}")
            obs.record_healing_metric("latency", 100 + i)
            obs.tracing.finish_span(span.span_id)
        
        # Generate dashboard
        start = time.time()
        data = obs.get_dashboard()
        elapsed = time.time() - start
        
        # Should be fast (under 100ms)
        assert elapsed < 0.1
        assert "recent_traces" in data
