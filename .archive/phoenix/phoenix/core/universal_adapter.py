"""Universal System Adapter - Makes Phoenix work with ANY technology.

This module enables Phoenix to automatically detect and adapt to:
- ANY programming language (Python, JS, Java, Go, Rust, C++, etc.)
- ANY framework (LangChain, AutoGen, Temporal, Airflow, etc.)
- ANY platform (AWS, Azure, GCP, Kubernetes, Docker, etc.)
- ANY automation system (Zapier, n8n, Power Automate, etc.)

Phoenix is language-agnostic and platform-independent.
"""

import json
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class Language(str, Enum):
    """Supported programming languages (auto-detected)."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    CSHARP = "csharp"
    RUBY = "ruby"
    PHP = "php"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    SCALA = "scala"
    ELIXIR = "elixir"
    CLOJURE = "clojure"
    UNKNOWN = "unknown"


class FrameworkType(str, Enum):
    """Framework categories (auto-detected)."""
    AGENT_FRAMEWORK = "agent_framework"  # LangChain, AutoGen, CrewAI
    WEB_FRAMEWORK = "web_framework"      # FastAPI, Express, Spring
    WORKFLOW_ENGINE = "workflow_engine"  # Airflow, Temporal, Prefect
    ML_FRAMEWORK = "ml_framework"        # TensorFlow, PyTorch
    AUTOMATION = "automation"            # Zapier, n8n, Power Automate
    GENERIC = "generic"


@dataclass
class SystemProfile:
    """Complete profile of a system to be healed."""
    
    # Language detection
    primary_language: Language
    languages: List[Language]
    
    # Framework detection
    frameworks: List[str]
    framework_types: List[FrameworkType]
    
    # Build system
    build_tool: Optional[str]  # npm, maven, cargo, etc.
    build_command: Optional[str]
    
    # Test system
    test_framework: Optional[str]  # pytest, jest, junit, etc.
    test_command: Optional[str]
    test_pattern: Optional[str]
    
    # Runtime
    runtime: Optional[str]  # node, python, java, etc.
    runtime_version: Optional[str]
    
    # Dependencies
    dependency_file: Optional[str]  # package.json, requirements.txt, etc.
    dependencies: List[str]
    
    # Platform
    platform: Optional[str]  # kubernetes, docker, aws-lambda, etc.
    deployment_config: Dict[str, Any]
    
    # Project structure
    project_root: Path
    source_dirs: List[Path]
    config_files: List[Path]
    
    # Detected capabilities
    has_tests: bool
    has_ci_cd: bool
    has_docker: bool
    has_linting: bool
    
    # Meta
    confidence: float  # 0-1 confidence in detection


class UniversalSystemAdapter:
    """Automatically detects and adapts to ANY system."""
    
    # Language detection patterns
    LANGUAGE_MARKERS = {
        Language.PYTHON: {
            "files": [".py"],
            "configs": ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"],
        },
        Language.JAVASCRIPT: {
            "files": [".js", ".jsx"],
            "configs": ["package.json", ".eslintrc"],
        },
        Language.TYPESCRIPT: {
            "files": [".ts", ".tsx"],
            "configs": ["tsconfig.json", "package.json"],
        },
        Language.JAVA: {
            "files": [".java"],
            "configs": ["pom.xml", "build.gradle", "build.gradle.kts"],
        },
        Language.GO: {
            "files": [".go"],
            "configs": ["go.mod", "go.sum"],
        },
        Language.RUST: {
            "files": [".rs"],
            "configs": ["Cargo.toml", "Cargo.lock"],
        },
        Language.CPP: {
            "files": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
            "configs": ["CMakeLists.txt", "Makefile"],
        },
        Language.CSHARP: {
            "files": [".cs"],
            "configs": [".csproj", ".sln"],
        },
        Language.RUBY: {
            "files": [".rb"],
            "configs": ["Gemfile", "Rakefile"],
        },
        Language.PHP: {
            "files": [".php"],
            "configs": ["composer.json"],
        },
        Language.KOTLIN: {
            "files": [".kt", ".kts"],
            "configs": ["build.gradle.kts"],
        },
        Language.SWIFT: {
            "files": [".swift"],
            "configs": ["Package.swift"],
        },
    }
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        # Python AI/Agent Frameworks
        "langchain": {"imports": ["langchain"], "type": FrameworkType.AGENT_FRAMEWORK},
        "llamaindex": {"imports": ["llama_index"], "type": FrameworkType.AGENT_FRAMEWORK},
        "autogen": {"imports": ["autogen"], "type": FrameworkType.AGENT_FRAMEWORK},
        "crewai": {"imports": ["crewai"], "type": FrameworkType.AGENT_FRAMEWORK},
        "semantic-kernel": {"imports": ["semantic_kernel"], "type": FrameworkType.AGENT_FRAMEWORK},
        "haystack": {"imports": ["haystack"], "type": FrameworkType.AGENT_FRAMEWORK},
        
        # JavaScript/TypeScript AI Frameworks
        "langchain.js": {"deps": ["langchain", "@langchain"], "type": FrameworkType.AGENT_FRAMEWORK},
        "autogpt": {"deps": ["autogpt"], "type": FrameworkType.AGENT_FRAMEWORK},
        
        # Web Frameworks
        "fastapi": {"imports": ["fastapi"], "type": FrameworkType.WEB_FRAMEWORK},
        "flask": {"imports": ["flask"], "type": FrameworkType.WEB_FRAMEWORK},
        "django": {"imports": ["django"], "type": FrameworkType.WEB_FRAMEWORK},
        "express": {"deps": ["express"], "type": FrameworkType.WEB_FRAMEWORK},
        "spring": {"files": ["spring"], "type": FrameworkType.WEB_FRAMEWORK},
        
        # Workflow Engines
        "airflow": {"imports": ["airflow"], "type": FrameworkType.WORKFLOW_ENGINE},
        "prefect": {"imports": ["prefect"], "type": FrameworkType.WORKFLOW_ENGINE},
        "temporal": {"imports": ["temporal", "temporalio"], "type": FrameworkType.WORKFLOW_ENGINE},
        "dagster": {"imports": ["dagster"], "type": FrameworkType.WORKFLOW_ENGINE},
        
        # ML Frameworks
        "tensorflow": {"imports": ["tensorflow"], "type": FrameworkType.ML_FRAMEWORK},
        "pytorch": {"imports": ["torch"], "type": FrameworkType.ML_FRAMEWORK},
        "scikit-learn": {"imports": ["sklearn"], "type": FrameworkType.ML_FRAMEWORK},
    }
    
    # Test framework detection
    TEST_FRAMEWORKS = {
        "pytest": {"command": "pytest", "pattern": "test_*.py", "marker": "pytest.ini"},
        "jest": {"command": "npm test", "pattern": "*.test.js", "marker": "jest.config.js"},
        "junit": {"command": "mvn test", "pattern": "*Test.java", "marker": "pom.xml"},
        "go test": {"command": "go test ./...", "pattern": "*_test.go", "marker": "go.mod"},
        "cargo test": {"command": "cargo test", "pattern": "tests/", "marker": "Cargo.toml"},
        "mocha": {"command": "npm test", "pattern": "*.test.js", "marker": "mocha"},
        "rspec": {"command": "rspec", "pattern": "*_spec.rb", "marker": ".rspec"},
    }
    
    def __init__(self, project_path: Path):
        """Initialize universal adapter for a project."""
        self.project_path = Path(project_path)
        self.logger = get_logger(__name__)
    
    def analyze_system(self) -> SystemProfile:
        """
        Automatically analyze and profile ANY system.
        
        Returns:
            Complete system profile with detected capabilities
        """
        self.logger.info("analyzing_system", path=str(self.project_path))
        
        # Detect all aspects
        languages = self._detect_languages()
        frameworks = self._detect_frameworks()
        build_system = self._detect_build_system(languages[0] if languages else Language.UNKNOWN)
        test_system = self._detect_test_system(languages[0] if languages else Language.UNKNOWN)
        runtime = self._detect_runtime(languages[0] if languages else Language.UNKNOWN)
        dependencies = self._detect_dependencies(languages[0] if languages else Language.UNKNOWN)
        platform = self._detect_platform()
        structure = self._analyze_structure()
        
        profile = SystemProfile(
            primary_language=languages[0] if languages else Language.UNKNOWN,
            languages=languages,
            frameworks=[f["name"] for f in frameworks],
            framework_types=[f["type"] for f in frameworks],
            build_tool=build_system.get("tool"),
            build_command=build_system.get("command"),
            test_framework=test_system.get("framework"),
            test_command=test_system.get("command"),
            test_pattern=test_system.get("pattern"),
            runtime=runtime.get("name"),
            runtime_version=runtime.get("version"),
            dependency_file=dependencies.get("file"),
            dependencies=dependencies.get("packages", []),
            platform=platform.get("type"),
            deployment_config=platform.get("config", {}),
            project_root=self.project_path,
            source_dirs=structure["source_dirs"],
            config_files=structure["config_files"],
            has_tests=test_system.get("has_tests", False),
            has_ci_cd=structure["has_ci_cd"],
            has_docker=structure["has_docker"],
            has_linting=structure["has_linting"],
            confidence=self._calculate_confidence(languages, frameworks),
        )
        
        self.logger.info(
            "system_analyzed",
            language=profile.primary_language,
            frameworks=profile.frameworks,
            test_framework=profile.test_framework,
            confidence=profile.confidence,
        )
        
        return profile
    
    def _detect_languages(self) -> List[Language]:
        """Detect all languages used in the project."""
        detected = {}
        
        for lang, markers in self.LANGUAGE_MARKERS.items():
            score = 0
            
            # Check for source files
            for ext in markers["files"]:
                files = list(self.project_path.rglob(f"*{ext}"))
                score += len(files) * 10
            
            # Check for config files (stronger signal)
            for config in markers["configs"]:
                if (self.project_path / config).exists():
                    score += 100
            
            if score > 0:
                detected[lang] = score
        
        # Sort by score and return
        sorted_langs = sorted(detected.items(), key=lambda x: x[1], reverse=True)
        return [lang for lang, _ in sorted_langs] if sorted_langs else [Language.UNKNOWN]
    
    def _detect_frameworks(self) -> List[Dict[str, Any]]:
        """Detect frameworks and libraries used."""
        detected = []
        
        for name, pattern in self.FRAMEWORK_PATTERNS.items():
            found = False
            
            # Check imports in Python files
            if "imports" in pattern:
                for import_name in pattern["imports"]:
                    if self._search_in_files(f"import {import_name}", "*.py"):
                        found = True
                        break
            
            # Check dependencies in package.json
            if "deps" in pattern:
                package_json = self.project_path / "package.json"
                if package_json.exists():
                    content = package_json.read_text()
                    if any(dep in content for dep in pattern["deps"]):
                        found = True
            
            # Check for specific files
            if "files" in pattern:
                for file_pattern in pattern["files"]:
                    if list(self.project_path.rglob(f"*{file_pattern}*")):
                        found = True
                        break
            
            if found:
                detected.append({
                    "name": name,
                    "type": pattern["type"],
                })
        
        return detected
    
    def _detect_build_system(self, language: Language) -> Dict[str, Any]:
        """Detect build system and commands."""
        build_systems = {
            Language.PYTHON: [
                {"file": "setup.py", "tool": "setuptools", "command": "python setup.py build"},
                {"file": "pyproject.toml", "tool": "poetry", "command": "poetry build"},
            ],
            Language.JAVASCRIPT: [
                {"file": "package.json", "tool": "npm", "command": "npm run build"},
            ],
            Language.TYPESCRIPT: [
                {"file": "tsconfig.json", "tool": "tsc", "command": "npm run build"},
            ],
            Language.JAVA: [
                {"file": "pom.xml", "tool": "maven", "command": "mvn clean install"},
                {"file": "build.gradle", "tool": "gradle", "command": "gradle build"},
            ],
            Language.GO: [
                {"file": "go.mod", "tool": "go", "command": "go build"},
            ],
            Language.RUST: [
                {"file": "Cargo.toml", "tool": "cargo", "command": "cargo build"},
            ],
        }
        
        for system in build_systems.get(language, []):
            if (self.project_path / system["file"]).exists():
                return system
        
        return {}
    
    def _detect_test_system(self, language: Language) -> Dict[str, Any]:
        """Detect test framework and commands."""
        for name, config in self.TEST_FRAMEWORKS.items():
            # Check for marker file
            if "marker" in config:
                if (self.project_path / config["marker"]).exists():
                    has_tests = bool(list(self.project_path.rglob(config["pattern"])))
                    return {
                        "framework": name,
                        "command": config["command"],
                        "pattern": config["pattern"],
                        "has_tests": has_tests,
                    }
        
        return {"has_tests": False}
    
    def _detect_runtime(self, language: Language) -> Dict[str, Any]:
        """Detect runtime environment."""
        runtimes = {
            Language.PYTHON: {"name": "python", "cmd": "python --version"},
            Language.JAVASCRIPT: {"name": "node", "cmd": "node --version"},
            Language.TYPESCRIPT: {"name": "node", "cmd": "node --version"},
            Language.JAVA: {"name": "java", "cmd": "java -version"},
            Language.GO: {"name": "go", "cmd": "go version"},
            Language.RUST: {"name": "rust", "cmd": "rustc --version"},
        }
        
        runtime = runtimes.get(language)
        if runtime:
            try:
                result = subprocess.run(
                    runtime["cmd"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                version = result.stdout + result.stderr
                return {"name": runtime["name"], "version": version.strip()}
            except Exception:
                return {"name": runtime["name"]}
        
        return {}
    
    def _detect_dependencies(self, language: Language) -> Dict[str, Any]:
        """Detect dependencies and packages."""
        dep_files = {
            Language.PYTHON: ["requirements.txt", "pyproject.toml", "Pipfile"],
            Language.JAVASCRIPT: ["package.json"],
            Language.JAVA: ["pom.xml", "build.gradle"],
            Language.GO: ["go.mod"],
            Language.RUST: ["Cargo.toml"],
        }
        
        for dep_file in dep_files.get(language, []):
            path = self.project_path / dep_file
            if path.exists():
                packages = self._parse_dependencies(path)
                return {"file": dep_file, "packages": packages}
        
        return {}
    
    def _parse_dependencies(self, path: Path) -> List[str]:
        """Parse dependency file to extract package names."""
        try:
            content = path.read_text()
            
            # Python requirements.txt
            if path.name == "requirements.txt":
                return [line.split("==")[0].strip() for line in content.splitlines() 
                        if line.strip() and not line.startswith("#")]
            
            # package.json
            if path.name == "package.json":
                data = json.loads(content)
                deps = []
                for key in ["dependencies", "devDependencies"]:
                    if key in data:
                        deps.extend(data[key].keys())
                return deps
            
            # pyproject.toml
            if path.name == "pyproject.toml":
                # Simple parsing - extract lines with package names
                deps = re.findall(r'"([^"]+)"', content)
                return [d for d in deps if not d.startswith("python")]
            
        except Exception as e:
            self.logger.warning("dependency_parse_error", file=str(path), error=str(e))
        
        return []
    
    def _detect_platform(self) -> Dict[str, Any]:
        """Detect deployment platform and configuration."""
        platforms = []
        
        # Docker
        if (self.project_path / "Dockerfile").exists():
            platforms.append("docker")
        
        # Kubernetes
        if (self.project_path / "kubernetes").exists() or list(self.project_path.rglob("*.yaml")):
            platforms.append("kubernetes")
        
        # AWS
        if (self.project_path / "serverless.yml").exists():
            platforms.append("aws-lambda")
        
        # Azure
        if (self.project_path / "azure-pipelines.yml").exists():
            platforms.append("azure")
        
        # Terraform
        if list(self.project_path.rglob("*.tf")):
            platforms.append("terraform")
        
        return {"type": platforms[0] if platforms else None, "config": {"all": platforms}}
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze project structure."""
        return {
            "source_dirs": self._find_source_dirs(),
            "config_files": self._find_config_files(),
            "has_ci_cd": self._has_ci_cd(),
            "has_docker": (self.project_path / "Dockerfile").exists(),
            "has_linting": self._has_linting(),
        }
    
    def _find_source_dirs(self) -> List[Path]:
        """Find source code directories."""
        common_dirs = ["src", "lib", "app", "core", "pkg"]
        found = []
        for dir_name in common_dirs:
            path = self.project_path / dir_name
            if path.exists() and path.is_dir():
                found.append(path)
        return found or [self.project_path]
    
    def _find_config_files(self) -> List[Path]:
        """Find configuration files."""
        patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg"]
        configs = []
        for pattern in patterns:
            configs.extend(self.project_path.glob(pattern))
        return configs
    
    def _has_ci_cd(self) -> bool:
        """Check for CI/CD configuration."""
        ci_markers = [
            ".github/workflows",
            ".gitlab-ci.yml",
            "azure-pipelines.yml",
            "Jenkinsfile",
            ".circleci",
        ]
        return any((self.project_path / marker).exists() for marker in ci_markers)
    
    def _has_linting(self) -> bool:
        """Check for linting configuration."""
        lint_markers = [
            ".eslintrc",
            "pylint.rc",
            ".flake8",
            "tslint.json",
            ".rubocop.yml",
        ]
        return any((self.project_path / marker).exists() for marker in lint_markers)
    
    def _search_in_files(self, pattern: str, glob_pattern: str) -> bool:
        """Search for pattern in files matching glob."""
        for file in self.project_path.rglob(glob_pattern):
            try:
                if pattern in file.read_text():
                    return True
            except Exception:
                continue
        return False
    
    def _calculate_confidence(self, languages: List[Language], frameworks: List[Dict]) -> float:
        """Calculate confidence in system detection."""
        score = 0.0
        
        # Language detection confidence
        if languages and languages[0] != Language.UNKNOWN:
            score += 0.4
        
        # Framework detection confidence
        if frameworks:
            score += 0.3
        
        # Config file presence
        if (self.project_path / "package.json").exists() or \
           (self.project_path / "pyproject.toml").exists() or \
           (self.project_path / "Cargo.toml").exists():
            score += 0.3
        
        return min(score, 1.0)
    
    def get_test_command(self, profile: SystemProfile) -> str:
        """Get the appropriate test command for this system."""
        if profile.test_command:
            return profile.test_command
        
        # Fallback defaults by language
        defaults = {
            Language.PYTHON: "pytest",
            Language.JAVASCRIPT: "npm test",
            Language.TYPESCRIPT: "npm test",
            Language.JAVA: "mvn test",
            Language.GO: "go test ./...",
            Language.RUST: "cargo test",
        }
        
        return defaults.get(profile.primary_language, "make test")
    
    def get_build_command(self, profile: SystemProfile) -> Optional[str]:
        """Get the appropriate build command for this system."""
        return profile.build_command
    
    def adapt_error_patterns(self, profile: SystemProfile) -> Dict[str, List[str]]:
        """Get language-specific error patterns for detection."""
        patterns = {
            Language.PYTHON: [
                r"Traceback",
                r"Error:",
                r"Exception:",
                r"AssertionError",
                r"ImportError",
            ],
            Language.JAVASCRIPT: [
                r"Error:",
                r"TypeError:",
                r"ReferenceError:",
                r"SyntaxError:",
                r"at .+:\d+:\d+",
            ],
            Language.JAVA: [
                r"Exception in thread",
                r"at .+\(.+\.java:\d+\)",
                r"Caused by:",
                r"Error:",
            ],
            Language.GO: [
                r"panic:",
                r"goroutine \d+ \[running\]:",
                r"fatal error:",
            ],
            Language.RUST: [
                r"thread '.+' panicked at",
                r"error\[E\d+\]:",
                r"error: could not compile",
            ],
        }
        
        return patterns.get(profile.primary_language, [r"error", r"Error", r"ERROR"])
