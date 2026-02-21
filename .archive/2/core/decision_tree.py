"""
Decision Tree Engine for Decision Optimization

This module generates decision trees from learned knowledge rules and patterns.
Provides efficient decision path selection based on error context.

Based on: Self-Refine framework for decision optimization
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
import json

from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy


class DecisionNodeType(Enum):
    """Types of decision nodes"""
    ROOT = "root"                  # Entry point
    CONDITION = "condition"        # Test condition
    ACTION = "action"              # Execute action
    STRATEGY = "strategy"          # Select strategy
    LEAF = "leaf"                  # Terminal node


@dataclass
class DecisionCondition:
    """A condition in a decision tree"""
    attribute: str                  # What to test (e.g., "error_type", "execution_time")
    operator: str                   # Comparison operator (>, <, ==, contains, etc.)
    value: Any                      # Value to compare against
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context"""
        if attribute not in context:
            return False
        
        context_value = context[self.attribute]
        
        if self.operator == "==":
            return context_value == self.value
        elif self.operator == ">":
            return context_value > self.value
        elif self.operator == "<":
            return context_value < self.value
        elif self.operator == ">=":
            return context_value >= self.value
        elif self.operator == "<=":
            return context_value <= self.value
        elif self.operator == "in":
            return context_value in self.value
        elif self.operator == "contains":
            return self.value in str(context_value)
        
        return False


@dataclass
class DecisionNode:
    """Node in a decision tree"""
    node_id: str
    node_type: DecisionNodeType
    name: str
    description: str = ""
    
    # For condition nodes
    condition: Optional[DecisionCondition] = None
    true_child_id: Optional[str] = None
    false_child_id: Optional[str] = None
    
    # For action/strategy nodes
    action: Optional[str] = None
    strategy: Optional[CorrectionStrategy] = None
    expected_outcome: Optional[str] = None
    confidence: float = 0.0
    success_rate: float = 0.0
    
    # Metadata
    rule_id: Optional[str] = None  # Source rule
    depth: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.node_id,
            "type": self.node_type.value,
            "name": self.name,
            "description": self.description,
            "condition": {
                "attribute": self.condition.attribute,
                "operator": self.condition.operator,
                "value": self.condition.value
            } if self.condition else None,
            "strategy": self.strategy.value if self.strategy else None,
            "confidence": self.confidence,
            "success_rate": self.success_rate,
            "depth": self.depth
        }


