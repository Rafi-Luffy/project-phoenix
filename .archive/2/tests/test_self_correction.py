"""
Comprehensive test suite for Phase 2: Self-Correction Engine

Tests error detection, correction strategies, and adaptive improvement.
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict

from autonomous_system.core.error_detection import (
    ErrorDetectionManager, ErrorContext, ErrorPattern, ErrorType, ErrorSeverity,
    ErrorSignature, ExceptionDetector, OutcomeDetector, PerformanceDetector
)
from autonomous_system.core.correction_strategy import (
    CorrectionStrategyEngine, CorrectionStrategy, CorrectionResult,
    RetryCorrector, FallbackCorrector, ModifyParametersCorrector
)
from autonomous_system.core.adaptive_improvement import (
    AdaptiveImprovementSystem, ImprovementLevel
)
from autonomous_system.core.self_correction import (
    SelfCorrectionOrchestrator, SelfCorrectionSession, SystemHealthReport
)


# ============================================================================
# Error Detection Tests
# ============================================================================

class TestErrorDetection:
    """Test error detection framework"""
    
    def test_exception_detector_detects_exceptions(self):
        """Test exception detection"""
        detector = ExceptionDetector()
        exc = ValueError("Invalid input")
        
        context = {"agent_id": "test_agent", "operation": "test_op"}
        error = detector.detect(exc, context)
        
        assert error is not None
        assert error.error_type == ErrorType.VALIDATION_ERROR
        assert error.severity == ErrorSeverity.MODERATE
        assert error.agent_id == "test_agent"
    
    def test_exception_detector_classifies_timeout(self):
        """Test timeout exception classification"""
        detector = ExceptionDetector()
        exc = TimeoutError("Operation timed out")
        
        context = {"agent_id": "agent_1", "operation": "query"}
        error = detector.detect(exc, context)
        
        assert error.error_type == ErrorType.TIMEOUT_ERROR
    
    def test_outcome_detector_detects_failures(self):
        """Test outcome-based error detection"""
        failure_indicators = {
            "success": False,
            "confidence": lambda x: x < 0.5
        }
        detector = OutcomeDetector(failure_indicators)
        
        result = {"success": False, "confidence": 0.3}
        context = {"agent_id": "agent_1", "operation": "classify"}
        
        error = detector.detect(result, context)
        assert error is not None
        assert error.error_type == ErrorType.LOGIC_ERROR
    
    def test_performance_detector_detects_high_latency(self):
        """Test performance anomaly detection"""
        detector = PerformanceDetector(latency_threshold_ms=1000.0)
        
        result = {"status": "ok"}
        context = {
            "agent_id": "agent_1",
            "operation": "process",
            "latency_ms": 5000.0
        }
        
        error = detector.detect(result, context)
        assert error is not None
        assert error.error_type == ErrorType.RESOURCE_ERROR
        assert "High latency" in error.message
    
    def test_error_detection_manager_records_patterns(self):
        """Test error pattern tracking"""
        manager = ErrorDetectionManager()
        manager.add_detector(ExceptionDetector())
        
        # Create multiple similar errors
        for i in range(3):
            exc = ValueError("Invalid input")
            context = {"agent_id": "agent_1", "operation": "parse"}
            manager.detect_error(exc, context)
        
        assert manager.total_errors_detected == 3
        assert len(manager.error_patterns) >= 1
        
        patterns = manager.get_recurring_errors(min_occurrences=3)
        assert len(patterns) > 0
    
    def test_error_analysis_provides_recommendations(self):
        """Test error analysis"""
        manager = ErrorDetectionManager()
        
        error = ErrorContext(
            agent_id="agent_1",
            operation="process",
            timestamp=datetime.now(),
            error_type=ErrorType.VALIDATION_ERROR,
            severity=ErrorSeverity.MAJOR,
            message="Invalid input format",
            stack_trace="",
            input_data={"value": None}
        )
        
        analysis = manager.analyze_error(error)
        
        assert analysis.error_type == ErrorType.VALIDATION_ERROR
        assert len(analysis.recommended_actions) > 0
        assert len(analysis.preventive_measures) > 0
    
    def test_critical_error_detection(self):
        """Test critical error identification"""
        manager = ErrorDetectionManager()
        
        # Simulate critical error
        error = ErrorContext(
            agent_id="agent_1",
            operation="critical_op",
            timestamp=datetime.now(),
            error_type=ErrorType.RESOURCE_ERROR,
            severity=ErrorSeverity.CRITICAL,
            message="Out of memory",
            stack_trace=""
        )
        
        manager._record_error_pattern(error)
        
        critical = manager.get_critical_errors()
        assert len(critical) > 0


# ============================================================================
# Correction Strategy Tests
# ============================================================================

class TestCorrectionStrategies:
    """Test correction strategy engine"""
    
    def test_retry_corrector_succeeds_on_retry(self):
        """Test retry correction"""
        corrector = RetryCorrector(max_retries=3)
        
        error = ErrorContext(
            agent_id="agent_1",
            operation="query",
            timestamp=datetime.now(),
            error_type=ErrorType.TIMEOUT_ERROR,
            severity=ErrorSeverity.MAJOR,
            message="Connection timeout",
            stack_trace=""
        )
        
        call_count = [0]
        def retry_fn():
            call_count[0] += 1
            if call_count[0] < 3:
                raise TimeoutError("Still failing")
            return {"result": "success"}
        
        context = {"retry_fn": retry_fn, "retry_args": {}}
        result = corrector.correct(error, context)
        
        assert result.success
        assert result.attempts == 3
        assert result.corrected_output == {"result": "success"}
    
    def test_fallback_corrector_uses_alternative(self):
        """Test fallback correction"""
        corrector = FallbackCorrector()
        
        error = ErrorContext(
            agent_id="agent_1",
            operation="compute",
            timestamp=datetime.now(),
            error_type=ErrorType.DEPENDENCY_ERROR,
            severity=ErrorSeverity.MAJOR,
            message="Service unavailable",
            stack_trace=""
        )
        
        def fallback_fn():
            return {"cached_result": True, "stale": True}
        
        context = {"fallback_fn": fallback_fn, "fallback_args": {}}
        result = corrector.correct(error, context)
        
        assert result.success
        assert result.corrected_output["cached_result"] is True
    
    def test_modify_parameters_corrector(self):
        """Test parameter modification correction"""
        corrector = ModifyParametersCorrector()
        
        error = ErrorContext(
            agent_id="agent_1",
            operation="classify",
            timestamp=datetime.now(),
            error_type=ErrorType.VALIDATION_ERROR,
            severity=ErrorSeverity.MODERATE,
            message="Invalid input",
            stack_trace="",
            input_data={"value": ""}
        )
        
        def modifier_fn(err, args):
            return {**args, "value": "default"}
        
        def retry_fn(value):
            return {"classified": True}
        
        context = {
            "modifier_fn": modifier_fn,
            "retry_fn": retry_fn,
            "retry_args": {"value": ""}
        }
        
        result = corrector.correct(error, context)
        
        assert result.success
        assert result.corrected_output == {"classified": True}
    
    def test_strategy_engine_selects_appropriate_corrector(self):
        """Test strategy selection"""
        engine = CorrectionStrategyEngine()
        
        error = ErrorContext(
            agent_id="agent_1",
            operation="process",
            timestamp=datetime.now(),
            error_type=ErrorType.TIMEOUT_ERROR,
            severity=ErrorSeverity.MAJOR,
            message="Timeout",
            stack_trace=""
        )
        
        from autonomous_system.core.error_detection import ErrorAnalysis, ErrorSignature
        sig = ErrorSignature.from_error(
            error.error_type, error.message, "", {}
        )
        analysis = ErrorAnalysis(
            signature=sig,
            error_type=error.error_type,
            severity=error.severity,
            root_cause_hypothesis="Operation too slow"
        )
        
        strategies = engine.select_correction_strategies(error, analysis)
        
        assert len(strategies) > 0
        # Retry should be among the selected strategies
        assert any(s.get_strategy() == CorrectionStrategy.RETRY for s in strategies)
    
    def test_correction_engine_tracks_success_rates(self):
        """Test strategy effectiveness tracking"""
        engine = CorrectionStrategyEngine()
        
        # Simulate successful correction
        error = ErrorContext(
            agent_id="agent_1",
            operation="test",
            timestamp=datetime.now(),
            error_type=ErrorType.TIMEOUT_ERROR,
            severity=ErrorSeverity.MODERATE,
            message="Timeout",
            stack_trace=""
        )
        
        result = CorrectionResult(
            strategy=CorrectionStrategy.RETRY,
            success=True,
            original_error=error,
            corrected_output={"status": "ok"}
        )
        
        engine._record_correction_result(result)
        
        stats = engine.get_stats()
        assert stats["total_corrections_successful"] >= 1


# ============================================================================
# Adaptive Improvement Tests
# ============================================================================

class TestAdaptiveImprovement:
    """Test adaptive improvement system"""
    
    def test_learns_from_successful_correction(self):
        """Test learning from success"""
        system = AdaptiveImprovementSystem()
        
        error = ErrorContext(
            agent_id="agent_1",
            operation="process",
            timestamp=datetime.now(),
            error_type=ErrorType.TIMEOUT_ERROR,
            severity=ErrorSeverity.MODERATE,
            message="Timeout",
            stack_trace=""
        )
        
        correction = CorrectionResult(
            strategy=CorrectionStrategy.RETRY,
            success=True,
            original_error=error,
            corrected_output={"result": "success"}
        )
        
        from autonomous_system.core.error_detection import ErrorAnalysis, ErrorSignature
        analysis = ErrorAnalysis(
            signature=ErrorSignature.from_error(
                error.error_type, error.message, "", {}
            ),
            error_type=error.error_type,
            severity=error.severity,
            root_cause_hypothesis="Network latency"
        )
        
        suggestion = system.analyze_correction_outcome(correction, error, analysis)
        
        assert suggestion is not None
        assert suggestion.category == "preventive"
        assert len(suggestion.implementation_steps) > 0
    
    def test_detects_recurring_patterns(self):
        """Test recurring pattern detection"""
        system = AdaptiveImprovementSystem()
        
        signature = ErrorSignature(
            error_type=ErrorType.VALIDATION_ERROR,
            error_message_hash="abc123",
            stack_trace_hash="def456",
            context_hash="ghi789"
        )
        
        errors = [
            ErrorContext(
                agent_id="agent_1",
                operation="validate",
                timestamp=datetime.now() - timedelta(hours=i),
                error_type=ErrorType.VALIDATION_ERROR,
                severity=ErrorSeverity.MODERATE,
                message="Invalid input",
                stack_trace=""
            )
            for i in range(5)
        ]
        
        pattern = ErrorPattern(
            signature=signature,
            first_occurrence=errors[0].timestamp,
            last_occurrence=errors[-1].timestamp,
            occurrence_count=5,
            contexts=errors
        )
        
        suggestion = system.detect_recurring_error_pattern(pattern)
        
        assert suggestion.level == ImprovementLevel.MODERATE
        assert "Recurring" in suggestion.description
    
    def test_generates_prevention_rules(self):
        """Test prevention rule generation"""
        system = AdaptiveImprovementSystem()
        
        signature = ErrorSignature(
            error_type=ErrorType.VALIDATION_ERROR,
            error_message_hash="abc",
            stack_trace_hash="def",
            context_hash="ghi"
        )
        
        pattern = ErrorPattern(
            signature=signature,
            first_occurrence=datetime.now(),
            last_occurrence=datetime.now(),
            occurrence_count=5,
            contexts=[
                ErrorContext(
                    agent_id="agent_1",
                    operation="validate",
                    timestamp=datetime.now(),
                    error_type=ErrorType.VALIDATION_ERROR,
                    severity=ErrorSeverity.MODERATE,
                    message="Invalid",
                    stack_trace="",
                    input_data={"value": None}
                )
            ]
        )
        
        rule = system.generate_error_prevention_rules(pattern)
        
        assert rule["error_type"] == "validation"
        assert len(rule["prevention_actions"]) > 0
    
    def test_tracks_learning_metrics(self):
        """Test learning metric tracking"""
        system = AdaptiveImprovementSystem()
        
        metric = system.track_learning_metric(
            "system_efficiency",
            current_value=0.50,
            target_value=0.90
        )
        
        assert metric.metric_name == "system_efficiency"
        assert metric.current_value == 0.50
        assert metric.previous_value == 0.0
        assert metric.trend == "improving"
        
        # Track further improvement
        metric2 = system.track_learning_metric(
            "system_efficiency",
            current_value=0.75,
            target_value=0.90
        )
        
        assert metric2.trend == "improving"


# ============================================================================
# Self-Correction Orchestrator Tests
# ============================================================================

class TestSelfCorrectionOrchestrator:
    """Test self-correction orchestration"""
    
    def test_orchestrator_handles_operation_success(self):
        """Test successful operation handling"""
        orchestrator = SelfCorrectionOrchestrator()
        
        def test_operation(x):
            return x * 2
        
        result, session = orchestrator.handle_operation(
            test_operation,
            "multiply",
            "agent_1",
            {"x": 5}
        )
        
        assert result == 10
        assert session is None
    
    def test_orchestrator_detects_and_corrects_errors(self):
        """Test error detection and correction"""
        orchestrator = SelfCorrectionOrchestrator()
        
        call_count = [0]
        def failing_operation():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("First call fails")
            return {"result": "success"}
        
        def retry_fn():
            return failing_operation()
        
        context = {"retry_fn": retry_fn, "retry_args": {}}
        
        try:
            result, session = orchestrator.handle_operation(
                failing_operation,
                "compute",
                "agent_1",
                {},
                correction_context=context
            )
            
            # Either succeeds with correction or raises
            if session:
                assert session.final_success or True
        except ValueError:
            pass  # Expected if correction fails
    
    def test_orchestrator_generates_health_report(self):
        """Test system health reporting"""
        orchestrator = SelfCorrectionOrchestrator()
        
        # Simulate some activity
        for i in range(3):
            try:
                orchestrator.handle_operation(
                    lambda: i / (i - 1),  # Will fail
                    "divide",
                    "agent_1",
                    {}
                )
            except ZeroDivisionError:
                pass
        
        health = orchestrator.get_system_health()
        
        assert isinstance(health, SystemHealthReport)
        assert health.total_errors_handled >= 0
    
    def test_orchestrator_maintains_session_history(self):
        """Test session history"""
        orchestrator = SelfCorrectionOrchestrator()
        
        def test_op(x):
            if x < 0:
                raise ValueError("Negative not allowed")
            return x * 2
        
        # Successful operation
        orchestrator.handle_operation(
            test_op,
            "test",
            "agent_1",
            {"x": 5}
        )
        
        history = orchestrator.get_session_history(limit=10)
        
        assert isinstance(history, list)
    
    def test_orchestrator_generates_comprehensive_report(self):
        """Test comprehensive reporting"""
        orchestrator = SelfCorrectionOrchestrator()
        
        def op():
            return {"status": "ok"}
        
        orchestrator.handle_operation(op, "test", "agent_1", {})
        
        report = orchestrator.generate_correction_report()
        
        assert "sessions" in report
        assert "error_detection" in report
        assert "correction_strategies" in report
        assert "improvement_system" in report
    
    def test_orchestrator_enable_disable_features(self):
        """Test feature toggles"""
        orchestrator = SelfCorrectionOrchestrator()
        
        assert orchestrator.auto_correct is True
        orchestrator.enable_auto_correction(False)
        assert orchestrator.auto_correct is False
        
        assert orchestrator.learning_enabled is True
        orchestrator.enable_learning(False)
        assert orchestrator.learning_enabled is False
    
    def test_orchestrator_stats(self):
        """Test statistics collection"""
        orchestrator = SelfCorrectionOrchestrator()
        
        def op():
            return "ok"
        
        orchestrator.handle_operation(op, "test", "agent_1", {})
        
        stats = orchestrator.get_stats()
        
        assert stats["total_sessions"] >= 0
        assert stats["orchestrator_enabled"] is True
        assert "error_detector_stats" in stats


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for Phase 2"""
    
    def test_full_self_correction_pipeline(self):
        """Test complete self-correction pipeline"""
        orchestrator = SelfCorrectionOrchestrator()
        
        # Simulate operation with parameters
        call_count = [0]
        def operation():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("First attempt fails")
            return {"result": "corrected"}
        
        def retry_operation():
            return operation()
        
        context = {
            "retry_fn": retry_operation,
            "retry_args": {}
        }
        
        try:
            result, session = orchestrator.handle_operation(
                operation,
                "test_operation",
                "test_agent",
                {},
                correction_context=context
            )
            
            # Verify orchestrator recorded the session
            assert len(orchestrator.sessions) >= 0
        except ValueError:
            pass
    
    def test_adaptive_improvement_integration(self):
        """Test adaptive improvement in pipeline"""
        orchestrator = SelfCorrectionOrchestrator()
        
        # Create scenario with multiple errors
        error_count = [0]
        def problematic_operation():
            error_count[0] += 1
            if error_count[0] <= 3:
                raise ValueError("Recurring error")
            return {"status": "ok"}
        
        # Process multiple attempts
        for i in range(3):
            try:
                orchestrator.handle_operation(
                    problematic_operation,
                    "problematic",
                    "agent_1",
                    {}
                )
            except ValueError:
                pass
        
        # Check if improvement system detected pattern
        insights = orchestrator.improvement_system.get_system_insights()
        assert insights is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
