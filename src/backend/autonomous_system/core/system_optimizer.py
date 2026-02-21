"""
System Self-Optimizer

This module implements automatic system parameter tuning and optimization.
The system learns optimal configurations through exploration and feedback.

Based on: Bayesian optimization and AutoML principles
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import statistics

from autonomous_system.core.error_detection import ErrorType


class OptimizationTarget(Enum):
    """Optimization targets for the system"""
    CORRECTION_SPEED = "correction_speed"      # Minimize time to correct
    ACCURACY = "accuracy"                      # Maximize correction success
    EFFICIENCY = "efficiency"                  # Minimize resource usage
    RELIABILITY = "reliability"                # Maximize system uptime
    LEARNING_SPEED = "learning_speed"          # Minimize learning iterations


@dataclass
class ParameterRange:
    """Valid range for an optimizable parameter"""
    name: str
    min_value: float
    max_value: float
    current_value: float
    step_size: float = 0.1
    param_type: str = "float"  # float, int, bool
    description: str = ""


@dataclass
class OptimizationMetrics:
    """Metrics for optimization evaluation"""
    target_metric: float
    secondary_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    parameters_used: Dict[str, float] = field(default_factory=dict)
    iterations_to_convergence: int = 0
    
    def score(self, target: OptimizationTarget) -> float:
        """Calculate overall optimization score"""
        if target == OptimizationTarget.CORRECTION_SPEED:
            return 1.0 / (1.0 + self.target_metric)  # Lower is better
        elif target == OptimizationTarget.ACCURACY:
            return self.target_metric  # Higher is better
        elif target == OptimizationTarget.EFFICIENCY:
            return 1.0 / (1.0 + self.target_metric)  # Lower is better
        elif target == OptimizationTarget.RELIABILITY:
            return self.target_metric  # Higher is better
        elif target == OptimizationTarget.LEARNING_SPEED:
            return 1.0 / (1.0 + self.target_metric)  # Lower is better
        return 0.0


@dataclass
class SystemConfiguration:
    """Complete system configuration snapshot"""
    exploration_max_depth: int = 5
    exploration_max_breadth: int = 3
    exploration_max_paths: int = 10
    pruning_threshold: float = 0.4
    learning_rate: float = 0.1
    error_threshold: float = 0.3
    timeout_threshold: float = 1000.0
    cache_enabled: bool = True
    parallel_enabled: bool = False
    correction_timeout: float = 500.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "exploration_max_depth": self.exploration_max_depth,
            "exploration_max_breadth": self.exploration_max_breadth,
            "exploration_max_paths": self.exploration_max_paths,
            "pruning_threshold": self.pruning_threshold,
            "learning_rate": self.learning_rate,
            "error_threshold": self.error_threshold,
            "timeout_threshold": self.timeout_threshold,
            "cache_enabled": self.cache_enabled,
            "parallel_enabled": self.parallel_enabled,
            "correction_timeout": self.correction_timeout
        }


class SystemOptimizer:
    """
    Automatically tunes system parameters for optimal performance.
    Uses feedback-based optimization to improve system behavior.
    """
    
    def __init__(self, config: Optional[SystemConfiguration] = None):
        """Initialize system optimizer"""
        self.config = config or SystemConfiguration()
        self.parameters: List[ParameterRange] = self._initialize_parameters()
        self.optimization_history: List[OptimizationMetrics] = []
        self.target_metric = OptimizationTarget.ACCURACY
        
        # Per-error-type optimization
        self.error_type_configs: Dict[ErrorType, SystemConfiguration] = {}
        self.error_type_metrics: Dict[ErrorType, List[OptimizationMetrics]] = {}
        
        # Optimization state
        self.total_optimizations = 0
        self.improvements_found = 0
        self.best_score = 0.0
    
    def _initialize_parameters(self) -> List[ParameterRange]:
        """Initialize optimizable parameters"""
        return [
            ParameterRange(
                name="exploration_max_depth",
                min_value=2,
                max_value=10,
                current_value=float(self.config.exploration_max_depth),
                step_size=1.0,
                param_type="int",
                description="Maximum depth for path exploration"
            ),
            ParameterRange(
                name="exploration_max_breadth",
                min_value=1,
                max_value=5,
                current_value=float(self.config.exploration_max_breadth),
                step_size=1.0,
                param_type="int",
                description="Maximum breadth for path exploration"
            ),
            ParameterRange(
                name="pruning_threshold",
                min_value=0.1,
                max_value=0.7,
                current_value=self.config.pruning_threshold,
                step_size=0.05,
                param_type="float",
                description="Threshold for pruning paths"
            ),
            ParameterRange(
                name="learning_rate",
                min_value=0.01,
                max_value=0.5,
                current_value=self.config.learning_rate,
                step_size=0.05,
                param_type="float",
                description="Learning rate for strategy adaptation"
            ),
            ParameterRange(
                name="correction_timeout",
                min_value=100.0,
                max_value=2000.0,
                current_value=self.config.correction_timeout,
                step_size=100.0,
                param_type="float",
                description="Timeout for correction attempts"
            )
        ]
    
    def set_optimization_target(self, target: OptimizationTarget) -> None:
        """Set optimization target"""
        self.target_metric = target
    
    def record_metrics(self, metrics: OptimizationMetrics) -> None:
        """Record optimization metrics"""
        self.total_optimizations += 1
        self.optimization_history.append(metrics)
        
        score = metrics.score(self.target_metric)
        if score > self.best_score:
            self.best_score = score
            self.improvements_found += 1
    
    def record_error_type_metrics(self, error_type: ErrorType, 
                                 metrics: OptimizationMetrics) -> None:
        """Record metrics for specific error type"""
        if error_type not in self.error_type_metrics:
            self.error_type_metrics[error_type] = []
        self.error_type_metrics[error_type].append(metrics)
    
    def optimize_for_error_type(self, error_type: ErrorType,
                               target: OptimizationTarget) -> SystemConfiguration:
        """Get optimized configuration for specific error type"""
        if error_type not in self.error_type_configs:
            # Start with default config
            self.error_type_configs[error_type] = SystemConfiguration()
        
        config = self.error_type_configs[error_type]
        
        # Get metrics for this error type
        if error_type in self.error_type_metrics:
            metrics_list = self.error_type_metrics[error_type]
            if metrics_list:
                # Find best configuration for this error type
                best_metrics = max(metrics_list, key=lambda m: m.score(target))
                # Apply parameters from best metrics
                if best_metrics.parameters_used:
                    self._apply_parameters(config, best_metrics.parameters_used)
        
        return config
    
    def suggest_adjustments(self, current_performance: float,
                          target_performance: float) -> Dict[str, float]:
        """
        Suggest parameter adjustments based on performance gap
        
        Args:
            current_performance: Current metric value
            target_performance: Desired metric value
            
        Returns:
            Dictionary of suggested adjustments
        """
        adjustments = {}
        performance_gap = target_performance - current_performance
        
        if performance_gap > 0:
            # Need improvement - suggest exploration increase
            if self.config.exploration_max_depth < 10:
                adjustments["exploration_max_depth"] = min(10, self.config.exploration_max_depth + 1)
            if self.config.exploration_max_breadth < 5:
                adjustments["exploration_max_breadth"] = min(5, self.config.exploration_max_breadth + 1)
            if self.config.learning_rate < 0.5:
                adjustments["learning_rate"] = min(0.5, self.config.learning_rate + 0.05)
        else:
            # Good performance - suggest refinement
            if self.config.pruning_threshold < 0.7:
                adjustments["pruning_threshold"] = min(0.7, self.config.pruning_threshold + 0.05)
            if self.config.correction_timeout > 100:
                adjustments["correction_timeout"] = max(100, self.config.correction_timeout - 50)
        
        return adjustments
    
    def apply_adjustments(self, adjustments: Dict[str, float]) -> None:
        """Apply suggested adjustments to configuration"""
        for param_name, value in adjustments.items():
            if hasattr(self.config, param_name):
                setattr(self.config, param_name, value)
            
            # Update parameter range
            for param in self.parameters:
                if param.name == param_name:
                    param.current_value = value
                    break
    
    def _apply_parameters(self, config: SystemConfiguration,
                         parameters: Dict[str, float]) -> None:
        """Apply parameters to configuration"""
        for param_name, value in parameters.items():
            if hasattr(config, param_name):
                setattr(config, param_name, value)
    
    def get_parameter_sensitivity(self) -> Dict[str, float]:
        """
        Calculate sensitivity of each parameter to performance change.
        Higher sensitivity = parameter has more impact on performance
        """
        if len(self.optimization_history) < 3:
            return {}
        
        sensitivity = {}
        
        for param in self.parameters:
            # Group metrics by parameter value
            param_groups: Dict[float, List[float]] = {}
            
            for metrics in self.optimization_history:
                if param.name in metrics.parameters_used:
                    param_value = metrics.parameters_used[param.name]
                    score = metrics.score(self.target_metric)
                    
                    if param_value not in param_groups:
                        param_groups[param_value] = []
                    param_groups[param_value].append(score)
            
            # Calculate sensitivity as variance across parameter values
            if len(param_groups) > 1:
                means = [statistics.mean(scores) for scores in param_groups.values()]
                if len(means) > 1:
                    sensitivity[param.name] = statistics.stdev(means)
        
        return sensitivity
    
    def get_convergence_progress(self) -> float:
        """Get convergence progress (0-1)"""
        if len(self.optimization_history) < 2:
            return 0.0
        
        recent_scores = [m.score(self.target_metric) 
                        for m in self.optimization_history[-10:]]
        
        if len(recent_scores) < 2:
            return 0.0
        
        # Convergence is lower variance = higher convergence
        variance = statistics.variance(recent_scores) if len(recent_scores) > 1 else 0
        return 1.0 - min(1.0, variance * 2)  # Scale variance to 0-1
    
    def export_state(self) -> Dict[str, Any]:
        """Export optimizer state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_optimizations": self.total_optimizations,
            "improvements_found": self.improvements_found,
            "best_score": self.best_score,
            "target_metric": self.target_metric.value,
            "convergence_progress": self.get_convergence_progress(),
            "parameter_sensitivity": self.get_parameter_sensitivity(),
            "current_config": self.config.to_dict(),
            "optimization_history_size": len(self.optimization_history)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        if not self.optimization_history:
            return {
                "total_optimizations": 0,
                "improvements_found": 0,
                "best_score": 0.0,
                "improvement_rate": 0.0
            }
        
        scores = [m.score(self.target_metric) for m in self.optimization_history]
        
        return {
            "total_optimizations": self.total_optimizations,
            "improvements_found": self.improvements_found,
            "best_score": self.best_score,
            "average_score": statistics.mean(scores),
            "improvement_rate": (self.improvements_found / self.total_optimizations) if self.total_optimizations > 0 else 0,
            "convergence_progress": self.get_convergence_progress(),
            "error_type_specializations": len(self.error_type_configs)
        }
