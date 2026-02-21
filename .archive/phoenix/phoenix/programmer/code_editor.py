"""Code editor utilities for applying patches."""

import difflib
from pathlib import Path
from typing import Optional, Tuple

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class CodeEditor:
    """Utilities for reading, editing, and applying code changes."""
    
    def __init__(self, project_path: Path):
        """
        Initialize code editor.
        
        Args:
            project_path: Path to the project root
        """
        self.project_path = project_path
        self.logger = get_logger(__name__)
    
    def read_file(self, file_path: str) -> str:
        """
        Read a source file.
        
        Args:
            file_path: Relative path to file from project root
            
        Returns:
            File content
        """
        full_path = self.project_path / file_path
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error("file_read_error", file=file_path, error=str(e))
            raise
    
    def write_file(self, file_path: str, content: str) -> None:
        """
        Write content to a file.
        
        Args:
            file_path: Relative path to file from project root
            content: New file content
        """
        full_path = self.project_path / file_path
        
        # Ensure directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info("file_written", file=file_path)
        except Exception as e:
            self.logger.error("file_write_error", file=file_path, error=str(e))
            raise
    
    def create_diff(self, file_path: str, original: str, modified: str) -> str:
        """
        Create a unified diff between original and modified content.
        
        Args:
            file_path: File path for context
            original: Original content
            modified: Modified content
            
        Returns:
            Unified diff string
        """
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
        
        return "".join(diff)
    
    def apply_patch(self, file_path: str, patched_content: str) -> Tuple[str, str]:
        """
        Apply a patch to a file.
        
        Args:
            file_path: Relative path to file from project root
            patched_content: New content to write
            
        Returns:
            Tuple of (original_content, diff)
        """
        # Read original
        original = self.read_file(file_path)
        
        # Create diff
        diff = self.create_diff(file_path, original, patched_content)
        
        # Write patched content
        self.write_file(file_path, patched_content)
        
        return original, diff
    
    def revert_file(self, file_path: str, original_content: str) -> None:
        """
        Revert a file to its original content.
        
        Args:
            file_path: Relative path to file from project root
            original_content: Original content to restore
        """
        self.write_file(file_path, original_content)
        self.logger.info("file_reverted", file=file_path)
    
    def get_function_source(self, file_path: str, function_name: str) -> Optional[str]:
        """
        Extract source code of a specific function.
        
        Args:
            file_path: Relative path to file from project root
            function_name: Name of the function
            
        Returns:
            Function source code or None if not found
        """
        content = self.read_file(file_path)
        
        # Simple regex-based extraction (works for Python)
        # For production, use AST parsing
        import re
        
        pattern = rf"(def {re.escape(function_name)}\([^)]*\):.*?)(?=\ndef |\nclass |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        
        return match.group(1) if match else None
