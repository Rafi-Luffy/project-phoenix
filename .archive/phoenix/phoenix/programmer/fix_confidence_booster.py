"""
Fix Confidence Booster

Improves LLM fix generation with better prompting and confidence scoring.
Helps ensure fixes are high-quality and safe.

Uses only standard library - no external dependencies needed.
"""

from typing import Dict, List, Any
from enum import Enum

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class ConfidenceLevel(str, Enum):
    """How confident we are in a fix."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class FixConfidenceAnalyzer:
    """
    Analyzes and improves fix confidence.
    
    Factors that increase confidence:
    - Similar fixes succeeded before
    - Failure pattern is well-understood
    - Fix has been validated
    - LLM confidence is high
    - Similar failures in codebase
    """
    
    def __init__(self):
        """Initialize confidence analyzer."""
        self.logger = get_logger(__name__)
        self.success_history: Dict[str, int] = {}  # failure_type -> success_count
        self.failure_history: Dict[str, int] = {}  # failure_type -> failure_count
    
    def record_fix_result(self, failure_type: str, success: bool):
        """Track if a fix succeeded or failed."""
        if success:
            self.success_history[failure_type] = self.success_history.get(failure_type, 0) + 1
        else:
            self.failure_history[failure_type] = self.failure_history.get(failure_type, 0) + 1
    
    def get_confidence_level(
        self,
        failure_type: str,
        llm_confidence: float,
        has_similar_fixes: bool,
        fix_has_tests: bool,
    ) -> ConfidenceLevel:
        """
        Determine confidence level for a fix.
        
        Args:
            failure_type: Type of failure
            llm_confidence: LLM's confidence (0-1)
            has_similar_fixes: Did similar failures get fixed before?
            fix_has_tests: Does fix have validation tests?
        
        Returns:
            ConfidenceLevel
        """
        score = 0
        
        # Historical success (0-30 points)
        total_attempts = (
            self.success_history.get(failure_type, 0) +
            self.failure_history.get(failure_type, 0)
        )
        if total_attempts > 0:
            success_rate = (
                self.success_history.get(failure_type, 0) / total_attempts
            )
            score += success_rate * 30
        
        # LLM confidence (0-40 points)
        score += llm_confidence * 40
        
        # Has similar fixes (0-20 points)
        if has_similar_fixes:
            score += 20
        
        # Has validation tests (0-10 points)
        if fix_has_tests:
            score += 10
        
        # Convert score to confidence level
        if score >= 85:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 70:
            return ConfidenceLevel.HIGH
        elif score >= 50:
            return ConfidenceLevel.MEDIUM
        elif score >= 30:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def get_confidence_score(
        self,
        failure_type: str,
        llm_confidence: float,
        has_similar_fixes: bool,
        fix_has_tests: bool,
    ) -> float:
        """Get numerical confidence score (0-100)."""
        level = self.get_confidence_level(
            failure_type,
            llm_confidence,
            has_similar_fixes,
            fix_has_tests,
        )
        
        level_scores = {
            ConfidenceLevel.VERY_LOW: 20,
            ConfidenceLevel.LOW: 40,
            ConfidenceLevel.MEDIUM: 60,
            ConfidenceLevel.HIGH: 80,
            ConfidenceLevel.VERY_HIGH: 95,
        }
        
        return level_scores[level]
    
    def should_apply_fix(
        self,
        confidence_level: ConfidenceLevel,
        require_minimum: ConfidenceLevel = ConfidenceLevel.MEDIUM,
    ) -> bool:
        """
        Should we apply this fix?
        
        Args:
            confidence_level: Confidence in the fix
            require_minimum: Minimum acceptable confidence
        
        Returns:
            True if confidence meets threshold
        """
        level_order = [
            ConfidenceLevel.VERY_LOW,
            ConfidenceLevel.LOW,
            ConfidenceLevel.MEDIUM,
            ConfidenceLevel.HIGH,
            ConfidenceLevel.VERY_HIGH,
        ]
        
        return level_order.index(confidence_level) >= level_order.index(require_minimum)
    
    def improve_fix_prompt(
        self,
        failure_type: str,
        base_prompt: str,
        similar_fixes: List[str],
    ) -> str:
        """
        Enhance the fix generation prompt.
        
        Adds context about similar fixes, expected patterns, etc.
        
        Args:
            failure_type: Type of failure
            base_prompt: Original prompt
            similar_fixes: Previous successful fixes for similar issues
        
        Returns:
            Enhanced prompt
        """
        enhanced = base_prompt
        
        # Add historical context
        success_count = self.success_history.get(failure_type, 0)
        if success_count > 0:
            enhanced += f"\n\nNote: {success_count} similar fixes have succeeded before."
        
        # Add examples of similar fixes
        if similar_fixes:
            enhanced += "\n\nExamples of similar successful fixes:\n"
            for fix_example in similar_fixes[:3]:
                enhanced += f"- {fix_example}\n"
        
        # Add best practices for this failure type
        best_practices = self._get_best_practices(failure_type)
        if best_practices:
            enhanced += f"\n\nBest practices for {failure_type}:\n"
            for practice in best_practices:
                enhanced += f"- {practice}\n"
        
        return enhanced
    
    def _get_best_practices(self, failure_type: str) -> List[str]:
        """Get best practices for a failure type."""
        practices = {
            "timeout": [
                "Add retry logic with exponential backoff",
                "Increase timeout threshold gradually",
                "Add logging to identify slow operations",
            ],
            "memory_leak": [
                "Check for circular references",
                "Ensure cleanup in finally blocks",
                "Add resource monitoring",
            ],
            "race_condition": [
                "Use proper locking mechanisms",
                "Add synchronization points",
                "Consider using async/await patterns",
            ],
            "null_pointer": [
                "Add null checks before access",
                "Use optional types when available",
                "Add defensive copying",
            ],
            "agent_deadlock": [
                "Set timeout on agent communications",
                "Add deadlock detection",
                "Implement timeout-based recovery",
            ],
            "hallucination": [
                "Add fact-checking against knowledge base",
                "Constrain response formats",
                "Add confidence thresholds",
            ],
        }
        
        return practices.get(failure_type, [])


class FixQualityValidator:
    """
    Validates fix quality before application.
    
    Checks for: syntax errors, logic errors, security issues,
    test coverage, performance impact.
    """
    
    def __init__(self):
        """Initialize validator."""
        self.logger = get_logger(__name__)
    
    def validate_fix_quality(
        self,
        fix_code: str,
        validation_tests: str,
        failure_type: str,
    ) -> Dict[str, Any]:
        """
        Validate fix quality.
        
        Args:
            fix_code: The fix code
            validation_tests: Tests for the fix
            failure_type: Type of failure being fixed
        
        Returns:
            Validation results with issues and score
        """
        issues = []
        score = 100
        
        # Check for syntax issues
        if not self._has_proper_syntax(fix_code):
            issues.append("fix_code_syntax_issue")
            score -= 20
        
        # Check for common mistakes
        if self._has_dangerous_patterns(fix_code):
            issues.append("dangerous_patterns_detected")
            score -= 30
        
        # Check for test coverage
        if not validation_tests or len(validation_tests) < 50:
            issues.append("insufficient_test_coverage")
            score -= 15
        
        # Check for documentation
        if not self._has_documentation(fix_code):
            issues.append("missing_code_documentation")
            score -= 10
        
        # Check for specific failure type best practices
        if not self._follows_best_practices(fix_code, failure_type):
            issues.append("not_following_best_practices")
            score -= 10
        
        return {
            "is_valid": score >= 60,
            "quality_score": max(0, score),
            "issues": issues,
        }
    
    def _has_proper_syntax(self, code: str) -> bool:
        """Basic syntax check - supports Python and common patterns."""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
        except Exception:
            # For non-Python, check for obvious issues
            return self._basic_syntax_check(code)
    
    def _basic_syntax_check(self, code: str) -> bool:
        """Basic syntax validation for non-Python code."""
        # Check for matching braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        
        # Check for matching brackets
        open_brackets = code.count('[')
        close_brackets = code.count(']')
        
        # Check for matching parens
        open_parens = code.count('(')
        close_parens = code.count(')')
        
        return (
            open_braces == close_braces and
            open_brackets == close_brackets and
            open_parens == close_parens
        )
    
    def _has_dangerous_patterns(self, code: str) -> bool:
        """Check for dangerous patterns - comprehensive list."""
        dangerous = [
            # Code execution
            "eval(",
            "exec(",
            "__import__",
            "compile(",
            "pickle.loads(",
            
            # System access
            "shell=True",
            "subprocess.call",
            "os.system(",
            "os.popen(",
            
            # File access risks
            "../",
            "rm -rf",
            "/etc/",
            "/sys/",
            
            # Unsafe operations
            "unsafe",
            "deprecated",
            "todo:",
            "hack:",
            "fixme:",
        ]
        
        code_lower = code.lower()
        for pattern in dangerous:
            if pattern in code_lower:
                return True
        
        return False
    
    def _has_documentation(self, code: str) -> bool:
        """Check if code has documentation/comments - multiple formats."""
        # Python docstrings
        if '"""' in code or "'''" in code:
            return True
        
        # Single-line comments
        comment_chars = ['#', '//', '/*', '--', '///', '!']
        for char in comment_chars:
            if char in code:
                return True
        
        # Inline documentation
        doc_keywords = ['todo', 'fixme', 'note:', 'warning:', 'see also']
        for keyword in doc_keywords:
            if keyword in code.lower():
                return True
        
        return False
    
    def _follows_best_practices(self, code: str, failure_type: str) -> bool:
        """Check if fix follows failure-type best practices - more patterns."""
        code_lower = code.lower()
        failure_lower = failure_type.lower()
        
        if "timeout" in failure_lower:
            patterns = ["retry", "backoff", "exponential", "wait", "sleep"]
            return any(p in code_lower for p in patterns)
        
        elif "memory" in failure_lower:
            patterns = ["cleanup", "del ", "release", "dispose", "gc.collect", "free"]
            return any(p in code_lower for p in patterns)
        
        elif "race" in failure_lower or "concurrent" in failure_lower:
            patterns = ["lock", "async", "mutex", "semaphore", "atomic", "synchronized"]
            return any(p in code_lower for p in patterns)
        
        elif "deadlock" in failure_lower:
            patterns = ["timeout", "lock", "release", "deadlock_detection"]
            return any(p in code_lower for p in patterns)
        
        elif "null" in failure_lower or "none" in failure_lower:
            patterns = ["none", "null", "check", "is not", "!= none", "!= null", "optional"]
            return any(p in code_lower for p in patterns)
        
        elif "hallucination" in failure_lower:
            patterns = ["fact", "verify", "confidence", "threshold", "knowledge_base"]
            return any(p in code_lower for p in patterns)
        
        else:
            return True  # Generic fixes OK
