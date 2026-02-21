"""
Strategy Learning Engine for Learning System

This module learns optimal strategy selection based on error patterns
and correction session history.

Based on: Self-Refine framework for adaptive strategy selection
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict
import json

from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy


class LearningPhase(Enum):
    """Learning phases for strategy adaptation"""
    EXPLORATION = "exploration"  # Initially trying all strategies
    EXPLOITATION = "exploitation"  # Focusing on best strategies
    OPTIMIZATION = "optimization"  # Fine-tuning strategy parameters
    PREDICTION = "prediction"  # Predicting optimal strategies


@dataclass
class StrategyPerformance:
    """Performance metrics for a strategy in a context"""
    strategy: CorrectionStrategy
    error_type: ErrorType
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    avg_execution_time: float = 0.0
    avg_resource_usage: float = 0.0
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_attempts / self.total_attempts
    
    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency based on speed and resource usage"""
        if self.avg_execution_time == 0:
            return 0.0
        # Normalize: lower time and resources = higher score
        efficiency = 1.0 / (1.0 + self.avg_execution_time)
        efficiency *= (1.0 - min(self.avg_resource_usage / 100.0, 1.0))
        return efficiency
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy": self.strategy.value,
            "error_type": self.error_type.value,
            "attempts": self.total_attempts,
            "successes": self.successful_attempts,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "confidence": self.confidence_score,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class StrategyRecommendation:
    """Recommendation for strategy use"""
    strategy: CorrectionStrategy
    error_type: ErrorType
    confidence: float
    reasoning: str
    estimated_success_rate: float
    alternative_strategies: List[CorrectionStrategy] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy": self.strategy.value,
            "error_type": self.error_type.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "estimated_success_rate": self.estimated_success_rate,
            "alternatives": [s.value for s in self.alternative_strategies]
        }


@dataclass
class StrategyAdaptationRecord:
    """Record of how strategy was adapted"""
    original_strategy: CorrectionStrategy
    adapted_strategy: CorrectionStrategy
    adaptation_reason: str
    success: bool
    confidence_change: float
    timestamp: datetime = field(default_factory=datetime.now)


