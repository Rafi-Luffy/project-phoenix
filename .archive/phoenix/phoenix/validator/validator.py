"""Validator - validates patches against tests in sandbox."""

from pathlib import Path
from uuid import UUID

from phoenix.core.logging import get_logger
from phoenix.core.models import Patch, ValidationResult, ValidationStatus
from phoenix.observer.test_runner import TestRunner
from phoenix.validator.sandbox import Sandbox

logger = get_logger(__name__)


class Validator:
    """Validates patches by running tests in a sandbox."""
    
    def __init__(self, project_path: Path, test_command: str = "pytest"):
        """
        Initialize validator.
        
        Args:
            project_path: Path to the project
            test_command: Command to run tests
        """
        self.project_path = project_path
        self.test_command = test_command
        self.logger = get_logger(__name__)
    
    def validate_patch(
        self,
        patch: Patch,
        original_failure_test: str,
        timeout: int = 300,
        use_docker: bool = True,
    ) -> ValidationResult:
        """
        Validate a patch by running tests in sandbox.
        
        Args:
            patch: The patch to validate
            original_failure_test: The test that originally failed
            timeout: Validation timeout in seconds
            use_docker: Whether to use Docker sandbox
            
        Returns:
            ValidationResult with test outcomes
        """
        self.logger.info(
            "validating_patch",
            patch_id=str(patch.id),
            file=patch.file_path,
        )
        
        with Sandbox(self.project_path) as sandbox:
            # Apply patch
            sandbox.apply_patch(patch.file_path, patch.patched_content)
            
            # Run tests
            test_command = self._build_test_command()
            exit_code, stdout, stderr = sandbox.run_command(
                test_command,
                timeout=timeout,
                use_docker=use_docker,
            )
            
            # Parse results
            result = self._parse_test_results(
                patch.id,
                exit_code,
                stdout,
                stderr,
                original_failure_test,
            )
            
            self.logger.info(
                "validation_complete",
                patch_id=str(patch.id),
                status=result.status,
                tests_passed=result.tests_passed,
                tests_failed=result.tests_failed,
            )
            
            return result
    
    def _build_test_command(self) -> str:
        """Build the test command for sandbox."""
        if "pytest" in self.test_command:
            # Install pytest and run tests with JSON output
            return (
                "pip install -q pytest pytest-json-report && "
                "pytest -v --tb=short --json-report --json-report-file=test-report.json"
            )
        else:
            return self.test_command
    
    def _parse_test_results(
        self,
        patch_id: UUID,
        exit_code: int,
        stdout: str,
        stderr: str,
        original_failure_test: str,
    ) -> ValidationResult:
        """Parse test results into ValidationResult."""
        # Simple parsing from output
        output = stdout + stderr
        
        tests_passed = output.count(" PASSED")
        tests_failed = output.count(" FAILED")
        tests_run = tests_passed + tests_failed
        
        # Check if original failure is fixed
        original_fixed = original_failure_test not in output or " PASSED" in output
        
        # Determine status
        if exit_code == 0 and tests_failed == 0:
            status = ValidationStatus.SUCCESS
        elif tests_failed > tests_passed:
            status = ValidationStatus.CATASTROPHIC
        elif tests_failed > 0:
            status = ValidationStatus.REGRESSION
        elif not original_fixed:
            status = ValidationStatus.PARTIAL
        else:
            status = ValidationStatus.SUCCESS
        
        # Count new failures (heuristic: failures not in original test)
        new_failures = max(0, tests_failed - (0 if original_fixed else 1))
        
        return ValidationResult(
            patch_id=patch_id,
            status=status,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            original_failures_fixed=1 if original_fixed else 0,
            new_failures_introduced=new_failures,
            test_outputs={"stdout": stdout, "stderr": stderr},
            logs=output,
            timeout_occurred=exit_code == -1,
            errors=[stderr] if stderr else [],
        )
