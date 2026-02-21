"""
Tests for Tier 4 Enhancements (Performance, Security, LLM Providers)
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Import modules
from phoenix.modules.llm_providers_extended import (
    ExtendedLLMProvider, MistralAIProvider, PerplexityAIProvider,
    TogetherAIProvider, ReplicateProvider, LocalLLMProvider,
    CustomEndpointProvider, ExtendedLLMProviderFactory, ProviderType, ProviderConfig
)

from phoenix.modules.performance.distributed_cache import (
    RedisClusterCache, MultiRegionCache, IntelligentEvictionPolicy, CacheWarming
)

from phoenix.modules.performance.request_batcher import (
    RequestBatcher, BatchStrategy, AdaptiveBatcher, BatchCostAnalyzer
)

from phoenix.modules.performance.streaming import (
    StreamingResponse, StreamingLLMResponse, StreamFormat, StreamingMetrics
)

from phoenix.security.encryption import (
    EncryptionManager, FieldEncryption, TLSConfiguration, EncryptedStorage
)

from phoenix.security.secrets_manager import (
    SecretsManager, SecretType, SecretRotationScheduler, PasswordGenerator
)

from phoenix.security.audit_trail import (
    AuditTrail, AuditAction, ComplianceFramework, ComplianceChecker
)

from phoenix.security.rbac import (
    RBACManager, Permission, AccessControlDecorator, JWTTokenGenerator
)


# ==================== Tests for LLM Providers ====================

class TestExtendedLLMProviders:
    """Test extended LLM provider integrations"""
    
    @pytest.mark.asyncio
    async def test_mistral_provider_complete(self):
        """Test Mistral AI provider"""
        config = ProviderConfig(
            provider_type=ProviderType.MISTRAL,
            api_key="test-key",
            model="mistral-small"
        )
        
        async with ExtendedLLMProviderFactory.create(config) as provider:
            assert provider.config.model == "mistral-small"
            assert provider.config.temperature == 0.7
    
    def test_provider_factory(self):
        """Test provider factory"""
        config = ProviderConfig(
            provider_type=ProviderType.LOCAL,
            base_url="http://localhost:8000",
            model="llama-2"
        )
        
        provider = ExtendedLLMProviderFactory.create(config)
        assert isinstance(provider, LocalLLMProvider)
    
    def test_provider_supports(self):
        """Test provider support check"""
        assert ExtendedLLMProviderFactory.supports(ProviderType.MISTRAL)
        assert ExtendedLLMProviderFactory.supports(ProviderType.LOCAL)
    
    def test_custom_endpoint_provider(self):
        """Test custom endpoint provider"""
        config = ProviderConfig(
            provider_type=ProviderType.CUSTOM,
            base_url="https://custom-llm.api/v1",
            model="custom-model",
            custom_headers={"X-API-Version": "2.0"}
        )
        
        provider = ExtendedLLMProviderFactory.create(config)
        assert isinstance(provider, CustomEndpointProvider)
        assert provider.config.custom_headers["X-API-Version"] == "2.0"


# ==================== Tests for Performance ====================

class TestDistributedCaching:
    """Test distributed caching"""
    
    @pytest.mark.asyncio
    async def test_cache_set_get(self):
        """Test basic cache operations"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        await cache.set("test_key", {"data": "value"}, ttl=300)
        result = await cache.get("test_key")
        
        assert result == {"data": "value"}
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self):
        """Test TTL expiration"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        # Set with 0 TTL (immediate expiration)
        await cache.set("expire_key", "value", ttl=0)
        await asyncio.sleep(0.01)
        
        result = await cache.get("expire_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_stats(self):
        """Test cache statistics"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.get("key1")  # Access to update stats
        
        stats = cache.get_stats()
        
        assert stats["entries"] == 2
        assert stats["total_accesses"] > 0
    
    @pytest.mark.asyncio
    async def test_multi_region_cache(self):
        """Test multi-region cache"""
        us_cache = RedisClusterCache(nodes=["us-node:6379"])
        eu_cache = RedisClusterCache(nodes=["eu-node:6379"])
        
        regions = {"us-east": us_cache, "eu-west": eu_cache}
        multi_cache = MultiRegionCache(regions)
        
        await multi_cache.set("distributed_key", {"region": "aware"})
        
        # Both regions should have the data
        us_result = await multi_cache.get("distributed_key", "us-east")
        eu_result = await multi_cache.get("distributed_key", "eu-west")
        
        assert us_result == {"region": "aware"}
        assert eu_result == {"region": "aware"}
    
    @pytest.mark.asyncio
    async def test_intelligent_eviction(self):
        """Test intelligent eviction policy"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        eviction = IntelligentEvictionPolicy(max_entries=10)
        
        # Fill cache
        for i in range(15):
            await cache.set(f"key_{i}", f"value_{i}")
        
        # Evaluate eviction
        to_evict = await eviction.evaluate(cache)
        
        # Should identify some entries for eviction
        assert len(to_evict) > 0
    
    @pytest.mark.asyncio
    async def test_cache_warming(self):
        """Test cache warming"""
        cache = RedisClusterCache(nodes=["localhost:6379"])
        warmer = CacheWarming(cache)
        
        warm_data = {
            "frequent_key1": "value1",
            "frequent_key2": "value2"
        }
        
        loaded = await warmer.warm_cache(warm_data)
        
        assert loaded == 2
        assert await cache.get("frequent_key1") == "value1"


class TestRequestBatching:
    """Test request batching"""
    
    @pytest.mark.asyncio
    async def test_batch_processor(self):
        """Test batch processor"""
        async def mock_processor(payloads):
            return [{"processed": True, "input": p} for p in payloads]
        
        batcher = RequestBatcher(
            processor=mock_processor,
            strategy=BatchStrategy.SIZE_BASED,
            max_batch_size=5
        )
        
        # Add requests
        for i in range(5):
            await batcher.add_request(f"req-{i}", {"data": f"request-{i}"})
        
        # Check stats
        stats = batcher.get_stats()
        assert stats["total_requests"] == 5
    
    @pytest.mark.asyncio
    async def test_adaptive_batcher(self):
        """Test adaptive batching"""
        async def mock_processor(payloads):
            return payloads
        
        batcher = RequestBatcher(
            processor=mock_processor,
            strategy=BatchStrategy.ADAPTIVE
        )
        
        adaptive = AdaptiveBatcher(batcher)
        
        # Add requests
        for i in range(10):
            await batcher.add_request(f"req-{i}", {"data": f"request-{i}"})
        
        # Adjust parameters
        await adaptive.adjust_parameters()
        
        # Get load metrics
        metrics = adaptive.get_load_metrics()
        assert "current_load" in metrics
    
    @pytest.mark.asyncio
    async def test_cost_analysis(self):
        """Test batch cost analysis"""
        analyzer = BatchCostAnalyzer(cost_per_request=0.001)
        
        analyzer.record_batch(batch_size=100, cost_per_batch=0.05)
        analyzer.record_batch(batch_size=50, cost_per_batch=0.03)
        
        summary = analyzer.get_cost_summary()
        
        assert summary["total_batches"] == 2
        assert summary["total_requests"] == 150
        assert summary["total_savings_usd"] > 0


class TestStreamingResponses:
    """Test streaming responses"""
    
    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """Test streaming response"""
        response = StreamingResponse("stream-1", StreamFormat.SSE)
        
        await response.write_chunk("Hello")
        await response.write_chunk(" ")
        await response.write_chunk("World")
        await response.finish()
        
        assert response.sequence >= 3
    
    @pytest.mark.asyncio
    async def test_streaming_format_sse(self):
        """Test SSE format"""
        async def mock_stream():
            yield "token1"
            yield "token2"
        
        stream = StreamingLLMResponse(mock_stream(), "test-stream")
        
        chunks = []
        async for chunk in stream.stream_with_format(StreamFormat.SSE):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert "data:" in "".join(chunks)
    
    @pytest.mark.asyncio
    async def test_streaming_metrics(self):
        """Test streaming metrics"""
        metrics = StreamingMetrics()
        
        metrics.start_stream("stream-1")
        metrics.record_chunk("stream-1", 1024)
        metrics.record_chunk("stream-1", 1024)
        metrics.end_stream("stream-1")
        
        summary = metrics.get_summary()
        
        assert summary["total_bytes"] == 2048
        assert summary["total_chunks"] == 2


# ==================== Tests for Security ====================

class TestEncryption:
    """Test encryption module"""
    
    def test_encryption_decryption(self):
        """Test encrypt/decrypt"""
        manager = EncryptionManager(master_key="secret-key-123")
        
        plaintext = "sensitive data"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_json_encryption(self):
        """Test JSON encryption"""
        manager = EncryptionManager(master_key="secret-key-123")
        
        data = {"user": "john", "role": "admin"}
        encrypted = manager.encrypt(data)
        decrypted = manager.decrypt_json(encrypted)
        
        assert decrypted == data
    
    def test_key_rotation(self):
        """Test key rotation"""
        manager = EncryptionManager(master_key="secret-key-123")
        
        original = manager.encrypt("test data")
        rotated = manager.rotate_key("new-secret-key-456")
        
        assert rotated == True
        assert manager.should_rotate_key() == False
    
    def test_field_encryption(self):
        """Test field-level encryption"""
        manager = EncryptionManager(master_key="secret-key-123")
        field_enc = FieldEncryption(manager, sensitive_fields=["password", "api_key"])
        
        user_data = {"name": "John", "password": "secret123", "api_key": "key-xyz"}
        encrypted = field_enc.encrypt_sensitive_fields(user_data)
        
        assert field_enc.is_encrypted(encrypted["password"])
        assert encrypted["name"] == "John"
        
        decrypted = field_enc.decrypt_sensitive_fields(encrypted)
        assert decrypted["password"] == "secret123"
    
    def test_encrypted_storage(self):
        """Test encrypted storage"""
        manager = EncryptionManager(master_key="secret-key-123")
        storage = EncryptedStorage(manager)
        
        storage.set("user_token", "secret-token-12345")
        retrieved = storage.get("user_token")
        
        assert retrieved == "secret-token-12345"


class TestSecretsManager:
    """Test secrets management"""
    
    def test_store_retrieve_secret(self):
        """Test store and retrieve secret"""
        manager = SecretsManager()
        
        manager.store_secret("api_key", "sk-123456", SecretType.API_KEY)
        retrieved = manager.get_secret("api_key")
        
        assert retrieved == "sk-123456"
    
    def test_secret_expiration(self):
        """Test secret expiration"""
        manager = SecretsManager()
        
        manager.store_secret("temp_key", "temp-value", expires_in_days=0)
        retrieved = manager.get_secret("temp_key")
        
        # Should be expired
        assert retrieved is None
    
    def test_secret_rotation(self):
        """Test secret rotation"""
        manager = SecretsManager()
        
        manager.store_secret("api_key", "old-value", rotation_enabled=True)
        manager.rotate_secret("api_key", "new-value")
        
        new_value = manager.get_secret("api_key")
        assert new_value == "new-value"
    
    def test_audit_log(self):
        """Test audit logging"""
        manager = SecretsManager()
        
        manager.store_secret("key1", "value1")
        manager.get_secret("key1")
        manager.get_secret("key1")
        
        audit_log = manager.get_audit_log(days=1)
        
        assert len(audit_log) > 0
        assert any(e["action"] == "SECRET_ACCESSED" for e in audit_log)
    
    def test_password_generation(self):
        """Test password generation"""
        password = PasswordGenerator.generate(length=32)
        
        assert len(password) == 32
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)


class TestAuditTrail:
    """Test audit trail"""
    
    def test_audit_logging(self):
        """Test audit logging"""
        trail = AuditTrail(retention_days=365)
        
        logged = trail.log_action(
            AuditAction.CREATE,
            "user",
            "user-123",
            user_id="admin-1",
            status="success"
        )
        
        assert logged == True
    
    def test_api_request_logging(self):
        """Test API request logging"""
        trail = AuditTrail()
        
        trail.log_api_request(
            "POST",
            "/api/llm/complete",
            "user-123",
            {"prompt": "What is AI?"},
            200,
            ip_address="192.168.1.1"
        )
        
        assert len(trail.entries) == 1
    
    def test_compliance_frameworks(self):
        """Test compliance framework tracking"""
        trail = AuditTrail()
        trail.enable_framework(ComplianceFramework.SOC2)
        trail.enable_framework(ComplianceFramework.GDPR)
        
        trail.log_action(
            AuditAction.READ,
            "data",
            "data-123",
            user_id="user-1"
        )
        
        report = trail.generate_compliance_report(ComplianceFramework.SOC2)
        
        assert report["framework"] == "soc2"
    
    def test_compliance_checker(self):
        """Test compliance checker"""
        trail = AuditTrail()
        trail.log_action(AuditAction.READ, "api", "endpoint-1")
        
        checker = ComplianceChecker(trail)
        soc2_check = checker.check_soc2_compliance()
        
        assert "all_requirements_met" in soc2_check


class TestRBAC:
    """Test role-based access control"""
    
    def test_create_user_and_assign_role(self):
        """Test user creation and role assignment"""
        rbac = RBACManager()
        
        rbac.create_user("user-123", "john_doe")
        rbac.assign_role_to_user("user-123", "user")
        
        user = rbac.users["user-123"]
        assert len(user.roles) == 1
    
    def test_permission_check(self):
        """Test permission checking"""
        rbac = RBACManager()
        
        rbac.create_user("user-123", "john_doe")
        rbac.assign_role_to_user("user-123", "user")
        
        # User role has READ permission
        assert rbac.has_permission("user-123", Permission.READ) == True
        assert rbac.has_permission("user-123", Permission.ADMIN) == False
    
    def test_custom_permissions(self):
        """Test custom permissions"""
        rbac = RBACManager()
        
        rbac.create_user("user-456", "jane_smith")
        rbac.grant_custom_permission("user-456", Permission.EXPORT_DATA)
        
        assert rbac.has_permission("user-456", Permission.EXPORT_DATA) == True
    
    def test_get_user_permissions(self):
        """Test getting user permissions"""
        rbac = RBACManager()
        
        rbac.create_user("user-789", "bob_jones")
        rbac.assign_role_to_user("user-789", "viewer")
        
        perms = rbac.get_user_permissions("user-789")
        
        assert Permission.READ in perms
        assert Permission.WRITE not in perms
    
    def test_jwt_token_generation(self):
        """Test JWT token generation"""
        rbac = RBACManager()
        rbac.create_user("user-123", "john_doe")
        rbac.assign_role_to_user("user-123", "user")
        
        jwt_gen = JWTTokenGenerator(rbac, "secret-key")
        token = jwt_gen.generate_token("user-123")
        
        assert token is not None
        
        # Validate token
        decoded = jwt_gen.validate_token(token)
        assert decoded is not None
        assert decoded["user_id"] == "user-123"


# ==================== Integration Tests ====================

class TestTier4Integration:
    """Integration tests for Tier 4 enhancements"""
    
    @pytest.mark.asyncio
    async def test_multi_provider_llm_support(self):
        """Test support for multiple LLM providers"""
        providers = [
            ProviderType.MISTRAL,
            ProviderType.PERPLEXITY,
            ProviderType.TOGETHER,
            ProviderType.LOCAL,
            ProviderType.CUSTOM
        ]
        
        for provider_type in providers:
            assert ExtendedLLMProviderFactory.supports(provider_type)
    
    @pytest.mark.asyncio
    async def test_performance_with_security(self):
        """Test performance and security together"""
        # Encrypt sensitive data
        manager = EncryptionManager(master_key="secret")
        encrypted = manager.encrypt("api_key_value")
        
        # Cache encrypted data
        cache = RedisClusterCache(nodes=["localhost:6379"])
        await cache.set("cached_key", encrypted)
        
        # Retrieve and decrypt
        cached = await cache.get("cached_key")
        decrypted = manager.decrypt(cached)
        
        assert decrypted == "api_key_value"
    
    @pytest.mark.asyncio
    async def test_rbac_with_audit_trail(self):
        """Test RBAC with audit trail"""
        rbac = RBACManager()
        trail = AuditTrail()
        
        # Create user with role
        rbac.create_user("user-123", "john_doe")
        rbac.assign_role_to_user("user-123", "user")
        
        # Check permission and log
        has_perm = rbac.has_permission("user-123", Permission.READ)
        
        trail.log_action(
            AuditAction.READ,
            "api",
            "endpoint",
            user_id="user-123",
            status="success" if has_perm else "failure"
        )
        
        assert has_perm == True
        assert len(trail.entries) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
