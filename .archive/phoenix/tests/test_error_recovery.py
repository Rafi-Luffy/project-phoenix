"""
Error Recovery & Resilience Tests

Tests circuit breaker, retry strategies, fallback mechanisms.
"""

import pytest
import time
from unittest.mock import Mock, patch

from phoenix.core.error_recovery import (
    CircuitBreaker,
    CircuitState,
    RetryStrategy,
    FallbackProvider,
    ErrorRecoveryOrchestrator,
    ErrorCategory,
    categorize_error,
    CircuitBreakerError,
    ExhaustedRetriesError,
)


# ============ Error Categorization Tests ============

class TestErrorCategorization:
    """Test error categorization logic."""
    
    def test_categorize_transient_timeout(self):
        """Test timeout is transient."""
        error = TimeoutError("Connection timeout")
        assert categorize_error(error) == ErrorCategory.TRANSIENT
    
    def test_categorize_transient_connection(self):
        """Test connection error is transient."""
        error = ConnectionError("Connection refused")
        assert categorize_error(error) == ErrorCategory.TRANSIENT
    
    def test_categorize_permanent_not_found(self):
        """Test 404 is permanent."""
        error = Exception("404 Not Found")
        assert categorize_error(error) == ErrorCategory.PERMANENT
    
    def test_categorize_permanent_unauthorized(self):
        """Test 401 is permanent."""
        error = Exception("401 Unauthorized")
        assert categorize_error(error) == ErrorCategory.PERMANENT
    
    def test_categorize_permanent_forbidden(self):
        """Test 403 is permanent."""
        error = Exception("403 Forbidden")
        assert categorize_error(error) == ErrorCategory.PERMANENT
    
    def test_categorize_unknown(self):
        """Test unknown error."""
        error = Exception("Something weird")
        assert categorize_error(error) == ErrorCategory.UNKNOWN
    
    def test_categorize_rate_limit(self):
        """Test rate limit is transient."""
        error = Exception("429 Too Many Requests")
        assert categorize_error(error) == ErrorCategory.TRANSIENT


# ============ Circuit Breaker Tests ============

class TestCircuitBreaker:
    """Test CircuitBreaker class."""
    
    @pytest.fixture
    def breaker(self):
        """Create circuit breaker."""
        return CircuitBreaker(
            name="test",
            failure_threshold=3,
            recovery_timeout=1,
        )
    
    def test_initial_state_closed(self, breaker):
        """Test initial state is closed."""
        assert breaker.state == CircuitState.CLOSED
    
    def test_successful_call_stays_closed(self, breaker):
        """Test successful calls keep breaker closed."""
        func = Mock(return_value="success")
        
        result = breaker.call(func)
        
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    def test_failure_increments_counter(self, breaker):
        """Test failures increment counter."""
        func = Mock(side_effect=Exception("error"))
        
        with pytest.raises(Exception):
            breaker.call(func)
        
        assert breaker.failure_count == 1
    
    def test_opens_after_threshold(self, breaker):
        """Test breaker opens after failure threshold."""
        func = Mock(side_effect=Exception("error"))
        
        # Fail 3 times
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(func)
        
        assert breaker.state == CircuitState.OPEN
    
    def test_rejects_calls_when_open(self, breaker):
        """Test circuit rejects calls when open."""
        func = Mock(side_effect=Exception("error"))
        
        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(func)
        
        # Now open, should reject
        with pytest.raises(CircuitBreakerError):
            breaker.call(Mock())
    
    def test_half_open_after_timeout(self, breaker):
        """Test breaker goes half-open after timeout."""
        func = Mock(side_effect=Exception("error"))
        
        # Open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Next call should attempt (go half-open)
        func.side_effect = None
        func.return_value = "recovered"
        
        result = breaker.call(func)
        assert result == "recovered"
        assert breaker.state == CircuitState.HALF_OPEN
    
    def test_closes_after_success_threshold(self, breaker):
        """Test breaker closes after success threshold in half-open."""
        func = Mock(side_effect=Exception("error"))
        
        # Open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(func)
        
        time.sleep(1.1)
        
        # Succeed twice to close
        func.side_effect = None
        func.return_value = "success"
        
        breaker.call(func)
        breaker.call(func)
        
        assert breaker.state == CircuitState.CLOSED
    
    def test_get_status(self, breaker):
        """Test getting circuit breaker status."""
        status = breaker.get_status()
        
        assert status["name"] == "test"
        assert status["state"] == "closed"
        assert status["failures"] == 0