class DecisionTree:
    """A decision tree for strategy selection"""
    
    def __init__(self, tree_id: str, error_type: ErrorType, root_node: DecisionNode):
        """
        Initialize decision tree
        
        Args:
            tree_id: Unique tree identifier
            error_type: Error type this tree handles
            root_node: Root node of the tree
        """
        self.tree_id = tree_id
        self.error_type = error_type
        self.root_node = root_node
        
        self.nodes: Dict[str, DecisionNode] = {root_node.node_id: root_node}
        self.decision_count = 0
        self.success_count = 0
        self.creation_time = datetime.now()
    
    def add_node(self, node: DecisionNode, parent_id: Optional[str] = None, 
                 on_true: bool = True) -> None:
        """Add node to tree"""
        self.nodes[node.node_id] = node
        
        if parent_id and parent_id in self.nodes:
            parent = self.nodes[parent_id]
            if on_true:
                parent.true_child_id = node.node_id
            else:
                parent.false_child_id = node.node_id
    
    def traverse(self, context: Dict[str, Any]) -> Optional[DecisionNode]:
        """
        Traverse tree to find decision node
        
        Args:
            context: Context information for evaluation
            
        Returns:
            Terminal decision node or None
        """
        current = self.root_node
        self.decision_count += 1
        
        while current.node_type == DecisionNodeType.CONDITION:
            if not current.condition:
                return current
            
            if current.condition.evaluate(context):
                if current.true_child_id and current.true_child_id in self.nodes:
                    current = self.nodes[current.true_child_id]
                else:
                    break
            else:
                if current.false_child_id and current.false_child_id in self.nodes:
                    current = self.nodes[current.false_child_id]
                else:
                    break
        
        return current
    
    def record_decision_outcome(self, success: bool) -> None:
        """Record outcome of decision"""
        if success:
            self.success_count += 1
    
    @property
    def success_rate(self) -> float:
        """Get success rate of this tree"""
        if self.decision_count == 0:
            return 0.0
        return self.success_count / self.decision_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tree to dictionary"""
        return {
            "id": self.tree_id,
            "error_type": self.error_type.value,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "success_rate": self.success_rate,
            "decisions_made": self.decision_count
        }


class DecisionTreeBuilder:
    """Builds decision trees from knowledge rules"""
    
    def __init__(self):
        """Initialize decision tree builder"""
        self.trees: Dict[str, DecisionTree] = {}
        self.total_trees_built = 0
    
    def build_tree_from_rules(self, error_type: ErrorType, 
                             rules: List[Dict[str, Any]]) -> DecisionTree:
        """
        Build decision tree from knowledge rules
        
        Args:
            error_type: Error type to build tree for
            rules: List of knowledge rules
            
        Returns:
            Decision tree for error type
        """
        tree_id = f"tree_{error_type.value}_{len(self.trees)}"
        
        # Create root node
        root = DecisionNode(
            node_id=f"{tree_id}_root",
            node_type=DecisionNodeType.ROOT,
            name=f"Decision Tree: {error_type.value}",
            description=f"Optimized decision tree for {error_type.value} errors"
        )
        
        tree = DecisionTree(tree_id, error_type, root)
        
        # Build tree from rules (simple breadth-first)
        if rules:
            # Sort rules by priority
            sorted_rules = sorted(rules, key=lambda r: r.get("priority", 50), reverse=True)
            
            current_parent_id = root.node_id
            for i, rule in enumerate(sorted_rules[:5]):  # Top 5 rules
                # Create strategy node
                strategy_name = rule.get("action", "ESCALATE")
                strategy_id = f"{tree_id}_strategy_{i}"
                
                strategy_node = DecisionNode(
                    node_id=strategy_id,
                    node_type=DecisionNodeType.STRATEGY,
                    name=f"Strategy: {strategy_name}",
                    description=rule.get("description", ""),
                    action=rule.get("action"),
                    strategy=self._parse_strategy(strategy_name),
                    confidence=rule.get("confidence", 0.7),
                    success_rate=rule.get("success_rate", 0.7),
                    rule_id=rule.get("id"),
                    depth=1
                )
                
                tree.add_node(strategy_node, current_parent_id, on_true=True)
        
        self.trees[tree_id] = tree
        self.total_trees_built += 1
        
        return tree
    
    def _parse_strategy(self, strategy_name: str) -> Optional[CorrectionStrategy]:
        """Parse strategy name to enum"""
        try:
            # Convert name to strategy enum
            if "retry" in strategy_name.lower():
                return CorrectionStrategy.RETRY
            elif "fallback" in strategy_name.lower():
                return CorrectionStrategy.FALLBACK
            elif "skip" in strategy_name.lower():
                return CorrectionStrategy.SKIP
            elif "rollback" in strategy_name.lower():
                return CorrectionStrategy.ROLLBACK
            elif "cache" in strategy_name.lower():
                return CorrectionStrategy.CACHE
            elif "escalate" in strategy_name.lower():
                return CorrectionStrategy.ESCALATE
            else:
                return CorrectionStrategy.ESCALATE
        except:
            return None
    
    def get_tree_for_error(self, error_type: ErrorType) -> Optional[DecisionTree]:
        """Get existing tree for error type"""
        for tree in self.trees.values():
            if tree.error_type == error_type:
                return tree
        return None
    
    def get_all_trees(self) -> List[DecisionTree]:
        """Get all built trees"""
        return list(self.trees.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get builder statistics"""
        return {
            "total_trees_built": self.total_trees_built,
            "active_trees": len(self.trees),
            "average_tree_success_rate": (
                sum(t.success_rate for t in self.trees.values()) / len(self.trees)
                if self.trees else 0.0
            ),
            "total_decisions_made": sum(t.decision_count for t in self.trees.values())
        }
