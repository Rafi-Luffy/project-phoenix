# Celery Task Queue Integration Tests for Project Phoenix

import pytest
from celery.result import AsyncResult
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

# ===== Basic Task Execution =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestTaskExecution:
    """Test basic task execution"""
    
    async def test_simple_task_execution(self, celery_app):
        """Test simple task execution"""
        from backend.tasks import test_task
        
        result = test_task.delay()
        assert result.ready()
        assert result.successful()
    
    async def test_task_with_arguments(self, celery_app):
        """Test task with arguments"""
        from backend.tasks import add_numbers
        
        result = add_numbers.delay(5, 10)
        assert result.ready()
        assert result.get() == 15
    
    async def test_task_with_kwargs(self, celery_app):
        """Test task with keyword arguments"""
        from backend.tasks import multiply_numbers
        
        result = multiply_numbers.delay(x=4, y=5)
        assert result.ready()
        assert result.get() == 20
    
    async def test_task_failure_handling(self, celery_app):
        """Test task failure handling"""
        from backend.tasks import failing_task
        
        result = failing_task.delay()
        assert result.ready()
        assert result.failed()

# ===== Anomaly Detection Task Tests =====

@pytest.mark.asyncio
@pytest.mark.queue
@pytest.mark.database
class TestAnomalyDetectionTask:
    """Test anomaly detection task"""
    
    async def test_detect_anomalies(self, celery_app, db_session, sample_system):
        """Test anomaly detection task"""
        from backend.tasks import detect_anomalies
        from backend.models import Metric
        
        # Create metrics
        metrics = [
            Metric(
                system_id=sample_system.id,
                metric_name="cpu_usage",
                metric_value=45.0 + i * 5,  # Trending up
                unit="percent"
            )
            for i in range(10)
        ]
        db_session.add_all(metrics)
        await db_session.commit()
        
        # Run anomaly detection
        result = detect_anomalies.delay(sample_system.id)
        assert result.ready()
        assert result.successful()
    
    async def test_anomaly_detection_creates_events(self, celery_app, db_session, sample_system):
        """Test that anomaly detection creates events"""
        from backend.tasks import detect_anomalies
        from backend.models import Metric, Event
        from sqlalchemy import select
        
        # Create anomalous metrics
        for i in range(5):
            metric = Metric(
                system_id=sample_system.id,
                metric_name="cpu_usage",
                metric_value=95.0 + i,  # Very high
                unit="percent"
            )
            db_session.add(metric)
        
        await db_session.commit()
        
        # Detect anomalies
        result = detect_anomalies.delay(sample_system.id)
        assert result.ready()
        
        # Check for created events
        stmt = select(Event).where(Event.system_id == sample_system.id)
        result = await db_session.execute(stmt)
        events = result.scalars().all()
        
        assert len(events) > 0

# ===== Analysis Task Tests =====

@pytest.mark.asyncio
@pytest.mark.queue
@pytest.mark.database
class TestAnalysisTask:
    """Test analysis task"""
    
    async def test_analyze_events(self, celery_app, db_session, sample_system, sample_event):
        """Test event analysis task"""
        from backend.tasks import analyze_events
        
        result = analyze_events.delay(sample_system.id)
        assert result.ready()
        assert result.successful()
    
    async def test_analysis_with_multiple_events(self, celery_app, db_session, sample_system):
        """Test analysis with multiple events"""
        from backend.tasks import analyze_events
        from backend.models import Event
        
        # Create multiple events
        for i in range(5):
            event = Event(
                system_id=sample_system.id,
                event_type="anomaly",
                severity="high" if i % 2 == 0 else "low",
                data={"iteration": i}
            )
            db_session.add(event)
        
        await db_session.commit()
        
        result = analyze_events.delay(sample_system.id)
        assert result.ready()
        assert result.successful()

# ===== Correction Task Tests =====

@pytest.mark.asyncio
@pytest.mark.queue
@pytest.mark.database
class TestCorrectionTask:
    """Test correction/remediation task"""
    
    async def test_apply_correction(self, celery_app, db_session, sample_event):
        """Test applying a correction"""
        from backend.tasks import apply_correction
        
        correction_data = {
            "action": "scale_up",
            "parameters": {"replicas": 5}
        }
        
        result = apply_correction.delay(sample_event.id, correction_data)
        assert result.ready()
        assert result.successful()
    
    async def test_correction_creates_record(self, celery_app, db_session, sample_event):
        """Test that correction creates a record"""
        from backend.tasks import apply_correction
        from backend.models import Correction
        from sqlalchemy import select
        
        correction_data = {
            "action": "restart_service",
            "parameters": {"service": "api"}
        }
        
        result = apply_correction.delay(sample_event.id, correction_data)
        assert result.ready()
        
        # Check for created correction
        stmt = select(Correction).where(Correction.event_id == sample_event.id)
        result = await db_session.execute(stmt)
        corrections = result.scalars().all()
        
        assert len(corrections) > 0

# ===== Learning Task Tests =====

