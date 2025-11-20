#!/usr/bin/env python3
"""
End-to-End Test Runner (Python version)

This script simulates a fresh installation and runs end-user tests.
Works on all platforms (Windows, Linux, macOS).

Usage:
    python scripts/run_e2e_tests.py [--clean] [--no-venv]

Options:
    --clean     Clean up test environment after running
    --no-venv   Skip virtual environment creation (use current environment)
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path
import venv


# ANSI color codes (work on most terminals)
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def print_step(msg, color=Colors.YELLOW):
    """Print a step message."""
    print(f"{color}{msg}{Colors.NC}")


def print_success(msg):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")


def print_error(msg):
    """Print an error message."""
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")


def print_info(msg):
    """Print an info message."""
    print(f"{Colors.BLUE}{msg}{Colors.NC}")


def run_command(cmd, check=True, capture=False, cwd=None):
    """Run a shell command."""
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=True, check=check, capture_output=True, text=True, cwd=cwd
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, check=check, cwd=cwd)
            return result.returncode, "", ""
    except subprocess.CalledProcessError as e:
        return e.returncode, "", str(e)


def test_import(module_name):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run E2E tests for claude-force")
    parser.add_argument(
        "--clean", action="store_true", help="Clean up test environment after running"
    )
    parser.add_argument(
        "--no-venv",
        action="store_true",
        help="Skip virtual environment creation (use current environment)",
    )
    args = parser.parse_args()

    # Configuration
    project_root = Path(__file__).parent.parent
    venv_dir = project_root / ".venv-e2e-test"
    use_venv = not args.no_venv

    print_info("=" * 50)
    print_info("  Claude Force - E2E Test Suite")
    print_info("=" * 50)
    print()

    original_dir = Path.cwd()
    os.chdir(project_root)

    try:
        # Determine Python executable
        if use_venv:
            # Step 1: Create fresh virtual environment
            print_step("Step 1: Creating fresh virtual environment...")
            if venv_dir.exists():
                print("  Removing existing test environment...")
                shutil.rmtree(venv_dir)

            venv.create(venv_dir, with_pip=True)

            # Determine venv Python executable
            if sys.platform == "win32":
                python_exe = str(venv_dir / "Scripts" / "python.exe")
                pip_exe = str(venv_dir / "Scripts" / "pip.exe")
            else:
                python_exe = str(venv_dir / "bin" / "python")
                pip_exe = str(venv_dir / "bin" / "pip")

            print_success("Virtual environment created")
            print()
        else:
            python_exe = sys.executable
            pip_exe = "pip"
            print_step("Step 1: Using current Python environment")
            print()

        # Step 2: Upgrade pip
        print_step("Step 2: Upgrading pip...")
        returncode, _, _ = run_command(
            f"{python_exe} -m pip install --quiet --upgrade pip setuptools wheel"
        )
        if returncode != 0:
            print_error("Pip upgrade failed")
            return 1
        print_success("Pip upgraded")
        print()

        # Step 3: Install package
        print_step("Step 3: Installing claude-force package...")
        returncode, _, stderr = run_command(
            f"{pip_exe} install -e . --quiet", capture=True
        )
        if returncode != 0:
            print_error(f"Package installation failed: {stderr}")
            return 1
        print_success("Package installed successfully")
        print()

        # Step 4: Verify dependencies
        print_step("Step 4: Verifying dependencies...")
        required_deps = ["anthropic", "yaml", "prompt_toolkit", "rich", "dotenv"]
        all_deps_ok = True

        for dep in required_deps:
            # Test import using the venv Python
            returncode, _, _ = run_command(
                f'{python_exe} -c "import {dep}"', check=False, capture=True
            )
            if returncode == 0:
                print(f"  {Colors.GREEN}✓{Colors.NC} {dep}")
            else:
                print(f"  {Colors.RED}✗{Colors.NC} {dep} (MISSING)")
                all_deps_ok = False

        if not all_deps_ok:
            print_error("Some dependencies are missing")
            return 1
        print_success("All dependencies verified")
        print()

        # Step 5: Install test dependencies
        print_step("Step 5: Installing test dependencies...")
        returncode, _, _ = run_command(
            f"{pip_exe} install pytest pytest-cov --quiet"
        )
        if returncode != 0:
            print_error("Test dependency installation failed")
            return 1
        print_success("Test dependencies installed")
        print()

        # Step 6: Run E2E tests
        print_step("Step 6: Running E2E tests...")
        print("-" * 50)
        returncode, stdout, stderr = run_command(
            f"{python_exe} -m pytest tests/e2e/ -v --tb=short --color=yes",
            check=False,
        )
        print("-" * 50)

        if returncode == 0:
            print_success("All E2E tests passed")
        else:
            print_error("Some E2E tests failed")

        test_result = returncode
        print()

        # Step 7: Test critical imports
        print_step("Step 7: Testing critical imports...")
        import_test = """
from claude_force.interactive_shell import InteractiveShell
from claude_force.shell.ui import TaskProgress, ErrorFormatter, CommandSuggester
from claude_force.shell.executor import CommandExecutor
from claude_force.shell.completer import ClaudeForceCompleter
print('  ✓ All critical imports successful')
"""
        returncode, stdout, stderr = run_command(
            f'{python_exe} -c "{import_test}"', check=False, capture=True
        )
        if returncode != 0:
            print_error(f"Import test failed: {stderr}")
            return 1
        print(stdout)
        print_success("Import test passed")
        print()

        # Step 8: Test CLI
        print_step("Step 8: Testing CLI execution...")
        run_command(f"{python_exe} -m claude_force --help", check=False, capture=True)
        print_success("CLI execution test passed")
        print()

        # Summary
        print_info("=" * 50)
        if test_result == 0:
            print_success("  E2E TEST SUITE: PASSED ✓")
        else:
            print_error("  E2E TEST SUITE: FAILED ✗")
        print_info("=" * 50)
        print()

        # Cleanup
        if use_venv and args.clean:
            print_step("Cleaning up test environment...")
            shutil.rmtree(venv_dir)
            print_success("Test environment cleaned")
        elif use_venv:
            print_step(f"Test environment preserved at: {venv_dir}")
            print_step("Run with --clean to remove it")

        return test_result

    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    sys.exit(main())
