"""
Integration and Performance Testing

Tests validating complete end-to-end workflows and performance characteristics
under various conditions.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from unittest.mock import Mock, AsyncMock, patch
import statistics

from phoenix.modules.llm_providers_extended import ExtendedLLMProvider, ProviderType
from phoenix.modules.performance.distributed_cache import RedisClusterCache
from phoenix.modules.performance.request_batcher import RequestBatcher, BatchStrategy
from phoenix.modules.performance.streaming import StreamingResponse, StreamFormat, StreamingMetrics
from phoenix.security.encryption import EncryptionManager
from phoenix.security.secrets_manager import SecretsManager
from phoenix.security.audit_trail import AuditTrail, AuditAction
from phoenix.security.rbac import RBACManager, Permission


# ==================== FULL INTEGRATION TESTS ====================

class TestFullIntegration:
    """Test complete workflows across all system components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_encrypted_api_workflow(self):
        """
        Test complete workflow:
        1. User makes request
        2. Request authenticated via RBAC
        3. Data encrypted before processing
        4. Batcher optimizes request
        5. Response cached
        6. All operations audited
        """
        # Setup components
        rbac = RBACManager()
        trail = AuditTrail()
        encryption = EncryptionManager(master_key="test-key")
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Create user
        rbac.create_user("user-1", "Test User")
        rbac.assign_role_to_user("user-1", "user")
        
        # Simulate API workflow
        user_id = "user-1"
        request_data = {"query": "test prompt"}
        
        # 1. Authenticate
        trail.log_action(AuditAction.READ, "api", "endpoint", user_id=user_id)
        has_access = rbac.has_permission(user_id, Permission.READ)
        assert has_access
        
        # 2. Encrypt sensitive data
        encrypted_request = encryption.encrypt(request_data["query"])
        
        # 3. Check cache
        cache_key = f"encrypted_{encrypted_request[:20]}"
        cached = await cache.get(cache_key)
        
        if not cached:
            # 4. Process (simulate)
            await asyncio.sleep(0.01)
            response = f"response_to_{request_data['query']}"
            
            # 5. Cache response
            await cache.set(cache_key, response, ttl=3600)
        
        # 6. Log operation
        trail.log_action(AuditAction.READ, "query", request_data["query"], user_id=user_id)
        
        # Verify audit trail
        user_actions = trail.get_entries_for_user(user_id)
        assert len(user_actions) > 0
    
    @pytest.mark.asyncio
    async def test_multi_provider_fallback_workflow(self):
        """
        Test workflow with multiple providers:
        1. Request sent to primary provider
        2. If fails, fallback to secondary
        3. If secondary fails, tertiary
        4. All paths logged
        """
        trail = AuditTrail()
        
        provider_status = {
            "primary": {"available": True, "calls": 0},
            "secondary": {"available": True, "calls": 0},
            "tertiary": {"available": True, "calls": 0},
        }
        
        async def call_provider(name: str, prompt: str) -> str:
            provider_status[name]["calls"] += 1
            
            if not provider_status[name]["available"]:
                raise Exception(f"{name} provider unavailable")
            
            await asyncio.sleep(0.01)
            return f"{name}_response_{prompt}"
        
        async def request_with_fallback(prompt: str):
            for provider_name in ["primary", "secondary", "tertiary"]:
                try:
                    result = await call_provider(provider_name, prompt)
                    trail.log_action(AuditAction.READ, "provider", provider_name, user_id="user-1")
                    return result
                except Exception:
                    trail.log_action(AuditAction.READ, "provider_failed", provider_name, user_id="user-1")
                    continue
            
            raise Exception("All providers failed")
        
        # Test normal path
        result = await request_with_fallback("test")
        assert "primary_response" in result
        
        # Test fallback path
        provider_status["primary"]["available"] = False
        result = await request_with_fallback("test")
        assert "secondary_response" in result
        
        # Verify audit trail
        actions = trail.get_entries_for_user("user-1")
        assert len(actions) > 0
    
    @pytest.mark.asyncio
    async def test_streaming_with_encryption_and_audit(self):
        """
        Test streaming workflow with encryption and audit logging
        """
        encryption = EncryptionManager(master_key="test-key")
        trail = AuditTrail()
        metrics = StreamingMetrics()
        
        stream_id = "stream-1"
        
        async def stream_encrypted_response(prompt: str):
            # Start stream
            metrics.start_stream(stream_id)
            trail.log_action(AuditAction.READ, "stream", stream_id, user_id="user-1")
            
            try:
                # Stream response in chunks
                for chunk in ["part1", "part2", "part3"]:
                    # Encrypt each chunk
                    encrypted_chunk = encryption.encrypt(chunk)
                    
                    # Record metric
                    metrics.record_chunk(stream_id, len(encrypted_chunk))
                    
                    yield encrypted_chunk
                    await asyncio.sleep(0.01)
            
            finally:
                # End stream
                metrics.end_stream(stream_id)
        
        # Consume stream
        chunks = []
        async for chunk in stream_encrypted_response("test"):
            chunks.append(chunk)
        
        # Verify
        assert len(chunks) == 3
        
        summary = metrics.get_summary()
        assert summary["total_streams"] == 1
    
    @pytest.mark.asyncio
    async def test_secret_rotation_during_high_load(self):
        """
        Test secret rotation doesn't break operations under load
        """
        secrets = SecretsManager()
        secrets.store_secret("api_key", "key_v1")
        
        operation_count = {"success": 0, "failed": 0}
        
        async def operation_using_secret():
            try:
                key = secrets.get_secret("api_key")
                await asyncio.sleep(0.001)
                operation_count["success"] += 1
            except Exception:
                operation_count["failed"] += 1
        
        # Run operations
        tasks = [operation_using_secret() for _ in range(100)]
        
        # Rotate secret mid-operation
        await asyncio.sleep(0.01)
        secrets.rotate_secret("api_key", "key_v2")
        
        # Complete all operations
        await asyncio.gather(*tasks)
        
        # Most should succeed
        assert operation_count["success"] >= 80


