"""
Decision Optimization Orchestrator

This module coordinates decision tree generation, resource optimization,
and strategy selection for optimal outcomes.

Based on: Self-Refine framework for decision making
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from autonomous_system.core.decision_tree import DecisionTreeBuilder, DecisionTree
from autonomous_system.core.resource_optimizer import (
    ResourceOptimizationEngine, ResourceCost, OptimizationResult, ResourceBudget
)
from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy


@dataclass
class DecisionContext:
    """Context for decision making"""
    error_type: ErrorType
    operation: str
    agent_id: str
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    resource_constraints: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "error_type": self.error_type.value,
            "operation": self.operation,
            "agent_id": self.agent_id,
            "execution_history_size": len(self.execution_history),
            "metadata": self.metadata
        }


@dataclass
class Decision:
    """A made decision"""
    decision_id: str
    context: DecisionContext
    selected_strategy: CorrectionStrategy
    confidence: float
    rationale: str
    resource_optimization: Optional[OptimizationResult] = None
    decision_tree_path: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    outcome: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "decision_id": self.decision_id,
            "strategy": self.selected_strategy.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "timestamp": self.timestamp.isoformat(),
            "outcome": self.outcome
        }


class DecisionOptimizationOrchestrator:
    """
    Master coordinator for decision optimization.
    Generates decision trees, optimizes resources, makes decisions.
    """
    
    def __init__(self):
        """Initialize decision optimization orchestrator"""
        self.decision_tree_builder = DecisionTreeBuilder()
        self.resource_optimizer = ResourceOptimizationEngine()
        
        self.decisions: Dict[str, Decision] = {}
        self.decision_history: List[Decision] = []
        
        self.total_decisions = 0
        self.successful_decisions = 0
        self.decision_confidence_sum = 0.0
    
    def register_strategy_cost(self, strategy: CorrectionStrategy, 
                              error_type: ErrorType,
                              cpu_ms: float,
                              memory_mb: float,
                              success_rate: float) -> None:
        """Register cost profile for strategy-error combination"""
        cost = ResourceCost(
            strategy=strategy,
            error_type=error_type,
            cpu_cost=cpu_ms,
            memory_cost=memory_mb,
            success_probability=success_rate
        )
        self.resource_optimizer.register_strategy_cost(cost)
    
    def build_decision_tree(self, error_type: ErrorType, 
                           rules: List[Dict[str, Any]]) -> DecisionTree:
        """
        Build decision tree for error type
        
        Args:
            error_type: Error type to build tree for
            rules: Knowledge rules from learning system
            
        Returns:
            Decision tree
        """
        tree = self.decision_tree_builder.build_tree_from_rules(error_type, rules)
        return tree
    
    def make_decision(self, context: DecisionContext,
                     candidate_strategies: List[CorrectionStrategy],
                     budget: Optional[ResourceBudget] = None) -> Decision:
        """
        Make optimized decision for given context
        
        Args:
            context: Decision context
            candidate_strategies: Available strategies
            budget: Resource constraints
            
        Returns:
            Optimized decision
        """
        self.total_decisions += 1
        decision_id = f"decision_{self.total_decisions}"
        
        # Step 1: Check decision tree if available
        tree = self.decision_tree_builder.get_tree_for_error(context.error_type)
        tree_path = []
        tree_strategy = None
        tree_confidence = 0.0
        
        if tree:
            # Traverse decision tree
            decision_node = tree.traverse(context.to_dict())
            if decision_node:
                tree_path = [decision_node.node_id]
                tree_strategy = decision_node.strategy
                tree_confidence = decision_node.confidence
        
        # Step 2: Optimize for resources
        optimization_result = self.resource_optimizer.optimize_strategy_selection(
            error_type=context.error_type,
            available_strategies=candidate_strategies,
            budget=budget
        )
        
        # Step 3: Select final strategy
        if tree_strategy and tree_confidence > 0.7:
            # Use tree decision if confident
            selected_strategy = tree_strategy
            final_confidence = tree_confidence
            rationale = f"Selected from decision tree ({tree_confidence:.0%} confidence)"
        else:
            # Use resource optimization result
            selected_strategy = optimization_result.selected_strategy
            final_confidence = optimization_result.cost.success_probability
            rationale = optimization_result.reasoning
        
        # Step 4: Create decision
        decision = Decision(
            decision_id=decision_id,
            context=context,
            selected_strategy=selected_strategy,
            confidence=final_confidence,
            rationale=rationale,
            resource_optimization=optimization_result,
            decision_tree_path=tree_path,
            timestamp=datetime.now()
        )
        
        self.decisions[decision_id] = decision
        self.decision_history.append(decision)
        self.decision_confidence_sum += final_confidence
        
        return decision
    
    def record_decision_outcome(self, decision_id: str, success: bool) -> None:
        """
        Record outcome of a decision
        
        Args:
            decision_id: ID of decision
            success: Whether decision led to success
        """
        if decision_id in self.decisions:
            decision = self.decisions[decision_id]
            decision.outcome = success
            
            if success:
                self.successful_decisions += 1
            
            # Update decision tree
            for tree in self.decision_tree_builder.get_all_trees():
                tree.record_decision_outcome(success)
    
    def get_decision_analysis(self) -> Dict[str, Any]:
        """Get analysis of decision making"""
        if self.total_decisions == 0:
            return {
                "total_decisions": 0,
                "success_rate": 0.0,
                "average_confidence": 0.0
            }
        
        success_rate = self.successful_decisions / self.total_decisions
        avg_confidence = self.decision_confidence_sum / self.total_decisions
        
        # Analyze by strategy
        strategy_success = defaultdict(lambda: {"successes": 0, "total": 0})
        for decision in self.decision_history:
            if decision.outcome is not None:
                strategy = decision.selected_strategy.value
                strategy_success[strategy]["total"] += 1
                if decision.outcome:
                    strategy_success[strategy]["successes"] += 1
        
        strategy_rates = {
            strategy: data["successes"] / data["total"] if data["total"] > 0 else 0
            for strategy, data in strategy_success.items()
        }
        
        return {
            "total_decisions": self.total_decisions,
            "successful_decisions": self.successful_decisions,
            "success_rate": success_rate,
            "average_confidence": avg_confidence,
            "strategy_success_rates": strategy_rates,
            "decision_trees_built": len(self.decision_tree_builder.trees)
        }
    
    def get_optimal_path(self, error_type: ErrorType, depth: int = 3) -> List[str]:
        """
        Get optimal decision path for error type
        
        Args:
            error_type: Error type
            depth: Maximum path depth
            
        Returns:
            List of decisions forming optimal path
        """
        tree = self.decision_tree_builder.get_tree_for_error(error_type)
        if not tree:
            return []
        
        # Simple traversal to find high-confidence path
        path = [tree.root_node.node_id]
        current = tree.root_node
        
        for _ in range(depth - 1):
            if current.true_child_id and current.true_child_id in tree.nodes:
                next_node = tree.nodes[current.true_child_id]
                path.append(next_node.node_id)
                current = next_node
            else:
                break
        
        return path
    
    def export_decision_state(self) -> Dict[str, Any]:
        """Export complete decision optimization state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "decision_trees": {
                tree.tree_id: tree.to_dict()
                for tree in self.decision_tree_builder.get_all_trees()
            },
            "recent_decisions": [
                d.to_dict() for d in self.decision_history[-100:]
            ],
            "statistics": {
                "total_decisions": self.total_decisions,
                "successful_decisions": self.successful_decisions,
                "success_rate": (
                    self.successful_decisions / self.total_decisions
                    if self.total_decisions > 0 else 0
                ),
                "average_confidence": (
                    self.decision_confidence_sum / self.total_decisions
                    if self.total_decisions > 0 else 0
                )
            },
            "resource_optimizer_stats": self.resource_optimizer.get_stats()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "total_decisions": self.total_decisions,
            "successful_decisions": self.successful_decisions,
            "decision_trees": len(self.decision_tree_builder.trees),
            "resource_optimizations": self.resource_optimizer.total_optimizations,
            "decision_history_size": len(self.decision_history),
            "analysis": self.get_decision_analysis()
        }
