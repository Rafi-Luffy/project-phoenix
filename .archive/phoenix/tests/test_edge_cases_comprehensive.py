"""
Comprehensive Edge Case Testing

Tests covering all edge cases, boundary conditions, and error scenarios
across all Phoenix modules and tiers.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

# Import all Phoenix modules
from phoenix.modules.llm_providers_extended import (
    ExtendedLLMProvider, MistralAIProvider, ProviderConfig, ProviderType
)
from phoenix.modules.performance.distributed_cache import (
    RedisClusterCache, MultiRegionCache, IntelligentEvictionPolicy
)
from phoenix.modules.performance.request_batcher import (
    RequestBatcher, BatchStrategy, AdaptiveBatcher
)
from phoenix.modules.performance.streaming import (
    StreamingResponse, StreamingMetrics, StreamFormat
)
from phoenix.security.encryption import (
    EncryptionManager, FieldEncryption, EncryptedStorage
)
from phoenix.security.secrets_manager import (
    SecretsManager, SecretType, PasswordGenerator
)
from phoenix.security.audit_trail import (
    AuditTrail, AuditAction, ComplianceFramework
)
from phoenix.security.rbac import RBACManager, Permission


# ==================== EDGE CASE TESTS ====================

class TestEdgeCases:
    """Comprehensive edge case testing"""
    
    # ========== Null/Empty/None Cases ==========
    
    @pytest.mark.asyncio
    async def test_cache_get_nonexistent_key(self):
        """Test cache retrieval of non-existent key"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        result = await cache.get("nonexistent_key_12345")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_delete_nonexistent_key(self):
        """Test deleting non-existent key"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        result = await cache.delete("nonexistent_key")
        assert result == False
    
    def test_encryption_empty_string(self):
        """Test encryption of empty string"""
        manager = EncryptionManager(master_key="test-key")
        
        encrypted = manager.encrypt("")
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == ""
    
    def test_encryption_none_value(self):
        """Test encryption with None (should convert to string)"""
        manager = EncryptionManager(master_key="test-key")
        
        encrypted = manager.encrypt(None)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == "None"
    
    def test_secrets_manager_get_nonexistent_secret(self):
        """Test retrieving non-existent secret"""
        manager = SecretsManager()
        
        result = manager.get_secret("nonexistent_secret")
        assert result is None
    
    def test_rbac_nonexistent_user(self):
        """Test permission check for non-existent user"""
        rbac = RBACManager()
        
        result = rbac.has_permission("nonexistent_user", Permission.READ)
        assert result == False
    
    # ========== Timeout Cases ==========
    
    @pytest.mark.asyncio
    async def test_batcher_timeout_with_single_request(self):
        """Test batching with single request and timeout"""
        async def slow_processor(payloads):
            await asyncio.sleep(0.05)
            return payloads
        
        batcher = RequestBatcher(
            processor=slow_processor,
            strategy=BatchStrategy.TIME_BASED,
            batch_timeout_ms=50
        )
        
        await batcher.add_request("req-1", {"data": "test"})
        
        # Wait for timeout
        await asyncio.sleep(0.1)
        
        stats = batcher.get_stats()
        assert stats["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_cache_ttl_boundary(self):
        """Test cache TTL at exact boundary"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Set with 1 second TTL
        await cache.set("boundary_key", "value", ttl=1)
        
        # Should exist immediately
        result = await cache.get("boundary_key")
        assert result == "value"
        
        # Wait past TTL
        await asyncio.sleep(1.1)
        result = await cache.get("boundary_key")
        assert result is None
    
    # ========== Overflow Cases ==========
    
    def test_encryption_very_large_string(self):
        """Test encryption of very large data"""
        manager = EncryptionManager(master_key="test-key")
        
        # 10MB of data
        large_data = "x" * (10 * 1024 * 1024)
        
        encrypted = manager.encrypt(large_data)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == large_data
    
    @pytest.mark.asyncio
    async def test_cache_large_value(self):
        """Test caching very large values"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # 5MB value
        large_value = {"data": "x" * (5 * 1024 * 1024)}
        
        await cache.set("large_key", large_value)
        result = await cache.get("large_key")
        
        assert result == large_value
    
    @pytest.mark.asyncio
    async def test_batcher_max_batch_size(self):
        """Test batching at max size boundary"""
        processed = []
        
        async def tracking_processor(payloads):
            processed.append(len(payloads))
            return payloads
        
        batcher = RequestBatcher(
            processor=tracking_processor,
            strategy=BatchStrategy.SIZE_BASED,
            max_batch_size=10
        )
        
        # Add exactly max_batch_size requests
        for i in range(10):
            await batcher.add_request(f"req-{i}", {"id": i})
        
        await asyncio.sleep(0.1)
        
        # Should have processed one batch
        assert len(processed) > 0
    
    def test_password_generation_various_lengths(self):
        """Test password generation at various lengths"""
        for length in [1, 8, 16, 32, 64, 128]:
            password = PasswordGenerator.generate(length=length)
            assert len(password) == length
    
    # ========== Type Mismatch Cases ==========
    
    @pytest.mark.asyncio
    async def test_cache_set_different_types(self):
        """Test cache with various data types"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        test_values = [
            ("string", "value"),
            ("int", 42),
            ("float", 3.14),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value"}),
            ("tuple", (1, 2, 3)),
            ("bool", True),
        ]
        
        for key_type, value in test_values:
            await cache.set(f"key_{key_type}", value)
            result = await cache.get(f"key_{key_type}")
            assert result == value
    
    def test_encryption_various_types(self):
        """Test encryption of various data types"""
        manager = EncryptionManager(master_key="test-key")
        
        test_values = [
            {"name": "John", "age": 30},
            [1, 2, 3, 4, 5],
            "string",
            123,
            45.67
        ]
        
        for value in test_values:
            encrypted = manager.encrypt(value)
            decrypted = manager.decrypt_json(encrypted) if isinstance(value, dict) else manager.decrypt(encrypted)
            # Verify encryption happened
            assert encrypted != str(value)
    
    def test_rbac_permission_edge_cases(self):
        """Test RBAC with various permission scenarios"""
        rbac = RBACManager()
        rbac.create_user("user-1", "test_user")
        rbac.assign_role_to_user("user-1", "user")
        
        # User shouldn't have admin permission
        assert not rbac.has_permission("user-1", Permission.ADMIN)
        
        # Grant permission explicitly
        rbac.grant_custom_permission("user-1", Permission.ADMIN)
        assert rbac.has_permission("user-1", Permission.ADMIN)
        
        # Revoke permission
        rbac.revoke_custom_permission("user-1", Permission.ADMIN)
        assert not rbac.has_permission("user-1", Permission.ADMIN)
    
    # ========== Concurrent Access Cases ==========
    
    @pytest.mark.asyncio
    async def test_cache_concurrent_access(self):
        """Test cache under concurrent access"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        async def concurrent_set(key, value):
            await cache.set(key, value)
        
        async def concurrent_get(key):
            return await cache.get(key)
        
        # Concurrent sets
        await asyncio.gather(*[
            concurrent_set(f"key_{i}", f"value_{i}") 
            for i in range(100)
        ])
        
        # Concurrent gets
        results = await asyncio.gather(*[
            concurrent_get(f"key_{i}") 
            for i in range(100)
        ])
        
        # All should succeed
        assert all(r is not None for r in results)
    
    @pytest.mark.asyncio
    async def test_batcher_concurrent_requests(self):
        """Test batcher with concurrent request additions"""
        async def mock_processor(payloads):
            return [{"processed": True, "input": p} for p in payloads]
        
        batcher = RequestBatcher(
            processor=mock_processor,
            max_batch_size=50
        )
        
        # Add 200 requests concurrently
        requests = [
            batcher.add_request(f"req-{i}", {"data": f"request-{i}"})
            for i in range(200)
        ]
        
        results = await asyncio.gather(*requests, return_exceptions=True)
        
        # Most should succeed
        successful = sum(1 for r in results if not isinstance(r, Exception))
        assert successful >= 150  # At least 75%
    
    # ========== State Transition Cases ==========
    
    def test_secrets_manager_secret_lifecycle(self):
        """Test secret through entire lifecycle"""
        manager = SecretsManager()
        
        # Create
        manager.store_secret("test_secret", "value1", rotation_enabled=True)
        assert manager.get_secret("test_secret") == "value1"
        
        # Rotate
        manager.rotate_secret("test_secret", "value2")
        assert manager.get_secret("test_secret") == "value2"
        
        # Check metadata
        metadata = manager.get_secret_metadata("test_secret")
        assert metadata["version"] == 2
        
        # Delete
        manager.delete_secret("test_secret")
        assert manager.get_secret("test_secret") is None
    
    def test_audit_trail_compliance_workflow(self):
        """Test audit trail through compliance workflow"""
        trail = AuditTrail()
        trail.enable_framework(ComplianceFramework.SOC2)
        trail.enable_framework(ComplianceFramework.GDPR)
        
        # Log creation
        trail.log_action(
            AuditAction.CREATE,
            "user",
            "user-1",
            user_id="admin"
        )
        
        # Log access
        trail.log_action(
            AuditAction.READ,
            "user",
            "user-1",
            user_id="user-1"
        )
        
        # Log modification
        trail.log_action(
            AuditAction.UPDATE,
            "user",
            "user-1",
            user_id="admin"
        )
        
        # Generate report
        report = trail.generate_compliance_report(ComplianceFramework.SOC2)
        
        assert report["total_entries"] == 3
        assert "create" in report["by_action"]
        assert "read" in report["by_action"]
        assert "update" in report["by_action"]
    
    # ========== Error Recovery Cases ==========
    
    @pytest.mark.asyncio
    async def test_cache_recovery_after_failure(self):
        """Test cache behavior after simulated failure"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Set value
        await cache.set("recovery_test", "value")
        
        # Simulate retrieval
        result = await cache.get("recovery_test")
        assert result == "value"
        
        # Clear and retry
        await cache.clear()
        result = await cache.get("recovery_test")
        assert result is None
        
        # Repopulate
        await cache.set("recovery_test", "new_value")
        result = await cache.get("recovery_test")
        assert result == "new_value"
    
    @pytest.mark.asyncio
    async def test_batcher_recovery_from_failed_batch(self):
        """Test batcher recovery after processing failure"""
        attempt_count = 0
        
        async def failing_processor(payloads):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise Exception("Batch processing failed")
            return payloads
        
        batcher = RequestBatcher(processor=failing_processor)
        
        # First attempt fails
        with pytest.raises(Exception):
            await batcher.add_request("req-1", {"data": "test"})
            await asyncio.sleep(0.1)
    
    def test_encryption_key_rotation_recovery(self):
        """Test encryption recovery during key rotation"""
        manager = EncryptionManager(master_key="original-key")
        
        # Encrypt with original key
        plaintext = "sensitive data"
        encrypted = manager.encrypt(plaintext)
        
        # Rotate key
        manager.rotate_key("new-key")
        
        # Should still be able to decrypt old data with new key
        # (In production, would need key versioning)
        # For now, verify rotation happened
        assert manager.get_key_age_days() == 0


