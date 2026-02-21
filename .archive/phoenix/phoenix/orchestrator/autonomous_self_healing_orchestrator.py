"""
Autonomous Self-Healing Orchestrator

This is the main engine that ties everything together. It runs the complete
healing cycle from detecting failures to applying fixes automatically.

The healing loop:
1. Monitor logs for failures
2. Detect what went wrong (using pattern matching + LLM)
3. Log everything with full context
4. Generate a fix using GPT-4/Claude
5. Apply the fix (with safety checks)
6. Validate it works
7. Learn from the outcome

I built this to run continuously in production - it monitors your agentic AI
system 24/7 and fixes issues as they happen. No human in the loop, no manual
debugging, no 3am pages.

This is what true autonomous operation looks like.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from phoenix.observer.agentic_failure_detector import (
    AgenticFailureDetector,
    FailureContext,
    FailureReport,
    AgenticFailureType,
)
from phoenix.programmer.autonomous_fix_generator import (
    AutonomousFixGenerator,
    AutonomousFix,
)
from phoenix.programmer.autonomous_fix_applier import (
    AutonomousFixApplier,
    FixApplicationResult,
    FixApplicationStatus,
)
from phoenix.observer.intelligent_failure_logger import (
    IntelligentFailureLogger,
)

# Optional module imports - enhance healing with additional features
from phoenix.observer.metrics_exporter import MetricsExporter
from phoenix.observer.slack_notifier import SlackNotifier
from phoenix.observer.performance_baseline import PerformanceBaselineTracker
from phoenix.programmer.fix_cache_manager import FixCacheManager, CostOptimizer
from phoenix.programmer.fix_confidence_booster import (
    FixConfidenceAnalyzer,
    FixQualityValidator,
)

# Configuration and health check imports
from phoenix.core.config_manager import ConfigurationManager, PhoenixConfig
from phoenix.core.health_checker import HealthCheckService
from phoenix.core.error_recovery import (
    ErrorRecoveryOrchestrator,
    CircuitBreaker,
    RetryStrategy,
)
from phoenix.core.observability import ObservabilityOrchestrator
from phoenix.core.performance import PerformanceOptimizer

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class HealingCycleResult:
    """Result of one complete autonomous healing cycle."""
    
    # Cycle info
    cycle_id: str
    started_at: datetime
    completed_at: datetime
    
    # Detection
    failures_detected: int
    composite_failures: int
    
    # Analysis
    failures_analyzed: int
    auto_fixable: int
    
    # Fix generation
    fixes_generated: int
    
    # Fix application
    fixes_applied: int
    fixes_successful: int
    fixes_failed: int
    fixes_rolled_back: int
    
    # Performance
    total_time_seconds: float
    avg_fix_time_seconds: float
    
    # Outcome
    system_health: str  # "healthy", "degraded", "critical"
    human_summary: str


class AutonomousSelfHealingOrchestrator:
    """
    The main orchestrator that runs autonomous healing.
    
    This coordinates all the pieces - detection, fix generation, application,
    validation, and learning. I designed it to run continuously in production,
    watching for failures and fixing them automatically.
    
    The workflow:
    1. Pull recent logs from your system
    2. Scan for failure patterns
    3. Capture full context (stack traces, agent state, etc.)
    4. Use LLM to generate a fix
    5. Apply the fix with safety checks
    6. Run validation tests
    7. Rollback if tests fail, commit if they pass
    8. Track success rate and learn patterns
    
    You can run it as a one-off (single healing cycle) or continuously (24/7 monitoring).
    Either way, no human intervention needed.
    """
    
    def __init__(
        self,
        workspace_path: str,
        log_dir: Optional[str] = None,
        auto_heal: bool = True,
        max_concurrent_fixes: int = 3,
    ):
        """
        Initialize autonomous healing orchestrator.
        
        Args:
            workspace_path: Root path of the project
            log_dir: Directory for logs (defaults to workspace/.phoenix_logs)
            auto_heal: Whether to automatically apply fixes (True = fully autonomous)
            max_concurrent_fixes: Max number of fixes to apply simultaneously
        """
        self.workspace_path = workspace_path
        self.auto_heal = auto_heal
        self.max_concurrent_fixes = max_concurrent_fixes
        
        # Core components
        self.failure_detector = AgenticFailureDetector()
        self.fix_generator = AutonomousFixGenerator()
        self.fix_applier = AutonomousFixApplier(workspace_path)
        
        # Logging
        log_dir = log_dir or f"{workspace_path}/.phoenix_logs"
        self.logger_system = IntelligentFailureLogger(log_dir)
        
        self.logger = get_logger(__name__)
        
        # Optional modules - all initialize gracefully even if not configured
        self.metrics_exporter = MetricsExporter(export_dir=log_dir)
        self.slack_notifier = SlackNotifier()  # Only enabled if SLACK_WEBHOOK_URL set
        self.baseline_tracker = PerformanceBaselineTracker()
        self.fix_cache = FixCacheManager()
        self.cost_optimizer = CostOptimizer()
        self.confidence_analyzer = FixConfidenceAnalyzer()
        self.quality_validator = FixQualityValidator()
        
        # Configuration and health checks
        self.config_manager = ConfigurationManager()
        self.health_checker = HealthCheckService()
        
        # Error recovery and resilience
        self.error_recovery = ErrorRecoveryOrchestrator()
        self.llm_circuit_breaker = self.error_recovery.create_circuit_breaker(
            "llm_provider",
            failure_threshold=5,
            recovery_timeout=60,
        )
        self.fix_generator_retry = self.error_recovery.create_retry_strategy(
            "fix_generation",
            max_retries=3,
            base_delay=2.0,
        )
        self.fix_applier_retry = self.error_recovery.create_retry_strategy(
            "fix_application",
            max_retries=2,
            base_delay=1.0,
        )
        
        # Observability (Tier 2.1)
        self.observability = ObservabilityOrchestrator()
        
        # Performance Optimization (Tier 2.2)
        self.performance = PerformanceOptimizer(
            max_cache_entries=1000,
            max_workers=max_concurrent_fixes,
            db_pool_size=10,
        )
        
        # State
        self.is_running = False
        self.healing_history: List[HealingCycleResult] = []
        self.stats = {
            "total_healed": 0,
            "total_failures": 0,
            "cache_hits": 0,
            "total_cycles": 0,
        }
        
        self.logger.info(
            "autonomous_orchestrator_initialized",
            workspace=workspace_path,
            auto_heal=auto_heal,
            optional_modules_enabled=True,
        )
    
    def startup_health_check(self) -> bool:
        """
        Perform startup health checks.
        
        Returns:
            True if system is ready, False if critical issues
        """
        self.logger.info("running_startup_health_checks")
        
        try:
            import asyncio
            
            # Run health check
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                health = loop.run_until_complete(self.health_checker.check_health())
            finally:
                loop.close()
            
            # Log results
            overall_status = health.get("status", "unknown")
            check_time = health.get("check_time_ms", 0)
            
            self.logger.info(
                "startup_health_check_complete",
                status=overall_status,
                check_time_ms=check_time,
                components=health.get("components", {}),
            )
            
            # Check for critical failures
            if overall_status == "unhealthy":
                self.logger.error(
                    "startup_health_check_failed",
                    components=health.get("components", {}),
                )
                return False
            
            return True
        
        except Exception as e:
            self.logger.error("startup_health_check_error", error=str(e))
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get current system health status.
        
        Returns:
            Health status report
        """
        try:
            import asyncio
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                return loop.run_until_complete(self.health_checker.check_health())
            finally:
                loop.close()
        
        except Exception as e:
            self.logger.error("health_check_error", error=str(e))
            return {"status": "unknown", "error": str(e)}
    
    def get_error_recovery_stats(self) -> Dict[str, Any]:
        """
        Get error recovery and resilience statistics.
        
        Returns:
            Statistics on circuit breakers and retry strategies
        """
        return self.error_recovery.get_all_stats()
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Combined health, recovery, and operational stats
        """
        return {
            "health": self.get_system_health(),
            "error_recovery": self.get_error_recovery_stats(),
            "operational_stats": self.stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_observability_dashboard(self) -> Dict[str, Any]:
        """
        Get observability dashboard data.
        
        Returns:
            Dashboard with traces, metrics, and system overview
        """
        dashboard = self.observability.get_dashboard()
        dashboard["system_status"] = self.get_system_status()
        return dashboard
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance optimization statistics.
        
        Returns:
            Performance metrics with cache, parallel, and database stats
        """
        perf_stats = self.performance.get_performance_stats()
        return {
            "timestamp": datetime.now().isoformat(),
            "cache": perf_stats.cache_stats,
            "parallel_healing": perf_stats.parallel_stats,
            "database": perf_stats.database_stats,
            "memory": perf_stats.memory_stats,
        }
    
    def run_healing_cycle(
        self,
        log_output: str,
        agent_context: Optional[Dict[str, Any]] = None,
    ) -> HealingCycleResult:
        """
        Run ONE complete autonomous healing cycle.
        
        This is the CORE of Phoenix's autonomous operation:
        1. Detect failures in logs
        2. Log them comprehensively
        3. Generate fixes
        4. Apply fixes automatically
        5. Validate success
        6. Learn from outcomes
        
        Args:
            log_output: Recent log output to analyze
            agent_context: Optional context about the agent/system
            
        Returns:
            Result of healing cycle
        """
        cycle_id = f"cycle_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.utcnow()
        
        self.logger.info(
            "starting_autonomous_healing_cycle",
            cycle_id=cycle_id,
        )
        
        # STEP 1: DETECT FAILURES
        self.logger.info("step_1_detecting_failures")
        failures = self.failure_detector.detect_from_logs(
            log_output,
            agent_context or {},
        )
        
        self.logger.info(
            "failures_detected",
            count=len(failures),
        )
        
        if not failures:
            return HealingCycleResult(
                cycle_id=cycle_id,
                started_at=start_time,
                completed_at=datetime.utcnow(),
                failures_detected=0,
                composite_failures=0,
                failures_analyzed=0,
                auto_fixable=0,
                fixes_generated=0,
                fixes_applied=0,
                fixes_successful=0,
                fixes_failed=0,
                fixes_rolled_back=0,
                total_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                avg_fix_time_seconds=0,
                system_health="healthy",
                human_summary=" No failures detected. System healthy.",
            )
        
        # Count composite failures
        composite_failures = sum(
            1 for f in failures
            if len(f.failure_type.value.split('_')) > 2  # Heuristic
        )
        
        # STEP 2: LOG ALL FAILURES
        self.logger.info("step_2_logging_failures")
        for failure in failures:
            self.logger_system.log_failure(failure)
        
        # STEP 3: ANALYZE & GENERATE FIXES (with caching & confidence)
        self.logger.info("step_3_generating_fixes")
        fixes: List[AutonomousFix] = []
        
        for failure in failures:
            if not failure.auto_fixable:
                self.logger.warning(
                    "failure_not_auto_fixable",
                    failure_type=failure.failure_type.value,
                )
                continue
            
            try:
                # Check cache first - avoid expensive LLM calls
                failure_sig = self.fix_cache.get_failure_signature(
                    failure_type=failure.failure_type.value,
                    error_message=failure.error_message,
                    stack_trace=failure.stack_trace,
                )
                
                cached_fix = self.fix_cache.get_cached_fix(failure_sig)
                if cached_fix:
                    self.logger.info("cache_hit", failure_type=failure.failure_type.value)
                    self.stats["cache_hits"] += 1
                    
                    # Use cached fix
                    fix = AutonomousFix(
                        fix_id=f"cached_{failure.failure_id}",
                        failure_id=failure.failure_id,
                        fix_code=cached_fix.fix_code,
                        validation_tests=cached_fix.validation_tests,
                        rollback_code=cached_fix.fix_code,
                        explanation=f"Cached fix for {failure.failure_type.value}",
                        confidence_score=0.95,
                    )
                else:
                    # Generate new fix with enhanced prompt
                    similar_fixes = []  # Could retrieve from history
                    enhanced_prompt = self.confidence_analyzer.improve_fix_prompt(
                        failure_type=failure.failure_type.value,
                        base_prompt=self.fix_generator.base_prompt if hasattr(self.fix_generator, 'base_prompt') else "",
                        similar_fixes=similar_fixes,
                    )
                    
                    fix = self.fix_generator.generate_fix(failure)
                    
                    # Validate fix quality
                    quality_result = self.quality_validator.validate_fix_quality(
                        fix_code=fix.fix_code,
                        validation_tests=fix.validation_tests,
                        failure_type=failure.failure_type.value,
                    )
                    
                    if not quality_result["is_valid"]:
                        self.logger.warning(
                            "low_quality_fix",
                            failure_id=failure.failure_id,
                            issues=quality_result["issues"],
                        )
                        continue
                
                # Check confidence before applying
                confidence_level = self.confidence_analyzer.get_confidence_level(
                    failure_type=failure.failure_type.value,
                    llm_confidence=fix.confidence_score if hasattr(fix, 'confidence_score') else 0.5,
                    has_similar_fixes=cached_fix is not None,
                    fix_has_tests=bool(fix.validation_tests),
                )
                
                if not self.confidence_analyzer.should_apply_fix(confidence_level):
                    self.logger.warning(
                        "low_confidence_fix",
                        failure_id=failure.failure_id,
                        confidence_level=confidence_level,
                    )
                    continue
                
                fixes.append(fix)
                
                self.logger.info(
                    "fix_generated",
                    fix_id=fix.fix_id,
                    failure_id=failure.failure_id,
                    cached=cached_fix is not None,
                )
            except Exception as e:
                self.logger.error(
                    "fix_generation_failed",
                    failure_id=failure.failure_id,
                    error=str(e),
                )
        
        # STEP 4: APPLY FIXES (if auto_heal enabled) with metrics tracking
        successful = 0
        failed = 0
        rolled_back = 0
        fix_times = []
        
        if self.auto_heal and fixes:
            self.logger.info("step_4_applying_fixes_autonomously")
            
            for fix in fixes[:self.max_concurrent_fixes]:
                try:
                    fix_start = datetime.utcnow()
                    
                    result = self.fix_applier.apply_fix(fix)
                    
                    fix_time = (datetime.utcnow() - fix_start).total_seconds()
                    fix_times.append(fix_time)
                    
                    # Log the fix
                    self.logger_system.log_fix(fix, result)
                    
                    if result.success:
                        successful += 1
                        
                        # Cache successful fix for reuse
                        if hasattr(fix, 'failure_id'):
                            failure_sig = self.fix_cache.get_failure_signature(
                                failure_type=str(fix.failure_id),
                                error_message="cached",
                                stack_trace="",
                            )
                            self.fix_cache.cache_fix(
                                failure_signature=failure_sig,
                                failure_type=str(fix.failure_id),
                                fix_code=fix.fix_code,
                                validation_tests=fix.validation_tests,
                                application_time_ms=fix_time * 1000,
                            )
                        
                        # Track success for confidence analyzer
                        self.confidence_analyzer.record_fix_result(
                            failure_type=str(fix.failure_id),
                            success=True,
                        )
                        
                        # Send Slack notification (if configured)
                        self.slack_notifier.notify_fix_success(
                            failure_type=str(fix.failure_id),
                            agent_name="auto",
                            fix_time_seconds=fix_time,
                        )
                        
                        self.logger.info(
                            "fix_applied_successfully",
                            fix_id=fix.fix_id,
                            time_seconds=fix_time,
                        )
                    else:
                        failed += 1
                        if result.rolled_back:
                            rolled_back += 1
                        
                        # Track failure for confidence analyzer
                        self.confidence_analyzer.record_fix_result(
                            failure_type=str(fix.failure_id),
                            success=False,
                        )
                        
                        # Send Slack alert
                        self.slack_notifier.notify_critical_failure(
                            failure_type=str(fix.failure_id),
                            agent_name="auto",
                            error_message=result.error_message[:100],
                        )
                        
                        self.logger.warning(
                            "fix_application_failed",
                            fix_id=fix.fix_id,
                            error=result.error_message,
                        )
                
                except Exception as e:
                    failed += 1
                    self.confidence_analyzer.record_fix_result(
                        failure_type=str(fix.failure_id if hasattr(fix, 'failure_id') else "unknown"),
                        success=False,
                    )
                    self.logger.error(
                        "fix_application_exception",
                        fix_id=fix.fix_id,
                        error=str(e),
                    )
        
        elif fixes:
            self.logger.warning(
                "auto_heal_disabled",
                fixes_pending=len(fixes),
            )
        
        # Calculate results
        auto_fixable = sum(1 for f in failures if f.auto_fixable)
        total_time = (datetime.utcnow() - start_time).total_seconds()
        avg_fix_time = (sum(fix_times) / len(fix_times)) if fix_times else 0
        
        # Determine system health
        if failed == 0 and successful > 0:
            health = "healthy"
        elif failed > 0 and successful >= failed:
            health = "degraded"
        else:
            health = "critical"
        
        # Human summary
        summary = self._generate_cycle_summary(
            failures_detected=len(failures),
            auto_fixable=auto_fixable,
            fixes_applied=successful + failed,
            successful=successful,
            failed=failed,
            health=health,
        )
        
        result = HealingCycleResult(
            cycle_id=cycle_id,
            started_at=start_time,
            completed_at=datetime.utcnow(),
            failures_detected=len(failures),
            composite_failures=composite_failures,
            failures_analyzed=len(failures),
            auto_fixable=auto_fixable,
            fixes_generated=len(fixes),
            fixes_applied=successful + failed,
            fixes_successful=successful,
            fixes_failed=failed,
            fixes_rolled_back=rolled_back,
            total_time_seconds=total_time,
            avg_fix_time_seconds=avg_fix_time,
            system_health=health,
            human_summary=summary,
        )
        
        # Store in history
        self.healing_history.append(result)
        
        # Update statistics
        self.stats["total_cycles"] += 1
        self.stats["total_healed"] += successful
        self.stats["total_failures"] += len(failures)
        
        # Export metrics in multiple formats
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_id": cycle_id,
            "failures_detected": len(failures),
            "fixes_applied": successful,
            "fixes_failed": failed,
            "success_rate": (successful / (successful + failed) * 100) if (successful + failed) > 0 else 0,
            "cache_hits": self.stats["cache_hits"],
            "avg_fix_time_ms": avg_fix_time * 1000,
            "total_time_ms": total_time * 1000,
            "system_health": health,
        }
        
        # Export metrics (JSON, Prometheus, CSV)
        self.metrics_exporter.export_healing_metrics(metrics)
        
        # Check if success rate is good for celebration
        overall_success_rate = (
            self.stats["total_healed"] / self.stats["total_failures"] * 100
            if self.stats["total_failures"] > 0 else 0
        )
        if overall_success_rate >= 90:
            self.slack_notifier.notify_high_success_rate(overall_success_rate)
        
        self.logger.info(
            "healing_cycle_complete",
            cycle_id=cycle_id,
            health=health,
            fixes_applied=successful,
            cache_hits=self.stats["cache_hits"],
        )
        
        return result
    
    def continuous_healing_loop(
        self,
        log_source_func,
        interval_seconds: int = 60,
        max_iterations: Optional[int] = None,
    ):
        """
        Run CONTINUOUS autonomous healing.
        
        This is the ultimate autonomous mode - Phoenix monitors and heals FOREVER.
        
        Args:
            log_source_func: Function that returns recent logs
            interval_seconds: How often to check (default 60s)
            max_iterations: Optional limit (None = infinite)
        """
        self.logger.info(
            "starting_continuous_healing",
            interval=interval_seconds,
            max_iterations=max_iterations or "infinite",
        )
        
        self.is_running = True
        iteration = 0
        
        try:
            while self.is_running:
                if max_iterations and iteration >= max_iterations:
                    break
                
                iteration += 1
                
                self.logger.info(
                    "continuous_healing_iteration",
                    iteration=iteration,
                )
                
                # Get logs
                try:
                    logs = log_source_func()
                except Exception as e:
                    self.logger.error(
                        "log_source_error",
                        error=str(e),
                    )
                    time.sleep(interval_seconds)
                    continue
                
                # Run healing cycle
                result = self.run_healing_cycle(logs)
                
                # Periodic metrics export (every 10 cycles)
                if iteration % 10 == 0:
                    self._export_all_metrics()
                
                # Report
                self.logger.info(
                    "iteration_complete",
                    iteration=iteration,
                    health=result.system_health,
                    fixes_applied=result.fixes_successful,
                    cache_hits=self.stats["cache_hits"],
                )
                
                # Sleep
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            self.logger.info("continuous_healing_stopped_by_user")
        
        finally:
            self.is_running = False
            self.logger.info(
                "continuous_healing_stopped",
                total_iterations=iteration,
            )
    
    def stop(self):
        """Stop continuous healing."""
        self.is_running = False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about autonomous healing."""
        
        # Failure stats
        failure_stats = self.logger_system.get_failure_statistics()
        
        # Fix stats
        fix_stats = self.logger_system.get_fix_statistics()
        
        # Recent failures
        recent = self.logger_system.get_recent_failures(limit=10)
        
        # Top failures
        top = self.logger_system.get_top_failures(limit=5)
        
        # Learning insights
        learning = self.logger_system.get_learning_insights()
        
        # Healing cycle stats
        if self.healing_history:
            total_cycles = len(self.healing_history)
            successful_cycles = sum(
                1 for c in self.healing_history
                if c.system_health == "healthy"
            )
            avg_cycle_time = sum(
                c.total_time_seconds for c in self.healing_history
            ) / total_cycles
        else:
            total_cycles = 0
            successful_cycles = 0
            avg_cycle_time = 0
        
        return {
            "autonomous_healing_stats": {
                "total_healing_cycles": total_cycles,
                "successful_cycles": successful_cycles,
                "success_rate": (successful_cycles / total_cycles * 100) if total_cycles else 0.0,
                "avg_cycle_time_seconds": avg_cycle_time,
            },
            "failure_stats": failure_stats,
            "fix_stats": fix_stats,
            "recent_failures": recent,
            "top_failures": top,
            "learning_insights": learning,
            "current_system_health": (
                self.healing_history[-1].system_health
                if self.healing_history else "unknown"
            ),
        }
    
    def get_dashboard(self) -> str:
        """
        Generate human-readable dashboard.
        
        Returns:
            Markdown-formatted dashboard
        """
        stats = self.get_statistics()
        
        dashboard = f"""# Phoenix Autonomous Healing Dashboard

