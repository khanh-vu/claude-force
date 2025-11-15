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


def get_version_from_pyproject():
    """Extract version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return None

    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None


def get_version_from_setup():
    """Extract version from setup.py."""
    setup_path = Path("setup.py")
    if not setup_path.exists():
        return None

    content = setup_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None


def get_version_from_init():
    """Extract version from claude_force/__init__.py."""
    init_path = Path("claude_force/__init__.py")
    if not init_path.exists():
        return None

    content = init_path.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else None


def get_version_from_readme():
    """Extract version from README.md."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return None

    content = readme_path.read_text()
    # Look for **Version**: X.Y.Z pattern
    match = re.search(r'\*\*Version\*\*:\s*([0-9]+\.[0-9]+\.[0-9]+)', content)
    return match.group(1) if match else None


def main():
    """Check version consistency across all files."""
    print("=" * 70)
    print("Version Consistency Check")
    print("=" * 70)

    versions = {
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
    missing = [source for source, version in versions.items() if version is None]
    if missing:
        print(f"\n❌ Missing version in: {', '.join(missing)}")
        return 1

    # Check for consistency
    unique_versions = set(versions.values())
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
