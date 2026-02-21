"""Programmer agent - generates code patches using LLM with self-refine."""

from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from phoenix.core.config import get_config
from phoenix.core.logging import get_logger
from phoenix.core.models import DiagnosticReport, FailureEvent, Patch
from phoenix.critic.llm_client import LLMClient, create_llm_client
from phoenix.programmer.code_editor import CodeEditor

logger = get_logger(__name__)


class ProgrammerAgent:
    """LLM-based agent that generates code patches to fix failures."""
    
    def __init__(
        self,
        project_path: Path,
        llm_client: Optional[LLMClient] = None,
    ):
        """
        Initialize Programmer agent.
        
        Args:
            project_path: Path to the project being fixed
            llm_client: LLM client to use (creates default if None)
        """
        config = get_config()
        self.project_path = project_path
        self.llm_client = llm_client or create_llm_client(
            model=config.programmer_model
        )
        self.code_editor = CodeEditor(project_path)
        self.logger = get_logger(__name__)
    
    def generate_patch(
        self,
        remediation_attempt_id: UUID,
        failure_event: FailureEvent,
        diagnostic_report: DiagnosticReport,
        iteration: int = 1,
        reflection: Optional[str] = None,
        similar_fixes: Optional[List[str]] = None,
    ) -> Patch:
        """
        Generate a code patch to fix a failure.
        
        Args:
            remediation_attempt_id: ID of the remediation attempt
            failure_event: The failure being fixed
            diagnostic_report: Diagnosis from Critic
            iteration: Iteration number (for self-refine loop)
            reflection: Reflection on previous failed patch
            similar_fixes: Examples of similar fixes from knowledge base
            
        Returns:
            Patch object with proposed changes
        """
        self.logger.info(
            "generating_patch",
            failure_id=str(failure_event.id),
            iteration=iteration,
        )
        
        # Determine which file to patch
        target_file = self._select_target_file(
            failure_event, diagnostic_report
        )
        
        # Read current source code
        current_code = self.code_editor.read_file(target_file)
        
        # Build patch generation prompt
        prompt = self._build_patch_prompt(
            failure_event,
            diagnostic_report,
            target_file,
            current_code,
            iteration,
            reflection,
            similar_fixes,
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
                temperature=0.2,  # Low temperature for deterministic fixes
            )
            
            # Extract code from response
            patched_code = self._extract_code(response, current_code)
            
            # Create diff
            diff = self.code_editor.create_diff(
                target_file, current_code, patched_code
            )
            
            # Create patch object
            patch = Patch(
                remediation_attempt_id=remediation_attempt_id,
                iteration=iteration,
                patch_type="code",
                file_path=target_file,
                original_content=current_code,
                patched_content=patched_code,
                diff=diff,
                description=self._extract_description(response),
                reasoning=self._extract_reasoning(response),
            )
            
            self.logger.info(
                "patch_generated",
                failure_id=str(failure_event.id),
                target_file=target_file,
                iteration=iteration,
            )
            
            return patch
            
        except Exception as e:
            self.logger.error(
                "patch_generation_failed",
                failure_id=str(failure_event.id),
                error=str(e),
            )
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Programmer agent."""
        return """You are an expert software engineer specializing in automated code repair.

Your role is to generate precise, minimal code patches that fix bugs while:
- Preserving all existing functionality
- Following the codebase's style and conventions
- Not modifying tests unless absolutely necessary
- Avoiding over-engineering or unnecessary refactoring
- Handling edge cases properly

Always respond with:
1. A brief description of the fix
2. Your reasoning
3. The complete modified code wrapped in ```python ``` code blocks

