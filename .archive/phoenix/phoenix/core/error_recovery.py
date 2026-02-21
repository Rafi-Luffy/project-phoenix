"""
Error Recovery & Resilience Patterns

Implements circuit breaker, retry strategies, fallback mechanisms,
and graceful degradation for autonomous healing system.
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Callable, Any, List, Dict
from enum import Enum
import random

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class ErrorCategory(str, Enum):
    """Error categorization for retry decisions."""
    TRANSIENT = "transient"  # Temporary, worth retrying
    PERMANENT = "permanent"  # Won't resolve with retry
    UNKNOWN = "unknown"  # Unclear, treat as transient


class CircuitState(str, Enum):
    """States of circuit breaker."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class ErrorRecoveryError(Exception):
    """Base error for recovery system."""
    pass


class CircuitBreakerError(ErrorRecoveryError):
    """Raised when circuit breaker is open."""
    pass


class ExhaustedRetriesError(ErrorRecoveryError):
    """Raised when all retries exhausted."""
    pass


def categorize_error(error: Exception) -> ErrorCategory:
    """
    Categorize error to determine if retry is worthwhile.
    
    Args:
        error: Exception to categorize
        
    Returns:
        ErrorCategory classification
    """
    error_msg = str(error).lower()
    
    # Transient errors - worth retrying
    transient_indicators = [
        "timeout",
        "connection",
        "temporarily",
        "unavailable",
        "try again",
        "rate limit",
        "429",
        "503",
        "502",
    ]
    
    # Permanent errors - don't retry
    permanent_indicators = [
        "unauthorized",
        "forbidden",
        "not found",
        "invalid",
        "401",
        "403",
        "404",
        "bad request",
        "400",
    ]
    
    for indicator in transient_indicators:
        if indicator in error_msg:
            return ErrorCategory.TRANSIENT
    
    for indicator in permanent_indicators:
        if indicator in error_msg:
            return ErrorCategory.PERMANENT
    
    return ErrorCategory.UNKNOWN


class CircuitBreaker:
    """
    Circuit breaker pattern for LLM provider failures.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject requests
    - HALF_OPEN: Testing if service recovered
    
    Flow:
    1. Request succeeds -> CLOSED
    2. Requests fail threshold -> OPEN (fast-fail)
    3. Wait timeout -> HALF_OPEN (test recovery)
    4. Test succeeds -> CLOSED
    5. Test fails -> OPEN again
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Service name for logging
            failure_threshold: Failures before opening
            recovery_timeout: Seconds before half-open test
            success_threshold: Successes in half-open to close
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.logger = get_logger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.logger.info(f"circuit_breaker_{self.name}_half_open")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is open"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure(e)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time passed to test recovery."""
        if not self.last_failure_time:
            return True
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful request."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.logger.info(f"circuit_breaker_{self.name}_closed")
        
        elif self.state == CircuitState.CLOSED:
            # Normal success, keep counting
            pass
    
    def _on_failure(self, error: Exception):
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failure during recovery test
            self.state = CircuitState.OPEN
            self.success_count = 0
            self.logger.warning(
                f"circuit_breaker_{self.name}_reopened_on_test",
                error=str(error),
            )
        
        elif self.state == CircuitState.CLOSED:
            # Failure in normal operation
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.logger.warning(
                    f"circuit_breaker_{self.name}_opened",
                    failure_count=self.failure_count,
                    error=str(error),
                )
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        last_failure_iso = None
        if self.last_failure_time:
            import datetime
            last_failure_iso = datetime.datetime.fromtimestamp(
                self.last_failure_time
            ).isoformat()
        
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self.failure_count,
            "successes": self.success_count,
            "last_failure": last_failure_iso,
        }