# ============ Retry Strategy Tests ============

class TestRetryStrategy:
    """Test RetryStrategy class."""
    
    @pytest.fixture
    def strategy(self):
        """Create retry strategy."""
        return RetryStrategy(
            max_retries=3,
            base_delay=0.01,
            max_delay=1.0,
            jitter=False,
        )
    
    def test_immediate_success(self, strategy):
        """Test immediate success."""
        func = Mock(return_value="success")
        
        result = strategy.execute(func)
        
        assert result == "success"
        assert func.call_count == 1
    
    def test_retries_on_transient_error(self, strategy):
        """Test retries on transient error."""
        func = Mock(side_effect=[
            TimeoutError("timeout"),
            TimeoutError("timeout"),
            "success",
        ])
        
        result = strategy.execute(func)
        
        assert result == "success"
        assert func.call_count == 3
    
    def test_gives_up_on_permanent_error(self, strategy):
        """Test stops retrying on permanent error."""
        func = Mock(side_effect=Exception("404 Not Found"))
        
        with pytest.raises(Exception):  # Will raise the permanent error
            strategy.execute(func)
        
        # Should only try once for permanent error (won't retry)
        assert func.call_count == 1
    
    def test_exhausts_retries(self, strategy):
        """Test exhausts retries for transient error."""
        func = Mock(side_effect=TimeoutError("always timeout"))
        
        with pytest.raises(ExhaustedRetriesError):
            strategy.execute(func)
        
        # Should try max_retries + 1 times
        assert func.call_count == 4
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        strategy = RetryStrategy(
            base_delay=1.0,
            multiplier=2.0,
            jitter=False,
        )
        
        # Calculate delays for attempts
        delay1 = strategy._calculate_delay(0)
        delay2 = strategy._calculate_delay(1)
        delay3 = strategy._calculate_delay(2)
        
        assert delay1 == 1.0
        assert delay2 == 2.0
        assert delay3 == 4.0
    
    def test_jitter_adds_variance(self):
        """Test jitter adds randomness to delays."""
        strategy = RetryStrategy(
            base_delay=1.0,
            jitter=True,
        )
        
        # Get multiple delays
        delays = [strategy._calculate_delay(0) for _ in range(10)]
        
        # Should have variance
        assert len(set(delays)) > 1
        # All should be close to base
        assert all(0.5 < d < 1.5 for d in delays)


# ============ Fallback Provider Tests ============

class TestFallbackProvider:
    """Test FallbackProvider class."""
    
    def test_uses_first_provider(self):
        """Test uses first provider if successful."""
        provider1 = Mock(return_value="from1")
        provider2 = Mock(return_value="from2")
        
        fallback = FallbackProvider([provider1, provider2])
        result = fallback.call("arg")
        
        assert result == "from1"
        assert provider1.call_count == 1
        assert provider2.call_count == 0
    
    def test_fallback_to_second(self):
        """Test falls back to second provider."""
        provider1 = Mock(side_effect=Exception("failed"))
        provider2 = Mock(return_value="from2")
        
        fallback = FallbackProvider([provider1, provider2])
        result = fallback.call("arg")
        
        assert result == "from2"
        assert provider1.call_count == 1
        assert provider2.call_count == 1
    
    def test_uses_best_available(self):
        """Test tries all providers until one works."""
        provider1 = Mock(side_effect=Exception("failed"))
        provider2 = Mock(side_effect=Exception("failed"))
        provider3 = Mock(return_value="from3")
        
        fallback = FallbackProvider([provider1, provider2, provider3])
        result = fallback.call("arg")
        
        assert result == "from3"
        assert provider1.call_count == 1
        assert provider2.call_count == 1
        assert provider3.call_count == 1
    
    def test_exhausts_all_providers(self):
        """Test raises when all providers fail."""
        provider1 = Mock(side_effect=Exception("failed1"))
        provider2 = Mock(side_effect=Exception("failed2"))
        
        fallback = FallbackProvider([provider1, provider2])
        
        with pytest.raises(ExhaustedRetriesError):
            fallback.call("arg")
    
    def test_tracks_statistics(self):
        """Test tracks provider statistics."""
        provider1 = Mock(side_effect=Exception("failed"))
        provider2 = Mock(return_value="success")
        
        fallback = FallbackProvider([provider1, provider2])
        
        fallback.call("arg")
        fallback.call("arg")
        
        stats = fallback.get_stats()
        
        assert stats["providers"][0]["fail"] == 2
        assert stats["providers"][1]["success"] == 2


