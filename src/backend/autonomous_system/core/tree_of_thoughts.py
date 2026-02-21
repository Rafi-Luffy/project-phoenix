"""
Tree of Thoughts Orchestrator

This module orchestrates multi-path reasoning and parallel decision exploration
using the Tree of Thoughts (ToT) framework.

Based on: Tree of Thoughts (Yao et al., 2023)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import heapq

from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy
from autonomous_system.core.thought_node import (
    ThoughtNode, ThoughtPath, ThoughtType, ThoughtStatus
)
from autonomous_system.core.outcome_prediction import (
    OutcomePredictionEngine, OutcomePrediction
)


@dataclass
class ToTExplorationConfig:
    """Configuration for ToT exploration"""
    max_depth: int = 5
    max_breadth: int = 3  # Max children per node
    max_paths: int = 10   # Max paths to explore
    pruning_threshold: float = 0.4  # Prune paths below this score
    exploration_timeout: float = 5000.0  # milliseconds
    use_parallel: bool = True
    beam_width: int = 3  # For beam search


@dataclass
class ExplorationResult:
    """Result of ToT exploration"""
    best_path: Optional[ThoughtPath] = None
    all_paths: List[ThoughtPath] = field(default_factory=list)
    exploration_time: float = 0.0
    nodes_explored: int = 0
    paths_pruned: int = 0
    
    def best_strategy(self) -> Optional[CorrectionStrategy]:
        """Get best strategy from best path"""
        if self.best_path and self.best_path.strategies:
            return self.best_path.strategies[-1]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "best_path": self.best_path.to_dict() if self.best_path else None,
            "paths_explored": len(self.all_paths),
            "exploration_time": self.exploration_time,
            "nodes_explored": self.nodes_explored,
            "paths_pruned": self.paths_pruned,
            "best_strategy": self.best_strategy().value if self.best_strategy() else None
        }


class TreeOfThoughtsOrchestrator:
    """
    Master orchestrator for Tree of Thoughts reasoning.
    Explores multiple solution paths in parallel.
    """
    
    def __init__(self, config: Optional[ToTExplorationConfig] = None):
        """Initialize ToT orchestrator"""
        self.config = config or ToTExplorationConfig()
        self.prediction_engine = OutcomePredictionEngine()
        
        # Exploration tracking
        self.all_nodes: Dict[str, ThoughtNode] = {}
        self.all_paths: List[ThoughtPath] = []
        self.root_nodes: Dict[str, ThoughtNode] = {}
        
        # Statistics
        self.total_explorations = 0
        self.successful_explorations = 0
        self.exploration_history: List[ExplorationResult] = []
    
    def create_root_node(self, error_type: ErrorType, operation: str, 
                        agent_id: str, content: str = "") -> ThoughtNode:
        """Create root node for exploration"""
        node = ThoughtNode(
            thought_type=ThoughtType.OBSERVATION,
            content=content or f"Error: {error_type.value} in {operation}",
            error_type=error_type,
            operation=operation,
            agent_id=agent_id,
            depth=0,
            status=ThoughtStatus.EXPLORING
        )
        
        self.all_nodes[node.node_id] = node
        key = f"{error_type.value}_{operation}"
        self.root_nodes[key] = node
        
        return node
    
    def create_thought(self, parent: ThoughtNode, thought_type: ThoughtType,
                      content: str, strategy: Optional[CorrectionStrategy] = None,
                      parameters: Optional[Dict[str, Any]] = None) -> ThoughtNode:
        """Create child thought node"""
        node = ThoughtNode(
            thought_type=thought_type,
            content=content,
            error_type=parent.error_type,
            operation=parent.operation,
            agent_id=parent.agent_id,
            depth=parent.depth + 1,
            parent_id=parent.node_id,
            strategy=strategy,
            parameters=parameters or {},
            status=ThoughtStatus.EXPLORING
        )
        
        self.all_nodes[node.node_id] = node
        parent.add_child(node.node_id)
        
        return node
    
    def evaluate_thought(self, node: ThoughtNode, score: float,
                        confidence: float, reasoning: str,
                        feasibility: float = 0.8,
                        efficiency: float = 0.8,
                        reliability: float = 0.8) -> None:
        """Evaluate a thought node"""
        node.evaluate(score, confidence, reasoning, feasibility, efficiency, reliability)
    
    def explore_paths(self, root: ThoughtNode, 
                     candidate_strategies: List[CorrectionStrategy],
                     max_iterations: int = 100) -> ExplorationResult:
        """
        Explore multiple reasoning paths using ToT
        
        Args:
            root: Root node to start exploration
            candidate_strategies: Available strategies to try
            max_iterations: Maximum iterations
            
        Returns:
            ExplorationResult with best path and alternatives
        """
        self.total_explorations += 1
        start_time = datetime.now()
        
        # Initialize
        open_paths: List[Tuple[float, ThoughtPath]] = []
        closed_paths: List[ThoughtPath] = []
        
        # Start with root
        initial_path = ThoughtPath()
        initial_path.add_node(root)
        heapq.heappush(open_paths, (-root.evaluation.score if root.evaluation else -0.5, initial_path))
        
        explored_nodes = 0
        pruned_paths = 0
        
        # Explore
        for iteration in range(max_iterations):
            if not open_paths or len(closed_paths) >= self.config.max_paths:
                break
            
            # Get most promising path
            _, current_path = heapq.heappop(open_paths)
            current_node = current_path.nodes[-1]
            
            # Check depth limit
            if current_path.depth() >= self.config.max_depth:
                current_node.complete()
                closed_paths.append(current_path)
                continue
            
            # Check if should continue exploring
            if not current_node.is_promising():
                current_node.prune("Low score")
                pruned_paths += 1
                continue
            
            # Generate child thoughts
            num_children = min(self.config.max_breadth, len(candidate_strategies))
            for i in range(num_children):
                strategy = candidate_strategies[i % len(candidate_strategies)]
                
                # Create thought for this strategy
                child = self.create_thought(
                    current_node,
                    ThoughtType.STRATEGY,
                    f"Try strategy: {strategy.value}",
                    strategy=strategy
                )
                explored_nodes += 1
                
                # Evaluate with prediction
                prediction = self.prediction_engine.predict_outcome(current_path)
                
                child.evaluate(
                    score=prediction.success_probability,
                    confidence=prediction.confidence,
                    reasoning=prediction.reasoning,
                    feasibility=1.0 - prediction.risk_level,
                    efficiency=1.0 - (prediction.expected_cost / 100.0),
                    reliability=prediction.success_probability
                )
                
                # Create new path
                new_path = ThoughtPath()
                new_path.nodes = current_path.nodes.copy()
                new_path.add_node(child)
                new_path.calculate_metrics()
                
                # Add to open set if promising
                if child.is_promising():
                    heapq.heappush(
                        open_paths,
                        (-child.evaluation.overall_score(), new_path)
                    )
            
            # Current path is complete
            current_node.complete()
            closed_paths.append(current_path)
        
        # Select best path
        best_path = None
        best_score = -1.0
        
        for path in closed_paths:
            if path.is_viable and path.total_score > best_score:
                best_score = path.total_score
                best_path = path
        
        if best_path:
            self.successful_explorations += 1
        
        # Prepare result
        exploration_time = (datetime.now() - start_time).total_seconds() * 1000
        result = ExplorationResult(
            best_path=best_path,
            all_paths=closed_paths,
            exploration_time=exploration_time,
            nodes_explored=explored_nodes,
            paths_pruned=pruned_paths
        )
        
        self.all_paths.extend(closed_paths)
        self.exploration_history.append(result)
        
        return result
    
    def record_execution_outcome(self, path: ThoughtPath, success: bool, 
                                cost: float) -> None:
        """Record outcome of executed path"""
        self.prediction_engine.register_outcome(path, success, cost)
        
        # Update nodes
        for node in path.nodes:
            if node.strategy:
                self.prediction_engine.register_strategy_outcome(
                    node.error_type, node.strategy, success
                )
    
    def get_optimal_sequence(self, root: ThoughtNode) -> List[CorrectionStrategy]:
        """Extract optimal strategy sequence from explored paths"""
        best_strategies = []
        
        for path in self.all_paths:
            if path.nodes and path.nodes[0].node_id == root.node_id:
                if not best_strategies or path.total_score > sum([1]*len(best_strategies)):
                    best_strategies = path.strategies
        
        return best_strategies
    
    def prune_low_confidence_paths(self, threshold: float = 0.3) -> int:
        """Prune paths with low confidence"""
        pruned = 0
        for path in self.all_paths:
            if path.average_confidence < threshold and not path.is_complete:
                path.is_viable = False
                pruned += 1
        return pruned
    
    def get_exploration_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "total_explorations": self.total_explorations,
            "successful_explorations": self.successful_explorations,
            "success_rate": (
                self.successful_explorations / self.total_explorations
                if self.total_explorations > 0 else 0
            ),
            "total_nodes": len(self.all_nodes),
            "total_paths": len(self.all_paths),
            "prediction_accuracy": self.prediction_engine.get_prediction_accuracy(),
            "exploration_history_size": len(self.exploration_history)
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "exploration_stats": self.get_exploration_stats(),
            "total_nodes": len(self.all_nodes),
            "best_paths": [p.to_dict() for p in self.all_paths[:10]],
            "prediction_engine_stats": self.prediction_engine.get_stats(),
            "config": {
                "max_depth": self.config.max_depth,
                "max_breadth": self.config.max_breadth,
                "max_paths": self.config.max_paths,
                "pruning_threshold": self.config.pruning_threshold
            }
        }