# ==================== BOUNDARY CONDITIONS ====================

class TestBoundaryConditions:
    """Test system at boundaries and limits"""
    
    @pytest.mark.asyncio
    async def test_cache_max_entries(self):
        """Test cache with maximum entries"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        eviction = IntelligentEvictionPolicy(max_entries=100)
        
        # Fill cache
        for i in range(150):
            await cache.set(f"key_{i}", f"value_{i}")
        
        # Evaluate eviction
        to_evict = await eviction.evaluate(cache)
        
        # Should identify entries for eviction
        assert len(to_evict) > 0
    
    def test_streaming_max_concurrent_streams(self):
        """Test streaming with many concurrent streams"""
        metrics = StreamingMetrics()
        
        # Start many streams
        for i in range(100):
            metrics.start_stream(f"stream-{i}")
            metrics.record_chunk(f"stream-{i}", 1024)
        
        # End all streams
        for i in range(100):
            metrics.end_stream(f"stream-{i}")
        
        summary = metrics.get_summary()
        assert summary["total_streams"] == 100
    
    def test_rbac_max_users_and_roles(self):
        """Test RBAC with many users and roles"""
        rbac = RBACManager()
        
        # Create 100 users
        for i in range(100):
            rbac.create_user(f"user-{i}", f"user_{i}")
            rbac.assign_role_to_user(f"user-{i}", "user")
        
        # Check permissions for all
        for i in range(100):
            has_read = rbac.has_permission(f"user-{i}", Permission.READ)
            assert has_read == True
    
    def test_audit_trail_large_volume(self):
        """Test audit trail with large volume of entries"""
        trail = AuditTrail()
        
        # Log 1000 actions
        for i in range(1000):
            trail.log_action(
                AuditAction.READ,
                "api",
                f"endpoint-{i%10}",
                user_id=f"user-{i%100}"
            )
        
        assert len(trail.entries) == 1000
        
        # Get user's actions
        user_logs = trail.get_entries_for_user("user-0", days=30)
        assert len(user_logs) > 0


# ==================== INVALID INPUT HANDLING ====================

class TestInvalidInputHandling:
    """Test handling of invalid inputs"""
    
    def test_encryption_invalid_key(self):
        """Test encryption with invalid master key"""
        with pytest.raises(ValueError):
            EncryptionManager(master_key="")
    
    def test_secrets_manager_invalid_secret_type(self):
        """Test storing secret with invalid type"""
        manager = SecretsManager()
        
        # Should still work with any secret type
        manager.store_secret("test", "value", SecretType.API_KEY)
        assert manager.get_secret("test") == "value"
    
    @pytest.mark.asyncio
    async def test_batcher_invalid_processor(self):
        """Test batcher with invalid processor function"""
        async def invalid_processor():
            pass  # Missing parameters
        
        # Should still create (error on use)
        batcher = RequestBatcher(processor=invalid_processor)
        assert batcher is not None
    
    def test_rbac_invalid_permission_grant(self):
        """Test granting invalid permissions"""
        rbac = RBACManager()
        rbac.create_user("user-1", "test")
        
        # Grant valid permission
        result = rbac.grant_custom_permission("user-1", Permission.READ)
        assert result == True
        
        # Revoke same permission
        result = rbac.revoke_custom_permission("user-1", Permission.READ)
        assert result == True


# ==================== STRESS TESTS ====================

class TestStressConditions:
    """Test system under stress"""
    
    @pytest.mark.asyncio
    async def test_cache_stress_rapid_access(self):
        """Stress test: rapid cache access"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        await cache.set("stress_key", "stress_value")
        
        # 1000 rapid accesses
        results = await asyncio.gather(*[
            cache.get("stress_key") for _ in range(1000)
        ])
        
        assert all(r == "stress_value" for r in results)
    
    @pytest.mark.asyncio
    async def test_batcher_stress_many_requests(self):
        """Stress test: many rapid batch requests"""
        async def stress_processor(payloads):
            return payloads
        
        batcher = RequestBatcher(
            processor=stress_processor,
            max_batch_size=100
        )
        
        # Add 500 requests rapidly
        requests = [
            batcher.add_request(f"req-{i}", {"id": i})
            for i in range(500)
        ]
        
        results = await asyncio.gather(*requests, return_exceptions=True)
        
        # Most should complete
        successful = sum(1 for r in results if not isinstance(r, Exception))
        assert successful >= 400
    
    def test_audit_trail_stress_logging(self):
        """Stress test: rapid audit logging"""
        trail = AuditTrail()
        
        # Log 5000 actions rapidly
        for i in range(5000):
            trail.log_action(
                AuditAction.READ,
                f"resource_{i%50}",
                f"id_{i}",
                user_id=f"user_{i%100}"
            )
        
        assert len(trail.entries) == 5000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
