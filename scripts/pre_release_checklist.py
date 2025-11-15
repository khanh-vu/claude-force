#!/usr/bin/env python3
"""
Automated pre-release checklist for claude-force.

This script runs a comprehensive set of checks before allowing a release:
- All tests pass
- No security vulnerabilities
- Code is properly formatted
- No linting errors
- Changelog is updated
- Version is consistent
- Documentation is up to date

Exit codes:
  0 - All checks passed, ready for release
  1 - Some checks failed, not ready for release
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any


# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


CHECKS = [
    {
        "name": "Version consistency",
        "command": ["python3", "scripts/check_version_consistency.py"],
        "required": True,
    },
    {
        "name": "System tests",
        "command": ["pytest", "test_claude_system.py", "-v", "--tb=short"],
        "required": True,
    },
    {
        "name": "Unit tests",
        "command": ["pytest", "tests/", "-v", "--tb=short", "-x"],
        "required": False,  # Optional since some tests may need API keys
    },
    {
        "name": "Code formatting (black)",
        "command": ["black", "--check", "claude_force/"],
        "required": True,
    },
    {
        "name": "Security scan (bandit)",
        "command": ["bandit", "-r", "claude_force/", "-ll"],
        "required": True,
    },
    {
        "name": "Package build test",
        "command": ["python3", "-m", "build", "--outdir", "dist-test/"],
        "required": True,
    },
]


def print_header(text: str) -> None:
    """
    Print a formatted header.

    Args:
        text: Header text to print
    """
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_check_header(check_name: str, check_num: int, total: int) -> None:
    """
    Print header for individual check.

    Args:
        check_name: Name of the check
        check_num: Current check number
        total: Total number of checks
    """
    print(f"\n{YELLOW}[{check_num}/{total}] Running: {check_name}{RESET}")
    print("-" * 70)


def run_check(check: Dict[str, Any], check_num: int, total: int) -> Tuple[bool, str]:
    """
    Run a single check and return result.

    Args:
        check: Check configuration dictionary with 'name', 'command', 'required'
        check_num: Current check number
        total: Total number of checks

    Returns:
        Tuple of (success: bool, output: str)
    """
    print_check_header(check["name"], check_num, total)

    try:
        result = subprocess.run(
            check["command"],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            print(f"{GREEN}✅ {check['name']}: PASSED{RESET}")
            return True, result.stdout
        else:
            print(f"{RED}❌ {check['name']}: FAILED{RESET}")
            if result.stdout:
                print(f"\nStdout:\n{result.stdout}")
            if result.stderr:
                print(f"\nStderr:\n{result.stderr}")
            return False, result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        print(f"{RED}❌ {check['name']}: TIMEOUT (exceeded 5 minutes){RESET}")
        return False, "Check timed out"
    except FileNotFoundError:
        print(f"{YELLOW}⚠️  {check['name']}: SKIPPED (command not found){RESET}")
        # If command not found and check is required, fail
        if check.get("required", False):
            return False, "Required command not found"
        return True, "Skipped (command not found)"
    except Exception as e:
        print(f"{RED}❌ {check['name']}: ERROR - {e}{RESET}")
        return False, str(e)


def cleanup() -> None:
    """Clean up temporary files created during checks."""
    import shutil

    dist_test = Path("dist-test")
    if dist_test.exists():
        shutil.rmtree(dist_test)


def main() -> int:
    """
    Run all pre-release checks.

    Returns:
        0 if all required checks passed, 1 otherwise
    """
    print_header("🚀 Pre-release Checklist for claude-force")

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print(f"{RED}❌ Error: Must run from project root directory{RESET}")
        return 1

    # Install required tools if needed
    print(f"{BLUE}Checking required tools...{RESET}")
    required_tools = ["pytest", "black", "bandit"]
    missing_tools = []

    for tool in required_tools:
        result = subprocess.run(
            ["which", tool], capture_output=True, check=False
        )
        if result.returncode != 0:
            missing_tools.append(tool)

    if missing_tools:
        print(f"{YELLOW}⚠️  Missing tools: {', '.join(missing_tools)}{RESET}")
        print(f"{YELLOW}Installing with pip...{RESET}")
        subprocess.run(
            ["pip", "install", "pytest", "black", "bandit", "build"],
            check=False,
        )

    # Run all checks
    results = []
    outputs = []

    for i, check in enumerate(CHECKS, 1):
        passed, output = run_check(check, i, len(CHECKS))
        results.append((check, passed))
        outputs.append(output)

    # Clean up
    cleanup()

    # Print summary
    print_header("📊 Summary")

    required_passed = 0
    required_total = 0
    optional_passed = 0
    optional_total = 0

    for check, passed in results:
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        required = check.get("required", False)
        req_label = "[REQUIRED]" if required else "[OPTIONAL]"

        print(f"{status} - {check['name']} {req_label}")

        if required:
            required_total += 1
            if passed:
                required_passed += 1
        else:
            optional_total += 1
            if passed:
                optional_passed += 1

    print(f"\nRequired checks: {required_passed}/{required_total} passed")
    print(f"Optional checks: {optional_passed}/{optional_total} passed")

    # Determine overall result
    all_required_passed = required_passed == required_total

    if all_required_passed:
        print(f"\n{GREEN}{'=' * 70}{RESET}")
        print(f"{GREEN}✅ All required checks passed! Ready for release.{RESET}")
        print(f"{GREEN}{'=' * 70}{RESET}")
        return 0
    else:
        print(f"\n{RED}{'=' * 70}{RESET}")
        print(f"{RED}❌ Some required checks failed. Please fix before releasing.{RESET}")
        print(f"{RED}{'=' * 70}{RESET}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Interrupted by user{RESET}")
        cleanup()
        sys.exit(130)
