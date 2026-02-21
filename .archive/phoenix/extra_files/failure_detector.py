"""Failure detector - converts test results into FailureEvents."""

import re
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from phoenix.core.models import FailureEvent, FailureType
from phoenix.core.logging import get_logger
from phoenix.observer.test_runner import TestResult, TestRunResult

logger = get_logger(__name__)


class FailureDetector:
    """Detects and structures failures from test results."""
    
    def __init__(self, project_id: UUID, project_path: Path):
        """
        Initialize failure detector.
        
        Args:
            project_id: UUID of the project being monitored
            project_path: Path to the project root
        """
        self.project_id = project_id
        self.project_path = project_path
        self.logger = get_logger(__name__)
    
    def detect_failures(
        self,
        test_run_result: TestRunResult,
        commit_hash: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> List[FailureEvent]:
        """
        Detect failures from test run results.
        
        Args:
            test_run_result: Results from test execution
            commit_hash: Git commit hash
            branch: Git branch name
            
        Returns:
            List of FailureEvent objects
        """
        failures = []
        
        if test_run_result.failed == 0:
            self.logger.info("no_failures_detected")
            return failures
        
        for test_result in test_run_result.test_results:
            if not test_result.passed and test_result.error_message:
                failure_event = self._create_failure_event(
                    test_result, commit_hash, branch
                )
                failures.append(failure_event)
        
        self.logger.info(
            "failures_detected",
            count=len(failures),
            failed_tests=test_run_result.failed,
        )
        
        return failures
    
    def _create_failure_event(
        self,
        test_result: TestResult,
        commit_hash: Optional[str],
        branch: Optional[str],
    ) -> FailureEvent:
        """Create a FailureEvent from a test result."""
        # Classify failure type
        failure_type = self._classify_failure_type(
            test_result.error_type, test_result.error_message
        )
        
        # Extract implicated files and lines
        files_implicated, lines_implicated = self._extract_code_location(
            test_result.stack_trace
        )
        
        # Calculate severity
        severity = self._calculate_severity(failure_type, test_result.error_type)
        
        return FailureEvent(
            project_id=self.project_id,
            failure_type=failure_type,
            severity=severity,
            test_name=test_result.name,
            test_file=test_result.file,
            error_message=test_result.error_message or "Unknown error",
            stack_trace=test_result.stack_trace,
            error_type=test_result.error_type,
            files_implicated=files_implicated,
            lines_implicated=lines_implicated,
            commit_hash=commit_hash,
            branch=branch,
            logs=test_result.output,
        )
    
    def _classify_failure_type(
        self, error_type: Optional[str], error_message: Optional[str]
    ) -> FailureType:
        """Classify the type of failure."""
        if not error_type and not error_message:
            return FailureType.UNKNOWN
        
        error_text = (error_type or "") + " " + (error_message or "")
        error_text_lower = error_text.lower()
        
        if "assertionerror" in error_text_lower or "assert" in error_text_lower:
            return FailureType.ASSERTION_ERROR
        
        if "syntaxerror" in error_text_lower:
            return FailureType.SYNTAX_ERROR
        
        if "importerror" in error_text_lower or "modulenotfounderror" in error_text_lower:
            return FailureType.IMPORT_ERROR
        
        if "timeout" in error_text_lower:
            return FailureType.TIMEOUT
        
        if any(
            err in error_text_lower
            for err in ["error", "exception", "traceback"]
        ):
            return FailureType.RUNTIME_ERROR
        
        return FailureType.TEST_FAILURE
    
    def _extract_code_location(
        self, stack_trace: Optional[str]
    ) -> tuple[List[str], dict[str, List[int]]]:
        """
        Extract file paths and line numbers from stack trace.
        
        Returns:
            Tuple of (files_implicated, lines_implicated)
        """
        if not stack_trace:
            return [], {}
        
        files = []
        lines_by_file = {}
        
        # Pattern to match Python stack trace lines
        # Example: File "/path/to/file.py", line 42, in function_name
        pattern = r'File "([^"]+)", line (\d+)'
        
        for match in re.finditer(pattern, stack_trace):
            file_path = match.group(1)
            line_number = int(match.group(2))
            
            # Convert to relative path if possible
            try:
                rel_path = str(Path(file_path).relative_to(self.project_path))
            except ValueError:
                rel_path = file_path
            
            # Skip virtual environment and library files
            if self._is_project_file(rel_path):
                if rel_path not in files:
                    files.append(rel_path)
                
                if rel_path not in lines_by_file:
                    lines_by_file[rel_path] = []
                
                if line_number not in lines_by_file[rel_path]:
                    lines_by_file[rel_path].append(line_number)
        
        return files, lines_by_file
    
    def _is_project_file(self, file_path: str) -> bool:
        """Check if file is part of the project (not library/venv)."""
        exclude_patterns = [
            "site-packages",
            "venv",
            "env",
            ".venv",
            "virtualenv",
            "dist-packages",
        ]
        
        return not any(pattern in file_path for pattern in exclude_patterns)
    
    def _calculate_severity(
        self, failure_type: FailureType, error_type: Optional[str]
    ) -> int:
        """
        Calculate failure severity (1-10).
        
        Higher severity = more critical
        """
        base_severity = {
            FailureType.SYNTAX_ERROR: 8,
            FailureType.IMPORT_ERROR: 7,
            FailureType.RUNTIME_ERROR: 6,
            FailureType.ASSERTION_ERROR: 5,
            FailureType.TEST_FAILURE: 5,
            FailureType.TIMEOUT: 6,
            FailureType.PERFORMANCE_DEGRADATION: 4,
            FailureType.UNKNOWN: 5,
        }
        
        severity = base_severity.get(failure_type, 5)
        
        # Adjust based on error type
        if error_type:
            critical_errors = ["SystemError", "MemoryError", "SegmentationFault"]
            if any(err in error_type for err in critical_errors):
                severity = min(10, severity + 2)
        
        return severity