# ============ Error Recovery Orchestrator Tests ============

class TestErrorRecoveryOrchestrator:
    """Test ErrorRecoveryOrchestrator class."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator."""
        return ErrorRecoveryOrchestrator()
    
    def test_create_circuit_breaker(self, orchestrator):
        """Test creating circuit breaker."""
        breaker = orchestrator.create_circuit_breaker("test")
        
        assert isinstance(breaker, CircuitBreaker)
        assert "test" in orchestrator.circuit_breakers
    
    def test_create_retry_strategy(self, orchestrator):
        """Test creating retry strategy."""
        strategy = orchestrator.create_retry_strategy("test")
        
        assert isinstance(strategy, RetryStrategy)
        assert "test" in orchestrator.retry_strategies
    
    def test_create_fallback_provider(self, orchestrator):
        """Test creating fallback provider."""
        providers = [Mock(), Mock()]
        fallback = orchestrator.create_fallback_provider(
            "test",
            providers=providers,
        )
        
        assert isinstance(fallback, FallbackProvider)
        assert "test" in orchestrator.fallback_providers
    
    def test_get_all_stats(self, orchestrator):
        """Test getting all statistics."""
        orchestrator.create_circuit_breaker("breaker1")
        orchestrator.create_fallback_provider("fallback1", [Mock()])
        
        stats = orchestrator.get_all_stats()
        
        assert "circuit_breakers" in stats
        assert "fallback_providers" in stats
        assert "breaker1" in stats["circuit_breakers"]
        assert "fallback1" in stats["fallback_providers"]


# ============ Integration Tests ============

class TestErrorRecoveryIntegration:
    """Integration tests combining recovery mechanisms."""
    
    def test_circuit_breaker_with_retry(self):
        """Test circuit breaker with retry strategy."""
        breaker = CircuitBreaker(
            "test",
            failure_threshold=5,  # Higher threshold so circuit doesn't open
            recovery_timeout=0.5,
        )
        strategy = RetryStrategy(
            max_retries=2,
            base_delay=0.01,
            jitter=False,
        )
        
        # Will fail twice, then succeed
        call_count = [0]
        
        def failing_func():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise TimeoutError("timeout")
            return "success"
        
        # Retry strategy retries through circuit breaker
        result = strategy.execute(lambda: breaker.call(failing_func))
        
        assert result == "success"
    
    def test_graceful_degradation(self):
        """Test graceful degradation with fallback."""
        primary = Mock(side_effect=Exception("unavailable"))
        fallback = Mock(return_value="degraded_result")
        
        provider = FallbackProvider([primary, fallback])
        
        result = provider.call("arg")
        
        # System degraded but still functional
        assert result == "degraded_result"


# ============ Performance Tests ============

class TestErrorRecoveryPerformance:
    """Test performance of recovery mechanisms."""
    
    def test_circuit_breaker_fast_fail(self):
        """Test circuit breaker enables fast-fail."""
        breaker = CircuitBreaker("test", failure_threshold=2)
        slow_func = Mock(side_effect=TimeoutError("slow"))
        
        start = time.time()
        
        # Fail 2 times (opens circuit)
        for _ in range(2):
            with pytest.raises(TimeoutError):
                breaker.call(slow_func)
        
        # Next calls should be instant (no timeout)
        for _ in range(10):
            with pytest.raises(CircuitBreakerError):
                breaker.call(slow_func)
        
        elapsed = time.time() - start
        
        # Should be fast
        assert elapsed < 1.0
