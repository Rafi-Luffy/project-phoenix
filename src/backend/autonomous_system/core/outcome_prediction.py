"""
Outcome Prediction Engine for Tree of Thoughts

This module predicts likely outcomes of reasoning paths based on historical
patterns, learned strategies, and contextual analysis.

Based on: Tree of Thoughts outcome prediction strategies
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy
from autonomous_system.core.thought_node import ThoughtNode, ThoughtPath, Evaluation


@dataclass
class OutcomePrediction:
    """Prediction of path outcome"""
    success_probability: float          # P(success)
    expected_cost: float               # Expected cost
    expected_time: float               # Expected execution time
    confidence: float                  # Confidence in prediction
    reasoning: str                     # Why this prediction
    
    risk_level: float = 0.5            # Risk level (0-1)
    uncertainty: float = 0.3           # Prediction uncertainty
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success_probability": self.success_probability,
            "expected_cost": self.expected_cost,
            "expected_time": self.expected_time,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "risk_level": self.risk_level
        }


class OutcomePredictionEngine:
    """
    Predicts outcomes for reasoning paths using learned patterns
    and historical data.
    """
    
    def __init__(self):
        """Initialize prediction engine"""
        self.strategy_success_rates: Dict[CorrectionStrategy, Tuple[int, int]] = defaultdict(lambda: (0, 0))
        self.error_strategy_success: Dict[Tuple[ErrorType, CorrectionStrategy], Tuple[int, int]] = defaultdict(lambda: (0, 0))
        self.path_outcomes: List[Tuple[ThoughtPath, bool, float]] = []
        
        self.total_predictions = 0
        self.correct_predictions = 0
        self.prediction_history: List[Dict[str, Any]] = []
    
    def register_outcome(self, path: ThoughtPath, success: bool, actual_cost: float) -> None:
        """
        Register actual outcome of a path
        
        Args:
            path: The thought path that was executed
            success: Whether it succeeded
            actual_cost: Actual cost incurred
        """
        self.path_outcomes.append((path, success, actual_cost))
        
        # Update strategy success rates
        for strategy in path.strategies:
            successes, total = self.strategy_success_rates[strategy]
            self.strategy_success_rates[strategy] = (
                successes + (1 if success else 0),
                total + 1
            )
    
    def register_strategy_outcome(self, error_type: ErrorType, 
                                  strategy: CorrectionStrategy,
                                  success: bool) -> None:
        """Register outcome for strategy-error combination"""
        successes, total = self.error_strategy_success[(error_type, strategy)]
        self.error_strategy_success[(error_type, strategy)] = (
            successes + (1 if success else 0),
            total + 1
        )
    
    def predict_outcome(self, path: ThoughtPath) -> OutcomePrediction:
        """
        Predict outcome for a thought path
        
        Args:
            path: Thought path to predict
            
        Returns:
            OutcomePrediction with likelihood estimates
        """
        if not path.nodes:
            return OutcomePrediction(
                success_probability=0.5,
                expected_cost=0.0,
                expected_time=0.0,
                confidence=0.3,
                reasoning="Empty path - insufficient data"
            )
        
        # Calculate success probability from strategy history
        success_prob = self._calculate_success_probability(path)
        
        # Estimate cost and time
        expected_cost = self._estimate_cost(path)
        expected_time = self._estimate_time(path)
        
        # Determine confidence
        confidence = self._calculate_confidence(path, success_prob)
        
        # Assess risk
        risk_level = self._assess_risk(path, success_prob)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(path, success_prob, confidence)
        
        prediction = OutcomePrediction(
            success_probability=success_prob,
            expected_cost=expected_cost,
            expected_time=expected_time,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=risk_level
        )
        
        # Record prediction
        self.prediction_history.append({
            "path": path.path_id,
            "prediction": prediction.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
        self.total_predictions += 1
        
        return prediction
    
    def _calculate_success_probability(self, path: ThoughtPath) -> float:
        """Calculate success probability from strategy history"""
        if not path.strategies:
            return 0.5
        
        success_probs = []
        for strategy in path.strategies:
            successes, total = self.strategy_success_rates[strategy]
            if total > 0:
                prob = successes / total
                success_probs.append(prob)
        
        if success_probs:
            # Average with decay for less common strategies
            avg_prob = sum(success_probs) / len(success_probs)
            return min(1.0, max(0.0, avg_prob))
        
        return 0.5
    
    def _estimate_cost(self, path: ThoughtPath) -> float:
        """Estimate cost for path"""
        if not path.nodes:
            return 0.0
        
        cost = 0.0
        for node in path.nodes:
            if node.evaluation:
                cost += node.evaluation.overall_score() * 10  # Scale to cost units
        
        return cost
    
    def _estimate_time(self, path: ThoughtPath) -> float:
        """Estimate execution time for path"""
        depth = path.depth()
        num_strategies = len(path.strategies)
        
        # Base time increases with depth
        base_time = depth * 100  # milliseconds per depth level
        
        # Strategy complexity
        strategy_time = num_strategies * 50
        
        return base_time + strategy_time
    
    def _calculate_confidence(self, path: ThoughtPath, success_prob: float) -> float:
        """Calculate confidence in prediction"""
        # More data = higher confidence
        num_nodes = len(path.nodes)
        data_confidence = min(1.0, num_nodes / 5.0)
        
        # More strategies = higher confidence if they have history
        strategies_with_data = sum(
            1 for s in path.strategies 
            if self.strategy_success_rates[s][1] > 0
        )
        strategy_confidence = min(1.0, strategies_with_data / len(path.strategies)) if path.strategies else 0.5
        
        # Weighted average
        confidence = (data_confidence * 0.6 + strategy_confidence * 0.4)
        
        return min(1.0, max(0.2, confidence))
    
    def _assess_risk(self, path: ThoughtPath, success_prob: float) -> float:
        """Assess risk level of path"""
        # Risk is inverse of success probability
        base_risk = 1.0 - success_prob
        
        # Increase risk with path depth (more things can go wrong)
        depth_risk = path.depth() * 0.05
        
        return min(1.0, base_risk + depth_risk)
    
    def _generate_reasoning(self, path: ThoughtPath, success_prob: float, confidence: float) -> str:
        """Generate reasoning explanation"""
        reasons = []
        
        if path.depth() == 0:
            reasons.append("Path has no nodes yet")
        elif path.depth() < 3:
            reasons.append(f"Short path (depth {path.depth()})")
        
        if confidence > 0.8:
            reasons.append("High prediction confidence from historical data")
        elif confidence < 0.3:
            reasons.append("Low confidence due to limited data")
        
        if success_prob > 0.8:
            reasons.append("Strategies have high historical success rate")
        elif success_prob < 0.4:
            reasons.append("Strategies have low historical success rate")
        
        if not reasons:
            reasons.append(f"Moderate success probability ({success_prob:.0%})")
        
        return "; ".join(reasons)
    
    def get_prediction_accuracy(self) -> float:
        """Get accuracy of past predictions"""
        if self.total_predictions == 0:
            return 0.0
        return self.correct_predictions / self.total_predictions
    
    def get_strategy_success_rate(self, strategy: CorrectionStrategy) -> float:
        """Get success rate for strategy"""
        successes, total = self.strategy_success_rates[strategy]
        if total == 0:
            return 0.5  # Default if no data
        return successes / total
    
    def get_stats(self) -> Dict[str, Any]:
        """Get prediction engine statistics"""
        return {
            "total_predictions": self.total_predictions,
            "correct_predictions": self.correct_predictions,
            "accuracy": self.get_prediction_accuracy(),
            "registered_outcomes": len(self.path_outcomes),
            "strategy_count": len(self.strategy_success_rates),
            "prediction_history_size": len(self.prediction_history)
        }
