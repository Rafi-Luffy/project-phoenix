"""
Error Detection Framework for Self-Correction Engine

This module provides sophisticated error detection, analysis, and categorization
for the autonomous system. It integrates with the memory system to track,
learn from, and prevent recurring errors.

Based on: Self-Refine framework (Madaan et al.)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib
import json
from abc import ABC, abstractmethod


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = 5      # System-wide failure
    MAJOR = 4         # Significant functionality broken
    MODERATE = 3      # Feature impaired but functional
    MINOR = 2         # Cosmetic or edge case
    INFO = 1          # Non-error, informational


class ErrorType(Enum):
    """Error type classification"""
    LOGIC_ERROR = "logic"           # Incorrect reasoning
    RESOURCE_ERROR = "resource"     # Resource unavailable/exhausted
    VALIDATION_ERROR = "validation" # Input validation failed
    STATE_ERROR = "state"           # Invalid state transition
    TIMEOUT_ERROR = "timeout"       # Operation timeout
    DEPENDENCY_ERROR = "dependency" # External dependency failed
    CONFIGURATION_ERROR = "config"  # Configuration issue
    DATA_ERROR = "data"             # Data integrity/format issue
    PERMISSION_ERROR = "permission" # Access denied
    UNKNOWN_ERROR = "unknown"       # Unclassified


@dataclass
class ErrorSignature:
    """
    Unique signature for an error pattern.
    Used to identify recurring errors and track their frequency.
    """
    error_type: ErrorType
    error_message_hash: str
    stack_trace_hash: str
    context_hash: str
    
    @property
    def signature_hash(self) -> str:
        """Generate composite hash for this signature"""
        combined = f"{self.error_type.value}|{self.error_message_hash}|{self.stack_trace_hash}|{self.context_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @classmethod
    def from_error(cls, error_type: ErrorType, message: str, 
                   stack_trace: str, context: Dict[str, Any]) -> 'ErrorSignature':
        """Create signature from error details"""
        return cls(
            error_type=error_type,
            error_message_hash=hashlib.sha256(message.encode()).hexdigest()[:8],
            stack_trace_hash=hashlib.sha256(stack_trace.encode()).hexdigest()[:8],
            context_hash=hashlib.sha256(json.dumps(context, sort_keys=True, default=str).encode()).hexdigest()[:8]
        )


@dataclass
class ErrorContext:
    """Rich contextual information about an error"""
    agent_id: str
    operation: str
    timestamp: datetime
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    stack_trace: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat(),
            "error_type": self.error_type.value,
            "severity": self.severity.name,
            "message": self.message,
            "stack_trace": self.stack_trace,
            "input_data": self.input_data,
            "state_snapshot": self.state_snapshot,
            "metadata": self.metadata
        }


@dataclass
class ErrorPattern:
    """
    Represents a recurring error pattern.
    Tracks frequency, contexts, and potential causes.
    """
    signature: ErrorSignature
    first_occurrence: datetime
    last_occurrence: datetime
    occurrence_count: int = 1
    contexts: List[ErrorContext] = field(default_factory=list)
    agents_affected: Set[str] = field(default_factory=set)
    success_rate_after_error: float = 0.0
    estimated_impact: str = "unknown"
    
    def add_occurrence(self, context: ErrorContext) -> None:
        """Add a new occurrence of this error pattern"""
        self.occurrence_count += 1
        self.last_occurrence = context.timestamp
        self.contexts.append(context)
        self.agents_affected.add(context.agent_id)
    
    def is_recurring(self, min_occurrences: int = 3, 
                     time_window: timedelta = timedelta(hours=24)) -> bool:
        """Check if this error is recurring within a time window"""
        if self.occurrence_count < min_occurrences:
            return False
        
        recent_count = sum(
            1 for ctx in self.contexts
            if datetime.now() - ctx.timestamp <= time_window
        )
        return recent_count >= min_occurrences
    
    def get_common_factors(self) -> Dict[str, Any]:
        """Extract common factors across occurrences"""
        if not self.contexts:
            return {}
        
        # Analyze common input patterns
        common_inputs = {}
        if self.contexts[0].input_data:
            for key in self.contexts[0].input_data.keys():
                values = [
                    ctx.input_data.get(key) for ctx in self.contexts
                    if key in ctx.input_data
                ]
                if all(v == values[0] for v in values):
                    common_inputs[key] = values[0]
        
        # Analyze common states
        common_states = {}
        if self.contexts[0].state_snapshot:
            for key in self.contexts[0].state_snapshot.keys():
                values = [
                    ctx.state_snapshot.get(key) for ctx in self.contexts
                    if key in ctx.state_snapshot
                ]
                if all(v == values[0] for v in values):
                    common_states[key] = values[0]
        
        return {
            "common_inputs": common_inputs,
            "common_states": common_states,
            "affected_agents": list(self.agents_affected),
            "error_count": self.occurrence_count
        }


@dataclass
class ErrorAnalysis:
    """Analysis result for an error"""
    signature: ErrorSignature
    error_type: ErrorType
    severity: ErrorSeverity
    root_cause_hypothesis: str
    contributing_factors: List[str] = field(default_factory=list)
    similar_errors: List[str] = field(default_factory=list)
    preventive_measures: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "signature": self.signature.signature_hash,
            "error_type": self.error_type.value,
            "severity": self.severity.name,
            "root_cause": self.root_cause_hypothesis,
            "factors": self.contributing_factors,
            "similar": self.similar_errors,
            "prevention": self.preventive_measures,
            "actions": self.recommended_actions,
            "confidence": self.confidence_score
        }


class ErrorDetector(ABC):
    """
    Abstract base class for error detectors.
    Specific detectors implement different detection strategies.
    """
    
    @abstractmethod
    def detect(self, result: Any, context: Dict[str, Any]) -> Optional[ErrorContext]:
        """Detect error in result and context"""
        pass
    
    @abstractmethod
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """Check if this detector applies to the given context"""
        pass


class ExceptionDetector(ErrorDetector):
    """Detects and wraps exceptions"""
    
    def detect(self, result: Any, context: Dict[str, Any]) -> Optional[ErrorContext]:
        """Detect if result is an exception"""
        if not isinstance(result, Exception):
            return None
        
        error_type = self._classify_exception(result)
        severity = self._assess_severity(error_type)
        
        return ErrorContext(
            agent_id=context.get("agent_id", "unknown"),
            operation=context.get("operation", "unknown"),
            timestamp=datetime.now(),
            error_type=error_type,
            severity=severity,
            message=str(result),
            stack_trace=context.get("stack_trace", ""),
            input_data=context.get("input_data", {}),
            state_snapshot=context.get("state_snapshot", {}),
            metadata=context.get("metadata", {})
        )
    
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """Always applicable"""
        return True
    
    @staticmethod
    def _classify_exception(exc: Exception) -> ErrorType:
        """Classify exception type"""
        exc_type = type(exc).__name__
        
        if "Timeout" in exc_type or "Timeout" in str(exc):
            return ErrorType.TIMEOUT_ERROR
        elif "Permission" in exc_type or "Access" in exc_type:
            return ErrorType.PERMISSION_ERROR
        elif "Validation" in exc_type or "ValueError" in exc_type:
            return ErrorType.VALIDATION_ERROR
        elif "State" in exc_type:
            return ErrorType.STATE_ERROR
        elif "Resource" in exc_type or "Memory" in exc_type:
            return ErrorType.RESOURCE_ERROR
        elif "Configuration" in exc_type or "Config" in exc_type:
            return ErrorType.CONFIGURATION_ERROR
        elif "Data" in exc_type:
            return ErrorType.DATA_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    @staticmethod
    def _assess_severity(error_type: ErrorType) -> ErrorSeverity:
        """Assess severity based on error type"""
        severity_map = {
            ErrorType.LOGIC_ERROR: ErrorSeverity.MAJOR,
            ErrorType.RESOURCE_ERROR: ErrorSeverity.CRITICAL,
            ErrorType.VALIDATION_ERROR: ErrorSeverity.MODERATE,
            ErrorType.STATE_ERROR: ErrorSeverity.MAJOR,
            ErrorType.TIMEOUT_ERROR: ErrorSeverity.MAJOR,
            ErrorType.DEPENDENCY_ERROR: ErrorSeverity.MODERATE,
            ErrorType.CONFIGURATION_ERROR: ErrorSeverity.CRITICAL,
            ErrorType.DATA_ERROR: ErrorSeverity.MAJOR,
            ErrorType.PERMISSION_ERROR: ErrorSeverity.CRITICAL,
            ErrorType.UNKNOWN_ERROR: ErrorSeverity.MODERATE
        }
        return severity_map.get(error_type, ErrorSeverity.MODERATE)


class OutcomeDetector(ErrorDetector):
    """Detects errors in operation outcomes"""
    
    def __init__(self, failure_indicators: Optional[Dict[str, Any]] = None):
        """
        Initialize with failure indicators
        
        Args:
            failure_indicators: Dict mapping indicator names to their failure conditions
                e.g., {"confidence": lambda x: x < 0.5, "success": lambda x: not x}
        """
        self.failure_indicators = failure_indicators or {}
    
    def detect(self, result: Any, context: Dict[str, Any]) -> Optional[ErrorContext]:
        """Detect errors based on outcome indicators"""
        if not isinstance(result, dict):
            return None
        
        detected_failures = []
        for indicator, condition in self.failure_indicators.items():
            if indicator in result:
                try:
                    if callable(condition):
                        if condition(result[indicator]):
                            detected_failures.append(indicator)
                    else:
                        if result[indicator] != condition:
                            detected_failures.append(indicator)
                except Exception:
                    pass
        
        if not detected_failures:
            return None
        
        return ErrorContext(
            agent_id=context.get("agent_id", "unknown"),
            operation=context.get("operation", "unknown"),
            timestamp=datetime.now(),
            error_type=ErrorType.LOGIC_ERROR,
            severity=ErrorSeverity.MODERATE,
            message=f"Operation outcome failures: {', '.join(detected_failures)}",
            stack_trace="",
            input_data=context.get("input_data", {}),
            state_snapshot=context.get("state_snapshot", {}) | {"result": result},
            metadata={"failed_indicators": detected_failures}
        )
    
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """Check if outcome detection applies"""
        return bool(self.failure_indicators)


class PerformanceDetector(ErrorDetector):
    """Detects performance-related errors and anomalies"""
    
    def __init__(self, latency_threshold_ms: float = 5000.0,
                 memory_threshold_mb: float = 1000.0):
        """
        Initialize performance thresholds
        
        Args:
            latency_threshold_ms: Max acceptable latency in milliseconds
            memory_threshold_mb: Max acceptable memory usage in MB
        """
        self.latency_threshold_ms = latency_threshold_ms
        self.memory_threshold_mb = memory_threshold_mb
    
    def detect(self, result: Any, context: Dict[str, Any]) -> Optional[ErrorContext]:
        """Detect performance issues"""
        issues = []
        
        # Check latency
        if "latency_ms" in context:
            if context["latency_ms"] > self.latency_threshold_ms:
                issues.append(f"High latency: {context['latency_ms']:.1f}ms")
        
        # Check memory usage
        if "memory_mb" in context:
            if context["memory_mb"] > self.memory_threshold_mb:
                issues.append(f"High memory: {context['memory_mb']:.1f}MB")
        
        if not issues:
            return None
        
        return ErrorContext(
            agent_id=context.get("agent_id", "unknown"),
            operation=context.get("operation", "unknown"),
            timestamp=datetime.now(),
            error_type=ErrorType.RESOURCE_ERROR,
            severity=ErrorSeverity.MINOR,
            message=" | ".join(issues),
            stack_trace="",
            input_data=context.get("input_data", {}),
            state_snapshot=context.get("state_snapshot", {}),
            metadata={"performance_metrics": {
                "latency_ms": context.get("latency_ms"),
                "memory_mb": context.get("memory_mb")
            }}
        )
    
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """Always applicable for performance checks"""
        return True


class ErrorDetectionManager:
    """
    Manages error detection across the system.
    Coordinates multiple detectors and maintains error patterns.
    """
    
    def __init__(self, max_patterns: int = 500, 
                 max_context_per_pattern: int = 20):
        """
        Initialize error detection manager
        
        Args:
            max_patterns: Maximum error patterns to track
            max_context_per_pattern: Max error contexts per pattern
        """
        self.detectors: List[ErrorDetector] = []
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.max_patterns = max_patterns
        self.max_context_per_pattern = max_context_per_pattern
        self.total_errors_detected = 0
        self.total_patterns_found = 0
    
    def add_detector(self, detector: ErrorDetector) -> None:
        """Add error detector"""
        self.detectors.append(detector)
    
    def detect_error(self, result: Any, context: Dict[str, Any]) -> Optional[ErrorContext]:
        """
        Detect error using registered detectors
        
        Args:
            result: Operation result to check
            context: Context information for detection
            
        Returns:
            ErrorContext if error detected, None otherwise
        """
        for detector in self.detectors:
            if detector.is_applicable(context):
                error = detector.detect(result, context)
                if error:
                    self.total_errors_detected += 1
                    self._record_error_pattern(error)
                    return error
        
        return None
    
    def _record_error_pattern(self, error: ErrorContext) -> None:
        """Record error as a pattern"""
        signature = ErrorSignature.from_error(
            error.error_type,
            error.message,
            error.stack_trace,
            error.input_data
        )
        
        sig_hash = signature.signature_hash
        
        if sig_hash in self.error_patterns:
            pattern = self.error_patterns[sig_hash]
            pattern.add_occurrence(error)
            
            # Trim contexts if too many
            if len(pattern.contexts) > self.max_context_per_pattern:
                pattern.contexts = pattern.contexts[-self.max_context_per_pattern:]
        else:
            if len(self.error_patterns) < self.max_patterns:
                self.error_patterns[sig_hash] = ErrorPattern(
                    signature=signature,
                    first_occurrence=error.timestamp,
                    last_occurrence=error.timestamp,
                    contexts=[error],
                    agents_affected={error.agent_id}
                )
                self.total_patterns_found += 1
    
    def get_recurring_errors(self, min_occurrences: int = 3,
                            time_window: timedelta = timedelta(hours=24)) -> List[ErrorPattern]:
        """Get recurring error patterns"""
        recurring = [
            pattern for pattern in self.error_patterns.values()
            if pattern.is_recurring(min_occurrences, time_window)
        ]
        return sorted(recurring, key=lambda p: p.occurrence_count, reverse=True)
    
    def get_critical_errors(self) -> List[ErrorPattern]:
        """Get critical error patterns"""
        critical = [
            pattern for pattern in self.error_patterns.values()
            if pattern.contexts and 
            any(ctx.severity == ErrorSeverity.CRITICAL for ctx in pattern.contexts)
        ]
        return sorted(critical, key=lambda p: p.occurrence_count, reverse=True)
    
    def analyze_error(self, error: ErrorContext) -> ErrorAnalysis:
        """
        Analyze an error and provide detailed analysis
        
        Args:
            error: ErrorContext to analyze
            
        Returns:
            ErrorAnalysis with root cause and recommendations
        """
        signature = ErrorSignature.from_error(
            error.error_type,
            error.message,
            error.stack_trace,
            error.input_data
        )
        
        # Find similar patterns
        similar = [
            sig_hash for sig_hash, pattern in self.error_patterns.items()
            if pattern.error_type == error.error_type and
            sig_hash != signature.signature_hash
        ]
        
        # Determine root cause
        root_cause = self._determine_root_cause(error)
        factors = self._identify_contributing_factors(error)
        prevention = self._suggest_preventive_measures(error)
        actions = self._recommend_actions(error)
        
        return ErrorAnalysis(
            signature=signature,
            error_type=error.error_type,
            severity=error.severity,
            root_cause_hypothesis=root_cause,
            contributing_factors=factors,
            similar_errors=similar[:5],
            preventive_measures=prevention,
            recommended_actions=actions,
            confidence_score=0.75
        )
    
    @staticmethod
    def _determine_root_cause(error: ErrorContext) -> str:
        """Determine likely root cause"""
        if error.error_type == ErrorType.LOGIC_ERROR:
            return "Incorrect logic or reasoning in operation"
        elif error.error_type == ErrorType.RESOURCE_ERROR:
            return "Insufficient resources (memory, CPU, connections)"
        elif error.error_type == ErrorType.VALIDATION_ERROR:
            return "Input validation failed or invalid data format"
        elif error.error_type == ErrorType.STATE_ERROR:
            return "Invalid state transition or precondition not met"
        elif error.error_type == ErrorType.TIMEOUT_ERROR:
            return "Operation timeout - exceeded time limit"
        elif error.error_type == ErrorType.DEPENDENCY_ERROR:
            return "External dependency unavailable or failed"
        elif error.error_type == ErrorType.CONFIGURATION_ERROR:
            return "Configuration error or missing configuration"
        elif error.error_type == ErrorType.DATA_ERROR:
            return "Data integrity issue or format error"
        elif error.error_type == ErrorType.PERMISSION_ERROR:
            return "Insufficient permissions or access denied"
        else:
            return "Unknown cause - requires manual investigation"
    
    @staticmethod
    def _identify_contributing_factors(error: ErrorContext) -> List[str]:
        """Identify contributing factors"""
        factors = []
        
        if error.input_data:
            if any(v is None for v in error.input_data.values()):
                factors.append("Missing or null input values")
            if any(isinstance(v, str) and len(v) == 0 for v in error.input_data.values()):
                factors.append("Empty string inputs")
        
        if error.state_snapshot:
            if any(v is None for v in error.state_snapshot.values()):
                factors.append("Null values in state")
        
        if error.severity == ErrorSeverity.CRITICAL:
            factors.append("High error severity")
        
        return factors
    
    @staticmethod
    def _suggest_preventive_measures(error: ErrorContext) -> List[str]:
        """Suggest preventive measures"""
        measures = []
        
        if error.error_type == ErrorType.VALIDATION_ERROR:
            measures.append("Implement stricter input validation")
            measures.append("Add pre-condition checks")
        elif error.error_type == ErrorType.RESOURCE_ERROR:
            measures.append("Implement resource pooling")
            measures.append("Add resource limits and monitoring")
        elif error.error_type == ErrorType.TIMEOUT_ERROR:
            measures.append("Increase timeout thresholds")
            measures.append("Implement async processing")
        elif error.error_type == ErrorType.STATE_ERROR:
            measures.append("Validate state transitions")
            measures.append("Add state guards")
        
        measures.append("Add comprehensive logging")
        return measures
    
    @staticmethod
    def _recommend_actions(error: ErrorContext) -> List[str]:
        """Recommend corrective actions"""
        actions = []
        
        if error.severity == ErrorSeverity.CRITICAL:
            actions.append("Escalate to human operator immediately")
            actions.append("Implement fallback strategy")
        elif error.severity == ErrorSeverity.MAJOR:
            actions.append("Attempt automatic recovery")
            actions.append("Notify system administrator")
        
        actions.append("Log detailed error information")
        actions.append("Retry operation with modified parameters")
        
        return actions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get error detection statistics"""
        return {
            "total_errors_detected": self.total_errors_detected,
            "total_patterns_found": self.total_patterns_found,
            "active_patterns": len(self.error_patterns),
            "recurring_errors": len(self.get_recurring_errors()),
            "critical_errors": len(self.get_critical_errors()),
            "patterns_at_capacity": len(self.error_patterns) >= self.max_patterns
        }
