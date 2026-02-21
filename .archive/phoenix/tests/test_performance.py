"""
Comprehensive tests for performance optimization components - Tier 2.2
"""

import threading
import time
import pytest
from phoenix.core.performance import (
    AdvancedCacheManager,
    CacheEntry,
    CacheStats,
    ParallelHealingCoordinator,
    DatabaseOptimizer,
    MemoryOptimizer,
    PerformanceOptimizer,
    ParallelStats,
    DatabaseStats,
)


class TestAdvancedCacheManager:
    """Test advanced cache manager."""

    def test_cache_creation(self):
        """Test cache creation."""
        cache = AdvancedCacheManager(max_entries=100)
        assert cache.max_entries == 100
        assert len(cache.l1_cache) == 0
        assert len(cache.l2_cache) == 0
        assert len(cache.l3_cache) == 0

    def test_put_and_get(self):
        """Test put and get operations."""
        cache = AdvancedCacheManager()
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        cache = AdvancedCacheManager()
        cache.put("key1", "value1")
        
        # Hit
        assert cache.get("key1") == "value1"
        assert cache.stats.hits == 1
        
        # Miss
        assert cache.get("nonexistent") is None
        assert cache.stats.misses == 1
        
        stats = cache.get_stats()
        assert stats.hit_rate() == 50.0

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = AdvancedCacheManager()
        cache.put("key1", "value1", ttl_seconds=0.1)
        
        assert cache.get("key1") == "value1"
        time.sleep(0.2)
        assert cache.get("key1") is None

    def test_lru_eviction(self):
        """Test LRU eviction."""
        cache = AdvancedCacheManager(max_entries=3)
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        cache.put("key4", "value4")
        
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"

    def test_multi_level_promotion(self):
        """Test promotion across cache levels."""
        cache = AdvancedCacheManager(max_entries=10)
        
        # Put in L3
        cache.put("key1", "value1", level=3)
        assert "key1" in cache.l3_cache
        
        # Get from L3 should promote to L2
        assert cache.get("key1") == "value1"
        assert "key1" in cache.l2_cache
        assert "key1" not in cache.l3_cache

    def test_invalidate(self):
        """Test invalidation."""
        cache = AdvancedCacheManager()
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        """Test clear all."""
        cache = AdvancedCacheManager()
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestParallelHealingCoordinator:
    """Test parallel healing coordinator."""

    def test_coordinator_creation(self):
        """Test coordinator creation."""
        coord = ParallelHealingCoordinator(max_workers=4)
        assert coord.max_workers == 4
        assert len(coord.active_tasks) == 0

    def test_submit_single_task(self):
        """Test submitting a single task."""
        coord = ParallelHealingCoordinator()
        
        def dummy_operation():
            return "result"
        
        task = coord.submit_task("task1", dummy_operation)
        assert task.task_id == "task1"
        assert task.status == "pending"

    def test_task_execution(self):
        """Test task execution."""
        coord = ParallelHealingCoordinator()
        
        def dummy_operation(x):
            return x * 2
        
        task = coord.submit_task("task1", dummy_operation, 5)
        time.sleep(0.1)
        assert task.status == "completed"
        assert task.result == 10

    def test_batch_submission(self):
        """Test batch task submission."""
        coord = ParallelHealingCoordinator()
        
        def dummy_operation(x):
            return x * 2
        
        tasks = [
            ("task1", dummy_operation, (1,), {}),
            ("task2", dummy_operation, (2,), {}),
            ("task3", dummy_operation, (3,), {}),
        ]
        
        submitted = coord.submit_batch(tasks)
        assert len(submitted) == 3

    def test_wait_all(self):
        """Test waiting for all tasks."""
        coord = ParallelHealingCoordinator()
        
        def dummy_operation(x):
            time.sleep(0.05)
            return x * 2
        
        tasks = [
            ("task1", dummy_operation, (1,), {}),
            ("task2", dummy_operation, (2,), {}),
        ]
        
        coord.submit_batch(tasks)
        results = coord.wait_all(timeout=5)
        
        assert len(results) == 2
        assert all(t.status == "completed" for t in results.values())

    def test_parallel_statistics(self):
        """Test parallel execution statistics."""
        coord = ParallelHealingCoordinator()
        
        def dummy_operation(x):
            return x * 2
        
        tasks = [
            ("task1", dummy_operation, (i,), {})
            for i in range(5)
        ]
        
        coord.submit_batch(tasks)
        coord.wait_all(timeout=5)
        
        stats = coord.get_stats()
        assert stats.total_tasks == 5
        assert stats.completed_tasks == 5
        assert stats.failed_tasks == 0
        assert stats.success_rate() == 100.0


