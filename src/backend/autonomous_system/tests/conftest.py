import os
import sys
from pathlib import Path


def pytest_configure() -> None:
    """Ensure `autonomous_system` is importable when running tests from repo root."""
    repo_root = Path(__file__).resolve().parents[4]
    backend_root = repo_root / "src" / "backend"
    backend_root_str = str(backend_root)

    if backend_root.exists() and backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)

    # Also allow running tests from inside src/backend
    cwd_backend = Path(os.getcwd()).resolve()
    if (cwd_backend / "autonomous_system").exists():
        cwd_str = str(cwd_backend)
        if cwd_str not in sys.path:
            sys.path.insert(0, cwd_str)
