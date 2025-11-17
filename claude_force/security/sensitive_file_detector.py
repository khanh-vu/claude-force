"""
Sensitive File Detector

Detects and protects sensitive files during project analysis.
Prevents accidental exposure of credentials, keys, and secrets.
"""

from pathlib import Path
from typing import Union, List, Set, Optional
import re
import logging


logger = logging.getLogger(__name__)


# Patterns for sensitive files (regex)
SENSITIVE_FILE_PATTERNS = {
    # Environment files
    r"\.env$": "Environment variables",
    r"\.env\..*": "Environment variables (specific environment)",
    r"env\..*": "Environment variables",

    # Credentials and secrets
    r"credentials\.json$": "GCP/AWS credentials",
    r"credentials\.ya?ml$": "Credentials file",
    r"service-account.*\.json$": "Service account credentials",
    r"secrets\.json$": "Secrets file",
    r"secrets\.ya?ml$": "Secrets file",
    r"\.secrets$": "Secrets file",

    # Private keys and certificates
    r".*\.pem$": "PEM certificate/key",
    r".*\.key$": "Private key",
    r".*\.p12$": "PKCS12 certificate",
    r".*\.pfx$": "PFX certificate",
    r"id_rsa$": "SSH private key",
    r"id_dsa$": "SSH private key",
    r"id_ecdsa$": "SSH private key",
    r"id_ed25519$": "SSH private key",
    r".*_rsa$": "RSA private key",
    r".*_dsa$": "DSA private key",

    # API keys and tokens
    r"\.?api[-_]?keys?\..*": "API keys",
    r"\.?auth[-_]?tokens?\..*": "Authentication tokens",
    r"\.npmrc$": "NPM credentials",
    r"\.pypirc$": "PyPI credentials",

    # Cloud provider configs
    r"\.aws/credentials$": "AWS credentials",
    r"\.aws/config$": "AWS config",
    r"\.gcp/credentials$": "GCP credentials",
    r"\.azure/credentials$": "Azure credentials",

    # Database configs
    r"database\.ya?ml$": "Database configuration",
    r"db\.ya?ml$": "Database configuration",

    # Password files
    r"passwords?\.txt$": "Password file",
    r"passwd$": "Password file",
    r"shadow$": "Shadow password file",

    # Backup files that might contain sensitive data
    r".*\.sql\.gz$": "Database dump",
    r".*\.sql$": "Database dump",
    r"backup.*\.tar\.gz$": "Backup archive",

    # Private notes and documents
    r"private.*\.txt$": "Private document",
    r"confidential.*": "Confidential document",
}


# Directories that commonly contain sensitive data
SENSITIVE_DIRECTORIES = {
    ".git",
    ".ssh",
    ".gnupg",
    ".aws",
    ".azure",
    ".gcp",
    "credentials",
    "secrets",
    "private",
    "confidential",
}


# File extensions that may contain secrets
SENSITIVE_EXTENSIONS = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
}