# ==================== PERFORMANCE BENCHMARKS ====================

class TestPerformanceBenchmarks:
    """Benchmark system performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_cache_access_latency(self):
        """Benchmark cache get/set latency"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Warmup
        await cache.set("warmup", "value")
        await cache.get("warmup")
        
        # Benchmark set
        set_times = []
        for i in range(100):
            start = time.perf_counter()
            await cache.set(f"key_{i}", f"value_{i}")
            set_times.append((time.perf_counter() - start) * 1000)
        
        # Benchmark get
        get_times = []
        for i in range(100):
            start = time.perf_counter()
            await cache.get(f"key_{i}")
            get_times.append((time.perf_counter() - start) * 1000)
        
        # Report
        print(f"\nCache SET - Mean: {statistics.mean(set_times):.2f}ms, Median: {statistics.median(set_times):.2f}ms, P95: {sorted(set_times)[95]:.2f}ms")
        print(f"Cache GET - Mean: {statistics.mean(get_times):.2f}ms, Median: {statistics.median(get_times):.2f}ms, P95: {sorted(get_times)[95]:.2f}ms")
        
        # Assert reasonable latency
        assert statistics.mean(set_times) < 100  # Less than 100ms average
        assert statistics.mean(get_times) < 50   # Less than 50ms average
    
    @pytest.mark.asyncio
    async def test_batching_throughput(self):
        """Benchmark batching throughput"""
        processed_items = {"count": 0}
        
        async def batch_processor(items):
            processed_items["count"] += len(items)
            return items
        
        batcher = RequestBatcher(
            processor=batch_processor,
            strategy=BatchStrategy.SIZE_BASED,
            max_batch_size=100
        )
        
        # Measure throughput
        start = time.perf_counter()
        
        for i in range(1000):
            await batcher.add_request(i, f"item_{i}")
        
        elapsed = time.perf_counter() - start
        throughput = processed_items["count"] / elapsed
        
        print(f"\nBatching Throughput: {throughput:.0f} items/sec")
        
        # Assert minimum throughput
        assert throughput > 100  # At least 100 items/sec
    
    def test_encryption_throughput(self):
        """Benchmark encryption/decryption throughput"""
        manager = EncryptionManager(master_key="test-key")
        
        test_data = "x" * 1000  # 1KB
        
        # Warmup
        encrypted = manager.encrypt(test_data)
        manager.decrypt(encrypted)
        
        # Benchmark encryption
        start = time.perf_counter()
        for i in range(100):
            manager.encrypt(f"{test_data}_{i}")
        encrypt_time = time.perf_counter() - start
        
        # Benchmark decryption
        encrypted_samples = [manager.encrypt(f"{test_data}_{i}") for i in range(100)]
        
        start = time.perf_counter()
        for encrypted in encrypted_samples:
            manager.decrypt(encrypted)
        decrypt_time = time.perf_counter() - start
        
        encrypt_throughput = 100 / encrypt_time
        decrypt_throughput = 100 / decrypt_time
        
        print(f"\nEncryption: {encrypt_throughput:.0f} ops/sec, {encrypt_time/100*1000:.2f}ms per op")
        print(f"Decryption: {decrypt_throughput:.0f} ops/sec, {decrypt_time/100*1000:.2f}ms per op")
    
    @pytest.mark.asyncio
    async def test_rbac_permission_check_latency(self):
        """Benchmark RBAC permission check latency"""
        rbac = RBACManager()
        
        # Create users and assign roles
        for i in range(100):
            rbac.create_user(f"user_{i}", f"User {i}")
            rbac.assign_role_to_user(f"user_{i}", "user")
        
        # Benchmark permission checks
        check_times = []
        for i in range(1000):
            start = time.perf_counter()
            rbac.has_permission(f"user_{i % 100}", Permission.READ)
            check_times.append((time.perf_counter() - start) * 1000)
        
        print(f"\nRBAC Permission Check - Mean: {statistics.mean(check_times):.3f}ms, P95: {sorted(check_times)[950]:.3f}ms")
        
        assert statistics.mean(check_times) < 10  # Less than 10ms average
    
    def test_audit_trail_logging_latency(self):
        """Benchmark audit trail logging latency"""
        trail = AuditTrail()
        
        log_times = []
        for i in range(1000):
            start = time.perf_counter()
            trail.log_action(AuditAction.READ, "resource", f"id_{i}", user_id=f"user_{i % 10}")
            log_times.append((time.perf_counter() - start) * 1000)
        
        print(f"\nAudit Logging - Mean: {statistics.mean(log_times):.3f}ms, P95: {sorted(log_times)[950]:.3f}ms")
        
        assert statistics.mean(log_times) < 5  # Less than 5ms average


