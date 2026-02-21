"""
Thought Node - Building block for Tree of Thoughts

This module implements individual thought nodes that represent reasoning steps,
decision points, and strategy selections in a multi-path exploration framework.

Based on: Tree of Thoughts (Yao et al., 2023)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import uuid

from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy


class ThoughtType(Enum):
    """Types of thoughts in reasoning chain"""
    OBSERVATION = "observation"        # Initial observation
    REASONING = "reasoning"            # Intermediate reasoning
    ANALYSIS = "analysis"              # Deep analysis
    DECISION = "decision"              # Decision point
    STRATEGY = "strategy"              # Strategy selection
    EVALUATION = "evaluation"          # Evaluation of path
    OUTCOME = "outcome"                # Final outcome


class ThoughtStatus(Enum):
    """Status of a thought"""
    PENDING = "pending"                # Not yet evaluated
    EXPLORING = "exploring"            # Currently exploring
    EVALUATED = "evaluated"            # Has been evaluated
    PRUNED = "pruned"                  # Pruned from search
    COMPLETE = "complete"              # Complete/terminal


@dataclass
class Evaluation:
    """Evaluation of a thought/path"""
    score: float                        # Overall score (0-1)
    confidence: float                  # Confidence level
    reasoning: str                     # Why this score
    feasibility: float = 0.8           # Feasibility score
    efficiency: float = 0.8            # Efficiency score
    reliability: float = 0.8           # Reliability score
    timestamp: datetime = field(default_factory=datetime.now)
    
    def overall_score(self) -> float:
        """Calculate weighted overall score"""
        return (
            self.feasibility * 0.4 +
            self.efficiency * 0.3 +
            self.reliability * 0.3
        )


@dataclass
class ThoughtNode:
    """A node in the Tree of Thoughts"""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    thought_type: ThoughtType = ThoughtType.REASONING
    content: str = ""                  # Thought content/description
    
    # Context
    error_type: Optional[ErrorType] = None
    operation: str = ""
    agent_id: str = ""
    
    # Path information
    depth: int = 0
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    
    # Strategy information
    strategy: Optional[CorrectionStrategy] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Evaluation
    status: ThoughtStatus = ThoughtStatus.PENDING
    evaluation: Optional[Evaluation] = None
    intermediate_steps: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_terminal(self) -> bool:
        """Check if node is terminal (leaf)"""
        return len(self.children_ids) == 0 and self.status == ThoughtStatus.COMPLETE
    
    def is_promising(self) -> bool:
        """Check if node is promising enough to explore further"""
        if self.evaluation is None:
            return True
        return self.evaluation.score >= 0.5 and self.evaluation.confidence >= 0.4
    
    def add_child(self, child_id: str) -> None:
        """Add child node"""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)
    
    def add_step(self, step: str) -> None:
        """Add intermediate reasoning step"""
        self.intermediate_steps.append(step)
        self.updated_at = datetime.now()
    
    def evaluate(self, score: float, confidence: float, reasoning: str,
                feasibility: float = 0.8, efficiency: float = 0.8,
                reliability: float = 0.8) -> None:
        """Evaluate this thought"""
        self.evaluation = Evaluation(
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            feasibility=feasibility,
            efficiency=efficiency,
            reliability=reliability
        )
        self.status = ThoughtStatus.EVALUATED
        self.updated_at = datetime.now()
    
    def prune(self, reason: str = "") -> None:
        """Mark as pruned"""
        self.status = ThoughtStatus.PRUNED
        if reason:
            self.metadata["prune_reason"] = reason
        self.updated_at = datetime.now()
    
    def complete(self) -> None:
        """Mark as complete"""
        self.status = ThoughtStatus.COMPLETE
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.node_id,
            "type": self.thought_type.value,
            "content": self.content,
            "status": self.status.value,
            "depth": self.depth,
            "strategy": self.strategy.value if self.strategy else None,
            "score": self.evaluation.score if self.evaluation else 0.0,
            "confidence": self.evaluation.confidence if self.evaluation else 0.0,
            "children": len(self.children_ids),
            "created": self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """String representation"""
        score = f"(score: {self.evaluation.score:.2f})" if self.evaluation else ""
        return f"ThoughtNode({self.node_id}, {self.thought_type.value} {score})"


@dataclass
class ThoughtPath:
    """A complete reasoning path from root to leaf"""
    path_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    nodes: List[ThoughtNode] = field(default_factory=list)
    strategies: List[CorrectionStrategy] = field(default_factory=list)
    
    # Path metrics
    total_score: float = 0.0
    average_confidence: float = 0.0
    feasibility: float = 0.0
    
    # Status
    is_complete: bool = False
    is_viable: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    exploration_time: float = 0.0
    
    def add_node(self, node: ThoughtNode) -> None:
        """Add node to path"""
        self.nodes.append(node)
        if node.strategy and node.strategy not in self.strategies:
            self.strategies.append(node.strategy)
    
    def calculate_metrics(self) -> None:
        """Calculate path metrics"""
        if not self.nodes:
            return
        
        scores = [n.evaluation.score for n in self.nodes if n.evaluation]
        confidences = [n.evaluation.confidence for n in self.nodes if n.evaluation]
        
        if scores:
            self.total_score = sum(scores)
            self.average_confidence = sum(confidences) / len(confidences)
            self.feasibility = min([n.evaluation.feasibility for n in self.nodes if n.evaluation])
    
    def depth(self) -> int:
        """Get path depth"""
        return len(self.nodes)
    
    def is_promising(self) -> bool:
        """Check if path is promising"""
        if not self.nodes:
            return True
        
        terminal = self.nodes[-1]
        return terminal.is_promising() and self.is_viable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.path_id,
            "depth": self.depth(),
            "nodes": [n.node_id for n in self.nodes],
            "strategies": [s.value for s in self.strategies],
            "score": self.total_score,
            "confidence": self.average_confidence,
            "feasibility": self.feasibility,
            "viable": self.is_viable,
            "complete": self.is_complete
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ThoughtPath({self.path_id}, depth={self.depth()}, score={self.total_score:.2f})"
