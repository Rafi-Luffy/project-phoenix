"""
Predictive Maintenance Engine

This module anticipates failures before they occur and schedules maintenance.
Uses pattern analysis and trend detection for proactive failure prevention.

Based on: Predictive maintenance and anomaly detection principles
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import statistics

from autonomous_system.core.error_detection import ErrorType


class MaintenanceLevel(Enum):
    """Maintenance urgency levels"""
    NONE = "none"                      # No maintenance needed
    LOW = "low"                        # Can be scheduled
    MEDIUM = "medium"                  # Should be scheduled soon
    HIGH = "high"                      # Must be scheduled immediately
    CRITICAL = "critical"              # Immediate action required


@dataclass
class HealthIndicator:
    """Individual health indicator for a component"""
    name: str
    value: float                       # Current value (0-1, where 1 is healthy)
    trend: float                       # Trend direction (-1 to 1)
    last_check: datetime = field(default_factory=datetime.now)
    historical_values: List[float] = field(default_factory=list)
    
    def is_degrading(self) -> bool:
        """Check if indicator is degrading"""
        return self.trend < -0.1 and self.value < 0.7
    
    def time_to_failure(self) -> Optional[float]:
        """Estimate time to failure in hours"""
        if self.trend >= 0:
            return None  # Not failing
        
        if self.trend == 0:
            return None  # Can't estimate
        
        # Linear extrapolation
        hours_to_failure = abs(self.value / self.trend)
        return max(0, hours_to_failure)


@dataclass
class ComponentHealth:
    """Health status of a system component"""
    component_name: str
    indicators: Dict[str, HealthIndicator] = field(default_factory=dict)
    overall_health: float = 0.8        # Overall health (0-1)
    maintenance_level: MaintenanceLevel = MaintenanceLevel.NONE
    last_maintenance: Optional[datetime] = None
    estimated_failure_time: Optional[float] = None  # hours
    
    def update_health(self) -> None:
        """Update overall health from indicators"""
        if not self.indicators:
            self.overall_health = 0.8
            return
        
        values = [ind.value for ind in self.indicators.values()]
        self.overall_health = statistics.mean(values) if values else 0.8
        
        # Determine maintenance level
        if self.overall_health < 0.3:
            self.maintenance_level = MaintenanceLevel.CRITICAL
        elif self.overall_health < 0.4:
            self.maintenance_level = MaintenanceLevel.HIGH
        elif self.overall_health < 0.6:
            self.maintenance_level = MaintenanceLevel.MEDIUM
        elif self.overall_health < 0.8:
            self.maintenance_level = MaintenanceLevel.LOW
        else:
            self.maintenance_level = MaintenanceLevel.NONE
        
        # Estimate failure time
        failure_times = []
        for indicator in self.indicators.values():
            ftf = indicator.time_to_failure()
            if ftf is not None:
                failure_times.append(ftf)
        
        if failure_times:
            self.estimated_failure_time = min(failure_times)
        else:
            self.estimated_failure_time = None


class PredictiveMaintenanceEngine:
    """
    Predicts component failures and schedules maintenance.
    Uses health indicators and trend analysis.
    """
    
    def __init__(self):
        """Initialize predictive maintenance engine"""
        self.components: Dict[str, ComponentHealth] = {}
        self.error_history: Dict[ErrorType, List[datetime]] = {}
        self.maintenance_recommendations: List[Dict[str, Any]] = []
        
        # Statistics
        self.failures_prevented = 0
        self.maintenance_actions_taken = 0
        self.prediction_accuracy = 0.0
        self.maintenance_window = 24  # hours
    
    def register_component(self, component_name: str) -> None:
        """Register a system component for monitoring"""
        if component_name not in self.components:
            self.components[component_name] = ComponentHealth(component_name)
    
    def add_health_indicator(self, component_name: str, 
                            indicator_name: str,
                            value: float) -> None:
        """Add health indicator for a component"""
        self.register_component(component_name)
        component = self.components[component_name]
        
        if indicator_name not in component.indicators:
            component.indicators[indicator_name] = HealthIndicator(indicator_name, value)
        else:
            indicator = component.indicators[indicator_name]
            indicator.historical_values.append(indicator.value)
            
            # Calculate trend
            if len(indicator.historical_values) >= 2:
                recent = indicator.value
                previous = indicator.historical_values[-1] if indicator.historical_values else indicator.value
                indicator.trend = (recent - previous) / max(previous, 0.01)
            
            indicator.value = value
        
        # Update component health
        component.update_health()
    
    def record_error(self, error_type: ErrorType) -> None:
        """Record error occurrence for analysis"""
        if error_type not in self.error_history:
            self.error_history[error_type] = []
        
        self.error_history[error_type].append(datetime.now())
        
        # Limit history
        if len(self.error_history[error_type]) > 100:
            self.error_history[error_type] = self.error_history[error_type][-100:]
    
    def predict_error_frequency(self, error_type: ErrorType) -> Optional[float]:
        """
        Predict error frequency (errors per hour)
        """
        if error_type not in self.error_history:
            return None
        
        errors = self.error_history[error_type]
        if len(errors) < 2:
            return None
        
        # Calculate frequency
        time_span = (errors[-1] - errors[0]).total_seconds() / 3600  # hours
        if time_span == 0:
            return None
        
        frequency = len(errors) / time_span
        return frequency
    
    def get_maintenance_recommendations(self) -> List[Dict[str, Any]]:
        """Get maintenance recommendations"""
        recommendations = []
        
        for component_name, health in self.components.items():
            if health.maintenance_level.value in ["critical", "high", "medium"]:
                recommendation = {
                    "component": component_name,
                    "level": health.maintenance_level.value,
                    "overall_health": health.overall_health,
                    "timestamp": datetime.now().isoformat(),
                    "estimated_failure_time": health.estimated_failure_time,
                    "recommended_action": self._get_recommended_action(health)
                }
                recommendations.append(recommendation)
        
        self.maintenance_recommendations = recommendations
        return recommendations
    
    def _get_recommended_action(self, health: ComponentHealth) -> str:
        """Get recommended maintenance action"""
        if health.maintenance_level == MaintenanceLevel.CRITICAL:
            return "IMMEDIATE: Stop operations and perform emergency maintenance"
        elif health.maintenance_level == MaintenanceLevel.HIGH:
            return "URGENT: Schedule maintenance within 1 hour"
        elif health.maintenance_level == MaintenanceLevel.MEDIUM:
            return "Schedule maintenance within 24 hours"
        elif health.maintenance_level == MaintenanceLevel.LOW:
            return "Monitor closely, schedule maintenance in next week"
        else:
            return "Continue normal operation"
    
    def perform_maintenance(self, component_name: str) -> bool:
        """
        Perform maintenance on component
        
        Returns:
            True if maintenance successful, False otherwise
        """
        if component_name not in self.components:
            return False
        
        component = self.components[component_name]
        
        # Reset health indicators
        for indicator in component.indicators.values():
            indicator.value = 0.95  # Good health after maintenance
            indicator.historical_values = [indicator.value]
            indicator.trend = 0.0
        
        component.update_health()
        component.last_maintenance = datetime.now()
        
        self.maintenance_actions_taken += 1
        return True
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect health anomalies across system"""
        anomalies = []
        
        for component_name, health in self.components.items():
            for indicator_name, indicator in health.indicators.items():
                if indicator.is_degrading():
                    anomalies.append({
                        "component": component_name,
                        "indicator": indicator_name,
                        "current_value": indicator.value,
                        "trend": indicator.trend,
                        "time_to_failure": indicator.time_to_failure(),
                        "severity": "high" if indicator.value < 0.4 else "medium"
                    })
        
        return anomalies
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        if not self.components:
            return {"status": "no_components", "overall_health": 1.0}
        
        healths = [c.overall_health for c in self.components.values()]
        overall = statistics.mean(healths) if healths else 1.0
        
        critical_components = [c.component_name for c in self.components.values()
                              if c.maintenance_level == MaintenanceLevel.CRITICAL]
        
        return {
            "overall_health": overall,
            "components_monitored": len(self.components),
            "critical_components": critical_components,
            "maintenance_needed": len(self.get_maintenance_recommendations()),
            "anomalies_detected": len(self.detect_anomalies()),
            "failures_prevented": self.failures_prevented
        }
    
    def estimate_maintenance_window(self) -> Optional[timedelta]:
        """Estimate window for maintenance before critical failure"""
        recommendations = self.get_maintenance_recommendations()
        
        if not recommendations:
            return None
        
        critical = [r for r in recommendations if r["level"] == "critical"]
        if critical:
            return timedelta(hours=0.5)  # Immediate
        
        high = [r for r in recommendations if r["level"] == "high"]
        if high:
            min_time = min([r.get("estimated_failure_time", 24) for r in high])
            return timedelta(hours=max(1, min_time - 2))  # 2 hour buffer
        
        return timedelta(hours=24)  # Default 24 hour window
    
    def export_state(self) -> Dict[str, Any]:
        """Export maintenance engine state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "components_monitored": len(self.components),
            "maintenance_actions": self.maintenance_actions_taken,
            "failures_prevented": self.failures_prevented,
            "system_health": self.get_system_health_summary(),
            "maintenance_recommendations": self.get_maintenance_recommendations(),
            "anomalies": self.detect_anomalies(),
            "estimated_maintenance_window": str(self.estimate_maintenance_window())
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get maintenance statistics"""
        return {
            "components_monitored": len(self.components),
            "maintenance_actions_taken": self.maintenance_actions_taken,
            "failures_prevented": self.failures_prevented,
            "prediction_accuracy": self.prediction_accuracy,
            "system_health": statistics.mean([c.overall_health for c in self.components.values()]) if self.components else 1.0,
            "error_types_tracked": len(self.error_history)
        }
