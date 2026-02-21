"""
Meta-Learning Engine

This module implements meta-learning - learning how to learn.
The system optimizes its own learning process and strategy selection.

Based on: MAML (Model-Agnostic Meta-Learning) and meta-learning principles
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import statistics

from autonomous_system.core.correction_strategy import CorrectionStrategy
from autonomous_system.core.error_detection import ErrorType


class LearningPhase(Enum):
    """Phases in the meta-learning process"""
    EXPLORATION = "exploration"        # Exploring different strategies
    EVALUATION = "evaluation"          # Evaluating strategy performance
    ADAPTATION = "adaptation"          # Adapting meta-parameters
    CONSOLIDATION = "consolidation"   # Consolidating learned knowledge


@dataclass
class MetaLearningMetrics:
    """Metrics for meta-learning evaluation"""
    phase: LearningPhase
    learning_efficiency: float         # How quickly did it learn
    strategy_quality: float            # Quality of learned strategies
    generalization_score: float        # How well it generalizes to new situations
    adaptation_speed: float            # How fast does it adapt
    cumulative_improvement: float      # Overall improvement over time
    
    def overall_score(self) -> float:
        """Calculate overall meta-learning score"""
        return (
            self.learning_efficiency * 0.2 +
            self.strategy_quality * 0.3 +
            self.generalization_score * 0.3 +
            self.adaptation_speed * 0.2
        )


@dataclass
class StrategyMetaProfile:
    """Meta-profile of a strategy - how it learns"""
    strategy: CorrectionStrategy
    success_rate: float                # Overall success rate
    learning_curve: List[float]        # Performance improvement over time
    error_type_profiles: Dict[ErrorType, float] = field(default_factory=dict)
    adaptation_potential: float = 0.0  # Can this strategy adapt/improve
    confidence_trajectory: List[float] = field(default_factory=list)
    
    def trend(self) -> float:
        """Get learning trend (positive = improving)"""
        if len(self.learning_curve) < 2:
            return 0.0
        recent = statistics.mean(self.learning_curve[-5:]) if len(self.learning_curve) >= 5 else self.learning_curve[-1]
        early = statistics.mean(self.learning_curve[:5]) if len(self.learning_curve) >= 5 else self.learning_curve[0]
        return recent - early


class MetaLearningEngine:
    """
    Meta-learning engine that learns how to optimize the learning process.
    """
    
    def __init__(self):
        """Initialize meta-learning engine"""
        self.current_phase = LearningPhase.EXPLORATION
        self.phase_history: List[LearningPhase] = []
        self.metrics_history: List[MetaLearningMetrics] = []
        
        # Strategy meta-profiles
        self.strategy_profiles: Dict[CorrectionStrategy, StrategyMetaProfile] = {}
        
        # Meta-parameters being optimized
        self.meta_parameters = {
            "exploration_iterations": 100,  # How many times to try before deciding
            "confidence_threshold": 0.6,    # Confidence needed to adopt strategy
            "adaptation_window": 10,        # Number of experiences to adapt from
            "generalization_factor": 0.8,  # How much to generalize vs specialize
        }
        
        # Learning state
        self.total_meta_iterations = 0
        self.strategies_mastered = 0
        self.generalization_improvements = 0
        self.episode_count = 0
    
    def initialize_strategy_profile(self, strategy: CorrectionStrategy) -> None:
        """Initialize meta-profile for a strategy"""
        if strategy not in self.strategy_profiles:
            self.strategy_profiles[strategy] = StrategyMetaProfile(
                strategy=strategy,
                success_rate=0.5,
                learning_curve=[0.5]
            )
    
    def record_learning_experience(self, strategy: CorrectionStrategy,
                                  error_type: ErrorType,
                                  success: bool,
                                  confidence: float) -> None:
        """Record learning experience for meta-analysis"""
        self.episode_count += 1
        
        # Ensure profile exists
        self.initialize_strategy_profile(strategy)
        profile = self.strategy_profiles[strategy]
        
        # Update success rate
        old_rate = profile.success_rate
        profile.success_rate = (old_rate * (self.episode_count - 1) + (1 if success else 0)) / self.episode_count
        
        # Update error-type-specific profile
        if error_type not in profile.error_type_profiles:
            profile.error_type_profiles[error_type] = 0.5
        
        old_error_rate = profile.error_type_profiles[error_type]
        error_count = sum(1 for e in profile.error_type_profiles.keys())
        profile.error_type_profiles[error_type] = (
            old_error_rate * (error_count - 1) + (1 if success else 0)
        ) / error_count
        
        # Update learning curve
        profile.learning_curve.append(profile.success_rate)
        profile.confidence_trajectory.append(confidence)
        
        # Limit history
        if len(profile.learning_curve) > 100:
            profile.learning_curve = profile.learning_curve[-100:]
            profile.confidence_trajectory = profile.confidence_trajectory[-100:]
    
    def evaluate_strategy_potential(self, strategy: CorrectionStrategy) -> float:
        """
        Evaluate adaptation potential of a strategy.
        Returns 0-1 score: can this strategy improve further?
        """
        if strategy not in self.strategy_profiles:
            return 1.0  # Unknown strategies have high potential
        
        profile = self.strategy_profiles[strategy]
        
        # High potential if:
        # 1. Learning curve is trending upward
        # 2. Still below 0.9 success rate
        # 3. High variance in confidence (room to improve)
        
        trend = profile.trend()
        trend_score = min(1.0, max(0.0, trend / 0.1))  # Normalize trend
        
        success_score = (0.9 - profile.success_rate) / 0.9  # Lower success = higher potential
        
        if len(profile.confidence_trajectory) > 2:
            variance = statistics.variance(profile.confidence_trajectory[-10:]) if len(profile.confidence_trajectory) >= 10 else 0
            confidence_score = min(1.0, variance * 5)  # Normalize variance
        else:
            confidence_score = 0.5
        
        potential = (trend_score * 0.4 + success_score * 0.3 + confidence_score * 0.3)
        profile.adaptation_potential = potential
        
        return potential
    
    def decide_learning_phase(self) -> LearningPhase:
        """Decide next learning phase based on current state"""
        if self.episode_count < self.meta_parameters["exploration_iterations"]:
            return LearningPhase.EXPLORATION
        
        # Check if strategies are being learned
        learned_strategies = sum(1 for p in self.strategy_profiles.values() 
                                if p.success_rate > 0.7)
        total_strategies = len(self.strategy_profiles)
        
        if total_strategies == 0:
            return LearningPhase.EXPLORATION
        
        learning_rate = learned_strategies / total_strategies
        
        if learning_rate < 0.3:
            return LearningPhase.EXPLORATION
        elif learning_rate < 0.7:
            return LearningPhase.EVALUATION
        elif learning_rate < 0.9:
            return LearningPhase.ADAPTATION
        else:
            return LearningPhase.CONSOLIDATION
    
    def update_phase(self) -> None:
        """Update learning phase"""
        new_phase = self.decide_learning_phase()
        if new_phase != self.current_phase:
            self.phase_history.append(new_phase)
            self.current_phase = new_phase
    
    def record_metrics(self, metrics: MetaLearningMetrics) -> None:
        """Record meta-learning metrics"""
        self.total_meta_iterations += 1
        self.metrics_history.append(metrics)
        
        if metrics.overall_score() > 0.8:
            self.strategies_mastered += 1
        
        if metrics.generalization_score > 0.7:
            self.generalization_improvements += 1
    
    def get_best_strategy_for_error(self, error_type: ErrorType) -> Optional[CorrectionStrategy]:
        """Get best strategy for specific error type"""
        best_strategy = None
        best_score = 0.0
        
        for strategy, profile in self.strategy_profiles.items():
            if error_type in profile.error_type_profiles:
                score = profile.error_type_profiles[error_type]
                if score > best_score:
                    best_score = score
                    best_strategy = strategy
        
        return best_strategy
    
    def get_strategies_by_trend(self, limit: int = 3) -> List[Tuple[CorrectionStrategy, float]]:
        """Get strategies sorted by learning trend (improving strategies first)"""
        strategies_with_trend = [
            (s, p.trend()) for s, p in self.strategy_profiles.items()
        ]
        # Sort by trend descending
        strategies_with_trend.sort(key=lambda x: x[1], reverse=True)
        return strategies_with_trend[:limit]
    
    def optimize_meta_parameters(self) -> None:
        """Optimize meta-learning parameters based on history"""
        if len(self.metrics_history) < 5:
            return
        
        # Get recent metrics
        recent = self.metrics_history[-5:]
        avg_efficiency = statistics.mean([m.learning_efficiency for m in recent])
        avg_generalization = statistics.mean([m.generalization_score for m in recent])
        
        # Adjust exploration iterations
        if avg_efficiency > 0.8:
            # Learning quickly, can reduce exploration
            self.meta_parameters["exploration_iterations"] = max(50, 
                self.meta_parameters["exploration_iterations"] - 10)
        else:
            # Need more exploration
            self.meta_parameters["exploration_iterations"] = min(200,
                self.meta_parameters["exploration_iterations"] + 10)
        
        # Adjust adaptation window
        if avg_generalization > 0.75:
            # Good generalization, can use smaller window
            self.meta_parameters["adaptation_window"] = max(5,
                self.meta_parameters["adaptation_window"] - 1)
        else:
            # Poor generalization, need more data
            self.meta_parameters["adaptation_window"] = min(20,
                self.meta_parameters["adaptation_window"] + 1)
    
    def export_learned_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Export learned strategy profiles"""
        profiles = {}
        for strategy, profile in self.strategy_profiles.items():
            profiles[strategy.value] = {
                "success_rate": profile.success_rate,
                "trend": profile.trend(),
                "adaptation_potential": profile.adaptation_potential,
                "error_specializations": {
                    et.value: rate for et, rate in profile.error_type_profiles.items()
                },
                "learning_curve_length": len(profile.learning_curve)
            }
        return profiles
    
    def export_state(self) -> Dict[str, Any]:
        """Export meta-learning engine state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "current_phase": self.current_phase.value,
            "total_episodes": self.episode_count,
            "total_meta_iterations": self.total_meta_iterations,
            "strategies_mastered": self.strategies_mastered,
            "generalization_improvements": self.generalization_improvements,
            "meta_parameters": self.meta_parameters,
            "learned_profiles": self.export_learned_profiles(),
            "phase_history": [p.value for p in self.phase_history[-20:]]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get meta-learning statistics"""
        if not self.metrics_history:
            return {
                "episode_count": 0,
                "strategies_tracked": 0,
                "current_phase": self.current_phase.value
            }
        
        scores = [m.overall_score() for m in self.metrics_history]
        
        return {
            "episode_count": self.episode_count,
            "total_meta_iterations": self.total_meta_iterations,
            "strategies_tracked": len(self.strategy_profiles),
            "strategies_mastered": self.strategies_mastered,
            "average_meta_score": statistics.mean(scores),
            "best_meta_score": max(scores),
            "current_phase": self.current_phase.value,
            "generalization_improvements": self.generalization_improvements
        }
