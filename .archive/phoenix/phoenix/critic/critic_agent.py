"""Critic agent - diagnoses failures using LLM with evaluator-reflect pattern."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from phoenix.core.config import get_config
from phoenix.core.logging import get_logger
from phoenix.core.models import BugType, DiagnosticReport, FailureEvent
from phoenix.critic.llm_client import LLMClient, create_llm_client

logger = get_logger(__name__)


class CriticAgent:
    """LLM-based agent that diagnoses failures and provides feedback."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize Critic agent.
        
        Args:
            llm_client: LLM client to use (creates default if None)
        """
        config = get_config()
        self.llm_client = llm_client or create_llm_client(
            model=config.critic_model
        )
        self.logger = get_logger(__name__)
    
    def diagnose_failure(
        self,
        failure_event: FailureEvent,
        source_code: Dict[str, str],
        test_code: Optional[str] = None,
    ) -> DiagnosticReport:
        """
        Diagnose a failure and produce a diagnostic report.
        
        Args:
            failure_event: The failure to diagnose
            source_code: Dict mapping file paths to their content
            test_code: Optional test source code
            
        Returns:
            DiagnosticReport with diagnosis and remediation guidance
        """
        self.logger.info(
            "diagnosing_failure",
            failure_id=str(failure_event.id),
            failure_type=failure_event.failure_type,
        )
        
        # Build the diagnosis prompt
        prompt = self._build_diagnosis_prompt(
            failure_event, source_code, test_code
        )
        
        # Get LLM response
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        try:
            response = self.llm_client.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused analysis
            )
            
            # Parse the structured response
            diagnostic = self._parse_diagnosis(response, failure_event)
            
            self.logger.info(
                "diagnosis_complete",
                failure_id=str(failure_event.id),
                bug_type=diagnostic.bug_type,
                confidence=diagnostic.confidence_score,
            )
            
            return diagnostic
            
        except Exception as e:
            self.logger.error(
                "diagnosis_failed",
                failure_id=str(failure_event.id),
                error=str(e),
            )
            raise
    
    def reflect_on_patch_failure(
        self,
        original_failure: FailureEvent,
        patch_content: str,
        validation_errors: List[str],
    ) -> str:
        """
        Reflect on why a patch failed validation.
        
        Args:
            original_failure: The original failure being fixed
            patch_content: The patch that was tried
            validation_errors: Errors from validation
            
        Returns:
            Reflection explaining what went wrong
        """
        self.logger.info("reflecting_on_patch_failure")
        
        prompt = f"""A patch was applied to fix a failure, but it didn't work.

Original Failure:
{original_failure.error_message}

Attempted Patch:
{patch_content}

Validation Errors:
{chr(10).join(validation_errors)}

Analyze why the patch failed and what needs to be corrected. Be specific about:
1. What the patch was trying to do
2. Why it didn't work
3. What constraints or edge cases were missed
4. Specific guidance for the next attempt
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a code review expert analyzing failed patches.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        return self.llm_client.chat_completion(messages=messages, temperature=0.5)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Critic agent."""
        return """You are an expert software debugger and code analyzer. Your role is to:

1. Analyze test failures and runtime errors
2. Identify the root cause of bugs
3. Classify the type of bug (logic error, boundary case, null handling, etc.)
4. Locate the specific code that needs to be fixed
5. Provide clear guidance for remediation

When diagnosing failures, be:
- Precise: Identify exact files, functions, and lines
- Thorough: Consider edge cases and side effects
- Practical: Provide actionable remediation strategies
- Conservative: Note constraints that must be preserved

Always respond in the specified JSON format for structured parsing."""
    
    def _build_diagnosis_prompt(
        self,
        failure_event: FailureEvent,
        source_code: Dict[str, str],
        test_code: Optional[str],
    ) -> str:
        """Build the diagnosis prompt."""
        prompt_parts = [
            "# Failure Diagnosis Request",
            "",
            "## Failure Details",
            f"Type: {failure_event.failure_type}",
            f"Test: {failure_event.test_name or 'N/A'}",
            f"Error: {failure_event.error_message}",
            "",
        ]
        
        if failure_event.stack_trace:
            prompt_parts.extend([
                "## Stack Trace",
                "```",
                failure_event.stack_trace,
                "```",
                "",
            ])
        
        if test_code:
            prompt_parts.extend([
                "## Test Code",
                "```python",
                test_code,
                "```",
                "",
            ])
        
        prompt_parts.append("## Source Code")
        for file_path, content in source_code.items():
            prompt_parts.extend([
                f"### File: {file_path}",
                "```python",
                content,
                "```",
                "",
            ])
        
        prompt_parts.extend([
            "## Required Output",
            "Provide a structured diagnosis in JSON format with these fields:",
            "- explanation: Natural language explanation of the bug",
            "- bug_type: One of [logic_error, boundary_case, null_handling, type_mismatch, "
            "off_by_one, race_condition, resource_leak, configuration, dependency, unknown]",
            "- root_cause: Specific description of what's wrong",
            "- suspected_files: List of files that likely need changes",
            "- suspected_functions: List of functions that likely need changes",
            "- recommended_strategy: How to fix it (be specific)",
            "- constraints: List of things that must NOT be changed (e.g., 'do not modify test logic', "
            "'preserve API signature')",
            "- confidence_score: Your confidence (0.0 to 1.0)",
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_diagnosis(
        self, response: str, failure_event: FailureEvent
    ) -> DiagnosticReport:
        """Parse LLM response into a DiagnosticReport."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                # Fallback: treat entire response as explanation
                data = self._create_fallback_diagnosis(response)
            
            # Map bug_type string to enum
            bug_type_str = data.get("bug_type", "unknown")
            try:
                bug_type = BugType(bug_type_str)
            except ValueError:
                bug_type = BugType.UNKNOWN
            
            return DiagnosticReport(
                failure_event_id=failure_event.id,
                explanation=data.get("explanation", response),
                bug_type=bug_type,
                root_cause=data.get("root_cause", "Unknown"),
                suspected_files=data.get("suspected_files", []),
                suspected_functions=data.get("suspected_functions", []),
                recommended_strategy=data.get("recommended_strategy", ""),
                constraints=data.get("constraints", [
                    "Do not modify test logic",
                    "Preserve existing API signatures",
                ]),
                confidence_score=float(data.get("confidence_score", 0.7)),
                raw_response=response,
            )
            
        except Exception as e:
            self.logger.warning(
                "failed_to_parse_diagnosis",
                error=str(e),
                response_preview=response[:200],
            )
            # Return a basic diagnostic report
            return DiagnosticReport(
                failure_event_id=failure_event.id,
                explanation=response,
                bug_type=BugType.UNKNOWN,
                root_cause=failure_event.error_message,
                suspected_files=failure_event.files_implicated,
                suspected_functions=[],
                recommended_strategy="Manual investigation required",
                constraints=["Do not modify test logic"],
                confidence_score=0.5,
                raw_response=response,
            )
    
    def _create_fallback_diagnosis(self, response: str) -> Dict:
        """Create a fallback diagnosis structure when JSON parsing fails."""
        return {
            "explanation": response,
            "bug_type": "unknown",
            "root_cause": "Unable to determine",
            "suspected_files": [],
            "suspected_functions": [],
            "recommended_strategy": response,
            "constraints": ["Do not modify test logic"],
            "confidence_score": 0.5,
        }
