"""
Production-Grade Resilience & Error Handling Module
Implements circuit breakers, retries, fallbacks, and graceful degradation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from threading import Lock
from time import sleep


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: int = 60  # Seconds before trying recovery
    success_threshold: int = 2  # Successes to close from half-open
    failure_rate_threshold: float = 0.5  # Failure rate %


class CircuitBreaker:
    """Prevents cascading failures using circuit breaker pattern"""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_check_time = datetime.now()
        self.lock = Lock()
        
    def call(self, func: Callable, *args, **kwargs) -> tuple[bool, Any, Optional[str]]:
        """Execute function with circuit breaker protection
        
        Returns: (success, result, error_message)
        """
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    return False, None, "Circuit breaker is OPEN"
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return True, result, None
            except Exception as e:
                self._on_failure()
                return False, None, str(e)
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                logger.info(f"Circuit breaker {self.name} CLOSED")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name} OPEN after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.recovery_timeout


@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # Seconds
    max_delay: float = 30.0
    backoff_multiplier: float = 2.0
    jitter: bool = True


class RetryHandler:
    """Handles retries with exponential backoff"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.attempt_count = defaultdict(int)
        self.lock = Lock()
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        retryable_exceptions: tuple = (Exception,),
        **kwargs
    ) -> tuple[bool, Any, Optional[str]]:
        """Execute function with retries on failure
        
        Returns: (success, result, error_message)
        """
        func_name = func.__name__
        last_error = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                with self.lock:
                    self.attempt_count[func_name] = 0
                return True, result, None
            except retryable_exceptions as e:
                last_error = str(e)
                
                if attempt < self.config.max_attempts:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt}/{self.config.max_attempts} failed for {func_name}, "
                        f"retrying in {delay:.2f}s: {last_error}"
                    )
                    sleep(delay)
                else:
                    logger.error(
                        f"All {self.config.max_attempts} attempts failed for {func_name}: {last_error}"
                    )
                    with self.lock:
                        self.attempt_count[func_name] = 0
        
        return False, None, last_error
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        delay = self.config.initial_delay * (self.config.backoff_multiplier ** (attempt - 1))
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            import random
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay


@dataclass
class FallbackAction:
    """Represents a fallback action"""
    name: str
    func: Callable
    priority: int = 0  # Higher = executed first
    applicable_errors: List[str] = field(default_factory=list)


class FallbackHandler:
    """Manages fallback strategies when primary action fails"""
    
    def __init__(self):
        self.fallbacks: Dict[str, List[FallbackAction]] = defaultdict(list)
        self.lock = Lock()
    
    def register_fallback(self, primary_action: str, fallback: FallbackAction):
        """Register a fallback for a primary action"""
        with self.lock:
            self.fallbacks[primary_action].append(fallback)
            # Sort by priority (descending)
            self.fallbacks[primary_action].sort(key=lambda x: x.priority, reverse=True)
    
    def execute_with_fallback(
        self,
        primary_action: str,
        primary_func: Callable,
        *args,
        **kwargs
    ) -> tuple[bool, Any, str]:
        """Execute primary action with fallbacks
        
        Returns: (success, result, action_used)
        """
        # Try primary action
        try:
            result = primary_func(*args, **kwargs)
            return True, result, primary_action
        except Exception as e:
            error_str = str(e)
            logger.warning(f"Primary action {primary_action} failed: {error_str}")
        
        # Try fallbacks
        with self.lock:
            applicable_fallbacks = self.fallbacks.get(primary_action, [])
        
        for fallback in applicable_fallbacks:
            if fallback.applicable_errors and not any(
                err in error_str for err in fallback.applicable_errors
            ):
                continue
            
            try:
                logger.info(f"Attempting fallback: {fallback.name}")
                result = fallback.func(*args, **kwargs)
                return True, result, fallback.name
            except Exception as e:
                logger.error(f"Fallback {fallback.name} failed: {str(e)}")
                continue
        
        return False, None, "All actions failed"


class RateLimiter:
    """Prevents system overload with rate limiting"""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        with self.lock:
            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            
            # Check limit
            if len(self.requests[identifier]) >= self.max_requests:
                return False
            
            # Record request
            self.requests[identifier].append(now)
            return True
    
    def get_available_requests(self, identifier: str) -> int:
        """Get number of available requests in current window"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        with self.lock:
            valid_requests = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            return max(0, self.max_requests - len(valid_requests))


class BulkheadPattern:
    """Isolates components to prevent total system failure"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.active_count = 0
        self.lock = Lock()
    
    def execute(self, func: Callable, *args, **kwargs) -> tuple[bool, Any, Optional[str]]:
        """Execute with bulkhead isolation"""
        with self.lock:
            if self.active_count >= self.max_concurrent:
                return False, None, "Bulkhead limit reached"
            self.active_count += 1
        
        try:
            result = func(*args, **kwargs)
            return True, result, None
        except Exception as e:
            return False, None, str(e)
        finally:
            with self.lock:
                self.active_count -= 1
    
    def get_utilization(self) -> float:
        """Get current utilization percentage"""
        with self.lock:
            return self.active_count / self.max_concurrent


