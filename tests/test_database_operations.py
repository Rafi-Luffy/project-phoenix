# Database Operations Integration Tests for Project Phoenix

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ===== System Model Tests =====

@pytest.mark.asyncio
@pytest.mark.database
class TestSystemModel:
    """Test System model operations"""
    
    async def test_create_system(self, db_session: AsyncSession):
        """Test creating a system"""
        from backend.models import System
        
        system = System(
            name="prod-api-server",
            description="Production API server",
            environment="production",
            threshold=0.85,
            is_active=True
        )
        db_session.add(system)
        await db_session.commit()
        await db_session.refresh(system)
        
        assert system.id is not None
        assert system.name == "prod-api-server"
        assert system.is_active is True
    
    async def test_update_system(self, db_session: AsyncSession, sample_system):
        """Test updating a system"""
        sample_system.description = "Updated description"
        sample_system.threshold = 0.95
        await db_session.commit()
        await db_session.refresh(sample_system)
        
        assert sample_system.description == "Updated description"
        assert sample_system.threshold == 0.95
    
    async def test_delete_system(self, db_session: AsyncSession, sample_system):
        """Test deleting a system"""
        system_id = sample_system.id
        await db_session.delete(sample_system)
        await db_session.commit()
        
        from backend.models import System
        result = await db_session.get(System, system_id)
        assert result is None
    
    async def test_system_relationships(self, db_session: AsyncSession, sample_system):
        """Test system relationships with other models"""
        from backend.models import Event, Policy
        
        # Create related records
        event = Event(
            system_id=sample_system.id,
            event_type="test",
            severity="low",
            data={"test": "data"}
        )
        policy = Policy(
            system_id=sample_system.id,
            name="test-policy",
            rules={"rule": "value"}
        )
        
        db_session.add_all([event, policy])
        await db_session.commit()
        
        # Verify relationships
        await db_session.refresh(sample_system)
        assert len(sample_system.events) > 0
        assert len(sample_system.policies) > 0

# ===== Event Model Tests =====

