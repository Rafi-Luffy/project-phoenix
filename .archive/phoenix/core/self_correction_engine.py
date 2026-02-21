"""
Self-Correction Engine - Module 2: Self-Correction Engine
Error detection, feedback loops, and correction strategies
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import uuid
from dataclasses import dataclass, field


class ErrorCategory(Enum):
    DETECTION_ERROR = "detection_error"
    DECISION_ERROR = "decision_error"
    EXECUTION_ERROR = "execution_error"
    TIMING_ERROR = "timing_error"
    CONSISTENCY_ERROR = "consistency_error"
    UNKNOWN = "unknown"


class CorrectionMethod(Enum):
    RULE_BASED = "rule_based"
    ML_BASED = "ml_based"
    HYBRID = "hybrid"
    ROLLBACK = "rollback"
    REFINEMENT = "refinement"


@dataclass
class DetectedError:
    """Represents a detected error in the system"""
    error_id: str
    category: ErrorCategory
    source: str
    description: str
    severity: int  # 1-10
    detected_at: datetime = field(default_factory=datetime.now)
    affected_action_id: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> Dict:
        return {
            'error_id': self.error_id,
            'category': self.category.value,
            'source': self.source,
            'description': self.description,
            'severity': self.severity,
            'detected_at': self.detected_at.isoformat(),
            'confidence': self.confidence
        }


@dataclass
class CorrectionAction:
    """Represents an action to correct an error"""
    correction_id: str
    error_id: str
    method: CorrectionMethod
    original_decision: str
    corrected_decision: str
    rationale: str
    confidence: float
    estimated_impact: str
    created_at: datetime = field(default_factory=datetime.now)
    applied: bool = False
    result: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'correction_id': self.correction_id,
            'error_id': self.error_id,
            'method': self.method.value,
            'original': self.original_decision,
            'corrected': self.corrected_decision,
            'rationale': self.rationale,
            'confidence': self.confidence,
            'applied': self.applied
        }


class ErrorDetectionEngine:
    """Detects errors in decision-making and execution"""

    def __init__(self):
        self.detected_errors: Dict[str, DetectedError] = {}
        self.error_patterns: Dict[str, int] = {}
        self.false_positive_rate = 0.0

    def detect_anomaly(self, metric_name: str, current_value: float, 
                      baseline: float, threshold: float = 2.0) -> Optional[DetectedError]:
        """Detect anomalies using statistical deviation"""
        deviation = abs(current_value - baseline) / (baseline + 0.001)
        
        if deviation > threshold:
            error_id = str(uuid.uuid4())
            error = DetectedError(
                error_id=error_id,
                category=ErrorCategory.DETECTION_ERROR,
                source="anomaly_detector",
                description=f"Metric {metric_name} deviated {deviation:.2f}x from baseline",
                severity=min(10, int(deviation * 5)),
                evidence=[f"baseline={baseline}", f"current={current_value}"]
            )
            self.detected_errors[error_id] = error
            return error
        
        return None

    def detect_decision_mismatch(self, expected_outcome: str, 
                                actual_outcome: str) -> Optional[DetectedError]:
        """Detect when actual outcome differs from expected"""
        if expected_outcome != actual_outcome:
            error_id = str(uuid.uuid4())
            error = DetectedError(
                error_id=error_id,
                category=ErrorCategory.DECISION_ERROR,
                source="outcome_validator",
                description=f"Expected {expected_outcome}, got {actual_outcome}",
                severity=7,
                evidence=[f"expected={expected_outcome}", f"actual={actual_outcome}"],
                confidence=0.95
            )
            self.detected_errors[error_id] = error
            return error
        
        return None

    def detect_timeout(self, operation: str, elapsed_time: float, 
                      timeout_threshold: float) -> Optional[DetectedError]:
        """Detect timeout conditions"""
        if elapsed_time > timeout_threshold:
            error_id = str(uuid.uuid4())
            error = DetectedError(
                error_id=error_id,
                category=ErrorCategory.TIMING_ERROR,
                source="timeout_detector",
                description=f"Operation {operation} exceeded timeout ({elapsed_time:.2f}s > {timeout_threshold:.2f}s)",
                severity=8,
                evidence=[f"elapsed={elapsed_time}", f"timeout={timeout_threshold}"]
            )
            self.detected_errors[error_id] = error
            return error
        
        return None

    def detect_consistency_violation(self, state_id: str, 
                                    expected_state: Dict[str, Any],
                                    actual_state: Dict[str, Any]) -> Optional[DetectedError]:
        """Detect state consistency violations"""
        mismatches = []
        for key in expected_state:
            if key not in actual_state:
                mismatches.append(f"missing_{key}")
            elif expected_state[key] != actual_state[key]:
                mismatches.append(f"mismatch_{key}")

        if mismatches:
            error_id = str(uuid.uuid4())
            error = DetectedError(
                error_id=error_id,
                category=ErrorCategory.CONSISTENCY_ERROR,
                source="consistency_checker",
                description=f"State {state_id} has {len(mismatches)} inconsistencies",
                severity=min(10, len(mismatches) * 2),
                evidence=mismatches,
                confidence=0.9
            )
            self.detected_errors[error_id] = error
            return error
        
        return None

    def get_error_pattern(self, pattern_type: str) -> int:
        """Get occurrence count of error pattern"""
        return self.error_patterns.get(pattern_type, 0)

    def record_pattern(self, pattern_type: str):
        """Record an error pattern occurrence"""
        self.error_patterns[pattern_type] = self.error_patterns.get(pattern_type, 0) + 1


class FeedbackLoop:
    """Implements self-feedback mechanism"""

    def __init__(self):
        self.feedback_records: List[Dict[str, Any]] = []
        self.reflection_history: List[Dict[str, Any]] = []

    def generate_self_feedback(self, action_id: str, 
                              expected_result: Any, 
                              actual_result: Any) -> Dict[str, Any]:
        """Generate feedback on own actions"""
        is_correct = expected_result == actual_result
        
        feedback = {
            'feedback_id': str(uuid.uuid4()),
            'action_id': action_id,
            'expected': expected_result,
            'actual': actual_result,
            'is_correct': is_correct,
            'confidence': 0.95 if is_correct else 0.8,
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_records.append(feedback)
        return feedback

    def reflect_on_failure(self, error: DetectedError) -> Dict[str, Any]:
        """Self-reflection on detected errors"""
        reflection = {
            'reflection_id': str(uuid.uuid4()),
            'error_id': error.error_id,
            'error_category': error.category.value,
            'analysis': self._analyze_error(error),
            'lessons_learned': self._extract_lessons(error),
            'timestamp': datetime.now().isoformat()
        }
        
        self.reflection_history.append(reflection)
        return reflection

    def _analyze_error(self, error: DetectedError) -> str:
        """Analyze error causes"""
        if error.category == ErrorCategory.DETECTION_ERROR:
            return "Failed to properly detect component state changes"
        elif error.category == ErrorCategory.DECISION_ERROR:
            return "Decision making algorithm selected suboptimal action"
        elif error.category == ErrorCategory.TIMING_ERROR:
            return "Recovery action took longer than expected"
        elif error.category == ErrorCategory.CONSISTENCY_ERROR:
            return "System state divergence detected"
        else:
            return "Unknown error source"

    def _extract_lessons(self, error: DetectedError) -> List[str]:
        """Extract lessons from error"""
        lessons = []
        
        if error.severity >= 8:
            lessons.append("High severity - needs immediate prevention strategy")
        
        if error.confidence >= 0.9:
            lessons.append("High confidence detection - pattern is reliable")
        
        if error.category == ErrorCategory.TIMING_ERROR:
            lessons.append("Need to adjust timeout thresholds")
        
        if len(error.evidence) > 3:
            lessons.append("Multiple evidence points - pattern is clear")
        
        return lessons

    def get_accuracy_metrics(self) -> Dict[str, float]:
        """Get feedback accuracy metrics"""
        if not self.feedback_records:
            return {}

        correct_count = sum(1 for f in self.feedback_records if f['is_correct'])
        total_count = len(self.feedback_records)
        
        return {
            'accuracy': correct_count / total_count if total_count > 0 else 0,
            'total_feedback': total_count,
            'correct_predictions': correct_count,
            'error_rate': 1 - (correct_count / total_count) if total_count > 0 else 0
        }


class CorrectionStrategies:
    """Implements various correction strategies"""

    def __init__(self):
        self.rule_base: Dict[str, str] = {}
        self.correction_history: List[CorrectionAction] = []

    def add_correction_rule(self, error_pattern: str, correction: str):
        """Add rule-based correction"""
        self.rule_base[error_pattern] = correction

    def rule_based_correction(self, error: DetectedError) -> Optional[CorrectionAction]:
        """Apply rule-based correction"""
        for pattern, correction in self.rule_base.items():
            if pattern.lower() in error.description.lower():
                correction_action = CorrectionAction(
                    correction_id=str(uuid.uuid4()),
                    error_id=error.error_id,
                    method=CorrectionMethod.RULE_BASED,
                    original_decision="failed_action",
                    corrected_decision=correction,
                    rationale=f"Rule matched pattern: {pattern}",
                    confidence=0.85,
                    estimated_impact="positive"
                )
                self.correction_history.append(correction_action)
                return correction_action
        
        return None

    def ml_based_correction(self, error: DetectedError, 
                           similar_past_corrections: List[CorrectionAction]) -> Optional[CorrectionAction]:
        """Apply ML-based correction using similar past cases"""
        if not similar_past_corrections:
            return None

        # Find most similar correction
        best_match = max(similar_past_corrections, 
                        key=lambda x: x.confidence)

        correction_action = CorrectionAction(
            correction_id=str(uuid.uuid4()),
            error_id=error.error_id,
            method=CorrectionMethod.ML_BASED,
            original_decision="failed_action",
            corrected_decision=best_match.corrected_decision,
            rationale=f"Similar pattern handled with: {best_match.corrected_decision}",
            confidence=best_match.confidence * 0.9,  # Slightly lower confidence for new case
            estimated_impact="positive"
        )
        self.correction_history.append(correction_action)
        return correction_action

    def hybrid_correction(self, error: DetectedError, 
                         rule_correction: Optional[CorrectionAction],
                         ml_correction: Optional[CorrectionAction]) -> Optional[CorrectionAction]:
        """Combine rule-based and ML-based approaches"""
        if not rule_correction and not ml_correction:
            return None

        if rule_correction and ml_correction:
            # Combine both approaches
            chosen = rule_correction if rule_correction.confidence >= ml_correction.confidence else ml_correction
        else:
            chosen = rule_correction or ml_correction

        correction_action = CorrectionAction(
            correction_id=str(uuid.uuid4()),
            error_id=error.error_id,
            method=CorrectionMethod.HYBRID,
            original_decision=chosen.original_decision,
            corrected_decision=chosen.corrected_decision,
            rationale=f"Hybrid approach: {chosen.rationale}",
            confidence=min(0.95, chosen.confidence * 1.05),
            estimated_impact="positive"
        )
        self.correction_history.append(correction_action)
        return correction_action

    def rollback_correction(self, error: DetectedError, 
                           previous_state: Dict[str, Any]) -> CorrectionAction:
        """Apply rollback correction"""
        correction_action = CorrectionAction(
            correction_id=str(uuid.uuid4()),
            error_id=error.error_id,
            method=CorrectionMethod.ROLLBACK,
            original_decision="failed_action",
            corrected_decision="rollback_to_previous_state",
            rationale="Rolling back to last known good state",
            confidence=0.95,
            estimated_impact="neutral_to_positive"
        )
        self.correction_history.append(correction_action)
        return correction_action

    def get_correction_effectiveness(self) -> Dict[str, float]:
        """Measure effectiveness of corrections"""
        if not self.correction_history:
            return {}

        successful = sum(1 for c in self.correction_history if c.result == "success")
        total = len(self.correction_history)

        by_method = {}
        for method in CorrectionMethod:
            method_corrections = [c for c in self.correction_history if c.method == method]
            if method_corrections:
                successful_method = sum(1 for c in method_corrections if c.result == "success")
                by_method[method.value] = successful_method / len(method_corrections)

        return {
            'overall_effectiveness': successful / total if total > 0 else 0,
            'total_corrections': total,
            'successful_corrections': successful,
            'by_method': by_method
        }


class SelfCorrectionEngine:
    """Main engine coordinating self-correction"""

    def __init__(self):
        self.error_detector = ErrorDetectionEngine()
        self.feedback_loop = FeedbackLoop()
        self.correction_strategies = CorrectionStrategies()
        self.correction_queue: List[CorrectionAction] = []

    def detect_and_correct(self, error: DetectedError) -> Optional[CorrectionAction]:
        """Detect error and find correction"""
        # Step 1: Record reflection
        reflection = self.feedback_loop.reflect_on_failure(error)

        # Step 2: Try different correction strategies
        rule_correction = self.correction_strategies.rule_based_correction(error)
        ml_correction = self.correction_strategies.ml_based_correction(
            error, 
            self.correction_strategies.correction_history[-10:]
        )

        # Step 3: Select best correction
        if rule_correction and ml_correction:
            correction = self.correction_strategies.hybrid_correction(
                error, rule_correction, ml_correction
            )
        else:
            correction = rule_correction or ml_correction

        if correction:
            self.correction_queue.append(correction)
            return correction

        # Step 4: Fallback to rollback
        correction = self.correction_strategies.rollback_correction(error, {})
        self.correction_queue.append(correction)
        return correction

    def get_status(self) -> Dict[str, Any]:
        """Get correction engine status"""
        return {
            'detected_errors': len(self.error_detector.detected_errors),
            'pending_corrections': len(self.correction_queue),
            'feedback_accuracy': self.feedback_loop.get_accuracy_metrics(),
            'correction_effectiveness': self.correction_strategies.get_correction_effectiveness(),
            'error_patterns': dict(self.error_detector.error_patterns)
        }
