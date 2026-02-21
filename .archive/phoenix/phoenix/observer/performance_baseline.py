"""
Performance Baseline Tracker

Measures agent performance before and after fixes.
Tracks: execution speed, success rates, resource usage, error frequency.

Optional module - enables performance analytics without disrupting healing.
Uses only standard library (json) - no external dependencies needed.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentPerformanceSnapshot:
    """Single point-in-time performance measurement."""
    timestamp: str
    agent_name: str
    execution_time_ms: float
    success_count: int
    failure_count: int
    success_rate: float
    error_frequency: float  # errors per hour
    avg_recovery_time_ms: float
    memory_usage_mb: float


@dataclass
class PerformanceComparison:
    """Before/after performance metrics."""
    agent_name: str
    before: AgentPerformanceSnapshot
    after: AgentPerformanceSnapshot
    improvement_percent: float
    metrics_changed: Dict[str, Dict[str, float]]


class PerformanceBaselineTracker:
    """
    Tracks agent performance before and after fixes.
    
    Helps you see if your autonomous fixes are actually helping.
    """
    
    def __init__(self, storage_path: str = "./phoenix_performance.json"):
        """
        Initialize tracker.
        
        Args:
            storage_path: Where to save baseline data
        """
        self.storage_path = storage_path
        self.snapshots: Dict[str, List[AgentPerformanceSnapshot]] = {}
        self.logger = get_logger(__name__)
        self._load_existing_data()
    
    def record_baseline(
        self,
        agent_name: str,
        execution_time_ms: float,
        success_count: int,
        failure_count: int,
        error_frequency: float,
        avg_recovery_time_ms: float,
        memory_usage_mb: float,
    ) -> AgentPerformanceSnapshot:
        """
        Record pre-fix baseline for an agent.
        
        Args:
            agent_name: Name of the agent
            execution_time_ms: Avg execution time in ms
            success_count: Number of successful runs
            failure_count: Number of failed runs
            error_frequency: Errors per hour
            avg_recovery_time_ms: Avg time to recover from error
            memory_usage_mb: Memory usage in MB
        
        Returns:
            AgentPerformanceSnapshot
        """
        total = success_count + failure_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        snapshot = AgentPerformanceSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            agent_name=agent_name,
            execution_time_ms=execution_time_ms,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            error_frequency=error_frequency,
            avg_recovery_time_ms=avg_recovery_time_ms,
            memory_usage_mb=memory_usage_mb,
        )
        
        if agent_name not in self.snapshots:
            self.snapshots[agent_name] = []
        
        self.snapshots[agent_name].append(snapshot)
        self._save_data()
        
        self.logger.info("baseline_recorded", agent=agent_name)
        return snapshot
    
    def record_post_fix_metrics(
        self,
        agent_name: str,
        execution_time_ms: float,
        success_count: int,
        failure_count: int,
        error_frequency: float,
        avg_recovery_time_ms: float,
        memory_usage_mb: float,
    ) -> PerformanceComparison:
        """
        Record post-fix metrics and compare to baseline.
        
        Args:
            agent_name: Name of the agent
            execution_time_ms: New execution time
            success_count: Total successes
            failure_count: Total failures
            error_frequency: New error frequency
            avg_recovery_time_ms: New recovery time
            memory_usage_mb: New memory usage
        
        Returns:
            PerformanceComparison
        """
        after = self.record_baseline(
            agent_name=agent_name,
            execution_time_ms=execution_time_ms,
            success_count=success_count,
            failure_count=failure_count,
            error_frequency=error_frequency,
            avg_recovery_time_ms=avg_recovery_time_ms,
            memory_usage_mb=memory_usage_mb,
        )
        
        # Get the baseline (most recent one before this)
        if len(self.snapshots.get(agent_name, [])) < 2:
            return PerformanceComparison(
                baseline_metrics={},
                current_metrics={},
                improvements={},
                degradations={},
                comparison_time=datetime.now()
            )
        
        before = self.snapshots[agent_name][-2]
        
        # Calculate improvements
        metrics_changed = {
            "execution_time": {
                "before": before.execution_time_ms,
                "after": after.execution_time_ms,
                "change_percent": self._percent_change(
                    before.execution_time_ms,
                    after.execution_time_ms,
                ),
            },
            "success_rate": {
                "before": before.success_rate,
                "after": after.success_rate,
                "change_percent": after.success_rate - before.success_rate,
            },
            "error_frequency": {
                "before": before.error_frequency,
                "after": after.error_frequency,
                "change_percent": self._percent_change(
                    before.error_frequency,
                    after.error_frequency,
                ),
            },
            "recovery_time": {
                "before": before.avg_recovery_time_ms,
                "after": after.avg_recovery_time_ms,
                "change_percent": self._percent_change(
                    before.avg_recovery_time_ms,
                    after.avg_recovery_time_ms,
                ),
            },
            "memory_usage": {
                "before": before.memory_usage_mb,
                "after": after.memory_usage_mb,
                "change_percent": self._percent_change(
                    before.memory_usage_mb,
                    after.memory_usage_mb,
                ),
            },
        }
        
        # Overall improvement (weighted average of improvements)
        improvements = [
            metrics_changed["execution_time"]["change_percent"],  # Faster is better
            metrics_changed["success_rate"]["change_percent"],  # Higher is better
            -metrics_changed["error_frequency"]["change_percent"],  # Lower is better
            -metrics_changed["recovery_time"]["change_percent"],  # Lower is better
            -metrics_changed["memory_usage"]["change_percent"],  # Lower is better
        ]
        
        overall_improvement = sum(improvements) / len(improvements)
        
        comparison = PerformanceComparison(
            agent_name=agent_name,
            before=before,
            after=after,
            improvement_percent=overall_improvement,
            metrics_changed=metrics_changed,
        )
        
        self.logger.info(
            "performance_compared",
            agent=agent_name,
            improvement=overall_improvement,
        )
        
        return comparison
    
    def get_agent_improvement(self, agent_name: str) -> Optional[float]:
        """Get overall improvement percentage for an agent."""
        if agent_name not in self.snapshots or len(self.snapshots[agent_name]) < 2:
            return None
        
        snapshots = self.snapshots[agent_name]
        first = snapshots[0]
        latest = snapshots[-1]
        
        # Simple metric: success rate improvement
        return latest.success_rate - first.success_rate
    
    def get_best_performing_agents(self, top_n: int = 5) -> List[str]:
        """Get agents with best improvement."""
        improvements = []
        
        for agent_name in self.snapshots:
            improvement = self.get_agent_improvement(agent_name)
            if improvement is not None:
                improvements.append((agent_name, improvement))
        
        improvements.sort(key=lambda x: x[1], reverse=True)
        return [agent for agent, _ in improvements[:top_n]]
    
    def export_baseline_report(self) -> Dict[str, Any]:
        """Export all baseline data as report."""
        report = {
            "generated": datetime.utcnow().isoformat(),
            "agents": {},
        }
        
        for agent_name, snapshots in self.snapshots.items():
            first = snapshots[0]
            latest = snapshots[-1]
            
            report["agents"][agent_name] = {
                "baseline": asdict(first),
                "latest": asdict(latest),
                "improvement_percent": self.get_agent_improvement(agent_name),
                "snapshots_count": len(snapshots),
            }
        
        return report
    
    def _percent_change(self, before: float, after: float) -> float:
        """Calculate percent change (negative = improvement for errors)."""
        if before == 0:
            return 0
        return ((after - before) / before) * 100
    
    def _load_existing_data(self):
        """Load existing baseline data from file with recovery."""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                # Validate structure before loading
                if not isinstance(data, dict) or "agents" not in data:
                    self.logger.warning("baseline_invalid_structure")
                    return
                
                # Reconstruct snapshots from data
                for agent_name, agent_data in data.get("agents", {}).items():
                    if not isinstance(agent_data, dict):
                        continue
                    
                    snapshots = []
                    for snapshot_data in agent_data.get("snapshots", []):
                        try:
                            snapshots.append(AgentPerformanceSnapshot(**snapshot_data))
                        except TypeError as e:
                            # Skip corrupted entries
                            self.logger.debug("snapshot_load_skipped", error=str(e))
                            continue
                    
                    if snapshots:
                        self.snapshots[agent_name] = snapshots
        
        except json.JSONDecodeError as e:
            # File corrupted - try to recover by creating backup
            backup_path = f"{self.storage_path}.corrupted"
            try:
                os.rename(self.storage_path, backup_path)
                self.logger.warning("baseline_corrupted_backed_up", backup=backup_path)
            except Exception:
                pass
        
        except Exception as e:
            self.logger.warning("baseline_load_failed", error=str(e))
    
    def _save_data(self):
        """Save baseline data to file with atomic write."""
        try:
            # Create directory if needed
            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "generated": datetime.utcnow().isoformat(),
                "agents": {},
            }
            
            for agent_name, snapshots in self.snapshots.items():
                data["agents"][agent_name] = {
                    "snapshots": [asdict(s) for s in snapshots],
                }
            
            # Write to temporary file first
            temp_path = f"{self.storage_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename
            if os.path.exists(self.storage_path):
                backup_path = f"{self.storage_path}.backup"
                os.rename(self.storage_path, backup_path)
            
            os.rename(temp_path, self.storage_path)
            
            # Clean up old backup
            backup_path = f"{self.storage_path}.backup"
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except Exception:
                    pass
        
        except Exception as e:
            self.logger.warning("baseline_save_failed", error=str(e))