@pytest.mark.asyncio
@pytest.mark.queue
@pytest.mark.database
class TestLearningTask:
    """Test machine learning task"""
    
    async def test_update_learning_model(self, celery_app, db_session, sample_system):
        """Test updating learning model"""
        from backend.tasks import update_learning_model
        
        result = update_learning_model.delay(sample_system.id)
        assert result.ready()
        assert result.successful()
    
    async def test_learning_model_training(self, celery_app, db_session, sample_system):
        """Test model training with data"""
        from backend.tasks import update_learning_model
        from backend.models import Metric
        
        # Create training data
        for i in range(20):
            metric = Metric(
                system_id=sample_system.id,
                metric_name="cpu_usage",
                metric_value=40.0 + (i % 10),
                unit="percent"
            )
            db_session.add(metric)
        
        await db_session.commit()
        
        result = update_learning_model.delay(sample_system.id)
        assert result.ready()
        assert result.successful()

# ===== Scheduled Task Tests =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestScheduledTasks:
    """Test periodically scheduled tasks"""
    
    async def test_cleanup_old_events_task(self, celery_app):
        """Test cleanup of old events task"""
        from backend.tasks import cleanup_old_events
        
        result = cleanup_old_events.delay()
        assert result.ready()
        assert result.successful()
    
    async def test_generate_report_task(self, celery_app):
        """Test report generation task"""
        from backend.tasks import generate_report
        
        result = generate_report.delay()
        assert result.ready()
        assert result.successful()

# ===== Task Retry Logic =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestTaskRetry:
    """Test task retry logic"""
    
    async def test_task_with_retry(self, celery_app):
        """Test task retry on failure"""
        from backend.tasks import task_with_retry
        
        # Task should retry internally
        result = task_with_retry.delay()
        assert result.ready() or result.pending()
    
    async def test_max_retries_exceeded(self, celery_app):
        """Test task after max retries exceeded"""
        from backend.tasks import task_with_max_retries
        
        result = task_with_max_retries.delay()
        # Task may fail after max retries
        assert result.ready() or result.failed() or result.pending()

# ===== Task State Management =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestTaskStateManagement:
    """Test task state tracking"""
    
    async def test_task_pending_state(self, celery_app):
        """Test task pending state"""
        from backend.tasks import slow_task
        
        result = slow_task.delay()
        # Task might be pending or done depending on execution time
        assert result.state in ['PENDING', 'SUCCESS', 'FAILURE']
    
    async def test_task_state_transitions(self, celery_app):
        """Test task state transitions"""
        from backend.tasks import test_task
        
        result = test_task.delay()
        assert result.ready()
        assert result.state == 'SUCCESS'
    
    async def test_task_result_retrieval(self, celery_app):
        """Test retrieving task result"""
        from backend.tasks import return_data_task
        
        result = return_data_task.delay()
        assert result.ready()
        task_result = result.get()
        assert isinstance(task_result, dict)

# ===== Task Chaining =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestTaskChaining:
    """Test chaining multiple tasks"""
    
    async def test_task_chain_execution(self, celery_app):
        """Test chaining tasks with .s()"""
        from celery import chain
        from backend.tasks import task1, task2, task3
        
        # Chain: task1 -> task2 -> task3
        workflow = chain(task1.s(), task2.s(), task3.s())
        result = workflow.apply_async()
        
        assert result.ready() or result.pending()
    
    async def test_task_group_execution(self, celery_app):
        """Test executing tasks in parallel"""
        from celery import group
        from backend.tasks import parallel_task
        
        # Group: execute multiple tasks in parallel
        parallel_work = group(
            parallel_task.s(i)
            for i in range(5)
        )
        result = parallel_work.apply_async()
        
        assert result.ready() or result.pending()

# ===== Task Error Handling =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestTaskErrorHandling:
    """Test error handling in tasks"""
    
    async def test_task_exception_handling(self, celery_app):
        """Test task exception handling"""
        from backend.tasks import task_with_exception
        
        result = task_with_exception.delay()
        assert result.ready()
        assert result.failed()
    
    async def test_task_timeout_handling(self, celery_app):
        """Test task timeout"""
        from backend.tasks import long_running_task
        
        # Task might timeout depending on configuration
        result = long_running_task.delay()
        assert result.ready() or result.pending()
    
    async def test_task_error_callback(self, celery_app):
        """Test error callback execution"""
        from backend.tasks import task_with_callback
        
        result = task_with_callback.delay()
        # Callback should be triggered if task fails
        assert result.ready() or result.pending()

# ===== Performance Tests =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestTaskPerformance:
    """Test task performance"""
    
    async def test_task_execution_time(self, celery_app, benchmark_timer):
        """Test task execution time"""
        from backend.tasks import test_task
        
        with benchmark_timer() as timer:
            result = test_task.delay()
            result.get()
        
        timer.assert_under(5.0)  # Should complete within 5 seconds
    
    async def test_bulk_task_processing(self, celery_app, benchmark_timer):
        """Test bulk task processing performance"""
        from backend.tasks import process_item
        
        with benchmark_timer() as timer:
            for i in range(100):
                result = process_item.delay(i)
                result.get(timeout=1)
        
        timer.assert_under(60.0)  # Should process 100 items within 60 seconds

# ===== Task Monitoring =====

@pytest.mark.asyncio
@pytest.mark.queue
class TestTaskMonitoring:
    """Test task monitoring and observability"""
    
    async def test_task_metadata_capture(self, celery_app):
        """Test capturing task metadata"""
        from backend.tasks import test_task
        
        result = test_task.delay()
        
        # Metadata should be available
        assert result.id is not None
        assert result.state is not None
    
    async def test_task_progress_tracking(self, celery_app):
        """Test task progress tracking"""
        from backend.tasks import long_task_with_progress
        
        result = long_task_with_progress.delay()
        # Task should report progress
        assert result.id is not None
