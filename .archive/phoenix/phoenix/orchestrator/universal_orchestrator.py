"""Universal Orchestrator - Coordinates self-healing for ANY system.

This is the brain of Phoenix's universal capabilities. It:
- Detects what kind of system it's dealing with
- Adapts all agents to work with that system
- Coordinates healing across languages, frameworks, platforms
- Works with Python, JavaScript, Java, Go, Rust, and more
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

from phoenix.core.config import config
from phoenix.core.logging import get_logger
from phoenix.core.universal_adapter import UniversalSystemAdapter, SystemProfile, Language
from phoenix.observer.multi_language_runner import MultiLanguageTestRunner
from phoenix.observer.failure_detector import FailureDetector
from phoenix.critic.llm_client import create_llm_client_with_fallback
from phoenix.db.models import Project

logger = get_logger(__name__)


class UniversalOrchestrator:
    """
    Universal self-healing orchestrator for ANY AI system.
    
    Capabilities:
    - Works with ANY programming language
    - Works with ANY agent framework (LangChain, AutoGen, CrewAI, etc.)
    - Works with ANY automation system (Airflow, Temporal, n8n, etc.)
    - Works with ANY cloud platform (AWS, Azure, GCP, on-prem, edge)
    - Automatically adapts to the target system
    """
    
    def __init__(self, project: Project):
        """
        Initialize universal orchestrator for a project.
        
        Args:
            project: Phoenix project (can be ANY language/framework)
        """
        self.project = project
        self.logger = get_logger(__name__)
        
        # Step 1: Analyze the system
        self.logger.info("initializing_universal_orchestrator", project=project.name)
        
        self.adapter = UniversalSystemAdapter(Path(project.repository_path))
        self.system_profile = self.adapter.analyze_system()
        
        self.logger.info(
            "system_detected",
            language=self.system_profile.primary_language,
            frameworks=self.system_profile.frameworks,
            test_framework=self.system_profile.test_framework,
            confidence=self.system_profile.confidence,
        )
        
        # Step 2: Initialize adapted components
        self.test_runner = MultiLanguageTestRunner(
            Path(project.repository_path),
            self.system_profile
        )
        
        self.failure_detector = FailureDetector()
        
        # Step 3: LLM client (universal - understands all languages)
        self.llm_client = create_llm_client_with_fallback()
    
    def observe(self) -> Dict[str, Any]:
        """
        Observe the system for failures (universal).
        
        Works with:
        - Python tests (pytest, unittest)
        - JavaScript tests (Jest, Mocha)
        - Java tests (JUnit, TestNG)
        - Go tests (go test)
        - Rust tests (cargo test)
        - And more...
        """
        self.logger.info(
            "observing_system",
            language=self.system_profile.primary_language,
            test_command=self.system_profile.test_command,
        )
        
        # Run tests in native language
        test_result = self.test_runner.run_tests()
        
        # Detect failures (language-agnostic)
        if test_result.failed > 0:
            failures = self.failure_detector.detect_failures(
                test_result.stderr + test_result.stdout,
                language=self.system_profile.primary_language.value
            )
            
            return {
                "status": "failure_detected",
                "language": self.system_profile.primary_language.value,
                "test_result": test_result,
                "failures": failures,
            }
        else:
            return {
                "status": "healthy",
                "language": self.system_profile.primary_language.value,
                "test_result": test_result,
            }
    
    def diagnose(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose failures using LLM (universal - understands all languages).
        
        The LLM is language-agnostic:
        - GPT-4 understands Python, JS, Java, Go, Rust, C++, etc.
        - Claude understands all major programming languages
        - Gemini is polyglot-capable
        """
        self.logger.info(
            "diagnosing_failure",
            language=self.system_profile.primary_language,
        )
        
        # Build language-aware prompt
        prompt = self._build_diagnostic_prompt(observation)
        
        # LLM diagnoses in any language
        diagnosis = self.llm_client.complete(prompt)
        
        return {
            "diagnosis": diagnosis,
            "language": self.system_profile.primary_language.value,
            "frameworks": self.system_profile.frameworks,
            "confidence": 0.85,  # TODO: Calculate from LLM response
        }
    
    def generate_fix(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code fix using LLM (universal - generates any language).
        
        LLM can generate:
        - Python code
        - JavaScript/TypeScript code
        - Java code
        - Go code
        - Rust code
        - Any other language
        """
        self.logger.info(
            "generating_fix",
            language=self.system_profile.primary_language,
        )
        
        # Build language-specific fix prompt
        prompt = self._build_fix_prompt(diagnosis)
        
        # LLM generates fix in target language
        fix = self.llm_client.complete(prompt)
        
        return {
            "fix": fix,
            "language": self.system_profile.primary_language.value,
            "target_files": [],  # TODO: Extract from LLM response
        }
    
    def validate(self, fix: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fix by running tests (universal).
        
        Runs tests in the native language:
        - Python: pytest
        - JavaScript: Jest/Mocha
        - Java: JUnit/Maven
        - Go: go test
        - Rust: cargo test
        """
        self.logger.info(
            "validating_fix",
            language=self.system_profile.primary_language,
        )
        
        # Apply fix (language-agnostic file operations)
        # TODO: Implement file patching
        
        # Run tests again in native language
        test_result = self.test_runner.run_tests()
        
        success = test_result.failed == 0
        
        return {
            "validation": "success" if success else "failed",
            "test_result": test_result,
            "language": self.system_profile.primary_language.value,
        }
    
    def _build_diagnostic_prompt(self, observation: Dict[str, Any]) -> str:
        """Build language-aware diagnostic prompt for LLM."""
        
        lang = self.system_profile.primary_language.value
        frameworks = ", ".join(self.system_profile.frameworks) or "none"
        
        test_output = observation.get("test_result", {})
        stderr = test_output.stderr if hasattr(test_output, "stderr") else ""
        
        prompt = f"""You are debugging a {lang.upper()} application.

**Project Information:**
- Language: {lang}
- Frameworks: {frameworks}
- Test Framework: {self.system_profile.test_framework}
- Runtime: {self.system_profile.runtime}

**Test Failure Output:**
```
{stderr}
```

**Task:**
Analyze this {lang} code failure and provide:
1. Root cause of the error
2. Affected files/functions
3. Recommended fix approach

Consider {lang}-specific best practices and {frameworks} framework patterns.
"""
        
        return prompt
    
    def _build_fix_prompt(self, diagnosis: Dict[str, Any]) -> str:
        """Build language-specific fix generation prompt."""
        
        lang = self.system_profile.primary_language.value
        frameworks = ", ".join(self.system_profile.frameworks) or "none"
        
        diagnosis_text = diagnosis.get("diagnosis", "")
        
        # Language-specific code style guides
        style_guides = {
            Language.PYTHON: "Follow PEP 8. Use type hints.",
            Language.JAVASCRIPT: "Follow Airbnb style guide. Use modern ES6+ syntax.",
            Language.TYPESCRIPT: "Use strict TypeScript. Explicit types everywhere.",
            Language.JAVA: "Follow Google Java Style Guide. Use Java 17+ features.",
            Language.GO: "Follow Effective Go. Use gofmt formatting.",
            Language.RUST: "Follow Rust naming conventions. Use cargo fmt.",
        }
        
        style_guide = style_guides.get(
            self.system_profile.primary_language,
            "Follow language best practices."
        )
        
        prompt = f"""You are an expert {lang.upper()} developer.

**Project Context:**
- Language: {lang}
- Frameworks: {frameworks}
- Style Guide: {style_guide}

**Diagnosis:**
{diagnosis_text}

**Task:**
Generate a complete {lang} code fix that:
1. Resolves the identified issue
2. Follows {lang} best practices
3. Works with {frameworks} framework(s)
4. Includes proper error handling
5. Is production-ready

Provide the complete fixed code, not just snippets.
"""
        
        return prompt
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed information about the detected system."""
        return {
            "language": self.system_profile.primary_language.value,
            "all_languages": [l.value for l in self.system_profile.languages],
            "frameworks": self.system_profile.frameworks,
            "framework_types": [ft.value for ft in self.system_profile.framework_types],
            "build_tool": self.system_profile.build_tool,
            "build_command": self.system_profile.build_command,
            "test_framework": self.system_profile.test_framework,
            "test_command": self.system_profile.test_command,
            "runtime": self.system_profile.runtime,
            "runtime_version": self.system_profile.runtime_version,
            "dependencies": self.system_profile.dependencies[:10],  # Top 10
            "total_dependencies": len(self.system_profile.dependencies),
            "platform": self.system_profile.platform,
            "has_tests": self.system_profile.has_tests,
            "has_ci_cd": self.system_profile.has_ci_cd,
            "has_docker": self.system_profile.has_docker,
            "detection_confidence": self.system_profile.confidence,
        }
    
    def supports_system(self) -> bool:
        """Check if Phoenix can work with this system."""
        # Phoenix supports ANY system where we can:
        # 1. Detect the language
        # 2. Run tests
        # 3. Read/write files
        
        return (
            self.system_profile.primary_language != Language.UNKNOWN
            and self.system_profile.confidence > 0.3
        )
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get Phoenix capabilities for this specific system."""
        return {
            "can_run_tests": self.system_profile.has_tests,
            "can_build": self.system_profile.build_command is not None,
            "can_deploy": self.system_profile.has_docker or self.system_profile.has_ci_cd,
            "can_monitor": True,  # Always true - we can watch logs/processes
            "can_heal": self.supports_system(),
            "language_supported": self.system_profile.primary_language in config.supported_languages,
        }


def create_universal_orchestrator(project: Project) -> UniversalOrchestrator:
    """
    Create a universal orchestrator that adapts to ANY project.
    
    This is the main entry point for Phoenix's universal capabilities.
    
    Args:
        project: Project to heal (can be ANY language/framework)
        
    Returns:
        Configured UniversalOrchestrator ready to heal
    """
    orchestrator = UniversalOrchestrator(project)
    
    if not orchestrator.supports_system():
        logger.warning(
            "unsupported_system",
            language=orchestrator.system_profile.primary_language,
            confidence=orchestrator.system_profile.confidence,
        )
    
    return orchestrator
