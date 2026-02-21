"""
Adaptive Improvement System for Self-Correction

This module provides mechanisms for learning from errors and improvements,
adapting correction strategies based on outcomes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import json

from .error_detection import ErrorContext, ErrorPattern, ErrorAnalysis, ErrorType
from .correction_strategy import CorrectionResult, CorrectionStrategy


class ImprovementLevel(Enum):
    """Levels of improvement"""
    CRITICAL = 5    # System-wide improvement needed
    SIGNIFICANT = 4 # Major improvement opportunity
    MODERATE = 3    # Notable improvement possible
    MINOR = 2       # Small improvement opportunity
    NONE = 1        # No improvement needed


@dataclass
class ImprovementSuggestion:
    """Suggestion for system improvement"""
    level: ImprovementLevel
    category: str  # e.g., "validation", "performance", "resilience"
    description: str
    implementation_effort: str  # "low", "medium", "high"
    expected_benefit: str
    priority: int  # 1-10
    target_component: str
    implementation_steps: List[str] = field(default_factory=list)
    estimated_impact: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyAdaptation:
    """Record of strategy adaptation based on outcomes"""
    strategy: CorrectionStrategy
    original_success_rate: float
    new_success_rate: float
    error_pattern: str
    adaptation_reason: str
    changes_made: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LearningMetric:
    """Learning metrics for the system"""
    metric_name: str
    current_value: float
    previous_value: float
    target_value: float
    trend: str  # "improving", "degrading", "stable"
    time_period: str  # "1h", "24h", "7d", "30d"
    last_updated: datetime = field(default_factory=datetime.now)


class AdaptiveImprovementSystem:
    """
    System for continuous learning and adaptation.
    Analyzes error patterns and correction outcomes to suggest and implement improvements.
    """
    
    def __init__(self, memory_manager: Optional[Any] = None):
        """
        Initialize adaptive improvement system
        
        Args:
            memory_manager: Reference to memory manager for storing insights
        """
        self.memory_manager = memory_manager
        self.improvement_suggestions: List[ImprovementSuggestion] = []
        self.strategy_adaptations: List[StrategyAdaptation] = []
        self.learning_metrics: Dict[str, LearningMetric] = {}
        self.implemented_improvements: List[Dict[str, Any]] = []
        self.error_prevention_rules: List[Dict[str, Any]] = []
        self.max_suggestions = 100
    
    def analyze_correction_outcome(self, correction: CorrectionResult,
                                  error: ErrorContext,
                                  analysis: ErrorAnalysis) -> ImprovementSuggestion:
        """
        Analyze a correction outcome and suggest improvements
        
        Args:
            correction: CorrectionResult from correction engine
            error: Original ErrorContext
            analysis: ErrorAnalysis
            
        Returns:
            ImprovementSuggestion
        """
        suggestion = None
        
        if correction.success:
            # Learn from successful correction
            suggestion = self._learn_from_success(correction, error, analysis)
        else:
            # Learn from failed correction
            suggestion = self._learn_from_failure(correction, error, analysis)
        
        if suggestion and len(self.improvement_suggestions) < self.max_suggestions:
            self.improvement_suggestions.append(suggestion)
            # Store in memory if available
            if self.memory_manager:
                self._store_improvement_in_memory(suggestion)
        
        return suggestion
    
    def _learn_from_success(self, correction: CorrectionResult,
                           error: ErrorContext,
                           analysis: ErrorAnalysis) -> ImprovementSuggestion:
        """Learn from successful correction"""
        
        # Suggest preventive measure based on successful correction
        if correction.strategy == CorrectionStrategy.RETRY:
            description = (f"Implement automatic retry with exponential backoff "
                          f"for {error.error_type.value} errors")
            level = ImprovementLevel.MODERATE
        elif correction.strategy == CorrectionStrategy.FALLBACK:
            description = (f"Design fallback implementations for "
                          f"{error.operation} operation")
            level = ImprovementLevel.SIGNIFICANT
        elif correction.strategy == CorrectionStrategy.MODIFY_PARAMETERS:
            description = (f"Add parameter validation and transformation for "
                          f"{error.operation} to prevent {error.error_type.value}")
            level = ImprovementLevel.MODERATE
        else:
            description = f"Document successful {correction.strategy.value} strategy"
            level = ImprovementLevel.MINOR
        
        return ImprovementSuggestion(
            level=level,
            category="preventive",
            description=description,
            implementation_effort="medium" if level.value > 2 else "low",
            expected_benefit=f"Reduce {error.error_type.value} errors by ~40%",
            priority=level.value,
            target_component=error.operation,
            implementation_steps=[
                "Implement validation/checks",
                "Add error handlers",
                "Test with error injection",
                "Deploy and monitor"
            ]
        )
    
    def _learn_from_failure(self, correction: CorrectionResult,
                           error: ErrorContext,
                           analysis: ErrorAnalysis) -> ImprovementSuggestion:
        """Learn from failed correction"""
        
        factors = analysis.contributing_factors
        if not factors:
            factors = ["unknown factor"]
        
        primary_factor = factors[0]
        
        description = (f"Address '{primary_factor}' to prevent "
                      f"{error.error_type.value} errors in {error.operation}")
        
        level = ImprovementLevel.SIGNIFICANT if error.severity.value >= 4 else ImprovementLevel.MODERATE
        
        return ImprovementSuggestion(
            level=level,
            category="reactive",
            description=description,
            implementation_effort="high",
            expected_benefit=f"Prevent cascading failures from {error.error_type.value}",
            priority=level.value,
            target_component=error.operation,
            implementation_steps=[
                f"Investigate '{primary_factor}'",
                "Design mitigation strategy",
                "Implement safeguards",
                "Deploy monitoring",
                "Validate in production"
            ]
        )
    
    def _store_improvement_in_memory(self, suggestion: ImprovementSuggestion) -> None:
        """Store improvement suggestion in memory system"""
        if not self.memory_manager:
            return
        
        try:
            # Store as semantic knowledge
            self.memory_manager.store_semantic(
                concept_name=f"improvement_{suggestion.category}_{suggestion.target_component}",
                properties={
                    "level": suggestion.level.name,
                    "description": suggestion.description,
                    "priority": suggestion.priority,
                    "expected_benefit": suggestion.expected_benefit
                },
                source="adaptive_improvement_system"
            )
        except Exception:
            pass
    
    def detect_recurring_error_pattern(self, pattern: ErrorPattern) -> ImprovementSuggestion:
        """
        Detect and suggest improvements for recurring error pattern
        
        Args:
            pattern: ErrorPattern that is recurring
            
        Returns:
            ImprovementSuggestion
        """
        frequency = pattern.occurrence_count
        
        if frequency > 10:
            level = ImprovementLevel.CRITICAL
        elif frequency > 5:
            level = ImprovementLevel.SIGNIFICANT
        else:
            level = ImprovementLevel.MODERATE
        
        common_factors = pattern.get_common_factors()
        factors_str = ", ".join(
            f"{k}={v}" for k, v in common_factors.get("common_inputs", {}).items()
        )
        
        description = (f"Recurring {pattern.signature.error_type.value} error "
                      f"({frequency} occurrences). Common factors: {factors_str}")
        
        suggestion = ImprovementSuggestion(
            level=level,
            category="recurring",
            description=description,
            implementation_effort="high",
            expected_benefit=f"Eliminate ~{frequency} recurring errors",
            priority=level.value,
            target_component=pattern.contexts[0].operation if pattern.contexts else "unknown",
            implementation_steps=[
                "Root cause analysis",
                "Design targeted fix",
                "Implement solution",
                "Add regression tests",
                "Monitor for recurrence"
            ],
            estimated_impact={
                "error_reduction": 0.9,
                "system_reliability": 0.15,
                "operational_efficiency": 0.25
            }
        )
        
        if len(self.improvement_suggestions) < self.max_suggestions:
            self.improvement_suggestions.append(suggestion)
        
        return suggestion
    
    def generate_error_prevention_rules(self, pattern: ErrorPattern) -> Dict[str, Any]:
        """
        Generate prevention rules based on error pattern
        
        Args:
            pattern: ErrorPattern to learn from
            
        Returns:
            Prevention rule dictionary
        """
        rule = {
            "id": f"prevent_{pattern.signature.signature_hash[:8]}",
            "error_type": pattern.signature.error_type.value,
            "trigger_conditions": [],
            "prevention_actions": [],
            "severity": "medium",
            "created_at": datetime.now().isoformat(),
            "effectiveness": 0.0
        }
        
        # Extract trigger conditions from common factors
        factors = pattern.get_common_factors()
        for key, value in factors.get("common_inputs", {}).items():
            rule["trigger_conditions"].append({
                "field": key,
                "value": value,
                "operator": "equals"
            })
        
        # Suggest prevention actions
        error_type = pattern.signature.error_type
        if error_type == ErrorType.VALIDATION_ERROR:
            rule["prevention_actions"] = [
                "validate_input",
                "sanitize_data",
                "check_preconditions"
            ]
        elif error_type == ErrorType.RESOURCE_ERROR:
            rule["prevention_actions"] = [
                "check_resource_availability",
                "allocate_reserves",
                "implement_quota"
            ]
        elif error_type == ErrorType.TIMEOUT_ERROR:
            rule["prevention_actions"] = [
                "increase_timeout",
                "parallelize_operation",
                "enable_caching"
            ]
        elif error_type == ErrorType.STATE_ERROR:
            rule["prevention_actions"] = [
                "validate_state",
                "add_guards",
                "enforce_transitions"
            ]
        
        rule["severity"] = "critical" if pattern.occurrence_count > 10 else "medium"
        
        self.error_prevention_rules.append(rule)
        return rule
    
    def track_learning_metric(self, metric_name: str, current_value: float,
                             target_value: float, time_period: str = "1h") -> LearningMetric:
        """
        Track a learning metric
        
        Args:
            metric_name: Name of the metric
            current_value: Current value
            target_value: Target value
            time_period: Time period
            
        Returns:
            LearningMetric
        """
        previous_value = 0.0
        if metric_name in self.learning_metrics:
            previous_value = self.learning_metrics[metric_name].current_value
        
        # Determine trend
        if current_value > previous_value:
            trend = "improving"
        elif current_value < previous_value:
            trend = "degrading"
        else:
            trend = "stable"
        
        metric = LearningMetric(
            metric_name=metric_name,
            current_value=current_value,
            previous_value=previous_value,
            target_value=target_value,
            trend=trend,
            time_period=time_period
        )
        
        self.learning_metrics[metric_name] = metric
        return metric
    
    def get_top_improvements(self, limit: int = 10) -> List[ImprovementSuggestion]:
        """Get top improvement suggestions by priority"""
        sorted_suggestions = sorted(
            self.improvement_suggestions,
            key=lambda s: (s.priority, s.level.value),
            reverse=True
        )
        return sorted_suggestions[:limit]
    
    def implement_improvement(self, suggestion: ImprovementSuggestion) -> Dict[str, Any]:
        """
        Record implementation of an improvement
        
        Args:
            suggestion: ImprovementSuggestion to implement
            
        Returns:
            Implementation record
        """
        record = {
            "id": f"impl_{len(self.implemented_improvements)}",
            "suggestion": {
                "category": suggestion.category,
                "description": suggestion.description,
                "target": suggestion.target_component
            },
            "status": "implemented",
            "implemented_at": datetime.now().isoformat(),
            "expected_impact": suggestion.estimated_impact,
            "actual_impact": {}
        }
        
        self.implemented_improvements.append(record)
        
        # Track metric improvement
        if "error_reduction" in suggestion.estimated_impact:
            self.track_learning_metric(
                "system_error_rate",
                current_value=0.95,  # Placeholder
                target_value=0.99
            )
        
        return record
    
    def adapt_strategy_based_on_pattern(self, pattern: ErrorPattern,
                                       current_success_rate: float) -> StrategyAdaptation:
        """
        Recommend strategy adaptation based on error pattern
        
        Args:
            pattern: ErrorPattern to learn from
            current_success_rate: Current success rate of strategies
            
        Returns:
            StrategyAdaptation record
        """
        
        # Determine best strategy for this error type
        error_type = pattern.signature.error_type
        recommended_strategy = self._get_recommended_strategy(error_type)
        
        # Calculate expected improvement
        new_success_rate = min(current_success_rate + 0.2, 0.95)
        
        adaptation = StrategyAdaptation(
            strategy=recommended_strategy,
            original_success_rate=current_success_rate,
            new_success_rate=new_success_rate,
            error_pattern=pattern.signature.signature_hash[:8],
            adaptation_reason=f"Recurring {error_type.value} error pattern",
            changes_made={
                "priority_adjustment": True,
                "parameter_tuning": True,
                "fallback_addition": False
            }
        )
        
        self.strategy_adaptations.append(adaptation)
        return adaptation
    
    @staticmethod
    def _get_recommended_strategy(error_type: ErrorType) -> CorrectionStrategy:
        """Get recommended strategy for error type"""
        strategy_map = {
            ErrorType.LOGIC_ERROR: CorrectionStrategy.MODIFY_PARAMETERS,
            ErrorType.RESOURCE_ERROR: CorrectionStrategy.RETRY,
            ErrorType.VALIDATION_ERROR: CorrectionStrategy.MODIFY_PARAMETERS,
            ErrorType.STATE_ERROR: CorrectionStrategy.ROLLBACK,
            ErrorType.TIMEOUT_ERROR: CorrectionStrategy.RETRY,
            ErrorType.DEPENDENCY_ERROR: CorrectionStrategy.FALLBACK,
            ErrorType.CONFIGURATION_ERROR: CorrectionStrategy.ANALYZE,
            ErrorType.DATA_ERROR: CorrectionStrategy.MODIFY_PARAMETERS,
            ErrorType.PERMISSION_ERROR: CorrectionStrategy.ESCALATE,
            ErrorType.UNKNOWN_ERROR: CorrectionStrategy.ANALYZE
        }
        return strategy_map.get(error_type, CorrectionStrategy.ANALYZE)
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get overall system insights from learning"""
        
        # Calculate improvement opportunity score
        high_priority = sum(1 for s in self.improvement_suggestions if s.priority >= 8)
        medium_priority = sum(1 for s in self.improvement_suggestions if 5 <= s.priority < 8)
        
        # Get metric trends
        improving_metrics = sum(1 for m in self.learning_metrics.values() if m.trend == "improving")
        degrading_metrics = sum(1 for m in self.learning_metrics.values() if m.trend == "degrading")
        
        # Calculate implemented improvements impact
        total_expected_impact = sum(
            sum(imp.get("expected_impact", {}).values())
            for imp in self.implemented_improvements
        )
        
        return {
            "improvement_opportunities": {
                "critical": high_priority,
                "medium": medium_priority,
                "total_suggestions": len(self.improvement_suggestions)
            },
            "learning_progress": {
                "improving_metrics": improving_metrics,
                "degrading_metrics": degrading_metrics,
                "total_tracked_metrics": len(self.learning_metrics)
            },
            "implementation_status": {
                "implemented_improvements": len(self.implemented_improvements),
                "total_expected_impact": total_expected_impact,
                "strategy_adaptations": len(self.strategy_adaptations)
            },
            "prevention_rules": {
                "total_rules": len(self.error_prevention_rules),
                "active_rules": len([r for r in self.error_prevention_rules if r.get("active", True)])
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adaptive improvement system statistics"""
        return {
            "total_suggestions": len(self.improvement_suggestions),
            "suggestions_by_level": {
                "critical": len([s for s in self.improvement_suggestions if s.level == ImprovementLevel.CRITICAL]),
                "significant": len([s for s in self.improvement_suggestions if s.level == ImprovementLevel.SIGNIFICANT]),
                "moderate": len([s for s in self.improvement_suggestions if s.level == ImprovementLevel.MODERATE]),
                "minor": len([s for s in self.improvement_suggestions if s.level == ImprovementLevel.MINOR])
            },
            "implemented_improvements": len(self.implemented_improvements),
            "prevention_rules": len(self.error_prevention_rules),
            "strategy_adaptations": len(self.strategy_adaptations),
            "learning_metrics_tracked": len(self.learning_metrics),
            "system_insights": self.get_system_insights()
        }
