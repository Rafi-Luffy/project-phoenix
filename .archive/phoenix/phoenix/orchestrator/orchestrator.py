"""Orchestrator - manages the remediation loop."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from phoenix.core.config import get_config
from phoenix.core.logging import get_logger
from phoenix.core.models import (
    FailureEvent,
    RemediationAttempt,
    RemediationStatus,
    ValidationStatus,
)
from phoenix.critic.critic_agent import CriticAgent
from phoenix.programmer.programmer_agent import ProgrammerAgent
from phoenix.validator.validator import Validator

logger = get_logger(__name__)


@dataclass
class OrchestratorConfig:
    """Configuration for orchestrator."""
    
    max_retries: int = 3
    timeout: int = 3600
    auto_apply: bool = False


class Orchestrator:
    """Orchestrates the complete remediation loop."""
    
    def __init__(
        self,
        project_id: UUID,
        project_path: Path,
        test_command: str = "pytest",
    ):
        """
        Initialize orchestrator.
        
        Args:
            project_id: ID of the project being healed
            project_path: Path to the project
            test_command: Test command to use
        """
        self.project_id = project_id
        self.project_path = project_path
        self.test_command = test_command
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # Initialize agents
        self.critic = CriticAgent()
        self.programmer = ProgrammerAgent(project_path)
        self.validator = Validator(project_path, test_command)
    
    def remediate(
        self,
        failure_event: FailureEvent,
        max_attempts: Optional[int] = None,
    ) -> RemediationAttempt:
        """
        Execute full remediation loop for a failure.
        
        Args:
            failure_event: The failure to fix
            max_attempts: Maximum patch attempts (defaults to config)
            
        Returns:
            RemediationAttempt with results
        """
        max_attempts = max_attempts or self.config.max_attempts
        
        # Create remediation attempt
        attempt = RemediationAttempt(
            failure_event_id=failure_event.id,
            project_id=self.project_id,
            status=RemediationStatus.PENDING,
        )
        
        self.logger.info(
            "starting_remediation",
            attempt_id=str(attempt.id),
            failure_id=str(failure_event.id),
            max_attempts=max_attempts,
        )
        
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Diagnosis (Critic)
            attempt.status = RemediationStatus.DIAGNOSING
            source_code = self._gather_source_code(failure_event)
            test_code = self._gather_test_code(failure_event)
            
            diagnostic = self.critic.diagnose_failure(
                failure_event, source_code, test_code
            )
            attempt.diagnostic_report_id = diagnostic.id
            
            self.logger.info(
                "diagnosis_complete",
                attempt_id=str(attempt.id),
                bug_type=diagnostic.bug_type,
            )
            
            # Step 2-5: Generate and validate patches (Programmer + Validator)
            reflection = None
            for iteration in range(1, max_attempts + 1):
                attempt.attempts_count = iteration
                attempt.status = RemediationStatus.GENERATING_PATCH
                
                # Generate patch
                patch = self.programmer.generate_patch(
                    remediation_attempt_id=attempt.id,
                    failure_event=failure_event,
                    diagnostic_report=diagnostic,
                    iteration=iteration,
                    reflection=reflection,
                )
                attempt.patch_ids.append(patch.id)
                
                self.logger.info(
                    "patch_generated",
                    attempt_id=str(attempt.id),
                    iteration=iteration,
                    patch_id=str(patch.id),
                )
                
                # Validate patch
                attempt.status = RemediationStatus.VALIDATING
                validation_result = self.validator.validate_patch(
                    patch,
                    original_failure_test=failure_event.test_name or "",
                    timeout=self.config.validation_timeout,
                )
                
                patch.is_validated = True
                patch.validation_result_id = validation_result.id
                
                self.logger.info(
                    "patch_validated",
                    attempt_id=str(attempt.id),
                    iteration=iteration,
                    status=validation_result.status,
                )
                
                # Check if successful
                if validation_result.status == ValidationStatus.SUCCESS:
                    attempt.status = RemediationStatus.SUCCESS
                    attempt.is_successful = True
                    attempt.successful_patch_id = patch.id
                    
                    self.logger.info(
                        "remediation_successful",
                        attempt_id=str(attempt.id),
                        iterations=iteration,
                    )
                    break
                
                # If not successful and not last attempt, reflect
                if iteration < max_attempts:
                    reflection = self.critic.reflect_on_patch_failure(
                        failure_event,
                        patch.patched_content,
                        validation_result.errors,
                    )
                    
                    self.logger.info(
                        "reflecting_on_failure",
                        attempt_id=str(attempt.id),
                        iteration=iteration,
                    )
            else:
                # Max attempts exhausted
                attempt.status = RemediationStatus.FAILED
                attempt.failure_reason = f"Max attempts ({max_attempts}) exhausted"
                
                self.logger.warning(
                    "remediation_failed",
                    attempt_id=str(attempt.id),
                    reason=attempt.failure_reason,
                )
            
        except Exception as e:
            attempt.status = RemediationStatus.ABORTED
            attempt.failure_reason = str(e)
            
            self.logger.error(
                "remediation_aborted",
                attempt_id=str(attempt.id),
                error=str(e),
            )
        
        finally:
            # Record completion time
            attempt.completed_at = datetime.utcnow()
            attempt.updated_at = datetime.utcnow()
            attempt.total_time_seconds = (
                attempt.completed_at - start_time
            ).total_seconds()
        
        return attempt
    
    def _gather_source_code(self, failure_event: FailureEvent) -> dict[str, str]:
        """Gather relevant source code files."""
        source_code = {}
        
        for file_path in failure_event.files_implicated:
            try:
                full_path = self.project_path / file_path
                if full_path.exists():
                    source_code[file_path] = full_path.read_text(encoding="utf-8")
            except Exception as e:
                self.logger.warning(
                    "failed_to_read_source",
                    file=file_path,
                    error=str(e),
                )
        
        return source_code
    
    def _gather_test_code(self, failure_event: FailureEvent) -> Optional[str]:
        """Gather test code if available."""
        if not failure_event.test_file:
            return None
        
        try:
            test_path = self.project_path / failure_event.test_file
            if test_path.exists():
                return test_path.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.warning(
                "failed_to_read_test",
                file=failure_event.test_file,
                error=str(e),
            )
        
        return None