class StrategyLearningEngine:
    """
    Learns optimal strategy selection based on correction history.
    Tracks performance, adapts recommendations, predicts effectiveness.
    """
    
    def __init__(self):
        """Initialize strategy learning engine"""
        self.strategy_performances: Dict[str, StrategyPerformance] = {}
        self.adaptation_records: List[StrategyAdaptationRecord] = []
        self.error_strategy_matrix: Dict[ErrorType, Dict[CorrectionStrategy, float]] = {}
        self.learning_phase = LearningPhase.EXPLORATION
        self.total_learning_sessions = 0
        
        # Thresholds for phase transitions
        self.exploration_threshold = 50  # Sessions before exploitation
        self.exploitation_threshold = 200  # Sessions before optimization
    
    def update_strategy_performance(self, 
                                   strategy: CorrectionStrategy,
                                   error_type: ErrorType,
                                   success: bool,
                                   execution_time: float = 0.0,
                                   resource_usage: float = 0.0) -> None:
        """
        Update performance metrics for a strategy in a context
        
        Args:
            strategy: Strategy that was applied
            error_type: Type of error being corrected
            success: Whether correction was successful
            execution_time: Time taken (milliseconds)
            resource_usage: Resource usage percentage (0-100)
        """
        self.total_learning_sessions += 1
        key = f"{strategy.value}_{error_type.value}"
        
        if key not in self.strategy_performances:
            self.strategy_performances[key] = StrategyPerformance(
                strategy=strategy,
                error_type=error_type
            )
        
        perf = self.strategy_performances[key]
        perf.total_attempts += 1
        
        if success:
            perf.successful_attempts += 1
        else:
            perf.failed_attempts += 1
        
        # Update running averages
        if execution_time > 0:
            perf.avg_execution_time = (
                (perf.avg_execution_time * (perf.total_attempts - 1) + execution_time) /
                perf.total_attempts
            )
        
        if resource_usage > 0:
            perf.avg_resource_usage = (
                (perf.avg_resource_usage * (perf.total_attempts - 1) + resource_usage) /
                perf.total_attempts
            )
        
        # Update confidence based on sample size
        perf.confidence_score = min(perf.total_attempts / 20.0, 1.0)
        perf.last_updated = datetime.now()
        
        # Update learning phase
        self._update_learning_phase()
    
    def _update_learning_phase(self) -> None:
        """Update learning phase based on progress"""
        if self.total_learning_sessions < self.exploration_threshold:
            self.learning_phase = LearningPhase.EXPLORATION
        elif self.total_learning_sessions < self.exploitation_threshold:
            self.learning_phase = LearningPhase.EXPLOITATION
        else:
            self.learning_phase = LearningPhase.OPTIMIZATION
    
    def get_best_strategy(self, error_type: ErrorType) -> Optional[StrategyRecommendation]:
        """
        Get best strategy for an error type
        
        Args:
            error_type: Type of error
            
        Returns:
            Strategy recommendation or None
        """
        # Find all performance records for this error type
        relevant_perfs = [
            perf for perf in self.strategy_performances.values()
            if perf.error_type == error_type
        ]
        
        if not relevant_perfs:
            return None
        
        # In exploration phase, still try different strategies
        if self.learning_phase == LearningPhase.EXPLORATION:
            # Return most promising but ensure diversity
            relevant_perfs.sort(key=lambda p: (p.success_rate, p.efficiency_score), reverse=True)
        else:
            # Exploitation: focus on proven strategies
            relevant_perfs.sort(key=lambda p: (p.success_rate, p.efficiency_score), reverse=True)
        
        best_perf = relevant_perfs[0]
        
        # Get alternatives
        alternatives = [
            p.strategy for p in relevant_perfs[1:4]
            if p.success_rate > 0
        ]
        
        confidence = best_perf.confidence_score
        if best_perf.total_attempts >= 5:
            confidence = min(confidence + (best_perf.success_rate * 0.3), 1.0)
        
        reasoning = self._generate_reasoning(best_perf)
        
        return StrategyRecommendation(
            strategy=best_perf.strategy,
            error_type=error_type,
            confidence=confidence,
            reasoning=reasoning,
            estimated_success_rate=best_perf.success_rate,
            alternative_strategies=alternatives
        )
    
    def _generate_reasoning(self, perf: StrategyPerformance) -> str:
        """Generate human-readable reasoning"""
        if perf.total_attempts < 3:
            return f"Limited data ({perf.total_attempts} attempts)"
        
        if perf.success_rate >= 0.8:
            return f"High success rate ({perf.success_rate:.1%}) over {perf.total_attempts} attempts"
        elif perf.success_rate >= 0.5:
            return f"Moderate success ({perf.success_rate:.1%}), good efficiency"
        else:
            return f"Lower success rate ({perf.success_rate:.1%}), needs alternatives"
    
    def get_strategies_for_error(self, 
                                 error_type: ErrorType,
                                 limit: int = 5) -> List[StrategyPerformance]:
        """Get ranked strategies for an error type"""
        relevant = [
            perf for perf in self.strategy_performances.values()
            if perf.error_type == error_type
        ]
        
        if not relevant:
            return []
        
        # Rank by success rate + efficiency + confidence
        relevant.sort(
            key=lambda p: (p.success_rate, p.efficiency_score, p.confidence_score),
            reverse=True
        )
        
        return relevant[:limit]
    
    def adapt_strategy(self,
                      original_strategy: CorrectionStrategy,
                      error_type: ErrorType,
                      context: Dict[str, Any]) -> Tuple[CorrectionStrategy, float]:
        """
        Suggest adaptation of a strategy based on context
        
        Args:
            original_strategy: Original chosen strategy
            error_type: Type of error
            context: Additional context
            
        Returns:
            Tuple of (adapted_strategy, confidence)
        """
        # If original had high success rate, stick with it
        key = f"{original_strategy.value}_{error_type.value}"
        if key in self.strategy_performances:
            perf = self.strategy_performances[key]
            if perf.success_rate >= 0.7 and perf.total_attempts >= 5:
                return (original_strategy, perf.confidence_score)
        
        # Otherwise, try to find better strategy
        recommendation = self.get_best_strategy(error_type)
        if recommendation and recommendation.confidence > 0.7:
            record = StrategyAdaptationRecord(
                original_strategy=original_strategy,
                adapted_strategy=recommendation.strategy,
                adaptation_reason=recommendation.reasoning,
                success=False,  # Updated after execution
                confidence_change=recommendation.confidence - 0.5
            )
            self.adaptation_records.append(record)
            return (recommendation.strategy, recommendation.confidence)
        
        return (original_strategy, 0.5)
    
    def record_adaptation_result(self, success: bool) -> None:
        """Record result of an adaptation"""
        if self.adaptation_records:
            self.adaptation_records[-1].success = success
    
    def get_strategy_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Get performance matrix for all error-strategy combinations"""
        matrix = {}
        
        for key, perf in self.strategy_performances.items():
            error_key = perf.error_type.value
            if error_key not in matrix:
                matrix[error_key] = {}
            
            matrix[error_key][perf.strategy.value] = {
                "success_rate": perf.success_rate,
                "efficiency": perf.efficiency_score,
                "confidence": perf.confidence_score,
                "attempts": perf.total_attempts
            }
        
        return matrix
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about learning progress"""
        # Find most learned error types
        error_type_attempts = defaultdict(int)
        error_type_successes = defaultdict(int)
        
        for perf in self.strategy_performances.values():
            error_type_attempts[perf.error_type.value] += perf.total_attempts
            error_type_successes[perf.error_type.value] += perf.successful_attempts
        
        # Calculate success rates per error type
        error_type_success_rates = {}
        for error_type, attempts in error_type_attempts.items():
            successes = error_type_successes[error_type]
            error_type_success_rates[error_type] = {
                "success_rate": successes / attempts if attempts > 0 else 0,
                "attempts": attempts
            }
        
        # Find most improved strategies
        improved_strategies = []
        window_start = datetime.now() - timedelta(hours=24)
        recent_performances = [
            perf for perf in self.strategy_performances.values()
            if perf.last_updated > window_start
        ]
        
        if recent_performances:
            recent_performances.sort(
                key=lambda p: p.success_rate,
                reverse=True
            )
            improved_strategies = [
                p.strategy.value for p in recent_performances[:3]
            ]
        
        return {
            "learning_phase": self.learning_phase.value,
            "total_sessions": self.total_learning_sessions,
            "total_strategies_learned": len(self.strategy_performances),
            "error_type_insights": error_type_success_rates,
            "improved_strategies": improved_strategies,
            "adaptation_history_size": len(self.adaptation_records)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get learning engine statistics"""
        return {
            "total_learning_sessions": self.total_learning_sessions,
            "learning_phase": self.learning_phase.value,
            "strategy_performance_records": len(self.strategy_performances),
            "adaptation_records": len(self.adaptation_records),
            "exploration_complete": self.total_learning_sessions > self.exploration_threshold,
            "exploitation_complete": self.total_learning_sessions > self.exploitation_threshold
        }
