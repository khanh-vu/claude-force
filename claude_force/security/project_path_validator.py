"""
Project Path Validator

Enhanced path validation for analyzing existing projects.
Prevents path traversal attacks while allowing safe project scanning.
"""

from pathlib import Path
from typing import Union, Optional, Set
import logging

from claude_force.path_validator import PathValidationError, validate_path


logger = logging.getLogger(__name__)


# System directories that should NEVER be analyzed
FORBIDDEN_ROOTS = {
    "/etc",
    "/sys",
    "/proc",
    "/root",
    "/boot",
    "/dev",
    "/run",
    "/var/run",
    "/tmp/systemd-private",
    "C:\\Windows",
    "C:\\Windows\\System32",
    "C:\\Program Files",
}


class ProjectPathValidator:
    """
    Validates paths within a project boundary for safe analysis.

    Security guarantees:
    1. All paths must be within the project root
    2. Symlinks are detected and validated
    3. System directories are forbidden
    4. Path traversal attacks are prevented

    Example:
        validator = ProjectPathValidator("/home/user/my-project")
        safe_path = validator.validate("/home/user/my-project/src/main.py")  # OK
        validator.validate("/etc/passwd")  # Raises SecurityError
    """

    def __init__(self, project_root: Union[str, Path]):
        """
        Initialize validator with project root boundary.

        Args:
            project_root: Absolute path to project root directory

        Raises:
            ValueError: If project_root is invalid or forbidden
        """
        self.project_root = Path(project_root).resolve()

        # Validate project root exists
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")

        if not self.project_root.is_dir():
            raise ValueError(f"Project root is not a directory: {project_root}")

        # Prevent analysis of system directories
        self._check_forbidden_root(self.project_root)

        logger.info(f"ProjectPathValidator initialized for: {self.project_root}")

    def _check_forbidden_root(self, path: Path) -> None:
        """
        Check if path is a forbidden system directory.

        Args:
            path: Path to check

        Raises:
            ValueError: If path is a forbidden directory
        """
        path_str = str(path)

        for forbidden in FORBIDDEN_ROOTS:
            if path_str.startswith(forbidden):
                raise ValueError(
                    f"Cannot analyze system directory: {path}\n"
                    f"Forbidden roots: {', '.join(FORBIDDEN_ROOTS)}"
                )

    def validate(
        self,
        target_path: Union[str, Path],
        must_exist: bool = True,
        follow_symlinks: bool = False,
    ) -> Path:
        """
        Validate a path is within project boundaries.

        Args:
            target_path: Path to validate
            must_exist: If True, path must exist
            follow_symlinks: If True, follow symlinks (with validation)

        Returns:
            Validated Path object

        Raises:
            PathValidationError: If path is invalid or outside project
            SecurityError: If symlink points outside project
        """
        # Convert to Path object
        path_obj = Path(target_path)

        # Check for symlink BEFORE resolving
        if path_obj.is_symlink():
            return self._validate_symlink(path_obj, follow_symlinks)

        # Resolve path
        real_path = path_obj.resolve()

        # Validate within project boundary
        if not self._is_within_project(real_path):
            raise SecurityError(
                f"Path traversal detected: '{target_path}' resolves to '{real_path}' "
                f"which is outside project root '{self.project_root}'"
            )

        # Check existence if required
        if must_exist and not real_path.exists():
            raise PathValidationError(f"Path does not exist: {target_path}")

        return real_path

    def _validate_symlink(self, symlink_path: Path, follow: bool) -> Path:
        """
        Validate a symlink target is safe.

        Args:
            symlink_path: Path to the symlink
            follow: Whether to follow the symlink

        Returns:
            Validated Path object

        Raises:
            SecurityError: If symlink points outside project
        """
        # Resolve the symlink target
        try:
            target_path = symlink_path.resolve()
        except (OSError, RuntimeError) as e:
            raise SecurityError(f"Cannot resolve symlink {symlink_path}: {e}")

        # Check if target is within project
        if not self._is_within_project(target_path):
            if follow:
                raise SecurityError(
                    f"Symlink attack detected: {symlink_path} -> {target_path}\n"
                    f"Target is outside project root: {self.project_root}"
                )
            else:
                # Log warning but allow if not following
                logger.warning(
                    f"Skipping symlink pointing outside project: "
                    f"{symlink_path} -> {target_path}"
                )
                raise PathValidationError(f"Symlink points outside project: {symlink_path}")

        # Symlink is safe - points within project
        logger.debug(f"Following safe symlink: {symlink_path} -> {target_path}")
        return target_path

    def _is_within_project(self, path: Path) -> bool:
        """
        Check if a path is within the project root.

        Args:
            path: Path to check (should be resolved)

        Returns:
            True if path is within project, False otherwise
        """
        try:
            # This will raise ValueError if path is not relative to project_root
            path.relative_to(self.project_root)
            return True
        except ValueError:
            return False

    def safe_iterdir(self, directory: Path):
        """
        Safely iterate directory contents with validation.

        Args:
            directory: Directory to iterate

        Yields:
            Validated Path objects for each item

        Raises:
            PathValidationError: If directory is invalid
        """
        # Validate directory itself
        validated_dir = self.validate(directory, must_exist=True)

        if not validated_dir.is_dir():
            raise PathValidationError(f"Not a directory: {directory}")

        try:
            for item in validated_dir.iterdir():
                # Validate each item (handles symlinks)
                try:
                    validated_item = self.validate(item, must_exist=False, follow_symlinks=False)
                    yield validated_item
                except (SecurityError, PathValidationError) as e:
                    # Log and skip unsafe items
                    logger.warning(f"Skipping unsafe path: {item} - {e}")
                    continue
        except PermissionError as e:
            logger.warning(f"Permission denied reading directory: {directory} - {e}")

    def safe_walk(self, start_path: Path, max_depth: Optional[int] = None):
        """
        Safely walk directory tree with validation.

        Args:
            start_path: Starting directory
            max_depth: Maximum depth to traverse (None = unlimited)

        Yields:
            Tuple of (dirpath, dirnames, filenames) like os.walk

        Raises:
            PathValidationError: If start_path is invalid
        """
        # Validate start path
        validated_start = self.validate(start_path, must_exist=True)

        def _walk_recursive(path: Path, depth: int):
            """Recursive walk with depth limiting"""
            if max_depth is not None and depth > max_depth:
                return

            try:
                dirs = []
                files = []

                for item in self.safe_iterdir(path):
                    if item.is_dir():
                        dirs.append(item.name)
                    elif item.is_file():
                        files.append(item.name)

                yield (path, dirs, files)

                # Recurse into subdirectories
                for dirname in dirs:
                    subdir = path / dirname
                    yield from _walk_recursive(subdir, depth + 1)

            except PathValidationError as e:
                # Skip paths that don't exist (broken symlinks, deleted files, etc.)
                logger.warning(f"Skipping inaccessible path {path}: {e}")
            except (PermissionError, OSError) as e:
                logger.warning(f"Error walking directory {path}: {e}")

        yield from _walk_recursive(validated_start, 0)


class SecurityError(Exception):
    """Raised when a security violation is detected"""

    pass


def validate_project_root(project_path: Union[str, Path]) -> Path:
    """
    Validate a project root path is safe to analyze.

    Args:
        project_path: Path to validate as project root

    Returns:
        Validated Path object

    Raises:
        ValueError: If path is invalid or forbidden

    Example:
        root = validate_project_root("/home/user/my-project")  # OK
        root = validate_project_root("/etc")  # Raises ValueError
    """
    path = Path(project_path).resolve()

    # Check exists
    if not path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")

    # Check is directory
    if not path.is_dir():
        raise ValueError(f"Project path is not a directory: {project_path}")

    # Check not forbidden
    path_str = str(path)
    for forbidden in FORBIDDEN_ROOTS:
        if path_str.startswith(forbidden):
            raise ValueError(
                f"Cannot analyze system directory: {path}\n"
                f"System directories are forbidden for security."
            )

    return path
