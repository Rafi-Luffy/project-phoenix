"""Test runner for executing tests and capturing results."""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TestResult:
    """Result of running a single test."""
    
    name: str
    file: str
    passed: bool
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    duration: float = 0.0
    output: Optional[str] = None


@dataclass
class TestRunResult:
    """Result of a complete test run."""
    
    exit_code: int
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    test_results: List[TestResult]
    stdout: str
    stderr: str
    command: str


class TestRunner:
    """Runs tests and captures detailed results."""
    
    def __init__(self, project_path: Path, test_command: str = "pytest"):
        """
        Initialize test runner.
        
        Args:
            project_path: Path to the project root
            test_command: Command to run tests (default: pytest)
        """
        self.project_path = project_path
        self.test_command = test_command
        self.logger = get_logger(__name__)
    
    def run_tests(
        self,
        test_files: Optional[List[str]] = None,
        test_names: Optional[List[str]] = None,
        timeout: int = 300,
        extra_args: Optional[List[str]] = None,
    ) -> TestRunResult:
        """
        Run tests and capture results.
        
        Args:
            test_files: Specific test files to run (None = all)
            test_names: Specific test names to run (None = all)
            timeout: Timeout in seconds
            extra_args: Additional arguments to pass to test command
            
        Returns:
            TestRunResult with detailed information
        """
        command = self._build_command(test_files, test_names, extra_args)
        
        self.logger.info(
            "running_tests",
            command=command,
            project_path=str(self.project_path),
        )
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            test_run_result = self._parse_results(result, command)
            
            self.logger.info(
                "tests_completed",
                exit_code=result.returncode,
                total=test_run_result.total_tests,
                passed=test_run_result.passed,
                failed=test_run_result.failed,
            )
            
            return test_run_result
            
        except subprocess.TimeoutExpired as e:
            self.logger.error("test_timeout", timeout=timeout)
            return TestRunResult(
                exit_code=-1,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=timeout,
                test_results=[],
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else "",
                command=" ".join(command),
            )
        except Exception as e:
            self.logger.error("test_execution_failed", error=str(e))
            raise
    
    def _build_command(
        self,
        test_files: Optional[List[str]],
        test_names: Optional[List[str]],
        extra_args: Optional[List[str]],
    ) -> List[str]:
        """Build the test command with arguments."""
        if self.test_command.startswith("pytest"):
            return self._build_pytest_command(test_files, test_names, extra_args)
        else:
            # Generic command
            command = self.test_command.split()
            if extra_args:
                command.extend(extra_args)
            return command
    
    def _build_pytest_command(
        self,
        test_files: Optional[List[str]],
        test_names: Optional[List[str]],
        extra_args: Optional[List[str]],
    ) -> List[str]:
        """Build pytest command with detailed output."""
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-v",  # Verbose
            "--tb=long",  # Long traceback
            "--json-report",  # JSON output for parsing
            "--json-report-file=test-report.json",
        ]
        
        if test_files:
            command.extend(test_files)
        
        if test_names:
            for name in test_names:
                command.extend(["-k", name])
        
        if extra_args:
            command.extend(extra_args)
        
        return command
    
    def _parse_results(
        self, result: subprocess.CompletedProcess, command: List[str]
    ) -> TestRunResult:
        """Parse test results from output."""
        # Try to parse JSON report if available
        json_report_path = self.project_path / "test-report.json"
        
        if json_report_path.exists():
            import json
            
            try:
                with open(json_report_path) as f:
                    report = json.load(f)
                return self._parse_pytest_json(report, result, command)
            except Exception as e:
                self.logger.warning("failed_to_parse_json_report", error=str(e))
        
        # Fallback to text parsing
        return self._parse_text_output(result, command)
    
    def _parse_pytest_json(
        self, report: Dict, result: subprocess.CompletedProcess, command: List[str]
    ) -> TestRunResult:
        """Parse pytest JSON report."""
        summary = report.get("summary", {})
        tests = report.get("tests", [])
        
        test_results = []
        for test in tests:
            test_results.append(
                TestResult(
                    name=test.get("nodeid", "unknown"),
                    file=test.get("file", "unknown"),
                    passed=test.get("outcome") == "passed",
                    error_message=self._extract_error_message(test),
                    error_type=self._extract_error_type(test),
                    stack_trace=self._extract_stack_trace(test),
                    duration=test.get("duration", 0.0),
                    output=test.get("call", {}).get("stdout", ""),
                )
            )
        
        return TestRunResult(
            exit_code=result.returncode,
            total_tests=summary.get("total", 0),
            passed=summary.get("passed", 0),
            failed=summary.get("failed", 0),
            skipped=summary.get("skipped", 0),
            duration=report.get("duration", 0.0),
            test_results=test_results,
            stdout=result.stdout,
            stderr=result.stderr,
            command=" ".join(command),
        )
    
    def _parse_text_output(
        self, result: subprocess.CompletedProcess, command: List[str]
    ) -> TestRunResult:
        """Fallback text parsing for test output."""
        # Simple parsing - count PASSED/FAILED in output
        output = result.stdout + result.stderr
        
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        skipped = output.count(" SKIPPED")
        total = passed + failed + skipped
        
        return TestRunResult(
            exit_code=result.returncode,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=0.0,
            test_results=[],
            stdout=result.stdout,
            stderr=result.stderr,
            command=" ".join(command),
        )
    
    def _extract_error_message(self, test: Dict) -> Optional[str]:
        """Extract error message from test result."""
        call = test.get("call", {})
        if "longrepr" in call:
            return call["longrepr"]
        if "crash" in call:
            return call["crash"].get("message")
        return None
    
    def _extract_error_type(self, test: Dict) -> Optional[str]:
        """Extract error type from test result."""
        call = test.get("call", {})
        if "crash" in call:
            return call["crash"].get("path")
        # Try to extract from longrepr
        longrepr = call.get("longrepr", "")
        if ":" in longrepr:
            return longrepr.split(":")[0].split()[-1]
        return None
    
    def _extract_stack_trace(self, test: Dict) -> Optional[str]:
        """Extract stack trace from test result."""
        call = test.get("call", {})
        return call.get("longrepr")
