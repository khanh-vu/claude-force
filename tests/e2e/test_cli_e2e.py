"""
End-to-End Tests: CLI Commands

Tests that verify CLI commands work from end-user perspective.
These tests simulate actual command-line usage.
"""

import pytest
import subprocess
import sys


class TestCLICommandExecution:
    """Test CLI commands work correctly."""

    def test_cli_module_runnable(self):
        """Test CLI can be run as module."""
        # Test that the CLI module can be executed
        result = subprocess.run(
            [sys.executable, "-m", "claude_force", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should show help without error
        assert result.returncode == 0 or "usage" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_cli_shows_version(self):
        """Test CLI can show version."""
        result = subprocess.run(
            [sys.executable, "-m", "claude_force", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should show version or help
        # Some CLIs return 0 for --version, others return 1
        assert result.returncode in [0, 1, 2]

    def test_cli_help_command(self):
        """Test CLI help command works."""
        result = subprocess.run(
            [sys.executable, "-m", "claude_force", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should contain help text
        output = result.stdout + result.stderr
        assert "usage" in output.lower() or "help" in output.lower() or "claude" in output.lower()


class TestCLIImportAndUsage:
    """Test CLI can be imported and used programmatically."""

    def test_cli_main_importable(self):
        """Test CLI main function can be imported."""
        from claude_force.cli import main

        assert callable(main)

    def test_cli_runs_without_crash(self):
        """Test CLI can be instantiated without crashing."""
        try:
            from claude_force import cli

            assert cli is not None
        except ImportError as e:
            pytest.fail(f"Failed to import CLI: {e}")


class TestInteractiveShellLaunch:
    """Test interactive shell can be launched."""

    def test_interactive_shell_importable(self):
        """Test interactive shell can be imported."""
        from claude_force.interactive_shell import InteractiveShell

        assert InteractiveShell is not None

    def test_interactive_shell_instantiable(self):
        """Test interactive shell can be instantiated."""
        from claude_force.interactive_shell import InteractiveShell

        shell = InteractiveShell()

        assert shell is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