class RetryStrategy:
    """
    Intelligent retry strategy with jitter and backoff.
    
    Strategies:
    - Exponential backoff: delay = base * (multiplier ^ attempt)
    - With jitter: Prevents thundering herd
    - Adaptive: Adjust based on error category
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        jitter: bool = True,
    ):
        """
        Initialize retry strategy.
        
        Args:
            max_retries: Maximum retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay cap
            multiplier: Backoff multiplier
            jitter: Add random jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter
        self.logger = get_logger(__name__)
    
    def execute(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with retries.
        
        Args:
            func: Function to retry
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            ExhaustedRetriesError: All retries failed
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                last_error = e
                
                # Determine if worth retrying
                category = categorize_error(e)
                
                if attempt == self.max_retries:
                    # Last attempt failed
                    self.logger.error(
                        "retry_exhausted",
                        attempts=attempt + 1,
                        category=category.value,
                        error=str(e),
                    )
                    raise ExhaustedRetriesError(
                        f"Failed after {attempt + 1} attempts: {str(e)}"
                    ) from e
                
                if category == ErrorCategory.PERMANENT:
                    # Don't retry permanent errors
                    self.logger.warning(
                        "retry_skipped_permanent_error",
                        error=str(e),
                    )
                    raise
                
                # Calculate backoff delay
                delay = self._calculate_delay(attempt)
                
                self.logger.warning(
                    "retry_attempt",
                    attempt=attempt + 1,
                    delay_seconds=delay,
                    category=category.value,
                    error=str(e),
                )
                
                time.sleep(delay)
        
        raise ExhaustedRetriesError(
            f"All {self.max_retries} retries failed"
        ) from last_error
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for attempt with backoff."""
        delay = self.base_delay * (self.multiplier ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter (±20%)
            jitter_amount = delay * 0.2
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(delay, self.base_delay * 0.5)  # Don't go too low
        
        return delay


class FallbackProvider:
    """
    Fallback mechanism when primary fails.
    
    Chains multiple providers, tries each until one succeeds.
    """
    
    def __init__(self, providers: List[Callable], name: str = "fallback"):
        """
        Initialize fallback provider.
        
        Args:
            providers: List of provider functions (in order of preference)
            name: Name for logging
        """
        self.providers = providers
        self.name = name
        self.logger = get_logger(__name__)
        self.provider_stats = {i: {"success": 0, "fail": 0} for i in range(len(providers))}
    
    def call(self, *args, **kwargs) -> Any:
        """
        Try each provider until one succeeds.
        
        Args:
            *args: Arguments for providers
            **kwargs: Keyword arguments for providers
            
        Returns:
            Result from first successful provider
            
        Raises:
            ExhaustedRetriesError: All providers failed
        """
        last_error = None
        
        for i, provider in enumerate(self.providers):
            try:
                result = provider(*args, **kwargs)
                self.provider_stats[i]["success"] += 1
                self.logger.info(
                    f"fallback_provider_success",
                    provider_index=i,
                    provider_name=getattr(provider, "__name__", f"provider_{i}"),
                )
                return result
            
            except Exception as e:
                self.provider_stats[i]["fail"] += 1
                last_error = e
                
                self.logger.warning(
                    f"fallback_provider_failed",
                    provider_index=i,
                    provider_name=getattr(provider, "__name__", f"provider_{i}"),
                    error=str(e),
                    trying_next=i < len(self.providers) - 1,
                )
        
        # All providers failed
        self.logger.error(
            "fallback_all_providers_failed",
            count=len(self.providers),
        )
        raise ExhaustedRetriesError(
            f"All {len(self.providers)} fallback providers failed"
        ) from last_error
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics."""
        return {
            "name": self.name,
            "providers": self.provider_stats,
            "total_attempts": sum(
                s["success"] + s["fail"]
                for s in self.provider_stats.values()
            ),
        }


class ErrorRecoveryOrchestrator:
    """
    Orchestrates error recovery and resilience.
    
    Combines:
    - Circuit breakers for fast-fail
    - Retry strategies with jitter
    - Fallback providers
    - Graceful degradation
    """
    
    def __init__(self):
        """Initialize error recovery orchestrator."""
        self.circuit_breakers = {}
        self.retry_strategies = {}
        self.fallback_providers = {}
        self.logger = get_logger(__name__)
    
    def create_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Create new circuit breaker."""
        breaker = CircuitBreaker(name, **kwargs)
        self.circuit_breakers[name] = breaker
        self.logger.info(f"circuit_breaker_created", name=name)
        return breaker
    
    def create_retry_strategy(self, name: str, **kwargs) -> RetryStrategy:
        """Create new retry strategy."""
        strategy = RetryStrategy(**kwargs)
        self.retry_strategies[name] = strategy
        self.logger.info(f"retry_strategy_created", name=name)
        return strategy
    
    def create_fallback_provider(
        self,
        name: str,
        providers: List[Callable],
    ) -> FallbackProvider:
        """Create new fallback provider."""
        fallback = FallbackProvider(providers, name)
        self.fallback_providers[name] = fallback
        self.logger.info(f"fallback_provider_created", name=name)
        return fallback
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all recovery mechanisms."""
        return {
            "circuit_breakers": {
                name: breaker.get_status()
                for name, breaker in self.circuit_breakers.items()
            },
            "fallback_providers": {
                name: provider.get_stats()
                for name, provider in self.fallback_providers.items()
            },
        }