class SensitiveFileDetector:
    """
    Detects and filters sensitive files during project analysis.

    Security guarantees:
    1. Sensitive files are never read
    2. File paths are logged but not content
    3. Can be configured with custom patterns
    4. Provides clear reasons for filtering

    Example:
        detector = SensitiveFileDetector()

        if detector.is_sensitive(Path(".env")):
            print("Skipping sensitive file")

        # Get all sensitive files in project
        sensitive = detector.scan_directory(Path("/project"))
    """

    def __init__(
        self,
        custom_patterns: Optional[List[str]] = None,
        custom_dirs: Optional[Set[str]] = None,
    ):
        """
        Initialize detector with patterns.

        Args:
            custom_patterns: Additional regex patterns to consider sensitive
            custom_dirs: Additional directory names to consider sensitive
        """
        # Compile regex patterns for performance
        self.patterns = {}
        for pattern, description in SENSITIVE_FILE_PATTERNS.items():
            self.patterns[re.compile(pattern, re.IGNORECASE)] = description

        # Add custom patterns
        if custom_patterns:
            for pattern in custom_patterns:
                self.patterns[re.compile(pattern, re.IGNORECASE)] = "Custom sensitive pattern"

        # Sensitive directories
        self.sensitive_dirs = SENSITIVE_DIRECTORIES.copy()
        if custom_dirs:
            self.sensitive_dirs.update(custom_dirs)

        logger.info(
            f"SensitiveFileDetector initialized with {len(self.patterns)} patterns, "
            f"{len(self.sensitive_dirs)} sensitive directories"
        )

    def is_sensitive(self, path: Union[str, Path]) -> bool:
        """
        Check if a file or directory should be considered sensitive.

        Args:
            path: Path to check

        Returns:
            True if file/directory is sensitive, False otherwise
        """
        path_obj = Path(path)
        filename = path_obj.name.lower()

        # Check if in sensitive directory
        for part in path_obj.parts:
            if part.lower() in self.sensitive_dirs:
                logger.debug(f"Sensitive directory detected: {path} (contains '{part}')")
                return True

        # Check filename against patterns
        for pattern, description in self.patterns.items():
            if pattern.search(filename):
                logger.debug(
                    f"Sensitive file detected: {path} "
                    f"(matches '{pattern.pattern}': {description})"
                )
                return True

        # Check file extension
        if path_obj.suffix.lower() in SENSITIVE_EXTENSIONS:
            logger.debug(f"Sensitive extension detected: {path} ({path_obj.suffix})")
            return True

        return False

    def get_sensitivity_reason(self, path: Union[str, Path]) -> Optional[str]:
        """
        Get the reason why a file is considered sensitive.

        Args:
            path: Path to check

        Returns:
            String describing why file is sensitive, or None if not sensitive
        """
        path_obj = Path(path)
        filename = path_obj.name.lower()

        # Check directory
        for part in path_obj.parts:
            if part.lower() in self.sensitive_dirs:
                return f"In sensitive directory: {part}"

        # Check patterns
        for pattern, description in self.patterns.items():
            if pattern.search(filename):
                return description

        # Check extension
        if path_obj.suffix.lower() in SENSITIVE_EXTENSIONS:
            return f"Sensitive file extension: {path_obj.suffix}"

        return None

    def scan_directory(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> List[dict]:
        """
        Scan a directory for sensitive files.

        Args:
            directory: Directory to scan
            recursive: If True, scan subdirectories

        Returns:
            List of dicts with keys: 'path', 'reason', 'type'

        Example:
            results = detector.scan_directory(Path("/project"))
            for item in results:
                print(f"{item['path']}: {item['reason']}")
        """
        sensitive_files = []

        if recursive:
            paths = directory.rglob("*")
        else:
            paths = directory.glob("*")

        for path in paths:
            if self.is_sensitive(path):
                reason = self.get_sensitivity_reason(path)
                file_type = "directory" if path.is_dir() else "file"

                sensitive_files.append({
                    "path": str(path),
                    "reason": reason,
                    "type": file_type,
                })

        logger.info(f"Found {len(sensitive_files)} sensitive items in {directory}")
        return sensitive_files

    def filter_safe_files(self, files: List[Path]) -> List[Path]:
        """
        Filter a list of files, removing sensitive ones.

        Args:
            files: List of file paths

        Returns:
            List of non-sensitive file paths

        Example:
            all_files = list(Path("/project").glob("**/*"))
            safe_files = detector.filter_safe_files(all_files)
        """
        safe = []
        filtered_count = 0

        for file in files:
            if not self.is_sensitive(file):
                safe.append(file)
            else:
                filtered_count += 1
                logger.debug(f"Filtered sensitive file: {file}")

        if filtered_count > 0:
            logger.info(f"Filtered {filtered_count} sensitive files from {len(files)} total")

        return safe

    def should_skip_content(self, path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """
        Determine if file content should be skipped during analysis.

        Args:
            path: File path to check

        Returns:
            Tuple of (should_skip: bool, reason: Optional[str])

        Example:
            should_skip, reason = detector.should_skip_content(".env")
            if should_skip:
                print(f"Skipping: {reason}")
        """
        if self.is_sensitive(path):
            reason = self.get_sensitivity_reason(path)
            return (True, reason)
        return (False, None)

    def create_skip_report(self, skipped_files: List[Path]) -> str:
        """
        Create a human-readable report of skipped files.

        Args:
            skipped_files: List of files that were skipped

        Returns:
            Formatted report string
        """
        if not skipped_files:
            return "No sensitive files skipped."

        report_lines = [
            "Sensitive Files Skipped for Privacy:",
            "=" * 60,
        ]

        # Group by reason
        by_reason = {}
        for file in skipped_files:
            reason = self.get_sensitivity_reason(file) or "Unknown"
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(file)

        for reason, files in sorted(by_reason.items()):
            report_lines.append(f"\n{reason} ({len(files)} files):")
            for file in sorted(files):
                report_lines.append(f"  - {file}")

        report_lines.extend([
            "",
            "=" * 60,
            f"Total: {len(skipped_files)} sensitive files protected",
            "",
            "These files were NOT read or analyzed for your privacy and security.",
        ])

        return "\n".join(report_lines)


# Singleton instance for convenience
_default_detector = None


def get_default_detector() -> SensitiveFileDetector:
    """
    Get the default singleton detector instance.

    Returns:
        Default SensitiveFileDetector instance
    """
    global _default_detector
    if _default_detector is None:
        _default_detector = SensitiveFileDetector()
    return _default_detector


def is_sensitive_file(path: Union[str, Path]) -> bool:
    """
    Quick check if a file is sensitive using default detector.

    Args:
        path: Path to check

    Returns:
        True if sensitive, False otherwise
    """
    return get_default_detector().is_sensitive(path)