**Last Updated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## System Health

**Current Status**: {stats['current_system_health'].upper()}

## Autonomous Healing Performance

- **Total Healing Cycles**: {stats['autonomous_healing_stats']['total_healing_cycles']}
- **Success Rate**: {stats['autonomous_healing_stats']['success_rate']:.1f}%
- **Avg Cycle Time**: {stats['autonomous_healing_stats']['avg_cycle_time_seconds']:.2f}s

## Failure Detection

- **Total Failures**: {stats['failure_stats']['total_failures']}
- **Auto-Fixable**: {stats['failure_stats']['auto_fixable']} ({stats['failure_stats']['auto_fixable_rate']:.1f}%)
- **Fixed**: {stats['failure_stats']['fixed']}
- **Fix Success Rate**: {stats['failure_stats']['fix_success_rate']:.1f}%

## Fix Application

- **Total Fixes**: {stats['fix_stats']['total_fixes']}
- **Successful**: {stats['fix_stats']['successful']}
- **Failed**: {stats['fix_stats']['failed']}
- **Rolled Back**: {stats['fix_stats']['rolled_back']}
- **Success Rate**: {stats['fix_stats']['success_rate']:.1f}%

## Top Failures

"""
        
        for i, failure in enumerate(stats['top_failures'], 1):
            dashboard += f"{i}. **{failure['failure_type']}** - {failure['count']} occurrences ({failure['percentage']:.1f}%)\n"
        
        dashboard += "\n## Recent Failures\n\n"
        
        for failure in stats['recent_failures'][:5]:
            status = " Fixed" if failure['success'] else (" Failed" if failure['fixed'] else "⧗ Pending")
            dashboard += f"- {failure['timestamp']} - {failure['type']} - {status}\n"
        
        dashboard += f"""
