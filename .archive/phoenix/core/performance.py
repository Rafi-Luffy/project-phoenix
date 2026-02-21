"""
Performance Optimization Module
Provides async operations, connection pooling, batch processing, and caching
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Coroutine, TypeVar
from datetime import datetime, timedelta
from collections import deque
import asyncio
from enum import Enum
import time
from abc import ABC, abstractmethod


T = TypeVar('T')


class PoolStatus(Enum):
    """Connection pool status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    EXHAUSTED = "exhausted"


@dataclass
class PoolMetrics:
    """Connection pool metrics"""
    total_connections: int
    active_connections: int
    idle_connections: int
    connection_timeouts: int
    pool_exhausted_count: int
    avg_wait_time: float


class ConnectionPool:
    """Generic connection pool for resource management"""
    
    def __init__(self, factory: Callable, max_size: int = 100, timeout: float = 5.0):
        self.factory = factory
        self.max_size = max_size
        self.timeout = timeout
        self.available: deque = deque()
        self.in_use: set = set()
        self.lock = __import__('threading').Lock()
        self.condition = __import__('threading').Condition(self.lock)
        self.metrics = {
            "timeouts": 0,
            "exhausted_count": 0,
            "wait_times": deque(maxlen=1000)
        }
    
    def acquire(self) -> Any:
        """Acquire a connection from pool"""
        start_time = time.time()
        
        with self.condition:
            while True:
                # Try to get available connection
                if self.available:
                    conn = self.available.popleft()
                    self.in_use.add(conn)
                    wait_time = time.time() - start_time
                    self.metrics["wait_times"].append(wait_time)
                    return conn
                
                # Check if we can create new connection
                if len(self.in_use) < self.max_size:
                    conn = self.factory()
                    self.in_use.add(conn)
                    wait_time = time.time() - start_time
                    self.metrics["wait_times"].append(wait_time)
                    return conn
                
                # Wait for available connection
                if not self.condition.wait(timeout=self.timeout):
                    self.metrics["timeouts"] += 1
                    self.metrics["exhausted_count"] += 1
                    raise TimeoutError("Failed to acquire connection within timeout")
    
    def release(self, conn: Any):
        """Release a connection back to pool"""
        with self.condition:
            if conn in self.in_use:
                self.in_use.remove(conn)
                self.available.append(conn)
                self.condition.notify()
    
    def get_status(self) -> PoolStatus:
        """Get pool status"""
        with self.lock:
            if len(self.in_use) >= self.max_size:
                return PoolStatus.EXHAUSTED
            elif len(self.in_use) >= self.max_size * 0.8:
                return PoolStatus.DEGRADED
            return PoolStatus.HEALTHY
    
    def get_metrics(self) -> PoolMetrics:
        """Get pool metrics"""
        with self.lock:
            active = len(self.in_use)
            idle = len(self.available)
            avg_wait = sum(self.metrics["wait_times"]) / len(self.metrics["wait_times"]) \
                if self.metrics["wait_times"] else 0
            
            return PoolMetrics(
                total_connections=active + idle,
                active_connections=active,
                idle_connections=idle,
                connection_timeouts=self.metrics["timeouts"],
                pool_exhausted_count=self.metrics["exhausted_count"],
                avg_wait_time=avg_wait
            )


