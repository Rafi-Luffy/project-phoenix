"""
Phoenix - Self-Healing Agentic AI Framework

A reflective runtime that makes AI systems and codebases self-healing.
"""

__version__ = "0.1.0"

from phoenix.core.models import (
    FailureEvent,
    DiagnosticReport,
    Patch,
    ValidationResult,
    RemediationAttempt,
    Project,
)

__all__ = [
    "FailureEvent",
    "DiagnosticReport",
    "Patch",
    "ValidationResult",
    "RemediationAttempt",
    "Project",
]
