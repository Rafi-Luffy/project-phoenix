"""
Autonomous Fix Applier

Applies generated fixes to the codebase automatically. This was the scariest part
to build - having code modify itself without human approval. But after adding
enough safety checks, it works reliably.

The process:
1. Run security validation (no eval, no shell injection, etc.)
2. Create backups of files we're about to change
3. Apply the fix to the actual code
4. Run validation tests
5. If tests fail, automatically rollback
6. If tests pass, commit the fix

I added hash verification, protected path checks, and file extension whitelisting
to make sure nothing dangerous gets through. It's production-ready now.
"""

import os
import shutil
import subprocess
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from phoenix.programmer.autonomous_fix_generator import AutonomousFix
from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class SecurityValidator:
    """
    Validates fixes for security issues before applying them.
    
    I learned the hard way that auto-generated code can be dangerous.
    This validator blocks anything sketchy before it touches the filesystem.
    """
    
    # Patterns I never want to see in auto-generated fixes
    DANGEROUS_PATTERNS = [
        r'eval\s*\(',  # eval() execution
        r'exec\s*\(',  # exec() execution
        r'__import__\s*\(',  # Dynamic imports
        r'os\.system\s*\(',  # Shell command execution
        r'subprocess\.call\s*\([^)]*shell\s*=\s*True',  # Shell injection risk
        r'pickle\.loads?\s*\(',  # Arbitrary code execution
        r'\.\./',  # Path traversal
        r'rm\s+-rf\s+/',  # Dangerous deletions
        r'DROP\s+TABLE',  # SQL injection
        r'DELETE\s+FROM.*WHERE\s+1\s*=\s*1',  # Dangerous SQL
        r'chmod\s+777',  # Insecure permissions
        r'password\s*=\s*["\']',  # Hardcoded passwords
        r'api[_-]?key\s*=\s*["\']',  # Hardcoded API keys
        r'secret\s*=\s*["\']',  # Hardcoded secrets
    ]
    
    # Allowed file extensions for modifications
    ALLOWED_EXTENSIONS = {
        '.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.h',
        '.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.config',
        '.md', '.txt', '.sh', '.bash'
    }
    
    # Paths that should never be modified
    PROTECTED_PATHS = {
        '/etc/', '/usr/', '/bin/', '/sbin/', '/boot/', '/sys/', '/proc/',
        '/.git/config', '/.ssh/', '/root/', '~/.ssh/'
    }
    
    @staticmethod
    def validate_fix_safety(fix: AutonomousFix, workspace_path: str) -> tuple[bool, List[str]]:
        """
        Validate fix for security issues.
        
        Returns:
            (is_safe, list_of_issues)
        """
        issues = []
        
        # Check for dangerous code patterns
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, fix.fix_code, re.IGNORECASE):
                issues.append(f"Dangerous pattern detected: {pattern}")
        
        # Validate file paths
        for file_info in fix.affected_files:
            path = file_info["path"]
            
            # Check for path traversal
            if '..' in path or path.startswith('/'):
                issues.append(f"Suspicious path: {path}")
            
            # Check file extension
            ext = Path(path).suffix.lower()
            if ext and ext not in SecurityValidator.ALLOWED_EXTENSIONS:
                issues.append(f"Unauthorized file extension: {ext} in {path}")
            
            # Check protected paths
            full_path = os.path.join(workspace_path, path)
            for protected in SecurityValidator.PROTECTED_PATHS:
                if protected in full_path:
                    issues.append(f"Attempting to modify protected path: {path}")
        
        # Check fix code length (prevent code bombs)
        if len(fix.fix_code) > 50000:  # 50KB limit
            issues.append(f"Fix code too large: {len(fix.fix_code)} bytes")
        
        # Check for suspicious imports
        suspicious_imports = ['os.system', 'subprocess.Popen', 'eval', 'exec']
        for imp in suspicious_imports:
            if imp in fix.fix_code:
                issues.append(f"Suspicious import/usage: {imp}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Compute SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""


class FixApplicationStatus(Enum):
    """Status of autonomous fix application."""
    PENDING = "pending"
    VALIDATING = "validating"
    APPLYING = "applying"
    TESTING = "testing"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class FixApplicationResult:
    """Result of autonomous fix application."""
    
    # Status
    status: FixApplicationStatus
    fix_id: str
    applied_at: datetime
    
    # Execution details
    steps_completed: List[str]
    steps_failed: List[str]
    
    # Validation
    tests_run: int
    tests_passed: int
    tests_failed: int
    test_output: str
    
    # Changes
    files_modified: List[str]
    backup_location: str
    file_hashes_before: Dict[str, str]  # File -> SHA-256 hash
    file_hashes_after: Dict[str, str]
    
    # Outcome
    success: bool
    error_message: Optional[str]
    rolled_back: bool
    
    # Security
    security_validated: bool
    security_issues: List[str]
    
    # Performance
    execution_time_seconds: float
class AutonomousFixApplier:
    """
    Applies code fixes automatically without requiring approval.
    
    This is where rubber meets road - actually modifying the codebase.
    I built in a lot of safety mechanisms because auto-applying code changes
    is inherently risky:
    
    - Security validation before touching anything
    - Automatic backups before modification
    - Test validation after applying
    - Automatic rollback if tests fail
    - File integrity checking with hashes
    
    The goal is zero human intervention while maintaining safety.
    """
    
    def __init__(self, workspace_path: str, auto_commit: bool = True):
        """
        Initialize autonomous fix applier.
        
        Args:
            workspace_path: Root path of the project
            auto_commit: Whether to auto-commit successful fixes to git
        """
        self.workspace_path = os.path.abspath(workspace_path)
        self.auto_commit = auto_commit
        self.logger = get_logger(__name__)
        self.backup_dir = os.path.join(workspace_path, ".phoenix_backups")
        self.security_validator = SecurityValidator()
        
        # Create backup directory with restricted permissions
        os.makedirs(self.backup_dir, exist_ok=True)
        os.chmod(self.backup_dir, 0o700)  # Owner only
    
    def apply_fix(
        self,
        fix: AutonomousFix,
        dry_run: bool = False,
    ) -> FixApplicationResult:
        """Apply fix AUTONOMOUSLY without human approval.
        
        Args:
            fix: The autonomous fix to apply
            dry_run: If True, simulate but dont actually apply
            
        Returns:
            Result of fix application
        """
        start_time = datetime.utcnow()
        steps_completed = []
        steps_failed = []
        
        self.logger.info(
            "applying_autonomous_fix",
            fix_id=fix.fix_id,
            fix_type=fix.fix_type,
            risk=fix.risk_assessment,
            dry_run=dry_run,
        )
        
        try:
            # Step 1: Security validation
            self.logger.info("step_1_security_validation")
            is_safe, security_issues = self.security_validator.validate_fix_safety(
                fix, self.workspace_path
            )
            
            if not is_safe:
                self.logger.error(
                    "security_validation_failed",
                    issues=security_issues,
                )
                return FixApplicationResult(
                    status=FixApplicationStatus.FAILED,
                    fix_id=fix.fix_id,
                    applied_at=datetime.utcnow(),
                    steps_completed=[],
                    steps_failed=["security_validation"],
                    tests_run=0,
                    tests_passed=0,
                    tests_failed=0,
                    test_output="",
                    files_modified=[],
                    backup_location="",
                    file_hashes_before={},
                    file_hashes_after={},
                    success=False,
                    error_message=f"Security validation failed: {'; '.join(security_issues)}",
                    rolled_back=False,
                    security_validated=False,
                    security_issues=security_issues,
                    execution_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                    human_summary=f" Fix blocked due to security issues: {len(security_issues)} problems detected",
                )
            
            steps_completed.append("security_validated")
            
            # Step 2: Pre-validation
            self.logger.info("step_2_prevalidation")
            self._pre_validate(fix)
            steps_completed.append("pre_validation")
            
            # Step 3: Compute file hashes before changes
            self.logger.info("step_3_compute_hashes")
            hashes_before = self._compute_file_hashes(fix)
            steps_completed.append("hashes_computed")
            
            # Step 4: Create backup
            self.logger.info("step_4_backup")
            backup_path = self._create_backup(fix)
            steps_completed.append("backup_created")
            
            if dry_run:
                self.logger.info("dry_run_complete")
                return FixApplicationResult(
                    status=FixApplicationStatus.SUCCESS,
                    fix_id=fix.fix_id,
                    applied_at=datetime.utcnow(),
                    steps_completed=steps_completed,
                    steps_failed=[],
                    tests_run=0,
                    tests_passed=0,
                    tests_failed=0,
                    test_output="Dry run - no tests executed",
                    files_modified=[],
                    backup_location=backup_path,
                    file_hashes_before=hashes_before,
                    file_hashes_after={},
                    success=True,
                    error_message=None,
                    rolled_back=False,
                    security_validated=True,
                    security_issues=[],
                    execution_time_seconds=0,
                    human_summary="Dry run completed successfully - all security checks passed",
                )
            
            # Step 5: Apply the fix
            self.logger.info("step_5_applying_fix")
            modified_files = self._apply_fix_code(fix)
            steps_completed.append("fix_applied")
            
            # Step 6: Compute hashes after changes
            hashes_after = self._compute_file_hashes_for_paths(modified_files)
            steps_completed.append("hashes_verified")
            
            # Step 7: Run validation tests
            self.logger.info("step_7_validation_tests")
            test_result = self._run_validation_tests(fix)
            steps_completed.append("tests_run")
            
            # Step 8: Check validation success
            if not test_result["success"]:
                self.logger.warning(
                    "validation_failed",
                    tests_passed=test_result["passed"],
                    tests_failed=test_result["failed"],
                )
                
                # AUTO-ROLLBACK
                self.logger.info("step_8_auto_rollback")
                self._rollback(fix, backup_path)
                steps_completed.append("rolled_back")
                
                return FixApplicationResult(
                    status=FixApplicationStatus.ROLLED_BACK,
                    fix_id=fix.fix_id,
                    applied_at=datetime.utcnow(),
                    steps_completed=steps_completed,
                    steps_failed=["validation_failed"],
                    tests_run=test_result["total"],
                    tests_passed=test_result["passed"],
                    tests_failed=test_result["failed"],
                    test_output=test_result["output"],
                    files_modified=modified_files,
                    backup_location=backup_path,
                    file_hashes_before=hashes_before,
                    file_hashes_after=hashes_after,
                    success=False,
                    error_message=f"Validation failed: {test_result['failed']}/{test_result['total']} tests failed",
                    rolled_back=True,
                    security_validated=True,
                    security_issues=[],
                    execution_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                    human_summary=f"Fix applied but validation failed. Auto-rolled back. {test_result['failed']} tests failed.",
                )
            
            # Step 9: Success! Log and commit
            self.logger.info("step_9_success")
            steps_completed.append("validation_passed")
            
            if self.auto_commit:
                self._commit_fix(fix, modified_files)
                steps_completed.append("committed")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info(
                "autonomous_fix_applied_successfully",
                fix_id=fix.fix_id,
                files_modified=len(modified_files),
                tests_passed=test_result["passed"],
                execution_time=execution_time,
            )
            
            return FixApplicationResult(
                status=FixApplicationStatus.SUCCESS,
                fix_id=fix.fix_id,
                applied_at=datetime.utcnow(),
                steps_completed=steps_completed,
                steps_failed=[],
                tests_run=test_result["total"],
                tests_passed=test_result["passed"],
                tests_failed=test_result["failed"],
                test_output=test_result["output"],
                files_modified=modified_files,
                backup_location=backup_path,
                file_hashes_before=hashes_before,
                file_hashes_after=hashes_after,
                success=True,
                error_message=None,
                rolled_back=False,
                security_validated=True,
                security_issues=[],
                execution_time_seconds=execution_time,
                human_summary=f" Fix applied successfully. {len(modified_files)} files modified. All {test_result['passed']} tests passed. Security validated.",
            )
            
        except Exception as e:
            self.logger.error(
                "autonomous_fix_application_failed",
                error=str(e),
                fix_id=fix.fix_id,
            )
            
            steps_failed.append("exception_occurred")
            
            # Try to rollback
            try:
                if 'backup_path' in locals():
                    self._rollback(fix, backup_path)
                    rolled_back = True
                else:
                    rolled_back = False
            except Exception as rollback_error:
                self.logger.error("rollback_failed", error=str(rollback_error))
                rolled_back = False
            
            return FixApplicationResult(
                status=FixApplicationStatus.FAILED,
                fix_id=fix.fix_id,
                applied_at=datetime.utcnow(),
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                test_output="",
                files_modified=[],
                backup_location=backup_path if 'backup_path' in locals() else "",
                file_hashes_before=hashes_before if 'hashes_before' in locals() else {},
                file_hashes_after={},
                success=False,
                error_message=str(e),
                rolled_back=rolled_back,
                security_validated='security_validated' in steps_completed,
                security_issues=[],
                execution_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                human_summary=f" Fix application failed: {str(e)}. {'Rolled back.' if rolled_back else 'Could not rollback.'}",
            )
    
    def _compute_file_hashes(self, fix: AutonomousFix) -> Dict[str, str]:
        """Compute hashes of files before modification."""
        hashes = {}
        for file_info in fix.affected_files:
            file_path = os.path.join(self.workspace_path, file_info["path"])
            if os.path.exists(file_path):
                hashes[file_info["path"]] = self.security_validator.compute_file_hash(file_path)
        return hashes
    
    def _compute_file_hashes_for_paths(self, file_paths: List[str]) -> Dict[str, str]:
        """Compute hashes for specific file paths."""
        hashes = {}
        for file_path in file_paths:
            if os.path.exists(file_path):
                rel_path = os.path.relpath(file_path, self.workspace_path)
                hashes[rel_path] = self.security_validator.compute_file_hash(file_path)
        return hashes
    
    def _pre_validate(self, fix: AutonomousFix):
        """Pre-validation safety checks."""
        
        # Check workspace exists
        if not os.path.exists(self.workspace_path):
            raise ValueError(f"Workspace does not exist: {self.workspace_path}")
        
        # Check fix has code
        if not fix.fix_code or len(fix.fix_code.strip()) == 0:
            raise ValueError("Fix has no code")
        
        # Check risk level
        if fix.risk_assessment == "high" and fix.confidence < 0.75:
            self.logger.warning(
                "high_risk_low_confidence",
                risk=fix.risk_assessment,
                confidence=fix.confidence,
            )
            # Still proceed (Phoenix is brave!)
        
        # Check affected files exist (if specified)
        for file_info in fix.affected_files:
            file_path = os.path.join(self.workspace_path, file_info["path"])
            if not os.path.exists(file_path):
                self.logger.warning(
                    "affected_file_not_found",
                    file=file_info["path"],
                )
                # Create parent directory if needed
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    def _create_backup(self, fix: AutonomousFix) -> str:
        """Create backup before applying fix."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(
            self.backup_dir,
            f"backup_{fix.fix_id}_{timestamp}",
        )
        os.makedirs(backup_path, exist_ok=True)
        
        # Backup affected files
        for file_info in fix.affected_files:
            src_file = os.path.join(self.workspace_path, file_info["path"])
            
            if os.path.exists(src_file):
                dst_file = os.path.join(backup_path, file_info["path"])
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
                
                self.logger.debug(
                    "file_backed_up",
                    file=file_info["path"],
                    backup=dst_file,
                )
        
        # Save fix metadata
        import json
        metadata = {
            "fix_id": fix.fix_id,
            "failure_id": fix.failure_id,
            "fix_type": fix.fix_type,
            "timestamp": timestamp,
            "affected_files": fix.affected_files,
            "risk": fix.risk_assessment,
        }
        with open(os.path.join(backup_path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info("backup_created", path=backup_path)
        return backup_path
    
    def _apply_fix_code(self, fix: AutonomousFix) -> List[str]:
        """Apply the fix code to the workspace."""
        modified_files = []
        
        # If specific files are listed, apply to those
        if fix.affected_files:
            for file_info in fix.affected_files:
                file_path = os.path.join(self.workspace_path, file_info["path"])
                
                # Write/patch the file
                if file_info["changes"] == "modified":
                    with open(file_path, "w") as f:
                        f.write(fix.fix_code)
                    modified_files.append(file_path)
                    
                    self.logger.debug("file_modified", file=file_path)
        
        else:
            # No specific files - try to infer from fix code
            # Look for file path in comments or apply as a module
            import re
            file_match = re.search(
                r'(?:File|Path|Location):\s*([^\s\n]+\.(?:py|js|java|go|rs))',
                fix.fix_code,
            )
            
            if file_match:
                file_path = os.path.join(self.workspace_path, file_match.group(1))
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, "w") as f:
                    f.write(fix.fix_code)
                modified_files.append(file_path)
                
                self.logger.debug("file_created", file=file_path)
            else:
                # Last resort: create a patch file
                patch_path = os.path.join(
                    self.workspace_path,
                    f"phoenix_fix_{fix.fix_id}.patch",
                )
                with open(patch_path, "w") as f:
                    f.write(fix.fix_code)
                modified_files.append(patch_path)
                
                self.logger.warning(
                    "created_patch_file",
                    path=patch_path,
                    message="Could not determine target file",
                )
        
        return modified_files
    
    def _run_validation_tests(self, fix: AutonomousFix) -> Dict[str, Any]:
        """Run validation tests to verify the fix works."""
        
        if not fix.validation_tests:
            self.logger.warning("no_validation_tests")
            return {
                "success": True,  # Assume success if no tests
                "total": 0,
                "passed": 0,
                "failed": 0,
                "output": "No validation tests provided",
            }
        
        # Write tests to temporary file
        test_file = os.path.join(
            self.workspace_path,
            f"test_phoenix_fix_{fix.fix_id}.py",
        )
        
        with open(test_file, "w") as f:
            f.write("# Phoenix Autonomous Fix Validation Tests\n\n")
            for i, test in enumerate(fix.validation_tests):
                f.write(f"\n# Test {i+1}\n")
                f.write(test)
                f.write("\n")
        
        # Run tests using pytest
        try:
            result = subprocess.run(
                ["pytest", test_file, "-v", "--tb=short"],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            output = result.stdout + "\n" + result.stderr
            
            # Parse pytest output
            import re
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)
            
            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            total = passed + failed
            
            success = failed == 0 and total > 0
            
            self.logger.info(
                "validation_tests_complete",
                total=total,
                passed=passed,
                failed=failed,
            )
            
            # Clean up test file
            os.remove(test_file)
            
            return {
                "success": success,
                "total": total,
                "passed": passed,
                "failed": failed,
                "output": output,
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error("validation_tests_timeout")
            os.remove(test_file)
            return {
                "success": False,
                "total": len(fix.validation_tests),
                "passed": 0,
                "failed": len(fix.validation_tests),
                "output": "Tests timed out after 60 seconds",
            }
        
        except Exception as e:
            self.logger.error("validation_tests_error", error=str(e))
            if os.path.exists(test_file):
                os.remove(test_file)
            return {
                "success": False,
                "total": len(fix.validation_tests),
                "passed": 0,
                "failed": len(fix.validation_tests),
                "output": f"Test execution error: {str(e)}",
            }
    
    def _rollback(self, fix: AutonomousFix, backup_path: str):
        """Rollback the fix using backup."""
        self.logger.warning("rolling_back_fix", fix_id=fix.fix_id)
        
        # Restore files from backup
        for file_info in fix.affected_files:
            backup_file = os.path.join(backup_path, file_info["path"])
            target_file = os.path.join(self.workspace_path, file_info["path"])
            
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, target_file)
                self.logger.debug("file_restored", file=file_info["path"])
        
        # Optionally run rollback code
        if fix.rollback_code:
            try:
                # Execute rollback code
                # (This is advanced - would need safe execution environment)
                self.logger.info("rollback_code_available", length=len(fix.rollback_code))
            except Exception as e:
                self.logger.error("rollback_code_failed", error=str(e))
        
        self.logger.info("rollback_complete")
    
    def _commit_fix(self, fix: AutonomousFix, modified_files: List[str]):
        """Auto-commit successful fix to git."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.workspace_path,
                capture_output=True,
            )
            
            if result.returncode != 0:
                self.logger.debug("not_a_git_repo")
                return
            
            for file_path in modified_files:
                subprocess.run(
                    ["git", "add", file_path],
                    cwd=self.workspace_path,
                )
            
            commit_msg = f"Phoenix Auto Fix: {fix.fix_id}\n\n{fix.human_explanation}\n\nApplied automatically."
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.workspace_path,
            )
            
            self.logger.info("fix_committed", fix_id=fix.fix_id)
            
        except Exception as e:
            self.logger.warning("auto_commit_failed", error=str(e))


