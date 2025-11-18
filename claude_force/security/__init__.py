"""
Security Module

Provides security utilities for safe project analysis:
- Path validation and traversal prevention
- Sensitive file detection and filtering
- Safe subprocess execution
"""

from claude_force.security.project_path_validator import (
    ProjectPathValidator,
    SecurityError,
    validate_project_root,
    FORBIDDEN_ROOTS,
)

from claude_force.security.sensitive_file_detector import (
    SensitiveFileDetector,
    is_sensitive_file,
    get_default_detector,
    SENSITIVE_FILE_PATTERNS,
    SENSITIVE_DIRECTORIES,
)


__all__ = [
    # Path validation
    "ProjectPathValidator",
    "SecurityError",
    "validate_project_root",
    "FORBIDDEN_ROOTS",
    # Sensitive file detection
    "SensitiveFileDetector",
    "is_sensitive_file",
    "get_default_detector",
    "SENSITIVE_FILE_PATTERNS",
    "SENSITIVE_DIRECTORIES",
]