class TimeoutHandler:
    """Manages execution timeouts"""
    
    def __init__(self, default_timeout: float = 30.0):
        self.default_timeout = default_timeout
    
    def execute_with_timeout(
        self,
        func: Callable,
        timeout: Optional[float] = None,
        *args,
        **kwargs
    ) -> tuple[bool, Any, Optional[str]]:
        """Execute function with timeout
        
        Note: This is a simple implementation. For true timeout,
        use signal module or multiprocessing on Unix systems.
        """
        timeout = timeout or self.default_timeout
        
        try:
            # Start time
            import time
            start = time.time()
            
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            if elapsed > timeout:
                logger.warning(f"Function {func.__name__} exceeded timeout: {elapsed:.2f}s > {timeout}s")
                return False, None, "Function execution exceeded timeout"
            
            return True, result, None
        except Exception as e:
            return False, None, str(e)


class GracefulDegradation:
    """Manages graceful degradation when components fail"""
    
    def __init__(self):
        self.component_status: Dict[str, bool] = {}
        self.fallback_modes: Dict[str, Callable] = {}
        self.lock = Lock()
    
    def register_component(self, name: str, fallback_func: Optional[Callable] = None):
        """Register a component with optional fallback"""
        with self.lock:
            self.component_status[name] = True
            if fallback_func:
                self.fallback_modes[name] = fallback_func
    
    def mark_component_failed(self, name: str):
        """Mark component as failed"""
        with self.lock:
            self.component_status[name] = False
            logger.warning(f"Component {name} marked as FAILED")
    
    def mark_component_recovered(self, name: str):
        """Mark component as recovered"""
        with self.lock:
            self.component_status[name] = True
            logger.info(f"Component {name} marked as RECOVERED")
    
    def is_component_healthy(self, name: str) -> bool:
        """Check if component is healthy"""
        with self.lock:
            return self.component_status.get(name, True)
    
    def get_system_health(self) -> dict:
        """Get overall system health"""
        with self.lock:
            total = len(self.component_status)
            healthy = sum(1 for status in self.component_status.values() if status)
            degraded = total - healthy
            
            return {
                "total_components": total,
                "healthy_components": healthy,
                "degraded_components": degraded,
                "health_percentage": (healthy / total * 100) if total > 0 else 100,
                "is_degraded": degraded > 0,
            }


class ResilienceManager:
    """Centralized resilience management"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
        self.fallback_handlers: Dict[str, FallbackHandler] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.bulkheads: Dict[str, BulkheadPattern] = {}
        self.graceful_degradation = GracefulDegradation()
        self.lock = Lock()
    
    def get_or_create_circuit_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker"""
        with self.lock:
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(name, config)
            return self.circuit_breakers[name]
    
    def get_or_create_retry_handler(
        self,
        name: str,
        config: Optional[RetryConfig] = None
    ) -> RetryHandler:
        """Get or create retry handler"""
        with self.lock:
            if name not in self.retry_handlers:
                self.retry_handlers[name] = RetryHandler(config)
            return self.retry_handlers[name]
    
    def get_or_create_fallback_handler(self, name: str) -> FallbackHandler:
        """Get or create fallback handler"""
        with self.lock:
            if name not in self.fallback_handlers:
                self.fallback_handlers[name] = FallbackHandler()
            return self.fallback_handlers[name]
    
    def get_or_create_rate_limiter(
        self,
        name: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> RateLimiter:
        """Get or create rate limiter"""
        with self.lock:
            if name not in self.rate_limiters:
                self.rate_limiters[name] = RateLimiter(max_requests, window_seconds)
            return self.rate_limiters[name]
    
    def get_or_create_bulkhead(self, name: str, max_concurrent: int = 10) -> BulkheadPattern:
        """Get or create bulkhead"""
        with self.lock:
            if name not in self.bulkheads:
                self.bulkheads[name] = BulkheadPattern(max_concurrent)
            return self.bulkheads[name]
    
    def get_health_report(self) -> dict:
        """Get comprehensive health report"""
        return {
            "graceful_degradation": self.graceful_degradation.get_system_health(),
            "circuit_breakers": {
                name: cb.state.value for name, cb in self.circuit_breakers.items()
            },
            "bulkheads": {
                name: f"{bh.get_utilization():.1%}" for name, bh in self.bulkheads.items()
            },
        }