class TestDatabaseOptimizer:
    """Test database optimizer."""

    def test_database_creation(self):
        """Test database optimizer creation."""
        db = DatabaseOptimizer(pool_size=10)
        assert db.pool_size == 10

    def test_connection_acquisition(self):
        """Test connection acquisition."""
        db = DatabaseOptimizer(pool_size=3)
        conn1 = db.acquire_connection()
        conn2 = db.acquire_connection()
        
        assert conn1 != conn2
        assert db.stats.active_connections == 2

    def test_connection_release(self):
        """Test connection release."""
        db = DatabaseOptimizer(pool_size=3)
        conn = db.acquire_connection()
        assert db.stats.active_connections == 1
        
        db.release_connection(conn)
        assert db.stats.active_connections == 0

    def test_query_execution(self):
        """Test query execution."""
        db = DatabaseOptimizer()
        result = db.execute_query("SELECT * FROM table1", use_cache=False)
        
        assert result.cache_hit is False
        assert result.data is not None
        assert db.stats.query_count == 1

    def test_query_caching(self):
        """Test query caching."""
        db = DatabaseOptimizer()
        query = "SELECT * FROM table1"
        
        result1 = db.execute_query(query, use_cache=True)
        result2 = db.execute_query(query, use_cache=True)
        
        assert result1.cache_hit is False
        assert result2.cache_hit is True
        assert db.stats.cache_hits == 1
        assert db.stats.cache_misses == 1


class TestMemoryOptimizer:
    """Test memory optimizer."""

    def test_memory_optimizer_creation(self):
        """Test memory optimizer creation."""
        mem = MemoryOptimizer()
        assert len(mem.loaded_resources) == 0

    def test_lazy_resource_registration(self):
        """Test lazy resource registration."""
        mem = MemoryOptimizer()
        
        def loader():
            return {"data": "value"}
        
        mem.register_lazy_resource("resource1", loader)
        assert "resource1" in mem.resource_loaders

    def test_lazy_resource_loading(self):
        """Test lazy resource loading."""
        mem = MemoryOptimizer()
        
        def loader():
            return {"data": "value"}
        
        mem.register_lazy_resource("resource1", loader)
        resource = mem.get_resource("resource1")
        
        assert resource == {"data": "value"}
        assert "resource1" in mem.loaded_resources


class TestPerformanceOptimizer:
    """Test unified performance optimizer."""

    def test_optimizer_creation(self):
        """Test optimizer creation."""
        opt = PerformanceOptimizer(max_cache_entries=100, max_workers=4, db_pool_size=10)
        assert opt.cache is not None
        assert opt.parallel is not None
        assert opt.database is not None
        assert opt.memory is not None

    def test_optimize_healing_cycle(self):
        """Test healing cycle optimization."""
        opt = PerformanceOptimizer()
        
        fixes = [
            {"id": 1, "type": "code"},
            {"id": 2, "type": "config"},
        ]
        
        result = opt.optimize_healing_cycle(fixes)
        assert result["applied_fixes"] == 2
        assert result["total_fixes"] == 2
        assert "duration_ms" in result

    def test_performance_statistics(self):
        """Test performance statistics aggregation."""
        opt = PerformanceOptimizer()
        
        # Perform some operations
        opt.cache.put("key1", "value1")
        opt.cache.get("key1")
        opt.database.execute_query("SELECT 1", use_cache=True)
        
        stats = opt.get_performance_stats()
        assert "cache_stats" in stats.to_dict()
        assert "parallel_stats" in stats.to_dict()
        assert "database_stats" in stats.to_dict()
        assert "memory_stats" in stats.to_dict()

    def test_shutdown(self):
        """Test graceful shutdown."""
        opt = PerformanceOptimizer()
        opt.shutdown()


class TestPerformanceIntegration:
    """Integration tests for performance optimization."""

    def test_combined_optimization(self):
        """Test combined use of all optimization features."""
        opt = PerformanceOptimizer(max_workers=2)
        
        # Cache operation
        opt.cache.put("fix_template_1", {"code": "fix"})
        cached = opt.cache.get("fix_template_1")
        assert cached == {"code": "fix"}
        
        # Database operation
        result = opt.database.execute_query("SELECT * FROM fixes", use_cache=True)
        assert result.cache_hit is False
        
        result2 = opt.database.execute_query("SELECT * FROM fixes", use_cache=True)
        assert result2.cache_hit is True
        
        # Parallel operation
        def simple_fix():
            return {"status": "applied"}
        
        task = opt.parallel.submit_task("fix_1", simple_fix)
        opt.parallel.wait_all(timeout=5)
        assert task.status == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
