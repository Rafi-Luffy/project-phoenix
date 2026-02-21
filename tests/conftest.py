# Test Configuration and Fixtures for Project Phoenix

import os
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
import redis
from celery import Celery
from celery.result import AsyncResult
import testcontainers.compose
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== Test Database Configuration =====

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def docker_compose():
    """Start docker compose test environment"""
    env_file = os.path.join(os.path.dirname(__file__), '../docker-compose.test.yml')
    
    try:
        # Try new API (testcontainers >= 3.7.0)
        compose = testcontainers.compose.DockerCompose(
            compose_file_path=os.path.dirname(env_file),
            compose_file_name=os.path.basename(env_file),
            pull=True
        )
    except TypeError:
        try:
            # Try old API
            compose = testcontainers.compose.DockerCompose(
                filepath=os.path.dirname(env_file),
                compose_file_name=os.path.basename(env_file),
                pull=True
            )
        except TypeError:
            # If docker compose file doesn't exist, skip this fixture
            logger.warning(f"docker-compose.test.yml not found, tests will run without Docker Compose")
            yield None
            return
    
    try:
        with compose:
            yield compose
    except Exception as e:
        logger.warning(f"Docker Compose startup failed: {e}, continuing with tests")
        yield None

@pytest.fixture(scope="session")
async def async_engine():
    """Create async SQLAlchemy engine for tests"""
    # Use SQLite in-memory for fast testing, or PostgreSQL test container
    database_url = os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite+aiosqlite:///:memory:"
    )
    
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        poolclass=StaticPool if "sqlite" in database_url else None,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        try:
            from autonomous_system.core.database import Base
        except ImportError:
            try:
                from backend.models import Base
            except ImportError:
                # Use a fallback Base
                from sqlalchemy.orm import declarative_base
                Base = declarative_base()
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()

@pytest.fixture(scope="session")
async def async_session_factory(async_engine):
    """Create async session factory"""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return async_session

@pytest.fixture
async def db_session(async_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with async_session_factory() as session:
        yield session
        # Rollback after each test
        await session.rollback()

# ===== FastAPI Test Client =====

@pytest.fixture
async def client(async_engine, db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create FastAPI test client"""
    from backend.main import app
    from backend.database import get_session
    
    # Override dependency
    async def override_get_session():
        return db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# ===== Redis Test Fixture =====

@pytest.fixture(scope="session")
def redis_client():
    """Create test Redis client"""
    redis_url = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/0")
    client = redis.from_url(redis_url, decode_responses=True)
    
    try:
        client.ping()
        yield client
    finally:
        client.flushdb()
        client.close()

@pytest.fixture
def redis_flush(redis_client):
    """Flush Redis before each test"""
    redis_client.flushdb()
    yield redis_client
    redis_client.flushdb()

# ===== Celery Test Fixture =====

@pytest.fixture(scope="session")
def celery_config():
    """Celery test configuration"""
    return {
        'broker_url': os.environ.get("TEST_CELERY_BROKER", "redis://localhost:6379/1"),
        'result_backend': os.environ.get("TEST_CELERY_BACKEND", "redis://localhost:6379/2"),
        'task_always_eager': True,  # Execute tasks synchronously in tests
        'task_eager_propagates': True,
    }

@pytest.fixture(scope="session")
def celery_app(celery_config):
    """Create test Celery app"""
    from backend.tasks import celery_app as app
    app.conf.update(celery_config)
    return app

# ===== Test Data Factories =====

@pytest.fixture
async def sample_system(db_session):
    """Create sample system for testing"""
    from backend.models import System
    
    system = System(
        name="test-system",
        description="Test system",
        environment="test",
        threshold=0.8,
        is_active=True
    )
    db_session.add(system)
    await db_session.commit()
    return system

@pytest.fixture
async def sample_policy(db_session, sample_system):
    """Create sample policy for testing"""
    from backend.models import Policy
    
    policy = Policy(
        name="test-policy",
        description="Test policy",
        system_id=sample_system.id,
        rules={"pattern": "test.*", "threshold": 0.7},
        is_active=True
    )
    db_session.add(policy)
    await db_session.commit()
    return policy

@pytest.fixture
async def sample_event(db_session, sample_system):
    """Create sample event for testing"""
    from backend.models import Event
    from datetime import datetime
    
    event = Event(
        system_id=sample_system.id,
        event_type="anomaly",
        severity="high",
        timestamp=datetime.utcnow(),
        data={"metric": "cpu", "value": 95},
        is_processed=False
    )
    db_session.add(event)
    await db_session.commit()
    return event

@pytest.fixture
async def sample_metric(db_session, sample_system):
    """Create sample metric for testing"""
    from backend.models import Metric
    from datetime import datetime
    
    metric = Metric(
        system_id=sample_system.id,
        metric_name="cpu_usage",
        metric_value=45.5,
        unit="percent",
        timestamp=datetime.utcnow()
    )
    db_session.add(metric)
    await db_session.commit()
    return metric

# ===== Mock Fixtures =====

@pytest.fixture
def mock_aws_service(monkeypatch):
    """Mock AWS service calls"""
    def mock_s3_upload(bucket, key, data):
        return f"s3://{bucket}/{key}"
    
    def mock_lambda_invoke(function_name, payload):
        return {"StatusCode": 202, "FunctionArn": f"arn:aws:lambda:us-east-1:123456789:function:{function_name}"}
    
    # Mock boto3 calls here
    yield {
        "s3_upload": mock_s3_upload,
        "lambda_invoke": mock_lambda_invoke
    }

@pytest.fixture
def mock_external_api(monkeypatch):
    """Mock external API calls"""
    async def mock_get_data(url):
        return {"status": "ok", "data": []}
    
    async def mock_post_data(url, data):
        return {"status": "created", "id": "12345"}
    
    yield {
        "get_data": mock_get_data,
        "post_data": mock_post_data
    }

# ===== Performance Testing Fixtures =====

@pytest.fixture
def benchmark_timer():
    """Timer for performance benchmarks"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.elapsed = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, *args):
            self.elapsed = time.time() - self.start_time
        
        def assert_under(self, seconds):
            assert self.elapsed < seconds, f"Test took {self.elapsed}s, expected < {seconds}s"
    
    return Timer

# ===== Test Markers =====

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "database: marks tests as requiring database"
    )
    config.addinivalue_line(
        "markers", "cache: marks tests as requiring cache/Redis"
    )
    config.addinivalue_line(
        "markers", "queue: marks tests as requiring message queue"
    )
    config.addinivalue_line(
        "markers", "external: marks tests as requiring external services"
    )

# ===== Test Configuration =====

@pytest.fixture
def test_config():
    """Return test configuration"""
    return {
        "DATABASE_URL": os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:"),
        "REDIS_URL": os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/0"),
        "CELERY_BROKER": os.environ.get("TEST_CELERY_BROKER", "redis://localhost:6379/1"),
        "API_BASE_URL": "http://test",
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG"
    }
