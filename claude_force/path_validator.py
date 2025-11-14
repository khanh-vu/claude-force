"""
Path Validation Utilities

Provides secure path validation to prevent path traversal attacks.
All file paths from user input should be validated using these utilities.
"""

from pathlib import Path
from typing import Union, Optional


class PathValidationError(Exception):
    """Raised when path validation fails"""
    pass


def validate_path(
    path: Union[str, Path],
    base_dir: Optional[Union[str, Path]] = None,
    must_exist: bool = False,
    allow_symlinks: bool = False
) -> Path:
    """
    Validate a file path to prevent path traversal attacks

    Args:
        path: Path to validate
        base_dir: Base directory that path must be relative to (optional)
        must_exist: If True, raise error if path doesn't exist
        allow_symlinks: If False, raise error if path is a symlink

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If path is invalid or unsafe
    """
    try:
        # Validate path is not empty
        if not path or (isinstance(path, str) and not path.strip()):
            raise PathValidationError("Path cannot be empty")

        # Convert to Path object (don't resolve yet to check for symlinks)
        path_obj = Path(path)

        # Check if symlink BEFORE resolving (security: prevent symlink attacks)
        # Must check before resolve() because resolve() follows symlinks
        if not allow_symlinks and path_obj.is_symlink():
            raise PathValidationError(
                f"Symlinks not allowed: {path}"
            )

        # Now safe to resolve the path
        path_obj = path_obj.resolve()

        # Check existence if required
        if must_exist and not path_obj.exists():
            raise PathValidationError(
                f"Path does not exist: {path}"
            )

        # Validate against base directory if provided
        if base_dir:
            base_path = Path(base_dir).resolve()

            # Check if path is relative to base_dir
            try:
                path_obj.relative_to(base_path)
            except ValueError:
                raise PathValidationError(
                    f"Path traversal detected: '{path}' is outside allowed directory '{base_dir}'"
                )

        return path_obj

    except (OSError, RuntimeError) as e:
        raise PathValidationError(
            f"Invalid path: {path}. Error: {str(e)}"
        )


def validate_agent_file_path(path: Union[str, Path]) -> Path:
    """
    Validate an agent file path (must be in .claude/agents/)

    Args:
        path: Path to validate

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If path is invalid
    """
    path_obj = Path(path)

    # If relative path, assume it's relative to .claude
    if not path_obj.is_absolute():
        path_obj = Path(".claude") / path_obj

    # Validate against .claude directory
    return validate_path(
        path_obj,
        base_dir=".claude",
        must_exist=False,
        allow_symlinks=False
    )


def validate_config_file_path(path: Union[str, Path]) -> Path:
    """
    Validate a configuration file path (must be in .claude/)

    Args:
        path: Path to validate

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If path is invalid
    """
    path_obj = Path(path)

    # If relative path, assume it's relative to .claude
    if not path_obj.is_absolute():
        path_obj = Path(".claude") / path_obj

    # Validate against .claude directory
    return validate_path(
        path_obj,
        base_dir=".claude",
        must_exist=False,
        allow_symlinks=False
    )


def validate_output_file_path(
    path: Union[str, Path],
    allowed_dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    Validate an output file path

    Args:
        path: Path to validate
        allowed_dir: Directory where output is allowed (default: current directory)

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If path is invalid
    """
    if allowed_dir is None:
        allowed_dir = Path.cwd()

    return validate_path(
        path,
        base_dir=allowed_dir,
        must_exist=False,
        allow_symlinks=False
    )


def safe_join(base: Union[str, Path], *paths: str) -> Path:
    """
    Safely join paths and validate the result

    Args:
        base: Base directory
        *paths: Path components to join

    Returns:
        Validated Path object

    Raises:
        PathValidationError: If resulting path is outside base directory
    """
    base_path = Path(base).resolve()
    joined_path = base_path.joinpath(*paths).resolve()

    # Validate that joined path is still within base
    return validate_path(joined_path, base_dir=base_path)