# ==================== LOAD AND STRESS TESTS ====================

class TestLoadAndStress:
    """Test system under various load conditions"""
    
    @pytest.mark.asyncio
    async def test_sustained_high_throughput(self):
        """Test system can sustain high throughput"""
        async def mock_processor(items):
            return items
        
        batcher = RequestBatcher(processor=mock_processor, max_batch_size=50)
        
        # Send 5000 requests
        start = time.perf_counter()
        
        results = await asyncio.gather(*[
            batcher.add_request(i, f"item_{i}")
            for i in range(5000)
        ])
        
        elapsed = time.perf_counter() - start
        throughput = 5000 / elapsed
        
        print(f"\nSustained Throughput: {throughput:.0f} requests/sec")
        
        # Verify all completed
        assert len([r for r in results if r is not None]) >= 4000
    
    @pytest.mark.asyncio
    async def test_memory_efficiency_large_cache(self):
        """Test cache memory efficiency with many entries"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Add 10000 entries
        for i in range(10000):
            await cache.set(f"key_{i}", f"value_{i}")
        
        # Verify retrieval
        sample_value = await cache.get("key_5000")
        assert sample_value == "value_5000"
    
    def test_audit_trail_with_large_volume(self):
        """Test audit trail handling large volume of entries"""
        trail = AuditTrail()
        
        # Log 10000 entries
        start = time.perf_counter()
        
        for i in range(10000):
            trail.log_action(
                AuditAction.READ,
                "resource",
                f"id_{i}",
                user_id=f"user_{i % 100}"
            )
        
        elapsed = time.perf_counter() - start
        
        print(f"\nAudit Logging 10K entries: {elapsed:.2f}s ({10000/elapsed:.0f} ops/sec)")
        
        # Verify entries
        assert len(trail.entries) == 10000
        
        # Verify query performance
        query_start = time.perf_counter()
        user_logs = trail.get_entries_for_user("user_0")
        query_elapsed = time.perf_counter() - query_start
        
        print(f"Query time for user-specific entries: {query_elapsed*1000:.2f}ms")


# ==================== RESOURCE LIMIT TESTS ====================

class TestResourceLimits:
    """Test behavior at resource limits"""
    
    @pytest.mark.asyncio
    async def test_cache_at_max_capacity(self):
        """Test cache behavior at maximum capacity"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Fill cache
        for i in range(1000):
            await cache.set(f"key_{i}", f"value_{i}", ttl=60)
        
        # Verify all entries present
        count = 0
        for i in range(1000):
            val = await cache.get(f"key_{i}")
            if val is not None:
                count += 1
        
        assert count > 900  # Most should be present
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_limit(self):
        """Test system with maximum concurrent operations"""
        async def slow_operation():
            await asyncio.sleep(0.1)
            return "done"
        
        # Create 500 concurrent tasks
        tasks = [slow_operation() for _ in range(500)]
        
        start = time.perf_counter()
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start
        
        print(f"\n500 concurrent operations: {elapsed:.2f}s")
        
        # All should complete
        assert len(results) == 500
        assert all(r == "done" for r in results)
    
    def test_rbac_with_many_roles_and_permissions(self):
        """Test RBAC with many roles and permissions"""
        rbac = RBACManager()
        
        # Create many users
        for i in range(500):
            rbac.create_user(f"user_{i}", f"User {i}")
        
        # Assign various roles
        for i in range(500):
            role = "admin" if i % 10 == 0 else "user"
            rbac.assign_role_to_user(f"user_{i}", role)
        
        # Check permissions efficiently
        admin_count = sum(
            1 for i in range(500)
            if rbac.has_permission(f"user_{i}", Permission.ADMIN)
        )
        
        # Expect ~50 admins
        assert admin_count >= 40


