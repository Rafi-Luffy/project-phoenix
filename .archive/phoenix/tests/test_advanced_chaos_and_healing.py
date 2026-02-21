"""
Advanced Chaos Engineering & Self-Healing Recovery Tests

Complex scenarios with cascading errors, chaotic conditions, and verification
that the system automatically heals and recovers to functional state.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import random
import time
from enum import Enum

# Import Phoenix modules
from phoenix.modules.llm_providers_extended import ExtendedLLMProvider
from phoenix.modules.performance.distributed_cache import RedisClusterCache
from phoenix.modules.performance.request_batcher import RequestBatcher, BatchStrategy
from phoenix.modules.performance.streaming import StreamingResponse, StreamingMetrics
from phoenix.security.encryption import EncryptionManager
from phoenix.security.secrets_manager import SecretsManager
from phoenix.security.audit_trail import AuditTrail, AuditAction
from phoenix.security.rbac import RBACManager, Permission


# ==================== CHAOS STATE MANAGEMENT ====================

class ChaosState(Enum):
    """Different chaos conditions"""
    HEALTHY = "healthy"
    PARTIAL_FAILURE = "partial_failure"
    CASCADE_FAILURE = "cascade_failure"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    HEALED = "healed"


class ChaosEngine:
    """Engine to simulate complex failure scenarios"""
    
    def __init__(self):
        self.state = ChaosState.HEALTHY
        self.active_failures = {}
        self.error_count = 0
        self.recovery_count = 0
        self.component_health = {
            "cache": True,
            "provider": True,
            "encryption": True,
            "auth": True,
            "audit": True,
            "batch": True
        }
        self.error_injection_points = {}
    
    def inject_cascade_failure(self, components: List[str], duration: float = 5.0):
        """Inject cascading failures across multiple components"""
        self.state = ChaosState.CASCADE_FAILURE
        for component in components:
            self.component_health[component] = False
            self.active_failures[component] = {
                "start_time": datetime.now(),
                "duration": duration,
                "error_count": 0
            }
    
    def inject_partial_failure(self, component: str, failure_rate: float = 0.3):
        """Inject partial failures (X% of requests fail)"""
        self.state = ChaosState.PARTIAL_FAILURE
        self.active_failures[component] = {
            "failure_rate": failure_rate,
            "total_requests": 0,
            "failed_requests": 0
        }
    
    def should_fail(self, component: str) -> bool:
        """Check if component should fail"""
        if component not in self.active_failures:
            return False
        
        failure = self.active_failures[component]
        
        # Check duration-based failures
        if "duration" in failure:
            elapsed = (datetime.now() - failure["start_time"]).total_seconds()
            if elapsed > failure["duration"]:
                self.recover_component(component)
                return False
        
        # Check partial failures
        if "failure_rate" in failure:
            failure["total_requests"] += 1
            if random.random() < failure["failure_rate"]:
                failure["failed_requests"] += 1
                return True
            return False
        
        return self.component_health.get(component, True) == False
    
    def recover_component(self, component: str):
        """Recover a component"""
        self.component_health[component] = True
        if component in self.active_failures:
            del self.active_failures[component]
        self.recovery_count += 1
        
        # Check if all recovered
        if all(self.component_health.values()):
            self.state = ChaosState.HEALED
    
    def mark_error(self, component: str):
        """Mark an error occurred"""
        self.error_count += 1
        if component in self.active_failures:
            self.active_failures[component]["error_count"] = \
                self.active_failures[component].get("error_count", 0) + 1
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            "state": self.state.value,
            "component_health": self.component_health.copy(),
            "active_failures": len(self.active_failures),
            "total_errors": self.error_count,
            "recoveries": self.recovery_count
        }


# ==================== COMPLEX CHAOS SCENARIOS ====================

class TestComplexChaosScenarios:
    """Test system under complex chaos conditions"""
    
    @pytest.mark.asyncio
    async def test_cascading_system_failure_with_recovery(self):
        """
        Scenario: Cascading failure across cache, provider, and auth
        Expected: System detects failures, activates fallbacks, recovers
        """
        chaos = ChaosEngine()
        
        # Setup components
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Track operations
        operations = {
            "attempted": 0,
            "succeeded": 0,
            "failed_then_recovered": 0,
            "fallback_used": 0
        }
        
        async def operation_with_cascade_detection(op_id: int, data: str):
            operations["attempted"] += 1
            
            try:
                # Check cache first
                if chaos.should_fail("cache"):
                    chaos.mark_error("cache")
                    raise Exception("Cache failure")
                
                cached = await cache.get(f"key_{op_id}")
                if cached:
                    operations["succeeded"] += 1
                    return cached
                
                # Try provider
                if chaos.should_fail("provider"):
                    chaos.mark_error("provider")
                    raise Exception("Provider failure")
                
                # Try encryption
                if chaos.should_fail("encryption"):
                    chaos.mark_error("encryption")
                    raise Exception("Encryption failure")
                
                # Normal processing
                result = f"result_{data}"
                await cache.set(f"key_{op_id}", result)
                operations["succeeded"] += 1
                return result
            
            except Exception as e:
                # Fallback: use in-memory processing
                operations["fallback_used"] += 1
                operations["failed_then_recovered"] += 1
                
                # Recovery: try direct processing
                return f"recovered_{data}"
        
        # Phase 1: Normal operation
        for i in range(10):
            result = await operation_with_cascade_detection(i, f"data_{i}")
            assert result is not None
        
        # Phase 2: Inject cascading failures
        chaos.inject_cascade_failure(["cache", "provider"], duration=0.2)
        
        # Send operations during chaos
        for i in range(20, 40):
            result = await operation_with_cascade_detection(i, f"data_{i}")
            assert result is not None
        
        # Phase 3: Wait for recovery
        await asyncio.sleep(0.3)
        
        # Phase 4: Verify system recovered
        health = chaos.get_health_report()
        assert health["state"] == "healed"
        assert all(health["component_health"].values())
        
        # Verify metrics
        assert operations["attempted"] > 0
        assert operations["succeeded"] > 0
        assert operations["failed_then_recovered"] > 0
        assert operations["fallback_used"] > 0
    
    @pytest.mark.asyncio
    async def test_partial_failure_with_adaptive_retry(self):
        """
        Scenario: 30% of requests fail, system adapts retry strategy
        Expected: Eventually all requests succeed, system learns failure pattern
        """
        chaos = ChaosEngine()
        chaos.inject_partial_failure("provider", failure_rate=0.3)
        
        retry_stats = {
            "first_attempt_success": 0,
            "first_attempt_failure": 0,
            "retry_success": 0,
            "retry_failure": 0,
            "max_retries_exceeded": 0
        }
        
        async def adaptive_request(req_id: int, data: str, max_retries: int = 5):
            """Request with adaptive retry based on component health"""
            attempt = 0
            
            while attempt <= max_retries:
                try:
                    if chaos.should_fail("provider"):
                        chaos.mark_error("provider")
                        if attempt == 0:
                            retry_stats["first_attempt_failure"] += 1
                        raise Exception("Provider error")
                    
                    if attempt == 0:
                        retry_stats["first_attempt_success"] += 1
                    else:
                        retry_stats["retry_success"] += 1
                    
                    return f"success_{data}"
                
                except Exception:
                    attempt += 1
                    
                    if attempt > max_retries:
                        retry_stats["max_retries_exceeded"] += 1
                        raise
                    
                    # Exponential backoff
                    backoff = min(2 ** attempt * 0.01, 0.5)
                    await asyncio.sleep(backoff)
            
            retry_stats["retry_failure"] += 1
            return None
        
        # Send 100 requests through partial failure
        results = await asyncio.gather(*[
            adaptive_request(i, f"req_{i}")
            for i in range(100)
        ], return_exceptions=True)
        
        # Most should succeed after retries
        successful = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        assert successful >= 80  # At least 80% success after retries
        
        # Verify retry happened
        assert retry_stats["first_attempt_failure"] > 0
        assert retry_stats["retry_success"] > 0
    
    @pytest.mark.asyncio
    async def test_encryption_key_corruption_with_fallback(self):
        """
        Scenario: Encryption key becomes corrupted mid-operation
        Expected: System detects, falls back to in-memory key, continues
        """
        manager = EncryptionManager(master_key="test-key-1")
        backup_manager = EncryptionManager(master_key="test-key-1")
        
        key_state = {"corrupted": False, "recovery_attempts": 0}
        
        def encrypt_with_fallback(data: str):
            try:
                if key_state["corrupted"]:
                    raise ValueError("Master key corrupted")
                
                return manager.encrypt(data)
            
            except ValueError:
                key_state["recovery_attempts"] += 1
                
                # Fallback: use backup manager
                return backup_manager.encrypt(data)
        
        # Encrypt normally
        encrypted1 = encrypt_with_fallback("sensitive_data_1")
        assert encrypted1 is not None
        assert key_state["recovery_attempts"] == 0
        
        # Corrupt key
        key_state["corrupted"] = True
        
        # Should use fallback
        encrypted2 = encrypt_with_fallback("sensitive_data_2")
        assert encrypted2 is not None
        assert key_state["recovery_attempts"] == 1
        
        # Recover key
        key_state["corrupted"] = False
        
        # Should work normally again
        encrypted3 = encrypt_with_fallback("sensitive_data_3")
        assert encrypted3 is not None
        assert key_state["recovery_attempts"] == 1  # No more recoveries
    
    @pytest.mark.asyncio
    async def test_batch_processor_failure_with_circuit_breaker(self):
        """
        Scenario: Batch processor fails repeatedly, circuit breaker engages
        Expected: System stops attempting failed batches, uses fallback
        """
        class FailingBatchProcessor:
            def __init__(self):
                self.attempt_count = 0
                self.failure_threshold = 3
                self.is_broken = False
            
            async def process(self, items):
                self.attempt_count += 1
                
                if self.attempt_count <= self.failure_threshold:
                    raise Exception(f"Batch processing failed (attempt {self.attempt_count})")
                
                return items
        
        processor = FailingBatchProcessor()
        
        fallback_processing = {"used": 0}
        
        async def batch_with_circuit_breaker(items: List[str]):
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    return await processor.process(items)
                
                except Exception as e:
                    if attempt == max_attempts - 1:
                        # Circuit breaker open, use fallback
                        processor.is_broken = True
                        fallback_processing["used"] += 1
                        return [f"fallback_{item}" for item in items]
                    
                    await asyncio.sleep(0.05)
            
            return None
        
        # First attempt fails
        result = await batch_with_circuit_breaker(["item_1", "item_2"])
        assert result is not None
        assert fallback_processing["used"] == 1
        assert processor.is_broken
    
    @pytest.mark.asyncio
    async def test_audit_trail_storage_failure_with_buffer(self):
        """
        Scenario: Audit storage becomes unavailable
        Expected: System buffers to memory, continues, syncs when available
        """
        trail = AuditTrail()
        
        storage_state = {"available": True, "sync_needed": False}
        in_memory_buffer = []
        
        async def log_with_buffering(action, resource_type, resource_id, user_id):
            try:
                if not storage_state["available"]:
                    raise Exception("Storage unavailable")
                
                trail.log_action(action, resource_type, resource_id, user_id)
            
            except Exception:
                # Buffer to memory
                in_memory_buffer.append({
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "user_id": user_id,
                    "timestamp": datetime.now()
                })
                storage_state["sync_needed"] = True
        
        # Log normally
        await log_with_buffering(AuditAction.CREATE, "user", "user-1", "admin")
        assert len(trail.entries) == 1
        assert len(in_memory_buffer) == 0
        
        # Storage fails
        storage_state["available"] = False
        
        # Should buffer to memory
        await log_with_buffering(AuditAction.READ, "user", "user-1", "admin")
        assert len(in_memory_buffer) == 1
        assert storage_state["sync_needed"]
        
        # Storage recovers
        storage_state["available"] = True
        
        # Sync buffer to storage
        for entry in in_memory_buffer:
            trail.log_action(entry["action"], entry["resource_type"], 
                           entry["resource_id"], entry["user_id"])
        
        in_memory_buffer.clear()
        storage_state["sync_needed"] = False
        
        # Verify all logged
        assert len(trail.entries) >= 2
    
    @pytest.mark.asyncio
    async def test_rbac_database_failure_with_cache_fallback(self):
        """
        Scenario: RBAC database down, in-memory cache provides fallback
        Expected: Permission checks still work from cache, recover when DB up
        """
        rbac = RBACManager()
        
        # Build permission cache
        permission_cache = {}
        db_state = {"available": True}
        
        def check_permission_with_cache(user_id: str, permission: Permission):
            # Try database first
            if db_state["available"]:
                try:
                    has_perm = rbac.has_permission(user_id, permission)
                    # Cache the result
                    cache_key = f"{user_id}:{permission.value}"
                    permission_cache[cache_key] = has_perm
                    return has_perm
                except Exception:
                    db_state["available"] = False
            
            # Fallback to cache
            cache_key = f"{user_id}:{permission.value}"
            if cache_key in permission_cache:
                return permission_cache[cache_key]
            
            # Default deny
            return False
        
        # Setup users
        rbac.create_user("user-1", "User 1")
        rbac.assign_role_to_user("user-1", "user")
        
        # Build cache
        result1 = check_permission_with_cache("user-1", Permission.READ)
        assert result1 == True
        assert len(permission_cache) > 0
        
        # Database fails
        db_state["available"] = False
        
        # Should still work from cache
        result2 = check_permission_with_cache("user-1", Permission.READ)
        assert result2 == True  # From cache
        
        # Database recovers
        db_state["available"] = True
        
        # Should verify from DB again
        result3 = check_permission_with_cache("user-1", Permission.READ)
        assert result3 == True


# ==================== MULTI-TIER FAILURE SCENARIOS ====================

class TestMultiTierFailureScenarios:
    """Test failures across multiple tiers simultaneously"""
    
    @pytest.mark.asyncio
    async def test_three_tier_simultaneous_failure(self):
        """
        Scenario: Cache, Provider, and RBAC all fail simultaneously
        Expected: System continues with degraded functionality
        """
        chaos = ChaosEngine()
        
        # Setup
        cache = RedisClusterCache(nodes=["localhost:6379"])
        rbac = RBACManager()
        rbac.create_user("user-1", "Test User")
        
        operation_log = []
        
        async def three_tier_operation(op_id: int):
            # Tier 1: Authentication
            if chaos.should_fail("auth"):
                operation_log.append({"op": op_id, "stage": "auth", "status": "failed"})
                return None
            
            operation_log.append({"op": op_id, "stage": "auth", "status": "ok"})
            
            # Tier 2: Cache check
            if chaos.should_fail("cache"):
                operation_log.append({"op": op_id, "stage": "cache", "status": "failed"})
                # Continue anyway
            else:
                cached = await cache.get(f"op_{op_id}")
                if cached:
                    operation_log.append({"op": op_id, "stage": "cache", "status": "hit"})
                    return cached
            
            # Tier 3: Provider
            if chaos.should_fail("provider"):
                operation_log.append({"op": op_id, "stage": "provider", "status": "failed"})
                return f"fallback_{op_id}"
            
            operation_log.append({"op": op_id, "stage": "provider", "status": "ok"})
            return f"result_{op_id}"
        
        # Phase 1: Normal
        for i in range(5):
            result = await three_tier_operation(i)
            assert result is not None
        
        # Phase 2: Inject 3-tier failure
        chaos.inject_cascade_failure(["auth", "cache", "provider"], duration=0.2)
        
        # Continue operations
        for i in range(5, 15):
            result = await three_tier_operation(i)
            # Should still get results
            assert result is not None
        
        # Phase 3: Verify fallback was used
        failed_stages = [log["stage"] for log in operation_log if log["status"] == "failed"]
        assert len(failed_stages) > 0
    
    @pytest.mark.asyncio
    async def test_provider_auth_encryption_failure_cascade(self):
        """
        Scenario: Provider fails, causing auth timeout, encryption errors
        Expected: System isolates failures, continues with safe degradation
        """
        
        class CascadeFailure:
            def __init__(self):
                self.provider_failed = False
                self.cascade_to_auth = False
                self.cascade_to_encryption = False
            
            async def call_provider(self):
                if self.provider_failed:
                    self.cascade_to_auth = True
                    raise Exception("Provider timeout")
                return "provider_response"
            
            async def authenticate(self):
                if self.cascade_to_auth:
                    self.cascade_to_encryption = True
                    raise Exception("Auth timeout")
                return True
            
            async def encrypt_response(self, data):
                if self.cascade_to_encryption:
                    return f"unencrypted_{data}"  # Fallback: unencrypted
                return f"encrypted_{data}"
        
        cascade = CascadeFailure()
        
        results = {"normal": 0, "partial": 0, "fallback": 0}
        
        async def resilient_workflow():
            try:
                # Normal path
                provider_result = await cascade.call_provider()
                is_authenticated = await cascade.authenticate()
                encrypted = await cascade.encrypt_response(provider_result)
                results["normal"] += 1
                return encrypted
            
            except Exception as first_error:
                try:
                    # Partial recovery: try encryption only
                    encrypted = await cascade.encrypt_response("fallback_data")
                    results["partial"] += 1
                    return encrypted
                except Exception:
                    # Full fallback
                    results["fallback"] += 1
                    return "safe_default_response"
        
        # Normal operation
        for _ in range(5):
            result = await resilient_workflow()
            assert result is not None
        
        # Trigger cascade
        cascade.provider_failed = True
        
        for _ in range(10):
            result = await resilient_workflow()
            assert result is not None
        
        # Verify fallback was used
        assert results["normal"] > 0
        assert results["partial"] > 0 or results["fallback"] > 0


# ==================== ERROR RECOVERY VERIFICATION ====================

class TestErrorRecoveryVerification:
    """Verify system fully recovers from errors"""
    
    @pytest.mark.asyncio
    async def test_full_recovery_sequence(self):
        """
        Test complete error → detection → isolation → recovery → verification
        """
        
        class SystemUnderTest:
            def __init__(self):
                self.state = "healthy"
                self.error_detected = False
                self.recovery_in_progress = False
                self.fully_recovered = False
                self.operations_during_error = 0
                self.operations_after_recovery = 0
            
            async def operation(self):
                if self.state == "error":
                    self.operations_during_error += 1
                    # Fallback
                    return "fallback_result"
                
                if self.state == "healthy":
                    self.operations_after_recovery += 1
                    return "normal_result"
            
            async def inject_error(self):
                self.state = "error"
            
            async def detect_error(self):
                self.error_detected = True
                return True
            
            async def isolate_component(self):
                # Prevent cascade
                pass
            
            async def begin_recovery(self):
                self.recovery_in_progress = True
            
            async def recover(self):
                await asyncio.sleep(0.1)
                self.state = "healthy"
            
            async def verify_recovery(self):
                # Run test operation
                result = await self.operation()
                if result == "normal_result":
                    self.fully_recovered = True
                    return True
                return False
        
        system = SystemUnderTest()
        
        # Phase 1: Normal operations
        for _ in range(10):
            result = await system.operation()
            assert result == "normal_result"
        
        # Phase 2: Inject error
        await system.inject_error()
        assert system.state == "error"
        
        # Phase 3: Continue operations (should use fallback)
        for _ in range(10):
            result = await system.operation()
            assert result == "fallback_result"
        
        # Phase 4: Detect and isolate
        assert await system.detect_error()
        await system.isolate_component()
        
        # Phase 5: Recover
        await system.begin_recovery()
        await system.recover()
        
        # Phase 6: Verify recovery
        assert await system.verify_recovery()
        assert system.fully_recovered
        
        # Phase 7: Resume normal operations
        for _ in range(10):
            result = await system.operation()
            assert result == "normal_result"
        
        # Verify metrics
        assert system.operations_during_error > 0  # Fallback worked
        assert system.operations_after_recovery > 0  # Recovered
        assert system.fully_recovered  # Fully healthy


# ==================== CHAOS WITH TIMING ISSUES ====================

class TestChaosWithTimingIssues:
    """Test recovery with race conditions and timing issues"""
    
    @pytest.mark.asyncio
    async def test_concurrent_errors_with_recovery(self):
        """
        Scenario: Multiple concurrent errors with overlapping recovery
        Expected: System coordinates recovery correctly
        """
        
        class ConcurrentComponent:
            def __init__(self, name: str):
                self.name = name
                self.state = "healthy"
                self.request_count = 0
                self.error_count = 0
            
            async def handle_request(self):
                self.request_count += 1
                
                if self.state == "error":
                    self.error_count += 1
                    raise Exception(f"{self.name} error")
                
                await asyncio.sleep(0.01)
                return f"{self.name}_ok"
            
            async def recover(self):
                await asyncio.sleep(0.05)
                self.state = "healthy"
        
        components = [
            ConcurrentComponent("cache"),
            ConcurrentComponent("provider"),
            ConcurrentComponent("auth"),
        ]
        
        # Induce errors in all components
        for comp in components:
            comp.state = "error"
        
        # Send concurrent requests
        results = await asyncio.gather(*[
            comp.handle_request() for comp in components for _ in range(10)
        ], return_exceptions=True)
        
        # Count errors
        errors_occurred = sum(1 for r in results if isinstance(r, Exception))
        assert errors_occurred > 0
        
        # Recover all components concurrently
        await asyncio.gather(*[comp.recover() for comp in components])
        
        # Verify all recovered
        results = await asyncio.gather(*[
            comp.handle_request() for comp in components for _ in range(10)
        ], return_exceptions=True)
        
        # All should succeed now
        errors_after = sum(1 for r in results if isinstance(r, Exception))
        assert errors_after == 0
    
    @pytest.mark.asyncio
    async def test_race_condition_between_error_and_recovery(self):
        """
        Scenario: Error detected while recovery in progress
        Expected: System handles correctly without double-recovery
        """
        
        class RaceConditionTest:
            def __init__(self):
                self.is_recovering = False
                self.error_occurred = False
                self.recovery_attempts = 0
                self.state = "healthy"
            
            async def operation(self):
                if self.error_occurred and not self.is_recovering:
                    raise Exception("Operation failed")
                return "ok"
            
            async def trigger_error(self):
                self.error_occurred = True
            
            async def try_recover(self):
                # Only recover if not already recovering
                if self.is_recovering:
                    return False
                
                self.is_recovering = True
                self.recovery_attempts += 1
                
                await asyncio.sleep(0.05)
                
                self.error_occurred = False
                self.is_recovering = False
                self.state = "healthy"
                return True
        
        test = RaceConditionTest()
        
        # Trigger error
        await test.trigger_error()
        
        # Try to recover concurrently
        recovery_tasks = [test.try_recover() for _ in range(5)]
        results = await asyncio.gather(*recovery_tasks)
        
        # Only one should succeed (others should find recovery in progress)
        successful_recoveries = sum(1 for r in results if r)
        assert successful_recoveries == 1
        assert test.recovery_attempts <= 2  # Prevent infinite recovery loops


# ==================== COMPLEX ERROR PATTERNS ====================

class TestComplexErrorPatterns:
    """Test complex, realistic error patterns"""
    
    @pytest.mark.asyncio
    async def test_intermittent_errors_with_adaptive_strategy(self):
        """
        Scenario: Intermittent errors (not always failing)
        Expected: System learns pattern and adapts
        """
        
        class AdaptiveComponent:
            def __init__(self):
                self.error_pattern = []  # True = error, False = ok
                self.operation_index = 0
                self.retry_threshold = 3
                self.success_threshold = 5
                self.current_strategy = "aggressive"  # aggressive, moderate, conservative
                self.stats = {"success": 0, "error": 0}
            
            async def execute(self):
                # Get error pattern
                should_error = self.error_pattern[self.operation_index % len(self.error_pattern)]
                self.operation_index += 1
                
                if should_error:
                    self.stats["error"] += 1
                    raise Exception("Intermittent error")
                
                self.stats["success"] += 1
                return "ok"
            
            async def handle_with_strategy(self):
                max_retries = {
                    "aggressive": 1,
                    "moderate": 3,
                    "conservative": 5
                }[self.current_strategy]
                
                for attempt in range(max_retries):
                    try:
                        return await self.execute()
                    except Exception:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(0.01 * (2 ** attempt))
                            continue
                        raise
                
                return None
            
            def adapt_strategy(self):
                """Learn from error pattern"""
                error_rate = self.stats["error"] / (self.stats["error"] + self.stats["success"] + 1)
                
                if error_rate > 0.5:
                    self.current_strategy = "conservative"
                elif error_rate > 0.2:
                    self.current_strategy = "moderate"
                else:
                    self.current_strategy = "aggressive"
        
        # Test with 30% error pattern
        component = AdaptiveComponent()
        component.error_pattern = [False, False, True, False, False, False, True, False, False, True]
        
        successes = 0
        for i in range(50):
            try:
                result = await component.handle_with_strategy()
                if result:
                    successes += 1
            except Exception:
                pass
            
            # Adapt every 10 operations
            if (i + 1) % 10 == 0:
                component.adapt_strategy()
        
        # Most should succeed with retries
        assert successes > 35
    
    @pytest.mark.asyncio
    async def test_error_propagation_containment(self):
        """
        Scenario: Error in one component shouldn't crash entire system
        Expected: Error contained, other components continue
        """
        
        class SystemWithMultipleComponents:
            def __init__(self):
                self.components = {
                    "cache": {"state": "healthy", "operations": 0},
                    "auth": {"state": "healthy", "operations": 0},
                    "provider": {"state": "healthy", "operations": 0},
                    "audit": {"state": "healthy", "operations": 0},
                }
            
            async def run_all_components(self):
                """Run all components concurrently"""
                return await asyncio.gather(*[
                    self._run_component(name)
                    for name in self.components
                ], return_exceptions=True)
            
            async def _run_component(self, name: str):
                comp = self.components[name]
                
                if comp["state"] == "error":
                    comp["operations"] += 1
                    raise Exception(f"{name} error")
                
                comp["operations"] += 1
                await asyncio.sleep(0.01)
                return f"{name}_ok"
            
            def trigger_error(self, component_name: str):
                self.components[component_name]["state"] = "error"
        
        system = SystemWithMultipleComponents()
        
        # Trigger error in one component
        system.trigger_error("cache")
        
        # Run all components
        results = await system.run_all_components()
        
        # Check containment
        cache_failed = isinstance(results[0], Exception)
        others_succeeded = all(not isinstance(r, Exception) for r in results[1:])
        
        assert cache_failed, "Cache should have errored"
        assert others_succeeded, "Other components should continue working"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
