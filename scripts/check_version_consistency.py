#!/usr/bin/env python3
"""
Verify version consistency across all files in the claude-force package.

This script ensures that the version number is consistent across:
- pyproject.toml
- setup.py
- claude_force/__init__.py
- README.md

Exit codes:
  0 - All versions are consistent
  1 - Version mismatch detected
"""

import sys
import re
from pathlib import Path
from typing import Optional, Dict, List


def validate_semantic_version(version: str) -> bool:
    """
    Validate that a version string follows semantic versioning.

    Args:
        version: Version string to validate

    Returns:
        True if version is valid semantic version, False otherwise

    Examples:
        >>> validate_semantic_version("1.2.3")
        True
        >>> validate_semantic_version("1.2.3-alpha.1")
        True
        >>> validate_semantic_version("invalid")
        False
    """
    # Semantic versioning pattern: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
    pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$"
    return bool(re.match(pattern, version))


def get_version_from_pyproject() -> Optional[str]:
    """
    Extract version from pyproject.toml.

    Returns:
        Version string if found, None otherwise
    """
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return None

    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None


def get_version_from_setup() -> Optional[str]:
    """
    Extract version from setup.py.

    Returns:
        Version string if found, None otherwise
    """
    setup_path = Path("setup.py")
    if not setup_path.exists():
        return None

    content = setup_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None


def get_version_from_init() -> Optional[str]:
    """
    Extract version from claude_force/__init__.py.

    Returns:
        Version string if found, None otherwise
    """
    init_path = Path("claude_force/__init__.py")
    if not init_path.exists():
        return None

    content = init_path.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else None


def get_version_from_readme() -> Optional[str]:
    """
    Extract version from README.md.

    Returns:
        Version string if found, None otherwise
    """
    readme_path = Path("README.md")
    if not readme_path.exists():
        return None

    content = readme_path.read_text()
    # Look for **Version**: X.Y.Z pattern
    match = re.search(r'\*\*Version\*\*:\s*([0-9]+\.[0-9]+\.[0-9]+)', content)
    return match.group(1) if match else None


def main() -> int:
    """
    Check version consistency across all files.

    Returns:
        0 if all versions are consistent, 1 otherwise
    """
    print("=" * 70)
    print("Version Consistency Check")
    print("=" * 70)

    versions: Dict[str, Optional[str]] = {
        "pyproject.toml": get_version_from_pyproject(),
        "setup.py": get_version_from_setup(),
        "claude_force/__init__.py": get_version_from_init(),
        "README.md": get_version_from_readme(),
    }

    print("\nVersions found:")
    for source, version in versions.items():
        if version:
            print(f"  ✓ {source:30s} → {version}")
        else:
            print(f"  ✗ {source:30s} → NOT FOUND")

    # Check for missing versions
    missing: List[str] = [source for source, version in versions.items() if version is None]
    if missing:
        print(f"\n❌ Missing version in: {', '.join(missing)}")
        return 1

    # Validate semantic versioning format
    invalid_versions: List[str] = []
    for source, version in versions.items():
        if version and not validate_semantic_version(version):
            invalid_versions.append(f"{source} ({version})")

    if invalid_versions:
        print(f"\n⚠️  Invalid semantic version format in:")
        for invalid in invalid_versions:
            print(f"   • {invalid}")
        print("   Expected format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]")
        return 1

    # Check for consistency
    unique_versions = set(v for v in versions.values() if v is not None)
    if len(unique_versions) != 1:
        print(f"\n❌ Version mismatch detected!")
        print(f"   Found {len(unique_versions)} different versions:")
        for version in sorted(unique_versions):
            sources = [s for s, v in versions.items() if v == version]
            print(f"   • {version} in: {', '.join(sources)}")
        return 1

    # All checks passed
    version = list(unique_versions)[0]
    print(f"\n✅ All versions are consistent: {version}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