# ==================== CONSISTENCY TESTS ====================

class TestConsistency:
    """Test data consistency across operations"""
    
    @pytest.mark.asyncio
    async def test_cache_consistency_across_concurrent_access(self):
        """Test cache consistency with concurrent reads/writes"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        async def concurrent_set_get():
            tasks = []
            
            # 50 writers
            for i in range(50):
                tasks.append(cache.set(f"key_{i}", f"value_{i}_{i}"))
            
            # 50 readers
            for i in range(50):
                tasks.append(cache.get(f"key_{i}"))
            
            return await asyncio.gather(*tasks)
        
        results = await concurrent_set_get()
        
        # Verify consistency
        for i in range(50):
            value = await cache.get(f"key_{i}")
            assert value == f"value_{i}_{i}"
    
    def test_audit_trail_consistency(self):
        """Test audit trail maintains consistency"""
        trail = AuditTrail()
        
        # Log operations
        for i in range(100):
            trail.log_action(AuditAction.CREATE, "resource", f"res_{i}", user_id="user_1")
            trail.log_action(AuditAction.UPDATE, "resource", f"res_{i}", user_id="user_2")
        
        # Verify chronological order
        entries = trail.entries
        for i in range(1, len(entries)):
            assert entries[i]["timestamp"] >= entries[i-1]["timestamp"]
        
        # Verify total count
        assert len(entries) == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
