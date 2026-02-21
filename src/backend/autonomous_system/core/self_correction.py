"""
Self-Correction Orchestrator

This module coordinates error detection, correction strategy selection,
and adaptive improvement into a unified self-healing system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Callable
import time

from .error_detection import (
    ErrorDetectionManager, ErrorContext, ErrorPattern, ErrorAnalysis
)
from .correction_strategy import (
    CorrectionStrategyEngine, CorrectionResult, CorrectionStrategy
)
from .adaptive_improvement import (
    AdaptiveImprovementSystem, ImprovementSuggestion, LearningMetric
)


@dataclass
class SelfCorrectionSession:
    """Record of a self-correction session"""
    session_id: str
    error: ErrorContext
    analysis: Optional[ErrorAnalysis] = None
    correction: Optional[CorrectionResult] = None
    improvement: Optional[ImprovementSuggestion] = None
    final_success: bool = False
    total_time_ms: float = 0.0
    messages: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "error": self.error.to_dict() if self.error else None,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "correction": self.correction.to_dict() if self.correction else None,
            "final_success": self.final_success,
            "time_ms": self.total_time_ms,
            "messages": self.messages,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SystemHealthReport:
    """Report on system health and recovery status"""
    timestamp: datetime = field(default_factory=datetime.now)
    total_errors_handled: int = 0
    successful_corrections: int = 0
    failed_corrections: int = 0
    active_improvement_initiatives: int = 0
    critical_issues_remaining: int = 0
    system_stability_score: float = 0.0
    recovery_efficiency: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_errors_handled": self.total_errors_handled,
            "corrections": {
                "successful": self.successful_corrections,
                "failed": self.failed_corrections
            },
            "system_stability": self.system_stability_score,
            "recovery_efficiency": self.recovery_efficiency,
            "critical_issues": self.critical_issues_remaining,
            "recommendations": self.recommendations
        }


class SelfCorrectionOrchestrator:
    """
    Master orchestrator for self-correction.
    Coordinates error detection, correction, and continuous improvement.
    """
    
    def __init__(self, memory_manager: Optional[Any] = None):
        """
        Initialize self-correction orchestrator
        
        Args:
            memory_manager: Reference to memory manager for storing insights
        """
        self.memory_manager = memory_manager
        self.error_detector = ErrorDetectionManager()
        self.correction_engine = CorrectionStrategyEngine()
        self.improvement_system = AdaptiveImprovementSystem(memory_manager)
        
        self.sessions: Dict[str, SelfCorrectionSession] = {}
        self.session_counter = 0
        self.max_sessions = 10000
        
        self.enabled = True
        self.auto_correct = True
        self.learning_enabled = True
    
    def handle_operation(self, operation_fn: Callable[..., Any],
                        operation_name: str,
                        agent_id: str,
                        operation_args: Dict[str, Any],
                        correction_context: Optional[Dict[str, Any]] = None,
                        failure_indicators: Optional[Dict[str, Any]] = None) -> Tuple[Any, Optional[SelfCorrectionSession]]:
        """
        Execute operation with self-correction capability
        
        Args:
            operation_fn: Function to execute
            operation_name: Name of operation
            agent_id: ID of agent performing operation
            operation_args: Arguments for operation
            correction_context: Context for correction (retry_fn, fallback_fn, etc.)
            failure_indicators: Outcome indicators for failure detection
            
        Returns:
            Tuple of (result, session) where session is None if no correction needed
        """
        if not self.enabled:
            return operation_fn(**operation_args), None
        
        start_time = time.time()
        session = None
        
        try:
            # Execute operation
            result = operation_fn(**operation_args)
            
            # Check for output-based errors
            error_context = {
                "agent_id": agent_id,
                "operation": operation_name,
                "input_data": operation_args,
                "state_snapshot": {},
                "metadata": {}
            }
            
            # Add outcome detector if failure indicators provided
            if failure_indicators:
                from .error_detection import OutcomeDetector
                outcome_detector = OutcomeDetector(failure_indicators)
                self.error_detector.add_detector(outcome_detector)
            
            # Detect errors
            detected_error = self.error_detector.detect_error(result, error_context)
            
            if detected_error:
                session = self._handle_detected_error(
                    detected_error,
                    operation_fn,
                    operation_name,
                    correction_context or {},
                    start_time
                )
                
                if session.final_success:
                    return session.correction.corrected_output, session
                else:
                    return result, session
            
            return result, None
            
        except Exception as e:
            # Handle exceptions
            error_context = {
                "agent_id": agent_id,
                "operation": operation_name,
                "input_data": operation_args,
                "stack_trace": str(e),
                "state_snapshot": {},
                "metadata": {}
            }
            
            detected_error = self.error_detector.detect_error(e, error_context)
            
            if detected_error and self.auto_correct:
                session = self._handle_detected_error(
                    detected_error,
                    operation_fn,
                    operation_name,
                    correction_context or {},
                    start_time
                )
                
                if session.final_success:
                    return session.correction.corrected_output, session
                else:
                    raise
            else:
                raise
    
    def _handle_detected_error(self, error: ErrorContext,
                              operation_fn: Callable,
                              operation_name: str,
                              correction_context: Dict[str, Any],
                              start_time: float) -> SelfCorrectionSession:
        """Handle a detected error through analysis and correction"""
        
        # Create session
        self.session_counter += 1
        session_id = f"session_{self.session_counter}"
        session = SelfCorrectionSession(session_id=session_id, error=error)
        
        # Add to sessions
        self.sessions[session_id] = session
        if len(self.sessions) > self.max_sessions:
            # Remove oldest session
            oldest_id = min(
                self.sessions.keys(),
                key=lambda k: self.sessions[k].timestamp
            )
            del self.sessions[oldest_id]
        
        session.messages.append(f"Error detected: {error.error_type.value}")
        
        # Analyze error
        analysis = self.error_detector.analyze_error(error)
        session.analysis = analysis
        session.messages.append(f"Root cause: {analysis.root_cause_hypothesis}")
        
        # Attempt correction
        correction_context["operation_name"] = operation_name
        correction_context["agent_id"] = error.agent_id
        
        if self.auto_correct:
            correction = self.correction_engine.attempt_correction(
                error,
                analysis,
                correction_context
            )
            
            if correction:
                session.correction = correction
                session.final_success = correction.success
                session.messages.extend(correction.messages)
                session.messages.append(
                    f"Correction attempt using {correction.strategy.value}: "
                    f"{'SUCCESS' if correction.success else 'FAILED'}"
                )
        
        # Learning phase
        if self.learning_enabled and session.analysis:
            if session.correction:
                improvement = self.improvement_system.analyze_correction_outcome(
                    session.correction,
                    error,
                    session.analysis
                )
                session.improvement = improvement
                session.messages.append(
                    f"Improvement suggestion: {improvement.description}"
                )
            else:
                # No correction attempted
                improvement = self.improvement_system.analyze_correction_outcome(
                    CorrectionResult(
                        strategy=CorrectionStrategy.ANALYZE,
                        success=False,
                        original_error=error
                    ),
                    error,
                    session.analysis
                )
                session.improvement = improvement
        
        # Store in memory if available
        if self.memory_manager and session.correction and session.correction.success:
            self._store_successful_correction_in_memory(session)
        
        # Record timing
        session.total_time_ms = (time.time() - start_time) * 1000
        
        return session
    
    def _store_successful_correction_in_memory(self, session: SelfCorrectionSession) -> None:
        """Store successful correction as procedural memory"""
        if not self.memory_manager:
            return
        
        try:
            steps = [
                {
                    "step": 1,
                    "action": "detect",
                    "description": f"Detected {session.error.error_type.value}"
                },
                {
                    "step": 2,
                    "action": "analyze",
                    "description": f"Analyzed: {session.analysis.root_cause_hypothesis}" if session.analysis else "Analysis performed"
                },
                {
                    "step": 3,
                    "action": "correct",
                    "description": f"Applied {session.correction.strategy.value} strategy" if session.correction else "Correction attempted"
                }
            ]
            
            self.memory_manager.store_procedural(
                name=f"correction_procedure_{session.error.error_type.value}",
                steps=steps,
                parameters={"error_type": session.error.error_type.value},
                complexity=5
            )
        except Exception:
            pass
    
    def get_system_health(self) -> SystemHealthReport:
        """Generate system health report"""
        
        # Count corrections
        total_errors = self.error_detector.total_errors_detected
        successful_corrections = sum(
            1 for session in self.sessions.values()
            if session.correction and session.correction.success
        )
        failed_corrections = sum(
            1 for session in self.sessions.values()
            if session.correction and not session.correction.success
        )
        
        # Get critical issues
        critical_errors = self.error_detector.get_critical_errors()
        active_initiatives = len(
            [s for s in self.improvement_system.improvement_suggestions if s.priority >= 8]
        )
        
        # Calculate scores
        if total_errors > 0:
            success_rate = successful_corrections / total_errors
        else:
            success_rate = 1.0
        
        stability_score = success_rate * 100
        recovery_efficiency = (successful_corrections / (total_errors + 1)) * 100
        
        # Generate recommendations
        recommendations = []
        if len(critical_errors) > 0:
            recommendations.append(
                f"Address {len(critical_errors)} critical error patterns"
            )
        
        recurring = self.error_detector.get_recurring_errors()
        if len(recurring) > 2:
            recommendations.append(
                f"Implement preventive measures for {len(recurring)} recurring errors"
            )
        
        top_improvements = self.improvement_system.get_top_improvements(3)
        for improvement in top_improvements:
            recommendations.append(improvement.description)
        
        return SystemHealthReport(
            total_errors_handled=total_errors,
            successful_corrections=successful_corrections,
            failed_corrections=failed_corrections,
            active_improvement_initiatives=active_initiatives,
            critical_issues_remaining=len(critical_errors),
            system_stability_score=stability_score,
            recovery_efficiency=recovery_efficiency,
            recommendations=recommendations[:5]
        )
    
    def get_session_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent session history"""
        recent = sorted(
            self.sessions.values(),
            key=lambda s: s.timestamp,
            reverse=True
        )[:limit]
        
        return [session.to_dict() for session in recent]
    
    def generate_correction_report(self) -> Dict[str, Any]:
        """Generate comprehensive correction report"""
        
        sessions = list(self.sessions.values())
        successful = [s for s in sessions if s.final_success]
        failed = [s for s in sessions if not s.final_success]
        
        correction_stats = self.correction_engine.get_stats()
        improvement_stats = self.improvement_system.get_stats()
        error_stats = self.error_detector.get_stats()
        
        # Calculate trend
        recent_sessions = sorted(sessions, key=lambda s: s.timestamp, reverse=True)[:50]
        if recent_sessions:
            recent_success_rate = sum(1 for s in recent_sessions if s.final_success) / len(recent_sessions)
        else:
            recent_success_rate = 0.0
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "sessions": {
                "total": len(sessions),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(sessions) if sessions else 0.0,
                "recent_success_rate": recent_success_rate
            },
            "error_detection": error_stats,
            "correction_strategies": correction_stats,
            "improvement_system": improvement_stats,
            "system_health": self.get_system_health().to_dict(),
            "error_patterns": {
                "recurring": len(self.error_detector.get_recurring_errors()),
                "critical": len(self.error_detector.get_critical_errors()),
                "total_patterns": error_stats.get("total_patterns_found", 0)
            }
        }
    
    def enable_auto_correction(self, enabled: bool = True) -> None:
        """Enable/disable automatic correction"""
        self.auto_correct = enabled
    
    def enable_learning(self, enabled: bool = True) -> None:
        """Enable/disable adaptive learning"""
        self.learning_enabled = enabled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "total_sessions": len(self.sessions),
            "total_errors_detected": self.error_detector.total_errors_detected,
            "successful_sessions": sum(
                1 for s in self.sessions.values() if s.final_success
            ),
            "auto_correction_enabled": self.auto_correct,
            "learning_enabled": self.learning_enabled,
            "orchestrator_enabled": self.enabled,
            "error_detector_stats": self.error_detector.get_stats(),
            "correction_engine_stats": self.correction_engine.get_stats(),
            "improvement_system_stats": self.improvement_system.get_stats()
        }
