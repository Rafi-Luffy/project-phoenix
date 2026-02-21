"""Performance Optimization Module - Tier 2.2"""
import threading, time, json
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    ttl_seconds: Optional[float] = None
    def is_expired(self) -> bool:
        if self.ttl_seconds is None: return False
        return time.time() - self.created_at > self.ttl_seconds
    def to_dict(self) -> Dict[str, Any]:
        return {"key": self.key, "value": self.value, "created_at": self.created_at, "last_accessed": self.last_accessed, "access_count": self.access_count, "ttl_seconds": self.ttl_seconds, "expired": self.is_expired()}

@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size: int = 0
    entry_count: int = 0
    avg_access_count: float = 0.0
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) * 100 if total > 0 else 0.0
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

class AdvancedCacheManager:
    def __init__(self, max_entries: int = 1000, cleanup_interval: int = 300):
        self.max_entries = max_entries
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        self.l1_cache = OrderedDict()
        self.l2_cache = OrderedDict()
        self.l3_cache = OrderedDict()
        self.stats = CacheStats()
        self.lock = threading.RLock()
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            for cache in [self.l1_cache, self.l2_cache, self.l3_cache]:
                if key in cache:
                    entry = cache[key]
                    if not entry.is_expired():
                        self._update_access(entry)
                        cache.move_to_end(key)
                        self.stats.hits += 1
                        return entry.value
                    else: del cache[key]
            self.stats.misses += 1
            return None
    def put(self, key: str, value: Any, ttl_seconds: Optional[float] = None, level: int = 1) -> None:
        with self.lock:
            entry = CacheEntry(key=key, value=value, ttl_seconds=ttl_seconds)
            cache = [self.l1_cache, self.l2_cache, self.l3_cache][level-1]
            for c in [self.l1_cache, self.l2_cache, self.l3_cache]: c.pop(key, None)
            cache[key] = entry
            cache.move_to_end(key)
            if len(cache) > self.max_entries:
                oldest_key, _ = cache.popitem(last=False)
                self.stats.evictions += 1
    def invalidate(self, key: str) -> None:
        with self.lock:
            for cache in [self.l1_cache, self.l2_cache, self.l3_cache]: cache.pop(key, None)
    def clear(self) -> None:
        with self.lock:
            self.l1_cache.clear()
            self.l2_cache.clear()
            self.l3_cache.clear()
    def cleanup_expired(self) -> int:
        with self.lock:
            removed = 0
            for cache in [self.l1_cache, self.l2_cache, self.l3_cache]:
                for k in list(cache.keys()):
                    if cache[k].is_expired():
                        del cache[k]
                        removed += 1
            self.last_cleanup = time.time()
            return removed
    def get_stats(self) -> CacheStats:
        with self.lock:
            self.stats.entry_count = len(self.l1_cache) + len(self.l2_cache) + len(self.l3_cache)
            self.stats.total_size = sum(len(str(e.value)) for c in [self.l1_cache, self.l2_cache, self.l3_cache] for e in c.values())
            all_entries = list(self.l1_cache.values()) + list(self.l2_cache.values()) + list(self.l3_cache.values())
            if all_entries: self.stats.avg_access_count = sum(e.access_count for e in all_entries) / len(all_entries)
            return self.stats
    @staticmethod
    def _update_access(entry: CacheEntry) -> None:
        entry.last_accessed = time.time()
        entry.access_count += 1

@dataclass
class HealingTask:
    task_id: str
    operation: Callable
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    def duration_ms(self) -> float: return (self.completed_at - self.created_at) * 1000 if self.completed_at else 0.0
    def to_dict(self) -> Dict[str, Any]: return {"task_id": self.task_id, "status": self.status, "duration_ms": self.duration_ms(), "result": str(self.result) if self.result else None, "error": self.error}

@dataclass
class ParallelStats:
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_latency_ms: float = 0.0
    def success_rate(self) -> float: return ((self.total_tasks - self.failed_tasks) / self.total_tasks) * 100 if self.total_tasks > 0 else 0.0
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

