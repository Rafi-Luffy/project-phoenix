"""
Correction Strategy Engine for Self-Correction

This module provides strategies for automatically correcting detected errors.
It maintains a repository of correction strategies and selects appropriate ones
based on error analysis.

Based on: Self-Refine framework (Madaan et al.)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from abc import ABC, abstractmethod
import json

from .error_detection import (
    ErrorContext, ErrorPattern, ErrorAnalysis, ErrorType, ErrorSeverity
)


class CorrectionStrategy(Enum):
    """Available correction strategies"""
    RETRY = "retry"                           # Retry the operation
    FALLBACK = "fallback"                     # Use fallback implementation
    ROLLBACK = "rollback"                     # Rollback to previous state
    SKIP = "skip"                             # Skip this operation
    QUARANTINE = "quarantine"                 # Isolate problematic component
    ESCALATE = "escalate"                     # Escalate to human operator
    MODIFY_PARAMETERS = "modify_parameters"   # Modify operation parameters
    CACHE = "cache"                           # Use cached result
    PARALLEL = "parallel"                     # Try in parallel/distributed way
    ANALYZE = "analyze"                       # Deep analysis without fix


@dataclass
class StrategyConfig:
    """Configuration for a correction strategy"""
    strategy: CorrectionStrategy
    max_attempts: int = 3
    backoff_multiplier: float = 1.5
    parameters: Dict[str, Any] = field(default_factory=dict)
    preconditions: List[Callable[[ErrorContext], bool]] = field(default_factory=list)
    postconditions: List[Callable[[Any], bool]] = field(default_factory=list)
    enabled: bool = True


@dataclass
class CorrectionResult:
    """Result of a correction attempt"""
    strategy: CorrectionStrategy
    success: bool
    original_error: ErrorContext
    corrected_output: Optional[Any] = None
    new_error: Optional[ErrorContext] = None
    attempts: int = 1
    total_time_ms: float = 0.0
    messages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy": self.strategy.value,
            "success": self.success,
            "corrected_output": self.corrected_output,
            "attempts": self.attempts,
            "time_ms": self.total_time_ms,
            "messages": self.messages,
            "metadata": self.metadata
        }


class Corrector(ABC):
    """Abstract base class for error correctors"""
    
    @abstractmethod
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Check if this corrector can handle the error"""
        pass
    
    @abstractmethod
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Attempt to correct the error"""
        pass
    
    @abstractmethod
    def get_strategy(self) -> CorrectionStrategy:
        """Get the strategy this corrector implements"""
        pass


class RetryCorrector(Corrector):
    """Corrector that retries the operation"""
    
    def __init__(self, max_retries: int = 3, backoff_multiplier: float = 1.5):
        """
        Initialize retry corrector
        
        Args:
            max_retries: Maximum number of retries
            backoff_multiplier: Multiplier for exponential backoff
        """
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier
    
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Can retry transient errors"""
        transient_types = {
            ErrorType.TIMEOUT_ERROR,
            ErrorType.RESOURCE_ERROR,
            ErrorType.DEPENDENCY_ERROR
        }
        return error.error_type in transient_types
    
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Attempt correction through retry"""
        result = CorrectionResult(
            strategy=self.get_strategy(),
            success=False,
            original_error=error
        )
        
        # Get retry function from context
        retry_fn = context.get("retry_fn")
        if not retry_fn:
            result.messages.append("No retry function provided")
            return result
        
        # Retry with backoff
        wait_time = 0.1
        for attempt in range(1, self.max_retries + 1):
            result.attempts = attempt
            result.messages.append(f"Retry attempt {attempt}/{self.max_retries}")
            
            try:
                corrected = retry_fn(**context.get("retry_args", {}))
                result.success = True
                result.corrected_output = corrected
                result.messages.append(f"Succeeded on attempt {attempt}")
                break
            except Exception as e:
                result.new_error = ErrorContext(
                    agent_id=error.agent_id,
                    operation=error.operation,
                    timestamp=datetime.now(),
                    error_type=error.error_type,
                    severity=error.severity,
                    message=str(e),
                    stack_trace=""
                )
                
                if attempt < self.max_retries:
                    result.messages.append(f"Attempt {attempt} failed, will retry after {wait_time:.2f}s")
                    wait_time *= self.backoff_multiplier
                else:
                    result.messages.append(f"All {self.max_retries} attempts failed")
        
        return result
    
    def get_strategy(self) -> CorrectionStrategy:
        """Return retry strategy"""
        return CorrectionStrategy.RETRY


class FallbackCorrector(Corrector):
    """Corrector that uses fallback implementation"""
    
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Can use fallback for most errors"""
        return error.severity.value <= ErrorSeverity.MAJOR.value
    
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Use fallback implementation"""
        result = CorrectionResult(
            strategy=self.get_strategy(),
            success=False,
            original_error=error
        )
        
        fallback_fn = context.get("fallback_fn")
        if not fallback_fn:
            result.messages.append("No fallback function provided")
            return result
        
        try:
            output = fallback_fn(**context.get("fallback_args", {}))
            result.success = True
            result.corrected_output = output
            result.messages.append("Fallback implementation succeeded")
        except Exception as e:
            result.new_error = ErrorContext(
                agent_id=error.agent_id,
                operation=error.operation,
                timestamp=datetime.now(),
                error_type=ErrorType.LOGIC_ERROR,
                severity=error.severity,
                message=f"Fallback also failed: {str(e)}",
                stack_trace=""
            )
            result.messages.append(f"Fallback failed: {str(e)}")
        
        return result
    
    def get_strategy(self) -> CorrectionStrategy:
        """Return fallback strategy"""
        return CorrectionStrategy.FALLBACK


class RollbackCorrector(Corrector):
    """Corrector that rolls back to previous state"""
    
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Can rollback state errors"""
        return error.error_type == ErrorType.STATE_ERROR
    
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Rollback to previous state"""
        result = CorrectionResult(
            strategy=self.get_strategy(),
            success=False,
            original_error=error
        )
        
        rollback_fn = context.get("rollback_fn")
        if not rollback_fn:
            result.messages.append("No rollback function provided")
            return result
        
        try:
            rollback_fn()
            result.success = True
            result.messages.append("Rollback completed successfully")
            result.corrected_output = {"status": "rolled_back"}
        except Exception as e:
            result.new_error = ErrorContext(
                agent_id=error.agent_id,
                operation=error.operation,
                timestamp=datetime.now(),
                error_type=ErrorType.LOGIC_ERROR,
                severity=ErrorSeverity.CRITICAL,
                message=f"Rollback failed: {str(e)}",
                stack_trace=""
            )
            result.messages.append(f"Rollback failed: {str(e)}")
        
        return result
    
    def get_strategy(self) -> CorrectionStrategy:
        """Return rollback strategy"""
        return CorrectionStrategy.ROLLBACK


class SkipCorrector(Corrector):
    """Corrector that skips the problematic operation"""
    
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Can skip non-critical operations"""
        return error.severity in {ErrorSeverity.INFO, ErrorSeverity.MINOR}
    
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Skip the operation"""
        result = CorrectionResult(
            strategy=self.get_strategy(),
            success=True,
            original_error=error
        )
        result.corrected_output = context.get("skip_value", None)
        result.messages.append("Operation skipped safely")
        return result
    
    def get_strategy(self) -> CorrectionStrategy:
        """Return skip strategy"""
        return CorrectionStrategy.SKIP


class ModifyParametersCorrector(Corrector):
    """Corrector that modifies operation parameters"""
    
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Can modify parameters for validation errors"""
        return error.error_type in {
            ErrorType.VALIDATION_ERROR,
            ErrorType.LOGIC_ERROR
        }
    
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Modify parameters and retry"""
        result = CorrectionResult(
            strategy=self.get_strategy(),
            success=False,
            original_error=error
        )
        
        modifier_fn = context.get("modifier_fn")
        retry_fn = context.get("retry_fn")
        
        if not modifier_fn or not retry_fn:
            result.messages.append("Modifier or retry function not provided")
            return result
        
        try:
            # Get modified parameters
            modified_args = modifier_fn(
                error,
                context.get("retry_args", {})
            )
            result.messages.append(f"Parameters modified: {list(modified_args.keys())}")
            
            # Retry with modified parameters
            output = retry_fn(**modified_args)
            result.success = True
            result.corrected_output = output
            result.messages.append("Succeeded with modified parameters")
        except Exception as e:
            result.new_error = ErrorContext(
                agent_id=error.agent_id,
                operation=error.operation,
                timestamp=datetime.now(),
                error_type=error.error_type,
                severity=error.severity,
                message=f"Correction failed: {str(e)}",
                stack_trace=""
            )
            result.messages.append(f"Correction failed: {str(e)}")
        
        return result
    
    def get_strategy(self) -> CorrectionStrategy:
        """Return modify parameters strategy"""
        return CorrectionStrategy.MODIFY_PARAMETERS


class CacheCorrector(Corrector):
    """Corrector that uses cached results"""
    
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Can use cache for retrieval operations"""
        return error.error_type == ErrorType.DEPENDENCY_ERROR
    
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Use cached result"""
        result = CorrectionResult(
            strategy=self.get_strategy(),
            success=False,
            original_error=error
        )
        
        cached_result = context.get("cached_result")
        if cached_result is None:
            result.messages.append("No cached result available")
            return result
        
        result.success = True
        result.corrected_output = cached_result
        result.messages.append("Using cached result")
        return result
    
    def get_strategy(self) -> CorrectionStrategy:
        """Return cache strategy"""
        return CorrectionStrategy.CACHE


class EscalateCorrector(Corrector):
    """Corrector that escalates to human operator"""
    
    def can_correct(self, error: ErrorContext, analysis: ErrorAnalysis) -> bool:
        """Can escalate critical errors"""
        return error.severity == ErrorSeverity.CRITICAL
    
    def correct(self, error: ErrorContext, context: Dict[str, Any]) -> CorrectionResult:
        """Escalate to human"""
        result = CorrectionResult(
            strategy=self.get_strategy(),
            success=True,
            original_error=error
        )
        
        escalate_fn = context.get("escalate_fn")
        if escalate_fn:
            escalate_fn(error)
        
        result.corrected_output = {"status": "escalated", "requires_human": True}
        result.messages.append("Error escalated to human operator")
        return result
    
    def get_strategy(self) -> CorrectionStrategy:
        """Return escalate strategy"""
        return CorrectionStrategy.ESCALATE


class CorrectionStrategyEngine:
    """
    Engine for selecting and executing correction strategies.
    Maintains a registry of correctors and chooses appropriate ones.
    """
    
    def __init__(self):
        """Initialize correction strategy engine"""
        self.correctors: Dict[CorrectionStrategy, Corrector] = {}
        self.correction_history: List[CorrectionResult] = []
        self.strategy_success_rates: Dict[CorrectionStrategy, Tuple[int, int]] = {}
        self.max_history = 1000
        
        # Register default correctors
        self._register_default_correctors()
    
    def _register_default_correctors(self) -> None:
        """Register default correctors"""
        self.register_corrector(RetryCorrector())
        self.register_corrector(FallbackCorrector())
        self.register_corrector(RollbackCorrector())
        self.register_corrector(SkipCorrector())
        self.register_corrector(ModifyParametersCorrector())
        self.register_corrector(CacheCorrector())
        self.register_corrector(EscalateCorrector())
    
    def register_corrector(self, corrector: Corrector) -> None:
        """Register a corrector"""
        self.correctors[corrector.get_strategy()] = corrector
        self.strategy_success_rates[corrector.get_strategy()] = (0, 0)
    
    def select_correction_strategies(self, error: ErrorContext, 
                                    analysis: ErrorAnalysis) -> List[Corrector]:
        """
        Select correction strategies for an error
        
        Args:
            error: ErrorContext to correct
            analysis: ErrorAnalysis result
            
        Returns:
            List of applicable correctors, ordered by effectiveness
        """
        applicable = [
            corrector for corrector in self.correctors.values()
            if corrector.can_correct(error, analysis)
        ]
        
        # Sort by success rate
        def get_success_rate(corrector: Corrector) -> float:
            strategy = corrector.get_strategy()
            successes, total = self.strategy_success_rates.get(strategy, (0, 0))
            if total == 0:
                return 0.5  # Default score
            return successes / total
        
        applicable.sort(key=get_success_rate, reverse=True)
        return applicable
    
    def attempt_correction(self, error: ErrorContext, analysis: ErrorAnalysis,
                          context: Dict[str, Any]) -> Optional[CorrectionResult]:
        """
        Attempt to correct an error using appropriate strategies
        
        Args:
            error: ErrorContext to correct
            analysis: ErrorAnalysis result
            context: Additional context (retry_fn, fallback_fn, etc.)
            
        Returns:
            CorrectionResult if correction attempted, None if no applicable strategy
        """
        strategies = self.select_correction_strategies(error, analysis)
        
        if not strategies:
            return None
        
        # Try strategies in order
        for corrector in strategies:
            try:
                result = corrector.correct(error, context)
                self._record_correction_result(result)
                
                if result.success:
                    return result
            except Exception as e:
                # Log but continue to next strategy
                pass
        
        return None
    
    def _record_correction_result(self, result: CorrectionResult) -> None:
        """Record correction result for learning"""
        self.correction_history.append(result)
        
        # Trim history if too large
        if len(self.correction_history) > self.max_history:
            self.correction_history = self.correction_history[-self.max_history:]
        
        # Update success rate
        strategy = result.strategy
        successes, total = self.strategy_success_rates.get(strategy, (0, 0))
        if result.success:
            successes += 1
        total += 1
        self.strategy_success_rates[strategy] = (successes, total)
    
    def get_strategy_effectiveness(self) -> Dict[str, Dict[str, float]]:
        """Get effectiveness metrics for all strategies"""
        effectiveness = {}
        for strategy, (successes, total) in self.strategy_success_rates.items():
            effectiveness[strategy.value] = {
                "success_rate": successes / total if total > 0 else 0.0,
                "attempts": total,
                "successes": successes
            }
        return effectiveness
    
    def adapt_strategies(self, error_pattern: ErrorPattern) -> None:
        """
        Adapt correction strategies based on error patterns
        
        Args:
            error_pattern: ErrorPattern to learn from
        """
        # Could implement learning logic here to adjust strategy selection
        # based on recurring errors
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get correction engine statistics"""
        total_attempts = sum(total for _, total in self.strategy_success_rates.values())
        total_successes = sum(succ for succ, _ in self.strategy_success_rates.values())
        
        return {
            "total_corrections_attempted": total_attempts,
            "total_corrections_successful": total_successes,
            "overall_success_rate": total_successes / total_attempts if total_attempts > 0 else 0.0,
            "strategies_registered": len(self.correctors),
            "strategy_effectiveness": self.get_strategy_effectiveness(),
            "correction_history_size": len(self.correction_history)
        }
