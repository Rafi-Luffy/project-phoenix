"""
Tests for Programmer module - CodeEditor and ProgrammerAgent
"""
import pytest
import tempfile
from pathlib import Path
from phoenix.programmer.code_editor import CodeEditor
from phoenix.programmer.programmer_agent import ProgrammerAgent
from phoenix.critic.llm_client import LLMConfig, LLMProvider, create_llm_client
from phoenix.core.models import DiagnosticReport, BugType


class TestCodeEditor:
    """Tests for CodeEditor"""
    
    def test_read_file(self):
        """Test reading file content"""
        test_file = Path(__file__).parent.parent / "examples" / "calculator-buggy" / "calculator.py"
        project_path = test_file.parent
        editor = CodeEditor(project_path=project_path)
        content = editor.read_file(str(test_file))
        
        assert content is not None
        assert len(content) > 0
        assert "def" in content
    
    def test_write_file(self):
        """Test writing file content"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_path = Path(f.name)
        
        try:
            editor = CodeEditor(project_path=temp_path.parent)
            content = "def test():\n    return 42\n"
            editor.write_file(temp_path.name, content)
            
            # Verify content was written
            read_content = editor.read_file(temp_path.name)
            assert read_content == content
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestProgrammerAgent:
    """Tests for ProgrammerAgent"""
    
    def test_init_programmer_agent(self):
        """Test ProgrammerAgent initialization"""
        temp_dir = Path(tempfile.mkdtemp())
        llm_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        llm_client = create_llm_client(llm_config)
        
        programmer = ProgrammerAgent(project_path=temp_dir, llm_client=llm_client)
        
        assert programmer.llm_client is not None
        assert programmer.code_editor is not None
    
    def test_extract_code(self):
        """Test code extraction from LLM response"""
        temp_dir = Path(tempfile.mkdtemp())
        llm_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        llm_client = create_llm_client(llm_config)
        programmer = ProgrammerAgent(project_path=temp_dir, llm_client=llm_client)
        
        # Test with code blocks
        response = """
        Here's the fix:
        ```python
        def add(a, b):
            return a + b
        ```
        This should work now.
        """
        
        code = programmer._extract_code(response, fallback="")
        
        assert "def add" in code
        assert "return a + b" in code
        assert "```" not in code
