"""
Tests for core models and configuration
"""
import pytest
from uuid import uuid4
from phoenix.core.models import (
    FailureEvent, FailureType, BugType,
    DiagnosticReport, Patch, ValidationResult, ValidationStatus,
    RemediationAttempt, RemediationStatus, Project
)
from phoenix.core.config import PhoenixConfig, Settings


class TestCoreModels:
    """Tests for Pydantic models"""
    
    def test_failure_event_creation(self):
        """Test FailureEvent model"""
        project_id = uuid4()
        event = FailureEvent(
            project_id=project_id,
            test_name="test_add",
            failure_type=FailureType.TEST_FAILURE,
            error_message="AssertionError",
            stack_trace="test.py:10",
            files_implicated=["calc.py"],
            lines_implicated={"calc.py": [5]},
        )
        
        assert event.project_id == project_id
        assert event.test_name == "test_add"
        assert event.failure_type == FailureType.TEST_FAILURE
    
    def test_diagnostic_report_creation(self):
        """Test DiagnosticReport model"""
        failure_id = uuid4()
        report = DiagnosticReport(
            failure_event_id=failure_id,
            explanation="Math operator is incorrect",
            bug_type=BugType.LOGIC_ERROR,
            root_cause="Wrong operator used in addition function",
            recommended_strategy="Replace subtraction operator with addition",
            confidence_score=0.9,
        )
        
        assert report.failure_event_id == failure_id
        assert report.bug_type == BugType.LOGIC_ERROR
        assert report.confidence_score == 0.9
    
    def test_patch_creation(self):
        """Test Patch model"""
        remediation_id = uuid4()
        patch = Patch(
            remediation_attempt_id=remediation_id,
            file_path="calc.py",
            original_content="return a - b",
            patched_content="return a + b",
            diff="- return a - b\n+ return a + b",
            description="Fix operator in add function"
        )
        
        assert patch.remediation_attempt_id == remediation_id
        assert patch.file_path == "calc.py"
        assert patch.original_content != patch.patched_content
    
    def test_validation_result_creation(self):
        """Test ValidationResult model"""
        patch_id = uuid4()
        result = ValidationResult(
            patch_id=patch_id,
            status=ValidationStatus.SUCCESS,
            tests_run=5,
            tests_passed=5,
            tests_failed=0,
        )
        
        assert result.patch_id == patch_id
        assert result.status == ValidationStatus.SUCCESS
        assert result.tests_passed == 5
    
    def test_project_creation(self):
        """Test Project model"""
        project = Project(
            name="test-project",
            local_path="/path/to/project",
            repository_url="https://github.com/user/repo"
        )
        
        assert project.name == "test-project"
        assert project.local_path == "/path/to/project"


class TestSettings:
    """Tests for configuration"""
    
    def test_settings_defaults(self):
        """Test default configuration values"""
        config = PhoenixConfig()
        
        assert config.log_level == "INFO"
        assert config.default_llm_provider == "openai"
        assert hasattr(config, "critic_model")
        assert hasattr(config, "programmer_model")
    
    def test_settings_custom(self):
        """Test configuration with custom values"""
        config = PhoenixConfig(
            log_level="DEBUG",
            default_llm_provider="gemini"
        )
        
        assert config.log_level == "DEBUG"
        assert config.default_llm_provider == "gemini"
