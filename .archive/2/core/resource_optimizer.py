"""
Resource Optimization Engine for Decision Optimization

This module optimizes resource allocation based on learned patterns and strategy performance.
Analyzes execution costs and selects optimal strategies for resource constraints.

Based on: Self-Refine framework for resource optimization
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict

from autonomous_system.core.correction_strategy import CorrectionStrategy
from autonomous_system.core.error_detection import ErrorType


class ResourceType(Enum):
    """Types of resources to optimize"""
    CPU = "cpu"                    # CPU time (milliseconds)
    MEMORY = "memory"              # Memory usage (MB)
    NETWORK = "network"            # Network bandwidth (KB)
    DISK_IO = "disk_io"            # Disk I/O (operations)
    TIMEOUT = "timeout"            # Execution timeout (seconds)


@dataclass
class ResourceCost:
    """Cost of executing a strategy"""
    strategy: CorrectionStrategy
    error_type: ErrorType
    
    cpu_cost: float = 0.0          # Milliseconds
    memory_cost: float = 0.0       # MB
    network_cost: float = 0.0      # KB
    disk_io_cost: float = 0.0      # Operations
    timeout_cost: float = 0.0      # Seconds
    
    success_probability: float = 0.7
    avg_execution_time: float = 0.0
    
    def total_cost(self) -> float:
        """Calculate weighted total cost"""
        # Normalize and weight costs
        cpu_weight = self.cpu_cost / 1000.0 if self.cpu_cost > 0 else 0
        memory_weight = self.memory_cost / 100.0 if self.memory_cost > 0 else 0
        network_weight = self.network_cost / 1000.0 if self.network_cost > 0 else 0
        disk_weight = self.disk_io_cost / 100.0 if self.disk_io_cost > 0 else 0
        
        # Weighted sum
        total = (cpu_weight * 0.3 + memory_weight * 0.2 + 
                network_weight * 0.2 + disk_weight * 0.2)
        
        return total
    
    def cost_per_success(self) -> float:
        """Calculate cost normalized by success probability"""
        if self.success_probability == 0:
            return float('inf')
        return self.total_cost() / self.success_probability
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy": self.strategy.value,
            "error_type": self.error_type.value,
            "cpu_cost": self.cpu_cost,
            "memory_cost": self.memory_cost,
            "network_cost": self.network_cost,
            "disk_io_cost": self.disk_io_cost,
            "success_probability": self.success_probability,
            "total_cost": self.total_cost(),
            "cost_per_success": self.cost_per_success()
        }


@dataclass
class ResourceBudget:
    """Resource constraints"""
    max_cpu_ms: float = float('inf')
    max_memory_mb: float = float('inf')
    max_network_kb: float = float('inf')
    max_disk_io: float = float('inf')
    max_timeout_seconds: float = float('inf')
    
    def check_constraint(self, cost: ResourceCost) -> bool:
        """Check if cost fits within budget"""
        return (cost.cpu_cost <= self.max_cpu_ms and
                cost.memory_cost <= self.max_memory_mb and
                cost.network_cost <= self.max_network_kb and
                cost.disk_io_cost <= self.max_disk_io and
                cost.timeout_cost <= self.max_timeout_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "max_cpu_ms": self.max_cpu_ms,
            "max_memory_mb": self.max_memory_mb,
            "max_network_kb": self.max_network_kb,
            "max_disk_io": self.max_disk_io,
            "max_timeout_seconds": self.max_timeout_seconds
        }


@dataclass
class OptimizationResult:
    """Result of resource optimization"""
    selected_strategy: CorrectionStrategy
    cost: ResourceCost
    alternatives: List[Tuple[CorrectionStrategy, ResourceCost]]
    savings: float  # Cost saved vs. baseline
    efficiency_improvement: float  # % improvement
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "selected_strategy": self.selected_strategy.value,
            "cost": self.cost.to_dict(),
            "savings": self.savings,
            "efficiency_improvement": self.efficiency_improvement,
            "reasoning": self.reasoning
        }


class ResourceOptimizationEngine:
    """
    Optimizes strategy selection based on resource costs and constraints.
    Selects most efficient strategy within budget.
    """
    
    def __init__(self):
        """Initialize resource optimization engine"""
        self.resource_costs: Dict[str, ResourceCost] = {}
        self.optimization_history: List[OptimizationResult] = []
        self.total_optimizations = 0
    
    def register_strategy_cost(self, cost: ResourceCost) -> None:
        """Register cost profile for strategy-error combination"""
        key = f"{cost.strategy.value}_{cost.error_type.value}"
        self.resource_costs[key] = cost
    
    def optimize_strategy_selection(self, 
                                   error_type: ErrorType,
                                   available_strategies: List[CorrectionStrategy],
                                   budget: Optional[ResourceBudget] = None) -> OptimizationResult:
        """
        Select optimal strategy within resource constraints
        
        Args:
            error_type: Type of error
            available_strategies: Candidate strategies
            budget: Resource budget constraints
            
        Returns:
            Optimization result with selected strategy
        """
        self.total_optimizations += 1
        
        if not budget:
            budget = ResourceBudget()  # Unlimited
        
        # Get costs for all strategies
        strategy_costs = []
        for strategy in available_strategies:
            key = f"{strategy.value}_{error_type.value}"
            if key in self.resource_costs:
                cost = self.resource_costs[key]
                strategy_costs.append((strategy, cost))
        
        if not strategy_costs:
            # Return default if no costs registered
            default_cost = ResourceCost(strategy=available_strategies[0], error_type=error_type)
            return OptimizationResult(
                selected_strategy=available_strategies[0],
                cost=default_cost,
                alternatives=[],
                savings=0.0,
                efficiency_improvement=0.0,
                reasoning="No cost data available"
            )
        
        # Filter by budget constraints
        feasible_strategies = [
            (s, c) for s, c in strategy_costs
            if budget.check_constraint(c)
        ]
        
        if not feasible_strategies:
            # Find least expensive even if over budget
            feasible_strategies = strategy_costs
        
        # Sort by cost-per-success ratio
        feasible_strategies.sort(key=lambda x: x[1].cost_per_success())
        
        selected_strategy, selected_cost = feasible_strategies[0]
        
        # Calculate alternatives (next 2 best)
        alternatives = [
            (s, c) for s, c in feasible_strategies[1:3]
        ]
        
        # Calculate savings vs. worst option
        worst_cost = max(c.total_cost() for _, c in feasible_strategies)
        savings = worst_cost - selected_cost.total_cost()
        efficiency_improvement = (savings / worst_cost) * 100 if worst_cost > 0 else 0
        
        reasoning = self._generate_optimization_reasoning(
            selected_strategy, selected_cost, feasible_strategies
        )
        
        result = OptimizationResult(
            selected_strategy=selected_strategy,
            cost=selected_cost,
            alternatives=alternatives,
            savings=savings,
            efficiency_improvement=efficiency_improvement,
            reasoning=reasoning
        )
        
        self.optimization_history.append(result)
        return result
    
    def _generate_optimization_reasoning(self,
                                       selected: CorrectionStrategy,
                                       cost: ResourceCost,
                                       options: List[Tuple[CorrectionStrategy, ResourceCost]]) -> str:
        """Generate human-readable reasoning"""
        if len(options) == 1:
            return f"Only available option: {selected.value}"
        
        cost_per_success = cost.cost_per_success()
        return (
            f"Selected {selected.value} with cost/success ratio of {cost_per_success:.2f}. "
            f"Success probability: {cost.success_probability:.0%}. "
            f"Total cost: {cost.total_cost():.2f} (CPU: {cost.cpu_cost:.0f}ms, "
            f"Memory: {cost.memory_cost:.0f}MB)"
        )
    
    def optimize_for_constraint(self,
                               error_type: ErrorType,
                               available_strategies: List[CorrectionStrategy],
                               constraint_type: ResourceType,
                               constraint_value: float) -> OptimizationResult:
        """
        Optimize for specific resource constraint
        
        Args:
            error_type: Type of error
            available_strategies: Candidate strategies
            constraint_type: Which resource to constrain
            constraint_value: Maximum allowed value
            
        Returns:
            Optimization result
        """
        budget = ResourceBudget()
        
        if constraint_type == ResourceType.CPU:
            budget.max_cpu_ms = constraint_value
        elif constraint_type == ResourceType.MEMORY:
            budget.max_memory_mb = constraint_value
        elif constraint_type == ResourceType.NETWORK:
            budget.max_network_kb = constraint_value
        elif constraint_type == ResourceType.DISK_IO:
            budget.max_disk_io = constraint_value
        elif constraint_type == ResourceType.TIMEOUT:
            budget.max_timeout_seconds = constraint_value
        
        return self.optimize_strategy_selection(error_type, available_strategies, budget)
    
    def get_cost_analysis(self, error_type: ErrorType) -> Dict[str, Any]:
        """Get cost analysis for error type"""
        type_costs = [
            c for c in self.resource_costs.values()
            if c.error_type == error_type
        ]
        
        if not type_costs:
            return {"error_type": error_type.value, "strategies": {}}
        
        return {
            "error_type": error_type.value,
            "strategies": {
                c.strategy.value: c.to_dict()
                for c in type_costs
            },
            "most_efficient": min(type_costs, key=lambda c: c.cost_per_success()).strategy.value,
            "cheapest": min(type_costs, key=lambda c: c.total_cost()).strategy.value,
            "highest_success_rate": max(type_costs, key=lambda c: c.success_probability).strategy.value
        }
    
    def get_optimization_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent optimization history"""
        return [r.to_dict() for r in self.optimization_history[-limit:]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimization engine statistics"""
        if not self.optimization_history:
            return {
                "total_optimizations": self.total_optimizations,
                "average_savings": 0.0,
                "average_efficiency_improvement": 0.0
            }
        
        avg_savings = sum(r.savings for r in self.optimization_history) / len(self.optimization_history)
        avg_improvement = sum(r.efficiency_improvement for r in self.optimization_history) / len(self.optimization_history)
        
        return {
            "total_optimizations": self.total_optimizations,
            "optimizations_performed": len(self.optimization_history),
            "average_savings": avg_savings,
            "average_efficiency_improvement": avg_improvement,
            "registered_costs": len(self.resource_costs)
        }