## Learning Insights

{self._format_learning_insights(stats['learning_insights'])}

---

**Phoenix**: The world's first fully autonomous agentic AI healing system.
**Core Principle**: ZERO human interaction required.
"""
        
        return dashboard
    
    def _generate_cycle_summary(
        self,
        failures_detected: int,
        auto_fixable: int,
        fixes_applied: int,
        successful: int,
        failed: int,
        health: str,
    ) -> str:
        """Generate human-readable cycle summary."""
        
        if failures_detected == 0:
            return " No failures detected. System healthy."
        
        summary = f"Detected {failures_detected} failure(s)"
        
        if auto_fixable > 0:
            summary += f", {auto_fixable} auto-fixable"
        
        if fixes_applied > 0:
            summary += f". Applied {fixes_applied} fix(es)"
            
            if successful > 0:
                summary += f", {successful} successful"
            
            if failed > 0:
                summary += f", {failed} failed"
        
        summary += f". System: {health}."
        
        return summary
    
    def _format_learning_insights(self, insights: Dict[str, Any]) -> str:
        """Format learning insights for dashboard."""
        
        if "message" in insights:
            return insights["message"]
        
        text = f"- Analyzed {insights['total_failures_analyzed']} failures\n"
        text += f"- Applied {insights['total_fixes_applied']} fixes\n"
        
        if insights.get('failure_trends'):
            text += f"- Trend: {insights['failure_trends']['pattern']}\n"
        
        return text    
    def _export_all_metrics(self):
        """Export comprehensive metrics in all formats."""
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_cycles": self.stats["total_cycles"],
            "total_healed": self.stats["total_healed"],
            "total_failures": self.stats["total_failures"],
            "cache_hits": self.stats["cache_hits"],
            "success_rate": (
                self.stats["total_healed"] / self.stats["total_failures"] * 100
                if self.stats["total_failures"] > 0 else 0
            ),
            "cache_stats": self.fix_cache.get_cache_stats(),
            "baseline_report": self.baseline_tracker.export_baseline_report(),
        }
        
        # Export in multiple formats
        self.metrics_exporter.export_healing_metrics(stats)
        self.metrics_exporter.export_prometheus_format(stats)
        self.metrics_exporter.export_csv_for_excel(stats)
        
        self.logger.info("metrics_exported", stats=stats)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for visualization."""
        return {
            "statistics": self.get_statistics(),
            "healing_stats": {
                "total_cycles": self.stats["total_cycles"],
                "total_healed": self.stats["total_healed"],
                "total_failures": self.stats["total_failures"],
                "cache_hits": self.stats["cache_hits"],
                "success_rate": (
                    self.stats["total_healed"] / self.stats["total_failures"] * 100
                    if self.stats["total_failures"] > 0 else 0
                ),
            },
            "cache": self.fix_cache.get_cache_stats(),
            "performance": self.baseline_tracker.export_baseline_report(),
            "most_reused_fixes": [
                {"signature": f.failure_signature, "reuses": f.success_count}
                for f in self.fix_cache.get_most_reused_fixes()
            ],
        }