Be conservative and surgical in your changes."""
    
    def _build_patch_prompt(
        self,
        failure_event: FailureEvent,
        diagnostic_report: DiagnosticReport,
        target_file: str,
        current_code: str,
        iteration: int,
        reflection: Optional[str],
        similar_fixes: Optional[List[str]],
    ) -> str:
        """Build the patch generation prompt."""
        prompt_parts = [
            "# Code Repair Task",
            "",
            f"## Iteration {iteration}",
            "",
            "## Failure Information",
            f"Test: {failure_event.test_name or 'N/A'}",
            f"Error: {failure_event.error_message}",
            "",
        ]
        
        if failure_event.stack_trace:
            prompt_parts.extend([
                "## Stack Trace",
                "```",
                failure_event.stack_trace[:500],  # Truncate for token limits
                "```",
                "",
            ])
        
        prompt_parts.extend([
            "## Diagnosis",
            f"Bug Type: {diagnostic_report.bug_type}",
            f"Root Cause: {diagnostic_report.root_cause}",
            f"Recommended Strategy: {diagnostic_report.recommended_strategy}",
            "",
            "## Constraints",
        ])
        
        for constraint in diagnostic_report.constraints:
            prompt_parts.append(f"- {constraint}")
        
        prompt_parts.extend(["", "## Current Code"])
        prompt_parts.extend([
            f"File: {target_file}",
            "```python",
            current_code,
            "```",
            "",
        ])
        
        if reflection and iteration > 1:
            prompt_parts.extend([
                "## Reflection on Previous Attempt",
                reflection,
                "",
            ])
        
        if similar_fixes:
            prompt_parts.extend([
                "## Similar Fixes (for reference)",
            ])
            for i, fix in enumerate(similar_fixes, 1):
                prompt_parts.extend([
                    f"### Example {i}",
                    "```python",
                    fix,
                    "```",
                    "",
                ])
        
        prompt_parts.extend([
            "## Task",
            f"Generate a fixed version of {target_file} that:",
            "1. Fixes the reported bug",
            "2. Passes the failing test",
            "3. Doesn't break any existing functionality",
            "4. Follows the recommended strategy",
            "5. Respects all constraints",
            "",
            "Provide:",
            "- Description: Brief explanation of the fix",
            "- Reasoning: Why this fix works",
            "- Fixed Code: Complete file content in ```python ``` block",
        ])
        
        return "\n".join(prompt_parts)
    
    def _select_target_file(
        self,
        failure_event: FailureEvent,
        diagnostic_report: DiagnosticReport,
    ) -> str:
        """Select which file to patch."""
        # Priority: diagnostic suspected files > failure implicated files
        if diagnostic_report.suspected_files:
            return diagnostic_report.suspected_files[0]
        
        if failure_event.files_implicated:
            return failure_event.files_implicated[0]
        
        # Fallback: extract from test name or error
        if failure_event.test_file:
            # Convert test file to source file (heuristic)
            test_file = failure_event.test_file
            if test_file.startswith("test_"):
                return test_file.replace("test_", "", 1)
            if "/test_" in test_file:
                return test_file.replace("/test_", "/", 1)
        
        raise ValueError("Cannot determine target file for patching")
    
    def _extract_code(self, response: str, fallback: str) -> str:
        """Extract code from LLM response."""
        # Look for code blocks
        import re
        
        # Match ```python ... ```
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            # Return the last code block (most likely the full solution)
            return matches[-1].strip()
        
        # Try generic code blocks
        pattern = r"```\s*(.*?)\s*```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[-1].strip()
        
        # No code block found - return the whole response or fallback
        self.logger.warning("no_code_block_found_in_response")
        return response.strip() if response.strip() else fallback
    
    def _extract_description(self, response: str) -> str:
        """Extract description from LLM response."""
        import re
        
        # Look for "Description:" section
        match = re.search(
            r"Description:\s*(.+?)(?:\n\n|Reasoning:|Fixed Code|```)",
            response,
            re.DOTALL | re.IGNORECASE,
        )
        
        if match:
            return match.group(1).strip()
        
        # Return first line as description
        lines = response.split("\n")
        return lines[0] if lines else "Code fix"
    
    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning from LLM response."""
        import re
        
        # Look for "Reasoning:" section
        match = re.search(
            r"Reasoning:\s*(.+?)(?:\n\n|Fixed Code|```)",
            response,
            re.DOTALL | re.IGNORECASE,
        )
        
        if match:
            return match.group(1).strip()
        
        return "N/A"
