"""
Tests for Orchestrator module
"""
import pytest
import tempfile
from pathlib import Path
from uuid import uuid4
from phoenix.orchestrator.orchestrator import Orchestrator, OrchestratorConfig


class TestOrchestrator:
    """Tests for Orchestrator"""
    
    def test_init_orchestrator(self):
        """Test Orchestrator initialization"""
        temp_dir = Path(tempfile.mkdtemp())
        project_id = uuid4()
        
        orchestrator = Orchestrator(
            project_id=project_id,
            project_path=temp_dir,
            test_command="pytest"
        )
        
        assert orchestrator.project_id == project_id
        assert orchestrator.project_path == temp_dir
        assert orchestrator.test_command == "pytest"
        assert orchestrator.critic is not None
        assert orchestrator.programmer is not None
        assert orchestrator.validator is not None
    
    def test_orchestrator_config_defaults(self):
        """Test OrchestratorConfig defaults"""
        config = OrchestratorConfig()
        
        assert config.max_retries == 3
        assert config.timeout == 3600
        assert config.auto_apply is False
    
    def test_orchestrator_has_all_components(self):
        """Test that Orchestrator initializes all required components"""
        temp_dir = Path(tempfile.mkdtemp())
        project_id = uuid4()
        
        orchestrator = Orchestrator(
            project_id=project_id,
            project_path=temp_dir,
            test_command="pytest"
        )
        
        # Verify all components exist
        assert hasattr(orchestrator, 'critic')
        assert hasattr(orchestrator, 'programmer')
        assert hasattr(orchestrator, 'validator')
