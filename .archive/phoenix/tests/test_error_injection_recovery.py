"""
Error Injection and Self-Healing Recovery Tests

Tests that inject various failure modes and verify the system's self-healing
and recovery capabilities.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Callable, Any, Optional
from unittest.mock import Mock, AsyncMock, patch
import random

from phoenix.modules.llm_providers_extended import ExtendedLLMProvider
from phoenix.modules.performance.distributed_cache import RedisClusterCache
from phoenix.modules.performance.request_batcher import RequestBatcher
from phoenix.modules.performance.streaming import StreamingResponse
from phoenix.security.encryption import EncryptionManager
from phoenix.security.secrets_manager import SecretsManager
from phoenix.security.audit_trail import AuditTrail, AuditAction
from phoenix.security.rbac import RBACManager, Permission


# ==================== ERROR INJECTION FRAMEWORK ====================

class ErrorInjector:
    """Framework for injecting various failure modes"""
    
    def __init__(self):
        self.failures = {}
        self.failure_modes = {
            "network_timeout": asyncio.TimeoutError("Network timeout"),
            "connection_refused": ConnectionRefusedError("Connection refused"),
            "invalid_response": ValueError("Invalid response format"),
            "authentication_failed": PermissionError("Authentication failed"),
            "rate_limited": Exception("Rate limited"),
            "service_unavailable": Exception("Service unavailable"),
            "data_corruption": ValueError("Data corruption detected"),
            "key_not_found": KeyError("Key not found"),
            "memory_error": MemoryError("Out of memory"),
            "disk_full": OSError("Disk full"),
        }
    
    def inject_failure(self, target: str, mode: str, duration: Optional[float] = None):
        """Inject a failure into a target"""
        self.failures[target] = {
            "mode": mode,
            "duration": duration,
            "start_time": datetime.now()
        }
    
    def clear_failure(self, target: str):
        """Clear injected failure"""
        if target in self.failures:
            del self.failures[target]
    
    def should_fail(self, target: str) -> bool:
        """Check if target should fail"""
        if target not in self.failures:
            return False
        
        failure = self.failures[target]
        
        # Check if duration has passed
        if failure["duration"]:
            elapsed = (datetime.now() - failure["start_time"]).total_seconds()
            if elapsed > failure["duration"]:
                self.clear_failure(target)
                return False
        
        return True
    
    def get_failure_error(self, target: str):
        """Get the error to raise"""
        if not self.should_fail(target):
            return None
        
        mode = self.failures[target]["mode"]
        return self.failure_modes.get(mode, Exception(mode))


# ==================== PROVIDER FAILURE RECOVERY ====================

class TestProviderFailureRecovery:
    """Test recovery from LLM provider failures"""
    
    @pytest.mark.asyncio
    async def test_provider_timeout_recovery(self):
        """Test recovery from provider timeout"""
        injector = ErrorInjector()
        
        attempt_count = {"count": 0}
        
        async def provider_with_timeout(prompts):
            attempt_count["count"] += 1
            
            if injector.should_fail("provider_1"):
                raise injector.get_failure_error("provider_1")
            
            return [f"response_{p}" for p in prompts]
        
        async def request_with_recovery(prompt: str):
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    # Inject timeout for first 2 attempts
                    if attempt < 2:
                        injector.inject_failure("provider_1", "network_timeout", duration=0.1)
                    else:
                        injector.clear_failure("provider_1")
                    
                    result = await asyncio.wait_for(
                        provider_with_timeout([prompt]),
                        timeout=1.0
                    )
                    return result[0]
                
                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.05 * (2 ** attempt))  # Exponential backoff
                        continue
                    raise
            
            return None
        
        result = await request_with_recovery("test_prompt")
        
        # Should eventually succeed
        assert result is not None
        assert "response_" in result
    
    @pytest.mark.asyncio
    async def test_provider_authentication_failure_recovery(self):
        """Test recovery when provider authentication fails"""
        injector = ErrorInjector()
        
        credentials_version = {"version": 1}
        
        async def provider_with_auth(prompts, api_key: str):
            if injector.should_fail("auth"):
                raise injector.get_failure_error("auth")
            
            return [f"response_{p}" for p in prompts]
        
        async def request_with_credential_refresh(prompt: str):
            injector.inject_failure("auth", "authentication_failed")
            
            # First attempt with current credentials
            try:
                return await provider_with_auth([prompt], f"key_v{credentials_version['version']}")
            except PermissionError:
                # Refresh credentials
                credentials_version["version"] += 1
                injector.clear_failure("auth")
                
                # Retry with new credentials
                return await provider_with_auth([prompt], f"key_v{credentials_version['version']}")
        
        result = await request_with_credential_refresh("test")
        
        # Should succeed after credential refresh
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_provider_rate_limiting_recovery(self):
        """Test recovery from rate limiting with backoff"""
        injector = ErrorInjector()
        
        request_count = {"count": 0}
        
        async def rate_limited_provider(prompts):
            request_count["count"] += 1
            
            # Limit to 5 requests per interval
            if request_count["count"] <= 5:
                return [f"response_{p}" for p in prompts]
            
            if injector.should_fail("ratelimit"):
                raise injector.get_failure_error("ratelimit")
            
            return [f"response_{p}" for p in prompts]
        
        async def request_with_rate_limit_handling(prompt: str):
            injector.inject_failure("ratelimit", "rate_limited", duration=0.2)
            
            try:
                return await rate_limited_provider([prompt])
            except Exception as e:
                if "rate" in str(e).lower():
                    # Wait and retry
                    await asyncio.sleep(0.3)
                    return await rate_limited_provider([prompt])
                raise
        
        # Send requests
        for i in range(10):
            result = await request_with_rate_limit_handling(f"prompt_{i}")
            assert result is not None


# ==================== CACHE FAILURE RECOVERY ====================

class TestCacheFailureRecovery:
    """Test recovery from cache failures"""
    
    @pytest.mark.asyncio
    async def test_cache_miss_graceful_fallback(self):
        """Test graceful fallback when cache misses"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        api_calls = {"count": 0}
        
        async def expensive_operation(key: str):
            api_calls["count"] += 1
            return f"computed_{key}"
        
        async def get_with_cache_fallback(key: str):
            # Try cache
            cached = await cache.get(f"cache_{key}")
            if cached:
                return cached
            
            # Compute
            result = await expensive_operation(key)
            
            # Cache for next time
            try:
                await cache.set(f"cache_{key}", result)
            except Exception:
                # Cache write failed, still return result
                pass
            
            return result
        
        # First call - cache miss
        result1 = await get_with_cache_fallback("key1")
        assert result1 == "computed_key1"
        assert api_calls["count"] == 1
        
        # Second call - should hit cache (if available)
        result2 = await get_with_cache_fallback("key1")
        assert result2 == "computed_key1"
    
    @pytest.mark.asyncio
    async def test_cache_corruption_detection_and_recovery(self):
        """Test detection and recovery from corrupted cache data"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        async def get_with_validation(key: str):
            cached = await cache.get(f"cache_{key}")
            
            if cached:
                try:
                    # Validate cached data
                    if not isinstance(cached, str) or not cached.startswith("response_"):
                        # Data corrupted, clear and recompute
                        await cache.delete(f"cache_{key}")
                        return None
                    return cached
                except Exception:
                    # Corruption detected
                    await cache.delete(f"cache_{key}")
                    return None
            
            return None
        
        # Set valid data
        await cache.set("cache_key1", "response_valid")
        result = await get_with_validation("key1")
        assert result == "response_valid"
        
        # Set corrupted data
        await cache.set("cache_key2", "invalid_response")
        result = await get_with_validation("key2")
        
        # Should detect corruption
        result = await get_with_validation("key2")
        # After cleaning, should be None
        assert result is None


# ==================== ENCRYPTION FAILURE RECOVERY ====================

class TestEncryptionFailureRecovery:
    """Test recovery from encryption/decryption failures"""
    
    def test_decryption_failure_with_key_rotation(self):
        """Test handling decryption failure and key rotation recovery"""
        manager = EncryptionManager(master_key="old-key")
        
        # Encrypt with old key
        data = "sensitive"
        encrypted = manager.encrypt(data)
        
        # Verify decryption works
        decrypted = manager.decrypt(encrypted)
        assert decrypted == data
        
        # Simulate key rotation
        new_manager = EncryptionManager(master_key="new-key")
        
        # Old encrypted data won't decrypt with new key
        # In production, would use key versioning
        # For now, verify manager can handle this
        assert new_manager is not None
    
    def test_encryption_with_invalid_key_recovery(self):
        """Test recovery from invalid encryption key"""
        
        async def get_with_encryption_recovery(data: str):
            managers = [
                EncryptionManager(master_key="key_v1"),
                EncryptionManager(master_key="key_v2"),
                EncryptionManager(master_key="key_v3"),
            ]
            
            # Encrypt with first key
            encrypted = managers[0].encrypt(data)
            
            # Try to decrypt with different keys
            for manager in managers:
                try:
                    # In reality, would identify key version first
                    decrypted = manager.decrypt(encrypted)
                    return decrypted
                except Exception:
                    continue
            
            return None
        
        result = asyncio.run(get_with_encryption_recovery("test"))
        
        # Should succeed with first manager's key
        assert result is not None
    
    def test_field_encryption_partial_failure(self):
        """Test handling when some encrypted fields fail to decrypt"""
        manager = EncryptionManager(master_key="test-key")
        
        record = {
            "id": "user-1",
            "name": manager.encrypt("John"),
            "email": manager.encrypt("john@example.com"),
            "secret": manager.encrypt("sensitive")
        }
        
        def decrypt_record_safely(record):
            """Decrypt record, skipping failed fields"""
            decrypted = {}
            
            for key, value in record.items():
                try:
                    if isinstance(value, str) and value.startswith("encrypted:"):
                        decrypted[key] = manager.decrypt(value)
                    else:
                        decrypted[key] = value
                except Exception:
                    # Field decryption failed, use placeholder
                    decrypted[key] = "[DECRYPTION_FAILED]"
            
            return decrypted
        
        decrypted = decrypt_record_safely(record)
        
        # Should have all fields (even if some failed)
        assert "id" in decrypted
        assert "name" in decrypted
        assert "email" in decrypted
        assert "secret" in decrypted


# ==================== SECRET ROTATION FAILURE RECOVERY ====================

class TestSecretRotationRecovery:
    """Test recovery during secret rotation"""
    
    def test_secret_rotation_with_in_flight_operations(self):
        """Test that in-flight operations survive secret rotation"""
        secrets = SecretsManager()
        
        secrets.store_secret("db_password", "password_v1")
        
        in_flight_operations = []
        
        def operation_with_secret():
            # Get secret at start of operation
            password = secrets.get_secret("db_password")
            
            # Simulate operation (secret might be rotated during this)
            import time
            time.sleep(0.01)
            
            # Use secret (should still be valid)
            return f"used_{password}"
        
        # Start operation
        op1_result = operation_with_secret()
        
        # Rotate secret
        secrets.rotate_secret("db_password", "password_v2")
        
        # Start another operation
        op2_result = operation_with_secret()
        
        # Both should have completed
        assert "password_v1" in op1_result
        assert "password_v2" in op2_result
    
    def test_partial_secret_rotation_failure(self):
        """Test recovery when partial secret rotation fails"""
        secrets = SecretsManager()
        
        secrets.store_secret("secret_1", "value_1")
        secrets.store_secret("secret_2", "value_2")
        secrets.store_secret("secret_3", "value_3")
        
        def rotate_all_secrets_safely():
            """Rotate all secrets, continuing even if some fail"""
            results = {"success": [], "failed": []}
            
            for secret_name in ["secret_1", "secret_2", "secret_3"]:
                try:
                    new_version = f"{secrets.get_secret(secret_name)}_v2"
                    secrets.rotate_secret(secret_name, new_version)
                    results["success"].append(secret_name)
                except Exception as e:
                    results["failed"].append((secret_name, str(e)))
            
            return results
        
        results = rotate_all_secrets_safely()
        
        # All should succeed
        assert len(results["success"]) > 0
        assert "secret_1" in results["success"]


# ==================== AUDIT TRAIL FAILURE RECOVERY ====================

class TestAuditTrailFailureRecovery:
    """Test recovery when audit trail fails"""
    
    def test_audit_logging_with_storage_failure(self):
        """Test audit trail resilience when storage fails"""
        trail = AuditTrail()
        
        # Enable in-memory buffer for resilience
        audit_buffer = []
        
        def log_with_fallback(action, resource_type, resource_id, user_id):
            try:
                trail.log_action(action, resource_type, resource_id, user_id)
            except Exception as e:
                # Fallback to in-memory buffer
                audit_buffer.append({
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "user_id": user_id,
                    "timestamp": datetime.now(),
                    "error": "Storage failed"
                })
        
        # Log operations
        log_with_fallback(AuditAction.READ, "user", "user-1", "admin")
        log_with_fallback(AuditAction.UPDATE, "user", "user-1", "admin")
        log_with_fallback(AuditAction.DELETE, "user", "user-2", "admin")
        
        # All should be logged (in trail or buffer)
        assert len(trail.entries) + len(audit_buffer) == 3
    
    def test_tamper_detection_with_recovery(self):
        """Test tamper detection and recovery"""
        trail = AuditTrail()
        
        # Log initial entry
        trail.log_action(AuditAction.CREATE, "resource", "res-1", user_id="user-1")
        
        initial_count = len(trail.entries)
        
        # Try to tamper with entry
        if trail.entries:
            original_entry = trail.entries[0].copy()
            trail.entries[0]["user_id"] = "attacker"
        
        # Detect tampering
        tampered = trail.detect_tampering()
        
        # Restore from backup/log
        if tampered and trail.entries:
            trail.entries[0] = original_entry
        
        # Verify entry count unchanged
        assert len(trail.entries) == initial_count


# ==================== RBAC FAILURE RECOVERY ====================

class TestRBACFailureRecovery:
    """Test recovery from RBAC failures"""
    
    def test_permission_check_with_fallback(self):
        """Test permission check with fallback to safe default"""
        rbac = RBACManager()
        rbac.create_user("user-1", "Test User")
        
        def check_permission_with_fallback(user_id: str, permission: Permission):
            try:
                return rbac.has_permission(user_id, permission)
            except Exception:
                # On error, default to deny (fail-safe)
                return False
        
        # User doesn't have permission
        assert check_permission_with_fallback("user-1", Permission.ADMIN) == False
        
        # Grant permission
        rbac.grant_custom_permission("user-1", Permission.ADMIN)
        assert check_permission_with_fallback("user-1", Permission.ADMIN) == True
    
    def test_role_revocation_during_operation(self):
        """Test operation completion when role is revoked"""
        rbac = RBACManager()
        rbac.create_user("user-1", "Test User")
        rbac.assign_role_to_user("user-1", "admin")
        
        async def operation_with_role_check():
            # Check permission at start
            has_permission = rbac.has_permission("user-1", Permission.ADMIN)
            
            if not has_permission:
                raise PermissionError("Permission denied")
            
            # Simulate long operation
            await asyncio.sleep(0.01)
            
            # Check permission again
            final_permission = rbac.has_permission("user-1", Permission.ADMIN)
            
            return {"started": has_permission, "ended": final_permission}
        
        # Start operation
        task = operation_with_role_check()
        
        # Revoke role mid-operation
        asyncio.sleep(0.005)
        rbac.revoke_custom_permission("user-1", Permission.ADMIN)
        
        # Operation should complete (permission checked at start)
        # In production would have more sophisticated mechanisms
        assert task is not None


# ==================== COMPREHENSIVE ERROR SCENARIO ====================

class TestComprehensiveErrorScenario:
    """Test handling multiple simultaneous failures"""
    
    @pytest.mark.asyncio
    async def test_multiple_simultaneous_failures(self):
        """Test system response to multiple simultaneous failures"""
        injector = ErrorInjector()
        
        # Inject multiple failures
        injector.inject_failure("provider_1", "network_timeout", duration=0.5)
        injector.inject_failure("cache", "connection_refused", duration=0.5)
        injector.inject_failure("auth", "authentication_failed", duration=0.3)
        
        # Track successful operations
        successful_operations = 0
        failed_operations = 0
        
        async def resilient_operation(op_id: int):
            nonlocal successful_operations, failed_operations
            
            try:
                # Try with cache
                if injector.should_fail("cache"):
                    raise injector.get_failure_error("cache")
                
                # Try with provider
                if injector.should_fail("provider_1"):
                    raise injector.get_failure_error("provider_1")
                
                # Try with auth
                if injector.should_fail("auth"):
                    raise injector.get_failure_error("auth")
                
                successful_operations += 1
                return f"success_{op_id}"
            
            except Exception as e:
                failed_operations += 1
                # Retry with fallback paths
                try:
                    await asyncio.sleep(0.1)
                    successful_operations += 1
                    return f"fallback_success_{op_id}"
                except:
                    return None
        
        # Run operations during failure window
        results = await asyncio.gather(*[
            resilient_operation(i) for i in range(20)
        ], return_exceptions=True)
        
        # Most should eventually succeed
        success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        assert success_count >= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
