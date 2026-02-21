"""Sandbox for isolated patch testing using Docker."""

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from uuid import uuid4

import docker
from docker.models.containers import Container

from phoenix.core.config import get_config
from phoenix.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SandboxConfig:
    """Configuration for sandbox environment."""
    
    use_docker: bool = True
    timeout: int = 300
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    image: str = "python:3.11-slim"


class Sandbox:
    """Docker-based sandbox for safe patch validation."""
    
    def __init__(self, project_path: Path):
        """
        Initialize sandbox.
        
        Args:
            project_path: Path to the project to test
        """
        self.project_path = project_path
        self.config = get_config()
        self.docker_client = docker.from_env()
        self.logger = get_logger(__name__)
        self.sandbox_id = str(uuid4())[:8]
        self.container: Optional[Container] = None
        self.temp_dir: Optional[Path] = None
    
    def __enter__(self) -> "Sandbox":
        """Context manager entry."""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    def setup(self) -> None:
        """Set up the sandbox environment."""
        # Create temp directory for sandbox workspace
        self.temp_dir = Path(tempfile.mkdtemp(prefix=f"phoenix_sandbox_{self.sandbox_id}_"))
        
        # Copy project to sandbox
        shutil.copytree(
            self.project_path,
            self.temp_dir / "project",
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "*.pyc",
                ".git",
                "venv",
                ".venv",
                "node_modules",
            ),
        )
        
        self.logger.info(
            "sandbox_setup",
            sandbox_id=self.sandbox_id,
            temp_dir=str(self.temp_dir),
        )
    
    def apply_patch(self, file_path: str, patched_content: str) -> None:
        """
        Apply a patch in the sandbox.
        
        Args:
            file_path: Relative path to file
            patched_content: New content to write
        """
        if self.temp_dir is None:
            raise RuntimeError("Sandbox not initialized. Call setup() first.")
        target_file = self.temp_dir / "project" / file_path
        target_file.write_text(patched_content, encoding="utf-8")
        self.logger.debug("patch_applied_in_sandbox", file=file_path)
    
    def run_command(
        self,
        command: str,
        timeout: int = 300,
        use_docker: bool = True,
    ) -> tuple[int, str, str]:
        """
        Run a command in the sandbox.
        
        Args:
            command: Command to run
            timeout: Timeout in seconds
            use_docker: Whether to use Docker (False = subprocess)
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if use_docker:
            return self._run_in_docker(command, timeout)
        else:
            return self._run_in_subprocess(command, timeout)
    
    def _run_in_docker(self, command: str, timeout: int) -> tuple[int, str, str]:
        """Run command in Docker container."""
        if self.temp_dir is None:
            raise RuntimeError("Sandbox not initialized. Call setup() first.")
        
        try:
            # Create container
            self.container = self.docker_client.containers.run(
                image=self.config.sandbox_base_image,
                command=["sh", "-c", command],
                volumes={
                    str(self.temp_dir / "project"): {
                        "bind": "/workspace",
                        "mode": "rw",
                    }
                },
                working_dir="/workspace",
                mem_limit=self.config.sandbox_memory_limit,
                cpu_count=self.config.sandbox_cpu_limit,
                network_disabled=False,  # May need network for dependencies
                detach=True,
                remove=False,
            )
            
            # Wait for completion
            result = self.container.wait(timeout=timeout)
            exit_code = result["StatusCode"]
            
            # Get logs
            logs = self.container.logs().decode("utf-8")
            
            # Split stdout/stderr (Docker combines them)
            stdout = logs
            stderr = ""
            
            self.logger.info(
                "docker_command_completed",
                exit_code=exit_code,
                sandbox_id=self.sandbox_id,
            )
            
            return exit_code, stdout, stderr
            
        except docker.errors.ContainerError as e:  # type: ignore
            self.logger.error("docker_container_error", error=str(e))
            return e.exit_status, "", str(e)
        
        except Exception as e:
            self.logger.error("docker_execution_failed", error=str(e))
            return -1, "", str(e)
        
        finally:
            if self.container:
                try:
                    self.container.remove(force=True)
                except:
                    pass
    
    def _run_in_subprocess(self, command: str, timeout: int) -> tuple[int, str, str]:
        """Run command in subprocess (fallback without Docker)."""
        import subprocess
        
        if self.temp_dir is None:
            raise RuntimeError("Sandbox not initialized. Call setup() first.")
        
        try:
            result = subprocess.run(
                ["sh", "-c", command],
                cwd=self.temp_dir / "project",
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error("subprocess_timeout", timeout=timeout)
            return -1, "", "Timeout"
        
        except Exception as e:
            self.logger.error("subprocess_execution_failed", error=str(e))
            return -1, "", str(e)
    
    def cleanup(self) -> None:
        """Clean up sandbox resources."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.logger.info("sandbox_cleaned_up", sandbox_id=self.sandbox_id)
