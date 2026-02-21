"""Core utilities and configuration for Phoenix."""

import os
from pathlib import Path
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class PhoenixConfig(BaseSettings):
    """Phoenix runtime configuration."""
    
    # Database
    database_url: str = "postgresql://phoenix:phoenix@localhost:5432/phoenix"
    vector_store_path: str = "./data/vector_store"
    
    # LLM Providers - Commercial Cloud
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    ai21_api_key: Optional[str] = None
    
    # Azure & Enterprise
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    aws_bedrock_region: str = "us-east-1"
    vertex_ai_project: Optional[str] = None
    vertex_ai_location: str = "us-central1"
    
    # High-Performance Inference
    groq_api_key: Optional[str] = None
    together_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None
    anyscale_api_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    
    # Open Source / Local
    ollama_base_url: str = "http://localhost:11434"
    lm_studio_base_url: str = "http://localhost:1234"
    llamacpp_base_url: Optional[str] = None
    vllm_base_url: Optional[str] = None
    
    # Hugging Face
    huggingface_api_key: Optional[str] = None
    huggingface_endpoint: Optional[str] = None
    
    # Specialized
    mistral_api_key: Optional[str] = None
    deepinfra_api_key: Optional[str] = None
    fireworks_api_key: Optional[str] = None
    
    # LLM Configuration
    default_llm_provider: str = "openai"
    default_model: str = "gpt-4-turbo-preview"
    critic_model: str = "gpt-4-turbo-preview"
    programmer_model: str = "gpt-4-turbo-preview"
    
    # Fallback Configuration
    enable_llm_fallback: bool = True
    fallback_providers: list = ["openai", "gemini", "anthropic", "ollama"]
    
    # Model-Specific Settings
    use_vision_models: bool = False
    vision_model: str = "gpt-4-vision-preview"
    embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = "openai"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Phoenix Runtime
    max_attempts: int = 5
    validation_timeout: int = 300
    sandbox_memory_limit: str = "2g"
    sandbox_cpu_limit: int = 2
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Docker
    docker_registry: str = "phoenix"
    sandbox_base_image: str = "python:3.11-slim"
    
    # Metrics
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    
    # Paths
    workspaces_dir: Path = Path("./workspaces")
    sandboxes_dir: Path = Path("./sandboxes")
    logs_dir: Path = Path("./logs")
    data_dir: Path = Path("./data")
    
    # Universal System Support
    auto_detect_language: bool = True
    auto_detect_framework: bool = True
    auto_detect_test_runner: bool = True
    supported_languages: list = [
        "python", "javascript", "typescript", "java", "go", "rust",
        "cpp", "csharp", "ruby", "php", "kotlin", "swift"
    ]
    
    # Multi-Language Test Execution
    python_test_command: str = "pytest -v --tb=short"
    javascript_test_command: str = "npm test"
    java_test_command: str = "mvn test"
    go_test_command: str = "go test ./... -v"
    rust_test_command: str = "cargo test"
    
    # Cross-Platform Build Commands
    enable_multi_language_builds: bool = True
    docker_multi_arch: bool = True
    
    # Framework Integration
    enable_langchain_integration: bool = True
    enable_autogen_integration: bool = True
    enable_temporal_integration: bool = True
    enable_airflow_integration: bool = True
    
    # Universal Monitoring
    monitor_any_runtime: bool = True
    monitor_nodejs: bool = True
    monitor_jvm: bool = True
    monitor_dotnet: bool = True
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Global configuration instance
config = PhoenixConfig()

# Alias for compatibility
Settings = PhoenixConfig


def get_config() -> PhoenixConfig:
    """Get the global Phoenix configuration."""
    return config


def ensure_directories() -> None:
    """Create required directories if they don't exist."""
    config.workspaces_dir.mkdir(parents=True, exist_ok=True)
    config.sandboxes_dir.mkdir(parents=True, exist_ok=True)
    config.logs_dir.mkdir(parents=True, exist_ok=True)
    config.data_dir.mkdir(parents=True, exist_ok=True)
    Path(config.vector_store_path).parent.mkdir(parents=True, exist_ok=True)