class ParallelHealingCoordinator:
    def __init__(self, max_workers: int = 4, timeout_seconds: int = 60):
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks: Dict[str, HealingTask] = {}
        self.completed_tasks: List[HealingTask] = []
        self.stats = ParallelStats()
        self.lock = threading.RLock()
    def submit_task(self, task_id: str, operation: Callable, *args, **kwargs) -> HealingTask:
        with self.lock:
            task = HealingTask(task_id=task_id, operation=operation, args=args, kwargs=kwargs)
            self.active_tasks[task_id] = task
            self.stats.total_tasks += 1
            future = self.executor.submit(self._execute_task, task)
            task._future = future
            return task
    def submit_batch(self, tasks: List[Tuple[str, Callable, Tuple, Dict]]) -> List[HealingTask]:
        return [self.submit_task(task_id, operation, *args, **kwargs) for task_id, operation, args, kwargs in tasks]
    def wait_all(self, timeout: Optional[float] = None) -> Dict[str, HealingTask]:
        with self.lock:
            futures = {t.task_id: t._future for t in self.active_tasks.values()}
        timeout = timeout or self.timeout_seconds
        try:
            for future in as_completed(futures.values(), timeout=timeout): pass
        except: pass
        results = {}
        with self.lock:
            for task_id in list(self.active_tasks.keys()):
                task = self.active_tasks.pop(task_id)
                self.completed_tasks.append(task)
                results[task_id] = task
        return results
    def get_stats(self) -> ParallelStats:
        with self.lock:
            self.stats.completed_tasks = len(self.completed_tasks)
            self.stats.failed_tasks = sum(1 for t in self.completed_tasks if t.status == "failed")
            durations = [t.duration_ms() for t in self.completed_tasks if t.duration_ms() > 0]
            if durations: self.stats.avg_latency_ms = sum(durations) / len(durations)
            return self.stats
    def _execute_task(self, task: HealingTask) -> None:
        task.status = "running"
        try:
            task.result = task.operation(*task.args, **task.kwargs)
            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
        finally: task.completed_at = time.time()
    def shutdown(self) -> None: self.executor.shutdown(wait=True)

@dataclass
class QueryResult:
    data: Any
    cache_hit: bool
    cached_at: float = field(default_factory=time.time)
    executed_at: Optional[float] = None
    def to_dict(self) -> Dict[str, Any]: return {"data": str(self.data) if self.data else None, "cache_hit": self.cache_hit, "cached_at": self.cached_at, "executed_at": self.executed_at}

@dataclass
class DatabaseStats:
    query_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    connection_pool_size: int = 0
    active_connections: int = 0
    def cache_hit_rate(self) -> float: return (self.cache_hits / (self.cache_hits + self.cache_misses)) * 100 if (self.cache_hits + self.cache_misses) > 0 else 0.0
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

class DatabaseOptimizer:
    def __init__(self, pool_size: int = 10, query_cache_ttl: int = 300):
        self.pool_size = pool_size
        self.query_cache_ttl = query_cache_ttl
        self.query_cache: Dict[str, QueryResult] = {}
        self.active_connections: Set[str] = set()
        self.stats = DatabaseStats()
        self.stats.connection_pool_size = pool_size
        self.lock = threading.RLock()
    def acquire_connection(self) -> str:
        with self.lock:
            if len(self.active_connections) < self.pool_size:
                conn_id = f"conn_{len(self.active_connections)}_{int(time.time())}"
                self.active_connections.add(conn_id)
                self.stats.active_connections = len(self.active_connections)
                return conn_id
            raise RuntimeError("No available connections in pool")
    def release_connection(self, conn_id: str) -> None:
        with self.lock:
            self.active_connections.discard(conn_id)
            self.stats.active_connections = len(self.active_connections)
    def execute_query(self, query: str, use_cache: bool = True) -> QueryResult:
        with self.lock:
            if use_cache and query in self.query_cache:
                cached = self.query_cache[query]
                if time.time() - cached.cached_at < self.query_cache_ttl:
                    self.stats.cache_hits += 1
                    return QueryResult(data=cached.data, cache_hit=True)
                else: del self.query_cache[query]
            result_data = {"query": query, "rows": 100}
            self.stats.query_count += 1
            self.stats.cache_misses += 1
            if use_cache:
                result = QueryResult(data=result_data, cache_hit=False, executed_at=time.time())
                self.query_cache[query] = result
                return result
            return QueryResult(data=result_data, cache_hit=False)
    def invalidate_query_cache(self, pattern: Optional[str] = None) -> int:
        with self.lock:
            if pattern is None:
                count = len(self.query_cache)
                self.query_cache.clear()
                return count
            keys_to_delete = [k for k in self.query_cache.keys() if pattern in k]
            for key in keys_to_delete: del self.query_cache[key]
            return len(keys_to_delete)
    def get_stats(self) -> DatabaseStats: return self.stats

