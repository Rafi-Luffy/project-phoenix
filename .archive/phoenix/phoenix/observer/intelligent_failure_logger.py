"""
Intelligent Failure Logger

Logs everything that happens during the healing process. I needed rich, structured
logs that are both machine-readable (for analysis) and human-readable (for debugging).

This logger captures:
- Complete failure context (stack traces, agent state, conversation history)
- Fix generation and application details
- Test results and validation outcomes
- Success/failure metrics over time

The logs are in JSONL format so I can easily parse them, aggregate stats, and
build dashboards. Plus it tracks patterns over time so Phoenix learns which
fixes work best.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum

from phoenix.observer.agentic_failure_detector import (
    FailureContext,
    FailureReport,
    AgenticFailureType,
)
from phoenix.programmer.autonomous_fix_generator import AutonomousFix
from phoenix.programmer.autonomous_fix_applier import (
    FixApplicationResult,
    FixApplicationStatus,
)
from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class FailureLogEntry:
    """Comprehensive log entry for a failure event."""
    
    # Identity
    log_id: str
    failure_id: str
    timestamp: datetime
    
    # Failure details
    failure_type: str
    severity: str
    error_message: str
    
    # System context
    agent_name: str
    agent_type: str
    language: str
    framework: str
    
    # Failure context
    stack_trace: Optional[str]
    error_location: Dict[str, Any]
    agent_state: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    
    # Impact
    impact_scope: str
    downstream_effects: List[str]
    
    # Resolution
    auto_fixable: bool
    fix_id: Optional[str]
    fix_applied: bool
    fix_success: bool
    
    # Meta
    tags: List[str]
    related_failures: List[str]
    
    # Human-readable summary
    summary: str


@dataclass
class FixLogEntry:
    """Comprehensive log entry for a fix application."""
    
    # Identity
    log_id: str
    fix_id: str
    failure_id: str
    timestamp: datetime
    
    # Fix details
    fix_type: str
    fix_code_length: int
    risk_assessment: str
    confidence: float
    
    # Application
    status: str
    files_modified: List[str]
    
    # Validation
    tests_run: int
    tests_passed: int
    tests_failed: int
    
    # Outcome
    success: bool
    rolled_back: bool
    error_message: Optional[str]
    execution_time: float
    
    # Human summary
    summary: str


class IntelligentFailureLogger:
    """
    Comprehensive logging for failures and fixes.
    
    I wanted logs that actually help me understand what's happening:
    - What failed and why
    - What fix was generated
    - Did the fix work
    - What patterns am I seeing over time
    
    All stored in structured JSONL files for easy analysis. The logger
    automatically generates statistics, identifies trends, and builds
    insights from the data. No more grepping through log files manually.
    """
    
    def __init__(self, log_dir: str):
        """
        Initialize intelligent logger.
        
        Args:
            log_dir: Directory to store logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Log files
        self.failure_log_file = os.path.join(log_dir, "failures.jsonl")
        self.fix_log_file = os.path.join(log_dir, "fixes.jsonl")
        self.summary_log_file = os.path.join(log_dir, "summary.json")
        
        self.logger = get_logger(__name__)
    
    def log_failure(
        self,
        failure_context: FailureContext,
        failure_report: Optional[FailureReport] = None,
    ) -> str:
        """
        Log a failure with full context.
        
        Args:
            failure_context: Complete failure context
            failure_report: Optional failure analysis report
            
        Returns:
            Log ID
        """
        log_id = f"log_failure_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{failure_context.failure_id}"
        
        entry = FailureLogEntry(
            log_id=log_id,
            failure_id=failure_context.failure_id,
            timestamp=failure_context.timestamp,
            failure_type=failure_context.failure_type.value,
            severity=failure_context.severity,
            error_message=failure_context.error_message,
            agent_name=failure_context.agent_name,
            agent_type=failure_context.agent_type,
            language=failure_context.language,
            framework=failure_context.framework,
            stack_trace=failure_context.stack_trace,
            error_location=failure_context.error_location,
            agent_state=failure_context.agent_state,
            conversation_history=failure_context.conversation_history,
            impact_scope=failure_context.impact_scope,
            downstream_effects=failure_context.downstream_effects,
            auto_fixable=failure_context.auto_fixable,
            fix_id=None,  # Will be updated when fix is applied
            fix_applied=False,
            fix_success=False,
            tags=self._generate_tags(failure_context),
            related_failures=failure_context.similar_failures,
            summary=self._generate_failure_summary(failure_context, failure_report),
        )
        
        # Write to JSONL file
        with open(self.failure_log_file, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")
        
        self.logger.info(
            "failure_logged",
            log_id=log_id,
            failure_type=failure_context.failure_type.value,
            severity=failure_context.severity,
        )
        
        # Update summary statistics
        self._update_summary_stats()
        
        return log_id
    
    def log_fix(
        self,
        fix: AutonomousFix,
        result: FixApplicationResult,
    ) -> str:
        """
        Log a fix application.
        
        Args:
            fix: The autonomous fix
            result: Result of applying the fix
            
        Returns:
            Log ID
        """
        log_id = f"log_fix_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{fix.fix_id}"
        
        entry = FixLogEntry(
            log_id=log_id,
            fix_id=fix.fix_id,
            failure_id=fix.failure_id,
            timestamp=result.applied_at,
            fix_type=fix.fix_type,
            fix_code_length=len(fix.fix_code),
            risk_assessment=fix.risk_assessment,
            confidence=fix.confidence,
            status=result.status.value,
            files_modified=result.files_modified,
            tests_run=result.tests_run,
            tests_passed=result.tests_passed,
            tests_failed=result.tests_failed,
            success=result.success,
            rolled_back=result.rolled_back,
            error_message=result.error_message,
            execution_time=result.execution_time_seconds,
            summary=result.human_summary,
        )
        
        # Write to JSONL file
        with open(self.fix_log_file, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")
        
        self.logger.info(
            "fix_logged",
            log_id=log_id,
            fix_id=fix.fix_id,
            success=result.success,
        )
        
        # Update failure log with fix info
        self._update_failure_with_fix(fix.failure_id, fix.fix_id, result.success)
        
        # Update summary statistics
        self._update_summary_stats()
        
        return log_id
    
    def get_failure_statistics(
        self,
        time_window: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive failure statistics.
        
        Args:
            time_window: Optional time window (e.g., last 24 hours)
            
        Returns:
            Statistics dictionary
        """
        failures = self._read_failure_logs(time_window)
        
        if not failures:
            return {
                "total_failures": 0,
                "by_type": {},
                "by_severity": {},
                "auto_fixable": 0,
                "fixed": 0,
                "fix_success_rate": 0.0,
            }
        
        # Count by type
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        auto_fixable = 0
        fixed = 0
        fix_success = 0
        
        for failure in failures:
            by_type[failure["failure_type"]] += 1
            by_severity[failure["severity"]] += 1
            
            if failure["auto_fixable"]:
                auto_fixable += 1
            
            if failure["fix_applied"]:
                fixed += 1
                if failure["fix_success"]:
                    fix_success += 1
        
        fix_success_rate = (fix_success / fixed * 100) if fixed > 0 else 0.0
        
        return {
            "total_failures": len(failures),
            "by_type": dict(by_type),
            "by_severity": dict(by_severity),
            "auto_fixable": auto_fixable,
            "auto_fixable_rate": (auto_fixable / len(failures) * 100) if failures else 0.0,
            "fixed": fixed,
            "fix_success": fix_success,
            "fix_success_rate": fix_success_rate,
            "time_window": str(time_window) if time_window else "all_time",
        }
    
    def get_fix_statistics(
        self,
        time_window: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive fix statistics.
        
        Args:
            time_window: Optional time window
            
        Returns:
            Statistics dictionary
        """
        fixes = self._read_fix_logs(time_window)
        
        if not fixes:
            return {
                "total_fixes": 0,
                "successful": 0,
                "failed": 0,
                "rolled_back": 0,
                "success_rate": 0.0,
            }
        
        successful = sum(1 for f in fixes if f["success"])
        failed = sum(1 for f in fixes if not f["success"])
        rolled_back = sum(1 for f in fixes if f["rolled_back"])
        
        # Average execution time
        avg_execution_time = sum(f["execution_time"] for f in fixes) / len(fixes)
        
        # By risk
        by_risk = defaultdict(int)
        for fix in fixes:
            by_risk[fix["risk_assessment"]] += 1
        
        return {
            "total_fixes": len(fixes),
            "successful": successful,
            "failed": failed,
            "rolled_back": rolled_back,
            "success_rate": (successful / len(fixes) * 100) if fixes else 0.0,
            "avg_execution_time_seconds": avg_execution_time,
            "by_risk": dict(by_risk),
            "time_window": str(time_window) if time_window else "all_time",
        }
    
    def get_top_failures(
        self,
        limit: int = 10,
        time_window: Optional[timedelta] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get most common failures.
        
        Args:
            limit: Max number to return
            time_window: Optional time window
            
        Returns:
            List of failure types with counts
        """
        failures = self._read_failure_logs(time_window)
        
        # Count by type
        type_counts = defaultdict(int)
        for failure in failures:
            type_counts[failure["failure_type"]] += 1
        
        # Sort by count
        sorted_types = sorted(
            type_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:limit]
        
        return [
            {
                "failure_type": ftype,
                "count": count,
                "percentage": (count / len(failures) * 100) if failures else 0.0,
            }
            for ftype, count in sorted_types
        ]
    
    def get_recent_failures(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get most recent failures."""
        failures = self._read_failure_logs()
        
        # Sort by timestamp (most recent first)
        sorted_failures = sorted(
            failures,
            key=lambda x: x["timestamp"],
            reverse=True,
        )[:limit]
        
        return [
            {
                "failure_id": f["failure_id"],
                "timestamp": f["timestamp"],
                "type": f["failure_type"],
                "severity": f["severity"],
                "agent": f["agent_name"],
                "fixed": f["fix_applied"],
                "success": f["fix_success"] if f["fix_applied"] else None,
                "summary": f["summary"],
            }
            for f in sorted_failures
        ]
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights learned from failures and fixes.
        
        Returns:
            Learning insights
        """
        failures = self._read_failure_logs()
        fixes = self._read_fix_logs()
        
        if not failures:
            return {"message": "No failures logged yet"}
        
        # Success patterns
        successful_fix_types = defaultdict(int)
        failed_fix_types = defaultdict(int)
        
        for fix in fixes:
            if fix["success"]:
                successful_fix_types[fix["fix_type"]] += 1
            else:
                failed_fix_types[fix["fix_type"]] += 1
        
        # Failure trends
        failure_trends = defaultdict(list)
        for failure in failures:
            date = failure["timestamp"][:10]  # YYYY-MM-DD
            failure_trends[date].append(failure["failure_type"])
        
        # Auto-fixability by type
        fixable_by_type = defaultdict(lambda: {"total": 0, "fixable": 0})
        for failure in failures:
            ftype = failure["failure_type"]
            fixable_by_type[ftype]["total"] += 1
            if failure["auto_fixable"]:
                fixable_by_type[ftype]["fixable"] += 1
        
        fixability_rates = {
            ftype: (stats["fixable"] / stats["total"] * 100)
            for ftype, stats in fixable_by_type.items()
        }
        
        return {
            "total_failures_analyzed": len(failures),
            "total_fixes_applied": len(fixes),
            "most_successful_fix_types": dict(successful_fix_types),
            "least_successful_fix_types": dict(failed_fix_types),
            "fixability_by_type": fixability_rates,
            "failure_trends": {
                "dates": list(failure_trends.keys()),
                "pattern": "Improving" if self._is_improving(failure_trends) else "Stable",
            },
        }
    
    def _generate_tags(self, context: FailureContext) -> List[str]:
        """Generate tags for easier filtering."""
        tags = [
            context.failure_type.value,
            context.severity,
            context.language,
            context.framework,
            context.impact_scope,
        ]
        
        # Add auto-fixable tag
        if context.auto_fixable:
            tags.append("auto_fixable")
        
        # Add agent type
        if context.agent_type:
            tags.append(f"agent_{context.agent_type}")
        
        return tags
    
    def _generate_failure_summary(
        self,
        context: FailureContext,
        report: Optional[FailureReport],
    ) -> str:
        """Generate human-readable failure summary."""
        summary = f"{context.failure_type.value} in {context.agent_name}"
        
        if report:
            summary += f": {report.root_cause}"
        else:
            summary += f": {context.error_message[:100]}"
        
        if context.auto_fixable:
            summary += " (auto-fixable)"
        
        return summary
    
    def _read_failure_logs(
        self,
        time_window: Optional[timedelta] = None,
    ) -> List[Dict[str, Any]]:
        """Read failure logs from file."""
        if not os.path.exists(self.failure_log_file):
            return []
        
        failures = []
        cutoff_time = (
            datetime.utcnow() - time_window if time_window else None
        )
        
        with open(self.failure_log_file, "r") as f:
            for line in f:
                if line.strip():
                    failure = json.loads(line)
                    
                    # Filter by time window
                    if cutoff_time:
                        failure_time = datetime.fromisoformat(
                            failure["timestamp"].replace("Z", "+00:00")
                        )
                        if failure_time < cutoff_time:
                            continue
                    
                    failures.append(failure)
        
        return failures
    
    def _read_fix_logs(
        self,
        time_window: Optional[timedelta] = None,
    ) -> List[Dict[str, Any]]:
        """Read fix logs from file."""
        if not os.path.exists(self.fix_log_file):
            return []
        
        fixes = []
        cutoff_time = (
            datetime.utcnow() - time_window if time_window else None
        )
        
        with open(self.fix_log_file, "r") as f:
            for line in f:
                if line.strip():
                    fix = json.loads(line)
                    
                    # Filter by time window
                    if cutoff_time:
                        fix_time = datetime.fromisoformat(
                            fix["timestamp"].replace("Z", "+00:00")
                        )
                        if fix_time < cutoff_time:
                            continue
                    
                    fixes.append(fix)
        
        return fixes
    
    def _update_failure_with_fix(
        self,
        failure_id: str,
        fix_id: str,
        success: bool,
    ):
        """Update failure log entry with fix information."""
        # Read all failures
        if not os.path.exists(self.failure_log_file):
            return
        
        failures = []
        with open(self.failure_log_file, "r") as f:
            for line in f:
                if line.strip():
                    failures.append(json.loads(line))
        
        # Update matching failure
        for failure in failures:
            if failure["failure_id"] == failure_id:
                failure["fix_id"] = fix_id
                failure["fix_applied"] = True
                failure["fix_success"] = success
                break
        
        # Rewrite file
        with open(self.failure_log_file, "w") as f:
            for failure in failures:
                f.write(json.dumps(failure, default=str) + "\n")
    
    def _update_summary_stats(self):
        """Update summary statistics file."""
        failure_stats = self.get_failure_statistics()
        fix_stats = self.get_fix_statistics()
        top_failures = self.get_top_failures()
        learning = self.get_learning_insights()
        
        summary = {
            "last_updated": datetime.utcnow().isoformat(),
            "failure_statistics": failure_stats,
            "fix_statistics": fix_stats,
            "top_failures": top_failures,
            "learning_insights": learning,
        }
        
        with open(self.summary_log_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
    
    def _is_improving(self, trends: Dict[str, List[str]]) -> bool:
        """Determine if failure rate is improving."""
        if len(trends) < 2:
            return False
        
        # Compare recent vs earlier
        dates = sorted(trends.keys())
        recent_count = len(trends[dates[-1]])
        earlier_count = len(trends[dates[0]])
        
        return recent_count < earlier_count
