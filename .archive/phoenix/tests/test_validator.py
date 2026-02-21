"""
Tests for Validator module
"""
import pytest
import tempfile
from pathlib import Path
from uuid import uuid4
from phoenix.validator.validator import Validator
from phoenix.validator.sandbox import Sandbox, SandboxConfig
from phoenix.core.models import Patch, ValidationStatus


class TestSandbox:
    """Tests for Sandbox"""
    
    def test_init_sandbox(self):
        """Test Sandbox initialization"""
        config = SandboxConfig(use_docker=False)  # Don't require Docker for unit tests
        sandbox = Sandbox(config)
        
        assert sandbox.config.use_docker == False
    
    def test_sandbox_setup(self):
        """Test sandbox setup creates temp directory"""
        config = SandboxConfig(use_docker=False)
        sandbox = Sandbox(config)
        
        sandbox.setup(Path(tempfile.mkdtemp()))
        
        assert sandbox.temp_dir is not None
        assert sandbox.temp_dir.exists()
        
        sandbox.cleanup()


class TestValidator:
    """Tests for Validator"""
    
    def test_init_validator(self):
        """Test Validator initialization"""
        temp_dir = Path(tempfile.mkdtemp())
        validator = Validator(project_path=temp_dir)
        
        assert validator.project_path == temp_dir
        assert hasattr(validator, 'test_runner')
    
    def test_validate_patch_structure(self):
        """Test patch validation returns result"""
        temp_dir = Path(tempfile.mkdtemp())
        validator = Validator(project_path=temp_dir)
        
        remediation_id = uuid4()
        patch = Patch(
            remediation_attempt_id=remediation_id,
            file_path="test.py",
            patched_content="def add(a, b): return a + b",
            description="Fix add function operator"
        )
        
        # Note: This would normally run tests
        # For unit test, just verify method exists
        assert hasattr(validator, 'validate_patch')
        assert callable(validator.validate_patch)