class MemoryOptimizer:
    def __init__(self):
        self.loaded_resources: Dict[str, Any] = {}
        self.resource_loaders: Dict[str, Callable] = {}
        self.memory_usage: Dict[str, int] = {}
        self.lock = threading.RLock()
    def register_lazy_resource(self, resource_id: str, loader: Callable) -> None:
        with self.lock: self.resource_loaders[resource_id] = loader
    def get_resource(self, resource_id: str) -> Optional[Any]:
        with self.lock:
            if resource_id in self.loaded_resources: return self.loaded_resources[resource_id]
            if resource_id in self.resource_loaders:
                resource = self.resource_loaders[resource_id]()
                self.loaded_resources[resource_id] = resource
                self.memory_usage[resource_id] = len(str(resource))
                return resource
            return None
    def unload_resource(self, resource_id: str) -> None:
        with self.lock:
            self.loaded_resources.pop(resource_id, None)
            self.memory_usage.pop(resource_id, None)
    def get_memory_stats(self) -> Dict[str, Any]:
        with self.lock:
            total = sum(self.memory_usage.values())
            return {"total_memory_bytes": total, "loaded_resources": len(self.loaded_resources), "available_lazy_resources": len(self.resource_loaders), "per_resource": self.memory_usage.copy()}

@dataclass
class PerformanceStats:
    cache_stats: Dict[str, Any] = field(default_factory=dict)
    parallel_stats: Dict[str, Any] = field(default_factory=dict)
    database_stats: Dict[str, Any] = field(default_factory=dict)
    memory_stats: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

class PerformanceOptimizer:
    def __init__(self, max_cache_entries: int = 1000, max_workers: int = 4, db_pool_size: int = 10):
        self.cache = AdvancedCacheManager(max_entries=max_cache_entries)
        self.parallel = ParallelHealingCoordinator(max_workers=max_workers)
        self.database = DatabaseOptimizer(pool_size=db_pool_size)
        self.memory = MemoryOptimizer()
    def optimize_healing_cycle(self, fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_time = time.time()
        cache_key = f"healing_cycle_{hash(str(fixes))}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None: return {"cached": True, "result": cached_result}
        tasks = [(f"fix_{i}", self._apply_fix, (fix,), {}) for i, fix in enumerate(fixes)]
        self.parallel.submit_batch(tasks)
        results = self.parallel.wait_all(timeout=30)
        applied_fixes = [t.result for t in results.values() if t.status == "completed"]
        optimization_result = {"applied_fixes": len(applied_fixes), "total_fixes": len(fixes), "duration_ms": (time.time() - start_time) * 1000}
        self.cache.put(cache_key, optimization_result, ttl_seconds=300)
        return optimization_result
    @staticmethod
    def _apply_fix(fix: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(0.05)
        return {"fix_id": fix.get("id"), "applied": True}
    def get_performance_stats(self) -> PerformanceStats:
        return PerformanceStats(cache_stats=self.cache.get_stats().to_dict(), parallel_stats=self.parallel.get_stats().to_dict(), database_stats=self.database.get_stats().to_dict(), memory_stats=self.memory.get_memory_stats())
    def shutdown(self) -> None: self.parallel.shutdown()
