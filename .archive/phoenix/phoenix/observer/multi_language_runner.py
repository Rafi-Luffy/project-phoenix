"""Multi-Language Test Runner - Execute tests in ANY programming language.

Supports:
- Python: pytest, unittest, nose
- JavaScript/TypeScript: Jest, Mocha, Vitest, Ava
- Java: JUnit, TestNG, Maven, Gradle
- Go: go test
- Rust: cargo test
- Ruby: RSpec, Minitest
- PHP: PHPUnit
- C#: NUnit, xUnit
- And more...
"""

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from phoenix.core.logging import get_logger
from phoenix.core.universal_adapter import Language, SystemProfile
from phoenix.observer.test_runner import TestResult, TestRunResult

logger = get_logger(__name__)


@dataclass
class LanguageTestConfig:
    """Test configuration for a specific language."""
    
    language: Language
    default_command: str
    test_patterns: List[str]
    result_parsers: List[str]
    common_frameworks: Dict[str, str]


class MultiLanguageTestRunner:
    """Universal test runner for ANY programming language."""
    
    # Language-specific test configurations
    TEST_CONFIGS = {
        Language.PYTHON: LanguageTestConfig(
            language=Language.PYTHON,
            default_command="pytest -v --tb=short",
            test_patterns=["test_*.py", "*_test.py"],
            result_parsers=["pytest", "unittest"],
            common_frameworks={
                "pytest": "pytest -v --tb=short",
                "unittest": "python -m unittest discover",
                "nose": "nosetests -v",
            }
        ),
        Language.JAVASCRIPT: LanguageTestConfig(
            language=Language.JAVASCRIPT,
            default_command="npm test",
            test_patterns=["*.test.js", "*.spec.js"],
            result_parsers=["jest", "mocha"],
            common_frameworks={
                "jest": "npx jest --verbose",
                "mocha": "npx mocha",
                "vitest": "npx vitest run",
                "ava": "npx ava",
            }
        ),
        Language.TYPESCRIPT: LanguageTestConfig(
            language=Language.TYPESCRIPT,
            default_command="npm test",
            test_patterns=["*.test.ts", "*.spec.ts"],
            result_parsers=["jest", "mocha"],
            common_frameworks={
                "jest": "npx jest --verbose",
                "mocha": "npx mocha",
                "vitest": "npx vitest run",
            }
        ),
        Language.JAVA: LanguageTestConfig(
            language=Language.JAVA,
            default_command="mvn test",
            test_patterns=["*Test.java", "*Tests.java"],
            result_parsers=["maven", "gradle", "junit"],
            common_frameworks={
                "maven": "mvn test",
                "gradle": "gradle test",
                "junit": "mvn test",
                "testng": "mvn test",
            }
        ),
        Language.GO: LanguageTestConfig(
            language=Language.GO,
            default_command="go test ./... -v",
            test_patterns=["*_test.go"],
            result_parsers=["go"],
            common_frameworks={
                "default": "go test ./... -v",
                "race": "go test -race ./...",
                "coverage": "go test -cover ./...",
            }
        ),
        Language.RUST: LanguageTestConfig(
            language=Language.RUST,
            default_command="cargo test",
            test_patterns=["tests/*.rs"],
            result_parsers=["cargo"],
            common_frameworks={
                "cargo": "cargo test -- --nocapture",
                "nextest": "cargo nextest run",
            }
        ),
        Language.RUBY: LanguageTestConfig(
            language=Language.RUBY,
            default_command="rspec",
            test_patterns=["*_spec.rb"],
            result_parsers=["rspec", "minitest"],
            common_frameworks={
                "rspec": "rspec",
                "minitest": "ruby -Itest",
            }
        ),
        Language.PHP: LanguageTestConfig(
            language=Language.PHP,
            default_command="phpunit",
            test_patterns=["*Test.php"],
            result_parsers=["phpunit"],
            common_frameworks={
                "phpunit": "vendor/bin/phpunit",
            }
        ),
        Language.CSHARP: LanguageTestConfig(
            language=Language.CSHARP,
            default_command="dotnet test",
            test_patterns=["*Tests.cs"],
            result_parsers=["dotnet"],
            common_frameworks={
                "nunit": "dotnet test",
                "xunit": "dotnet test",
                "mstest": "dotnet test",
            }
        ),
    }
    
    def __init__(self, project_path: Path, system_profile: SystemProfile):
        """
        Initialize multi-language test runner.
        
        Args:
            project_path: Path to project root
            system_profile: Detected system profile
        """
        self.project_path = Path(project_path)
        self.profile = system_profile
        self.logger = get_logger(__name__)
        
        # Get language-specific config
        self.test_config = self.TEST_CONFIGS.get(
            system_profile.primary_language,
            self.TEST_CONFIGS[Language.PYTHON]  # Fallback to Python
        )
    
    def run_tests(
        self,
        test_files: Optional[List[str]] = None,
        test_names: Optional[List[str]] = None,
        timeout: int = 300,
    ) -> TestRunResult:
        """
        Run tests using language-appropriate test runner.
        
        Args:
            test_files: Specific test files (None = all)
            test_names: Specific test names (None = all)
            timeout: Timeout in seconds
            
        Returns:
            Universal TestRunResult
        """
        # Determine test command
        command = self._build_command(test_files, test_names)
        
        self.logger.info(
            "running_tests",
            language=self.profile.primary_language,
            command=command,
            framework=self.profile.test_framework,
        )
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True,
            )
            
            # Parse results based on language/framework
            test_run_result = self._parse_results(result, command)
            
            self.logger.info(
                "tests_completed",
                language=self.profile.primary_language,
                exit_code=result.returncode,
                total=test_run_result.total_tests,
                passed=test_run_result.passed,
                failed=test_run_result.failed,
            )
            
            return test_run_result
            
        except subprocess.TimeoutExpired:
            self.logger.error("test_timeout", timeout=timeout)
            return TestRunResult(
                exit_code=-1,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=timeout,
                test_results=[],
                stdout="",
                stderr=f"Test execution timed out after {timeout} seconds",
                command=command,
            )
        except Exception as e:
            self.logger.error("test_execution_error", error=str(e))
            return TestRunResult(
                exit_code=-1,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0,
                test_results=[],
                stdout="",
                stderr=f"Test execution failed: {str(e)}",
                command=command,
            )
    
    def _build_command(
        self,
        test_files: Optional[List[str]] = None,
        test_names: Optional[List[str]] = None,
    ) -> str:
        """Build language-appropriate test command."""
        
        # Use detected test command or default
        base_command = self.profile.test_command or self.test_config.default_command
        
        # Language-specific command building
        if self.profile.primary_language == Language.PYTHON:
            return self._build_python_command(base_command, test_files, test_names)
        elif self.profile.primary_language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            return self._build_js_command(base_command, test_files, test_names)
        elif self.profile.primary_language == Language.JAVA:
            return self._build_java_command(base_command, test_files, test_names)
        elif self.profile.primary_language == Language.GO:
            return self._build_go_command(base_command, test_files, test_names)
        elif self.profile.primary_language == Language.RUST:
            return self._build_rust_command(base_command, test_files, test_names)
        else:
            # Generic fallback
            cmd = base_command
            if test_files:
                cmd += " " + " ".join(test_files)
            return cmd
    
    def _build_python_command(
        self,
        base: str,
        test_files: Optional[List[str]],
        test_names: Optional[List[str]],
    ) -> str:
        """Build Python test command (pytest/unittest)."""
        cmd = base
        
        if test_files:
            cmd += " " + " ".join(test_files)
        
        if test_names:
            # pytest: -k for test name filtering
            cmd += " -k '" + " or ".join(test_names) + "'"
        
        return cmd
    
    def _build_js_command(
        self,
        base: str,
        test_files: Optional[List[str]],
        test_names: Optional[List[str]],
    ) -> str:
        """Build JavaScript/TypeScript test command."""
        cmd = base
        
        if test_files:
            cmd += " " + " ".join(test_files)
        
        if test_names:
            # Jest: -t for test name pattern
            cmd += " -t '" + "|".join(test_names) + "'"
        
        return cmd
    
    def _build_java_command(
        self,
        base: str,
        test_files: Optional[List[str]],
        test_names: Optional[List[str]],
    ) -> str:
        """Build Java test command (Maven/Gradle)."""
        cmd = base
        
        if test_names:
            # Maven: -Dtest for specific tests
            if "mvn" in base:
                cmd += " -Dtest=" + ",".join(test_names)
            # Gradle: --tests
            elif "gradle" in base:
                cmd += " --tests " + " --tests ".join(test_names)
        
        return cmd
    
    def _build_go_command(
        self,
        base: str,
        test_files: Optional[List[str]],
        test_names: Optional[List[str]],
    ) -> str:
        """Build Go test command."""
        cmd = base
        
        if test_names:
            # Go: -run for regex pattern
            cmd += " -run '" + "|".join(test_names) + "'"
        
        if test_files:
            # Go expects package paths
            packages = [str(Path(f).parent) for f in test_files]
            cmd = f"go test {' '.join(set(packages))} -v"
        
        return cmd
    
    def _build_rust_command(
        self,
        base: str,
        test_files: Optional[List[str]],
        test_names: Optional[List[str]],
    ) -> str:
        """Build Rust test command."""
        cmd = base
        
        if test_names:
            # Cargo: test name as argument
            cmd += " " + " ".join(test_names)
        
        return cmd
    
    def _parse_results(self, result: subprocess.CompletedProcess, command: str) -> TestRunResult:
        """Parse test results based on language/framework."""
        
        # Try language-specific parsers
        if self.profile.primary_language == Language.PYTHON:
            return self._parse_python_results(result, command)
        elif self.profile.primary_language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            return self._parse_js_results(result, command)
        elif self.profile.primary_language == Language.JAVA:
            return self._parse_java_results(result, command)
        elif self.profile.primary_language == Language.GO:
            return self._parse_go_results(result, command)
        elif self.profile.primary_language == Language.RUST:
            return self._parse_rust_results(result, command)
        else:
            return self._parse_generic_results(result, command)
    
    def _parse_python_results(self, result: subprocess.CompletedProcess, command: str) -> TestRunResult:
        """Parse pytest/unittest output."""
        output = result.stdout + result.stderr
        
        # Extract pytest summary
        passed = 0
        failed = 0
        skipped = 0
        
        # Pytest format: "X passed, Y failed, Z skipped"
        if match := re.search(r"(\d+) passed", output):
            passed = int(match.group(1))
        if match := re.search(r"(\d+) failed", output):
            failed = int(match.group(1))
        if match := re.search(r"(\d+) skipped", output):
            skipped = int(match.group(1))
        
        total = passed + failed + skipped
        
        # Extract individual test results
        test_results = []
        for match in re.finditer(r"(PASSED|FAILED|SKIPPED)\s+(.+?)(?:\[|$)", output):
            status, name = match.groups()
            test_results.append(TestResult(
                name=name.strip(),
                file="",
                passed=(status == "PASSED"),
                error_message=None if status == "PASSED" else "Test failed",
            ))
        
        return TestRunResult(
            exit_code=result.returncode,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=0.0,
            test_results=test_results,
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
        )
    
    def _parse_js_results(self, result: subprocess.CompletedProcess, command: str) -> TestRunResult:
        """Parse Jest/Mocha output."""
        output = result.stdout + result.stderr
        
        # Jest format
        passed = 0
        failed = 0
        
        if match := re.search(r"Tests:\s+(\d+) failed.*?(\d+) passed", output):
            failed = int(match.group(1))
            passed = int(match.group(2))
        elif match := re.search(r"Tests:\s+(\d+) passed", output):
            passed = int(match.group(1))
        
        total = passed + failed
        
        return TestRunResult(
            exit_code=result.returncode,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=0,
            duration=0.0,
            test_results=[],
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
        )
    
    def _parse_java_results(self, result: subprocess.CompletedProcess, command: str) -> TestRunResult:
        """Parse Maven/Gradle output."""
        output = result.stdout + result.stderr
        
        # Maven format: "Tests run: X, Failures: Y, Errors: Z, Skipped: W"
        passed = 0
        failed = 0
        skipped = 0
        
        if match := re.search(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)", output):
            total = int(match.group(1))
            failures = int(match.group(2))
            errors = int(match.group(3))
            skipped = int(match.group(4))
            failed = failures + errors
            passed = total - failed - skipped
        
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
            command=command,
        )
    
    def _parse_go_results(self, result: subprocess.CompletedProcess, command: str) -> TestRunResult:
        """Parse Go test output."""
        output = result.stdout + result.stderr
        
        # Count PASS/FAIL lines
        passed = len(re.findall(r"--- PASS:", output))
        failed = len(re.findall(r"--- FAIL:", output))
        total = passed + failed
        
        return TestRunResult(
            exit_code=result.returncode,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=0,
            duration=0.0,
            test_results=[],
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
        )
    
    def _parse_rust_results(self, result: subprocess.CompletedProcess, command: str) -> TestRunResult:
        """Parse Cargo test output."""
        output = result.stdout + result.stderr
        
        # Cargo format: "test result: ok. X passed; Y failed"
        passed = 0
        failed = 0
        
        if match := re.search(r"(\d+) passed; (\d+) failed", output):
            passed = int(match.group(1))
            failed = int(match.group(2))
        
        total = passed + failed
        
        return TestRunResult(
            exit_code=result.returncode,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=0,
            duration=0.0,
            test_results=[],
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
        )
    
    def _parse_generic_results(self, result: subprocess.CompletedProcess, command: str) -> TestRunResult:
        """Generic parser for unknown test frameworks."""
        # Simple heuristic: exit code 0 = all passed
        if result.returncode == 0:
            return TestRunResult(
                exit_code=0,
                total_tests=1,
                passed=1,
                failed=0,
                skipped=0,
                duration=0.0,
                test_results=[],
                stdout=result.stdout,
                stderr=result.stderr,
                command=command,
            )
        else:
            return TestRunResult(
                exit_code=result.returncode,
                total_tests=1,
                passed=0,
                failed=1,
                skipped=0,
                duration=0.0,
                test_results=[],
                stdout=result.stdout,
                stderr=result.stderr,
                command=command,
            )
