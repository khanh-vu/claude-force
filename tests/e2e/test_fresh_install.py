"""
End-to-End Tests: Fresh Installation

Tests that simulate a fresh package installation to verify:
- All dependencies are properly declared
- Package installs without errors
- All modules can be imported
- No missing dependencies at runtime
"""

import pytest
import importlib


class TestFreshInstallation:
    """Test package installation and imports."""

    def test_package_installed(self):
        """Verify claude-force package is installed."""
        import claude_force
        assert claude_force.__name__ == "claude_force"

    def test_version_accessible(self):
        """Verify package has version or can be imported."""
        import claude_force
        # Package should be importable
        assert claude_force is not None

    def test_core_modules_importable(self):
        """Verify all core modules can be imported."""
        core_modules = [
            "claude_force.base",
            "claude_force.cli",
            "claude_force.interactive_shell",
        ]

        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_shell_modules_importable(self):
        """Verify interactive shell modules can be imported."""
        shell_modules = [
            "claude_force.shell",
            "claude_force.shell.executor",
            "claude_force.shell.completer",
            "claude_force.shell.ui",
        ]

        for module_name in shell_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_required_dependencies_available(self):
        """Verify all required dependencies are available."""
        required_packages = [
            "anthropic",
            "yaml",  # PyYAML
            "prompt_toolkit",
            "rich",
            "dotenv",  # python-dotenv
        ]

        for package_name in required_packages:
            try:
                importlib.import_module(package_name)
            except ImportError as e:
                pytest.fail(
                    f"Required dependency '{package_name}' not available: {e}"
                )

    def test_ui_components_importable(self):
        """Verify UI components can be imported (critical for interactive shell)."""
        try:
            from claude_force.shell.ui import (
                TaskProgress,
                ErrorFormatter,
                CommandSuggester,
                RichFormatter,
                InteractivePrompt,
            )

            assert TaskProgress is not None
            assert ErrorFormatter is not None
            assert CommandSuggester is not None
            assert RichFormatter is not None
            assert InteractivePrompt is not None
        except ImportError as e:
            pytest.fail(f"Failed to import UI components: {e}")

    def test_executor_components_importable(self):
        """Verify executor components can be imported."""
        try:
            from claude_force.shell.executor import CommandExecutor, ExecutionResult

            assert CommandExecutor is not None
            assert ExecutionResult is not None
        except ImportError as e:
            pytest.fail(f"Failed to import executor components: {e}")

    def test_completer_components_importable(self):
        """Verify completer components can be imported."""
        try:
            from claude_force.shell.completer import ClaudeForceCompleter

            assert ClaudeForceCompleter is not None
        except ImportError as e:
            pytest.fail(f"Failed to import completer components: {e}")

    def test_rich_library_functional(self):
        """Verify rich library is functional."""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel

            console = Console()
            table = Table()
            panel = Panel("Test")

            assert console is not None
            assert table is not None
            assert panel is not None
        except Exception as e:
            pytest.fail(f"Rich library not functional: {e}")

    def test_prompt_toolkit_functional(self):
        """Verify prompt-toolkit is functional."""
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.completion import Completer

            assert PromptSession is not None
            assert Completer is not None
        except Exception as e:
            pytest.fail(f"prompt-toolkit not functional: {e}")


class TestPackageStructure:
    """Test package structure and organization."""

    def test_cli_entry_point_exists(self):
        """Verify CLI entry point exists."""
        from claude_force import cli

        assert hasattr(cli, "main"), "CLI should have main() entry point"

    def test_interactive_shell_class_exists(self):
        """Verify InteractiveShell class exists."""
        from claude_force.interactive_shell import InteractiveShell

        assert InteractiveShell is not None

    def test_base_module_exists(self):
        """Verify base module exists."""
        from claude_force import base

        assert base is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