class BatchProcessor:
    """Processes items in batches for efficiency"""
    
    def __init__(self, batch_size: int = 100, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch: List[Any] = []
        self.lock = __import__('threading').Lock()
        self.last_flush = datetime.now()
        self.callbacks: List[Callable] = []
    
    def add_item(self, item: Any):
        """Add item to batch"""
        with self.lock:
            self.batch.append(item)
            
            # Auto-flush if batch is full
            if len(self.batch) >= self.batch_size:
                self._flush()
    
    def add_batch(self, items: List[Any]):
        """Add multiple items"""
        with self.lock:
            self.batch.extend(items)
            
            # Auto-flush if batch is full
            while len(self.batch) >= self.batch_size:
                self._flush()
    
    def flush(self):
        """Flush current batch"""
        with self.lock:
            self._flush()
    
    def _flush(self):
        """Internal flush (assumes lock held)"""
        if not self.batch:
            return
        
        batch_to_process = self.batch[:]
        self.batch = []
        self.last_flush = datetime.now()
        
        # Execute callbacks
        for callback in self.callbacks:
            try:
                callback(batch_to_process)
            except Exception:
                pass  # Silently handle callback errors
    
    def on_batch_ready(self, callback: Callable):
        """Register callback for batch processing"""
        with self.lock:
            self.callbacks.append(callback)
    
    def should_flush(self) -> bool:
        """Check if batch should be flushed by timeout"""
        elapsed = (datetime.now() - self.last_flush).total_seconds()
        with self.lock:
            return elapsed > self.flush_interval and len(self.batch) > 0


class AsyncExecutor:
    """Handles async operations and task scheduling"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = __import__('concurrent.futures').ThreadPoolExecutor(max_workers=max_workers)
        self.loop = None
        self.tasks: Dict[str, asyncio.Task] = {}
        self.lock = __import__('threading').Lock()
    
    def execute_async(self, func: Callable, *args, **kwargs):
        """Execute function asynchronously"""
        return self.executor.submit(func, *args, **kwargs)
    
    async def schedule_task(self, task_id: str, coro: Coroutine):
        """Schedule async coroutine"""
        task = asyncio.create_task(coro)
        with self.lock:
            self.tasks[task_id] = task
        
        try:
            return await task
        finally:
            with self.lock:
                self.tasks.pop(task_id, None)
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get task status"""
        with self.lock:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            if task.done():
                return "completed"
            return "running"


class LazyLoader:
    """Lazy loads resources on demand"""
    
    def __init__(self, factory: Callable):
        self.factory = factory
        self._instance = None
        self.lock = __import__('threading').Lock()
    
    def get(self) -> Any:
        """Get or create instance"""
        if self._instance is None:
            with self.lock:
                if self._instance is None:
                    self._instance = self.factory()
        return self._instance


class CompressionCache:
    """Caches compressed data for efficient storage"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = __import__('threading').Lock()
    
    @staticmethod
    def compress_data(data: Any) -> bytes:
        """Compress data"""
        import gzip
        import json
        
        json_data = json.dumps(data) if not isinstance(data, str) else data
        return gzip.compress(json_data.encode())
    
    @staticmethod
    def decompress_data(compressed: bytes) -> Any:
        """Decompress data"""
        import gzip
        import json
        
        decompressed = gzip.decompress(compressed).decode()
        return json.loads(decompressed)
    
    def put(self, key: str, data: Any):
        """Store compressed data"""
        compressed = self.compress_data(data)
        
        with self.lock:
            self.cache[key] = {
                "data": compressed,
                "size": len(compressed),
                "created_at": datetime.now()
            }
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve and decompress data"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            return self.decompress_data(entry["data"])
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics"""
        with self.lock:
            total_size = sum(e["size"] for e in self.cache.values())
            return {
                "entries": len(self.cache),
                "total_size_bytes": total_size,
                "avg_size_bytes": total_size / len(self.cache) if self.cache else 0
            }


class RequestDeduplicator:
    """Deduplicates identical concurrent requests"""
    
    def __init__(self, cache_duration: float = 5.0):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = cache_duration
        self.lock = __import__('threading').Lock()
    
    def should_deduplicate(self, request_key: str) -> bool:
        """Check if request should be deduplicated"""
        with self.lock:
            if request_key not in self.cache:
                return False
            
            entry = self.cache[request_key]
            elapsed = (datetime.now() - entry["timestamp"]).total_seconds()
            
            if elapsed > self.cache_duration:
                del self.cache[request_key]
                return False
            
            return True
    
    def get_cached_result(self, request_key: str) -> Optional[Any]:
        """Get cached result"""
        with self.lock:
            if request_key in self.cache:
                return self.cache[request_key]["result"]
        return None
    
    def cache_result(self, request_key: str, result: Any):
        """Cache request result"""
        with self.lock:
            self.cache[request_key] = {
                "result": result,
                "timestamp": datetime.now()
            }


class QueryOptimizer:
    """Optimizes query patterns"""
    
    def __init__(self):
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.lock = __import__('threading').Lock()
    
    def suggest_index(self, query_pattern: str) -> Optional[str]:
        """Suggest index for query pattern"""
        with self.lock:
            if query_pattern not in self.patterns:
                self.patterns[query_pattern] = {
                    "count": 0,
                    "total_time": 0
                }
            
            pattern = self.patterns[query_pattern]
            pattern["count"] += 1
            
            # Suggest index for frequent queries
            if pattern["count"] > 100:
                return f"CREATE INDEX idx_{query_pattern.replace(' ', '_')} ON ..."
        
        return None


class PerformanceMonitor:
    """Monitors performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.lock = __import__('threading').Lock()
    
    def record_operation(self, operation_name: str, duration: float):
        """Record operation duration"""
        with self.lock:
            if operation_name not in self.metrics:
                self.metrics[operation_name] = deque(maxlen=10000)
            self.metrics[operation_name].append(duration)
    
    def get_statistics(self, operation_name: str) -> Optional[Dict[str, float]]:
        """Get performance statistics"""
        with self.lock:
            if operation_name not in self.metrics:
                return None
            
            times = list(self.metrics[operation_name])
            if not times:
                return None
            
            return {
                "min": min(times),
                "max": max(times),
                "avg": sum(times) / len(times),
                "count": len(times)
            }
    
    def identify_slow_operations(self, threshold_ms: float = 1000) -> List[str]:
        """Identify operations exceeding threshold"""
        with self.lock:
            slow_ops = []
            for op_name, times in self.metrics.items():
                if times and max(times) > threshold_ms / 1000:
                    slow_ops.append(op_name)
            return slow_ops


class PerformanceManager:
    """Centralized performance management"""
    
    def __init__(self, max_pool_size: int = 100):
        self.connection_pool = ConnectionPool(
            factory=lambda: f"connection_{time.time()}",
            max_size=max_pool_size
        )
        self.batch_processor = BatchProcessor()
        self.async_executor = AsyncExecutor(max_workers=10)
        self.compression_cache = CompressionCache()
        self.deduplicator = RequestDeduplicator()
        self.query_optimizer = QueryOptimizer()
        self.monitor = PerformanceMonitor()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        pool_status = self.connection_pool.get_status()
        cache_metrics = self.compression_cache.get_metrics()
        
        return {
            "pool_status": pool_status.value,
            "pool_metrics": self.connection_pool.get_metrics().__dict__,
            "cache_metrics": cache_metrics,
            "slow_operations": self.monitor.identify_slow_operations()
        }