@pytest.mark.asyncio
@pytest.mark.database
class TestEventModel:
    """Test Event model operations"""
    
    async def test_create_event(self, db_session: AsyncSession, sample_system):
        """Test creating an event"""
        from backend.models import Event
        
        event = Event(
            system_id=sample_system.id,
            event_type="performance",
            severity="high",
            timestamp=datetime.utcnow(),
            data={"cpu": 85, "memory": 90},
            is_processed=False
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        assert event.id is not None
        assert event.event_type == "performance"
        assert event.is_processed is False
    
    async def test_event_filtering_by_severity(self, db_session: AsyncSession, sample_system):
        """Test filtering events by severity"""
        from backend.models import Event
        from sqlalchemy import select
        
        # Create events with different severities
        severities = ["low", "medium", "high", "critical"]
        for severity in severities:
            event = Event(
                system_id=sample_system.id,
                event_type="test",
                severity=severity,
                data={}
            )
            db_session.add(event)
        
        await db_session.commit()
        
        # Query high severity events
        stmt = select(Event).where(Event.severity == "high")
        result = await db_session.execute(stmt)
        events = result.scalars().all()
        
        assert len(events) >= 1
        assert all(e.severity == "high" for e in events)
    
    async def test_event_mark_processed(self, db_session: AsyncSession, sample_event):
        """Test marking event as processed"""
        sample_event.is_processed = True
        sample_event.processed_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(sample_event)
        
        assert sample_event.is_processed is True
        assert sample_event.processed_at is not None
    
    async def test_event_time_range_query(self, db_session: AsyncSession, sample_system):
        """Test querying events in time range"""
        from backend.models import Event
        from sqlalchemy import select
        
        now = datetime.utcnow()
        old_time = now - timedelta(hours=2)
        future_time = now + timedelta(hours=2)
        
        # Create event in range
        event_in_range = Event(
            system_id=sample_system.id,
            event_type="test",
            severity="low",
            timestamp=now,
            data={}
        )
        db_session.add(event_in_range)
        await db_session.commit()
        
        # Query time range
        stmt = select(Event).where(
            Event.timestamp.between(old_time, future_time)
        )
        result = await db_session.execute(stmt)
        events = result.scalars().all()
        
        assert len(events) > 0

# ===== Policy Model Tests =====

@pytest.mark.asyncio
@pytest.mark.database
class TestPolicyModel:
    """Test Policy model operations"""
    
    async def test_create_policy(self, db_session: AsyncSession, sample_system):
        """Test creating a policy"""
        from backend.models import Policy
        
        policy = Policy(
            name="auto-scale-policy",
            description="Scale up on high CPU",
            system_id=sample_system.id,
            rules={
                "metric": "cpu_usage",
                "threshold": 80,
                "action": "scale_up",
                "replicas": 5
            },
            is_active=True
        )
        db_session.add(policy)
        await db_session.commit()
        await db_session.refresh(policy)
        
        assert policy.id is not None
        assert policy.rules["threshold"] == 80
    
    async def test_policy_rules_json(self, db_session: AsyncSession, sample_policy):
        """Test policy rules JSON storage"""
        assert isinstance(sample_policy.rules, dict)
        assert "pattern" in sample_policy.rules
        assert sample_policy.rules["threshold"] == 0.7
    
    async def test_policy_enable_disable(self, db_session: AsyncSession, sample_policy):
        """Test enabling/disabling policies"""
        sample_policy.is_active = False
        await db_session.commit()
        await db_session.refresh(sample_policy)
        
        assert sample_policy.is_active is False
        
        sample_policy.is_active = True
        await db_session.commit()
        await db_session.refresh(sample_policy)
        
        assert sample_policy.is_active is True

# ===== Metric Model Tests =====

@pytest.mark.asyncio
@pytest.mark.database
class TestMetricModel:
    """Test Metric model operations"""
    
    async def test_create_metric(self, db_session: AsyncSession, sample_system):
        """Test creating a metric"""
        from backend.models import Metric
        
        metric = Metric(
            system_id=sample_system.id,
            metric_name="disk_usage",
            metric_value=72.5,
            unit="percent",
            timestamp=datetime.utcnow()
        )
        db_session.add(metric)
        await db_session.commit()
        await db_session.refresh(metric)
        
        assert metric.id is not None
        assert metric.metric_value == 72.5
    
    async def test_bulk_metric_insert(self, db_session: AsyncSession, sample_system):
        """Test bulk inserting metrics"""
        from backend.models import Metric
        
        metrics = [
            Metric(
                system_id=sample_system.id,
                metric_name=f"metric_{i}",
                metric_value=float(i * 10),
                unit="percent"
            )
            for i in range(100)
        ]
        
        db_session.add_all(metrics)
        await db_session.commit()
        
        from sqlalchemy import select, func
        stmt = select(func.count(Metric))
        result = await db_session.execute(stmt)
        count = result.scalar()
        
        assert count >= 100
    
    async def test_metric_aggregation(self, db_session: AsyncSession, sample_system):
        """Test metric aggregation queries"""
        from backend.models import Metric
        from sqlalchemy import select, func
        
        # Create multiple metrics
        for i in range(10):
            metric = Metric(
                system_id=sample_system.id,
                metric_name="cpu_usage",
                metric_value=50.0 + i,
                unit="percent"
            )
            db_session.add(metric)
        
        await db_session.commit()
        
        # Get average metric value
        stmt = select(func.avg(Metric.metric_value)).where(
            Metric.system_id == sample_system.id,
            Metric.metric_name == "cpu_usage"
        )
        result = await db_session.execute(stmt)
        avg_value = result.scalar()
        
        assert avg_value is not None
        assert 50 < avg_value < 60

# ===== Correction Model Tests =====

@pytest.mark.asyncio
@pytest.mark.database
class TestCorrectionModel:
    """Test Correction model operations"""
    
    async def test_create_correction(self, db_session: AsyncSession, sample_event):
        """Test creating a correction"""
        from backend.models import Correction
        
        correction = Correction(
            event_id=sample_event.id,
            action="restart_service",
            parameters={"service_name": "api", "timeout": 30},
            status="pending"
        )
        db_session.add(correction)
        await db_session.commit()
        await db_session.refresh(correction)
        
        assert correction.id is not None
        assert correction.status == "pending"
    
    async def test_correction_status_update(self, db_session: AsyncSession, sample_event):
        """Test updating correction status"""
        from backend.models import Correction
        
        correction = Correction(
            event_id=sample_event.id,
            action="scale_up",
            parameters={},
            status="pending"
        )
        db_session.add(correction)
        await db_session.commit()
        
        correction.status = "in_progress"
        await db_session.commit()
        await db_session.refresh(correction)
        assert correction.status == "in_progress"
        
        correction.status = "completed"
        correction.completed_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(correction)
        
        assert correction.status == "completed"
        assert correction.completed_at is not None

# ===== Database Constraints =====

@pytest.mark.asyncio
@pytest.mark.database
class TestDatabaseConstraints:
    """Test database constraints and validations"""
    
    async def test_unique_system_name(self, db_session: AsyncSession):
        """Test unique constraint on system name"""
        from backend.models import System
        from sqlalchemy.exc import IntegrityError
        
        system1 = System(name="unique-system", environment="test")
        system2 = System(name="unique-system", environment="test")
        
        db_session.add(system1)
        await db_session.commit()
        
        db_session.add(system2)
        with pytest.raises(IntegrityError):
            await db_session.commit()
        
        await db_session.rollback()
    
    async def test_foreign_key_constraint(self, db_session: AsyncSession):
        """Test foreign key constraint"""
        from backend.models import Event
        from sqlalchemy.exc import IntegrityError
        
        # Create event with non-existent system_id
        event = Event(
            system_id=99999,
            event_type="test",
            severity="low",
            data={}
        )
        
        db_session.add(event)
        with pytest.raises(IntegrityError):
            await db_session.commit()
        
        await db_session.rollback()
    
    async def test_not_null_constraint(self, db_session: AsyncSession, sample_system):
        """Test NOT NULL constraint"""
        from backend.models import Event
        from sqlalchemy.exc import IntegrityError
        
        # Event without required fields
        event = Event(system_id=sample_system.id)
        # Don't set required fields
        
        db_session.add(event)
        with pytest.raises((IntegrityError, AttributeError)):
            await db_session.commit()
        
        await db_session.rollback()

# ===== Transaction Tests =====

@pytest.mark.asyncio
@pytest.mark.database
class TestDatabaseTransactions:
    """Test database transaction behavior"""
    
    async def test_rollback_on_error(self, db_session: AsyncSession, sample_system):
        """Test rollback on error"""
        from backend.models import Event
        
        try:
            event = Event(
                system_id=sample_system.id,
                event_type="test",
                severity="low",
                data={}
            )
            db_session.add(event)
            await db_session.commit()
            
            # Force error
            raise ValueError("Test error")
        except ValueError:
            await db_session.rollback()
        
        # Connection should still be usable
        from sqlalchemy import select
        stmt = select(Event)
        result = await db_session.execute(stmt)
        events = result.scalars().all()
        assert isinstance(events, list)
    
    async def test_concurrent_access(self, async_session_factory):
        """Test concurrent database access"""
        from backend.models import System
        import asyncio
        
        async def create_system(name):
            async with async_session_factory() as session:
                system = System(name=name, environment="test")
                session.add(system)
                await session.commit()
                return system.id
        
        # Create systems concurrently
        tasks = [
            create_system(f"concurrent-system-{i}")
            for i in range(5)
        ]
        
        ids = await asyncio.gather(*tasks)
        assert len(ids) == 5
        assert all(id is not None for id in ids)
