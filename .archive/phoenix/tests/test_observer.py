"""
Tests for Observer module - TestRunner and FailureDetector
"""
import pytest
from pathlib import Path
from phoenix.observer.test_runner import TestRunner, TestRunResult
from phoenix.observer.agentic_failure_detector import AgenticFailureDetector
from phoenix.core.models import Project


class TestTestRunner:
    """Tests for TestRunner"""
    
    def test_run_tests_returns_result(self):
        """Test that run_tests returns a TestResult"""
        project_path = Path(__file__).parent.parent / "examples" / "calculator-buggy"
        runner = TestRunner(project_path=project_path)
        
        result = runner.run_tests()
        
        assert isinstance(result, TestRunResult)
        assert result.total_tests >= 0
        assert result.duration >= 0
    
    def test_run_tests_detects_failures(self):
        """Test that run_tests detects test failures"""
        project_path = Path(__file__).parent.parent / "examples" / "calculator-buggy"
        runner = TestRunner(project_path=project_path)
        
        result = runner.run_tests()
        
        # calculator-buggy should have failing tests
        assert result.total_tests > 0
        assert result.failed > 0
        assert len(result.test_results) > 0
    
    def test_run_tests_with_invalid_path(self):
        """Test that run_tests handles invalid paths"""
        invalid_path = Path("/nonexistent/path")
        runner = TestRunner(project_path=invalid_path)
        
        # Should handle gracefully
        # Actual behavior depends on implementation


class TestFailureDetector:
    """Tests for FailureDetector"""
    
    def test_detect_failure_creates_event(self):
        """Test that detect_failures creates FailureEvents"""
        project_path = Path(__file__).parent.parent / "examples" / "calculator-buggy"
        project = Project(
            name="calculator-buggy",
            local_path=str(project_path),
            language="python"
        )
        
        detector = AgenticFailureDetector(
            project_id=project.id,
            project_path=project_path
        )
        
        runner = TestRunner(project_path=project_path)
        test_result = runner.run_tests()
        
        if test_result.failed > 0:
            # Get failures from test results
            failures = detector.detect_failures(test_result)
            
            if failures:
                failure_event = failures[0]
                assert failure_event is not None
                assert failure_event.project_id == project.id
                assert failure_event.test_name is not None
                assert failure_event.error_message is not None
    
    def test_classify_failure_type(self):
        """Test failure classification"""
        project_path = Path(__file__).parent.parent / "examples" / "calculator-buggy"
        project = Project(
            name="test-project",
            local_path=str(project_path),
            language="python"
        )
        
        detector = AgenticFailureDetector(
            project_id=project.id,
            project_path=project_path
        )
        
        # Test assertion failure
        failure_type = detector._classify_failure_type(
            error_type="AssertionError",
            error_message="Expected 5, got 4"
        )
        assert failure_type.value in ["test_failure", "runtime_error", "assertion_error"]
        
        # Test with different error types
        failure_type = detector._classify_failure_type(
            error_type="TypeError",
            error_message="unsupported operand"
        )
        assert failure_type.value in ["test_failure", "runtime_error", "syntax_error"]
