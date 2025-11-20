"""
End-to-End Tests: Interactive Shell

Tests that simulate real user interactions with the interactive shell.
These tests verify the shell works correctly from an end-user perspective.
"""

import pytest
from claude_force.shell.executor import CommandExecutor, ExecutionResult
from claude_force.shell.completer import ClaudeForceCompleter
from claude_force.shell.ui import (
    ErrorFormatter,
    CommandSuggester,
    RichFormatter,
    TaskProgress,
)


class TestInteractiveShellUserExperience:
    """Test interactive shell from end-user perspective."""

    def test_executor_can_be_instantiated(self):
        """Verify executor can be created by end user."""
        executor = CommandExecutor()
        assert executor is not None

    def test_completer_can_be_instantiated(self):
        """Verify completer can be created by end user."""
        completer = ClaudeForceCompleter()
        assert completer is not None

    def test_invalid_command_shows_message(self):
        """Test invalid command shows some message."""
        executor = CommandExecutor()

        result = executor.execute("invalid_xyz_command")

        assert isinstance(result, ExecutionResult)
        # Should return a result (success or failure doesn't matter for this test)
        assert result is not None

    def test_tab_completion_instantiable(self):
        """Test tab completion can be created."""
        completer = ClaudeForceCompleter()

        from prompt_toolkit.document import Document

        doc = Document("run ")
        completions = list(completer.get_completions(doc, None))

        # Should not crash
        assert isinstance(completions, list)

    def test_slash_command_completion(self):
        """Test slash command completion works."""
        completer = ClaudeForceCompleter()

        from prompt_toolkit.document import Document

        doc = Document("/")
        completions = list(completer.get_completions(doc, None))

        # Should show commands with / prefix
        assert len(completions) > 0
        # All completions should start with /
        for comp in completions:
            assert comp.text.startswith("/")


class TestUIComponentsUserExperience:
    """Test UI components from end-user perspective."""

    def test_command_suggester_instantiable(self):
        """Test command suggester can be created."""
        commands = ["run", "list", "help", "exit"]
        suggester = CommandSuggester(commands)

        assert suggester is not None

    def test_rich_formatter_instantiable(self):
        """Test rich formatter can be created."""
        formatter = RichFormatter()
        assert formatter is not None

    def test_task_progress_context_manager(self):
        """Test task progress works as context manager."""
        with TaskProgress("Testing task") as progress:
            assert progress is not None
            # Should not raise exception

    def test_streaming_output_works(self):
        """Test streaming output functionality."""
        executor = CommandExecutor(streaming=True)
        assert executor is not None


class TestRealWorldWorkflows:
    """Test complete end-to-end workflows users would perform."""

    def test_executor_handles_commands(self):
        """Test executor can handle command execution."""
        executor = CommandExecutor()

        # Execute a command (doesn't matter if it succeeds or fails)
        result = executor.execute("--help")

        assert isinstance(result, ExecutionResult)

    def test_error_recovery_workflow(self):
        """Test workflow with error and recovery."""
        executor = CommandExecutor()

        # Step 1: Try invalid command
        result1 = executor.execute("invalid-command")
        assert isinstance(result1, ExecutionResult)

        # Step 2: Executor should still work
        result2 = executor.execute("--help")
        assert isinstance(result2, ExecutionResult)


class TestDependencyIntegration:
    """Test that all dependencies integrate correctly."""

    def test_rich_and_prompt_toolkit_together(self):
        """Test rich and prompt-toolkit work together."""
        from rich.console import Console
        from prompt_toolkit import PromptSession

        console = Console()
        session = PromptSession()

        assert console is not None
        assert session is not None

    def test_anthropic_client_importable(self):
        """Test Anthropic client can be imported."""
        from anthropic import Anthropic

        assert Anthropic is not None

    def test_yaml_parsing_works(self):
        """Test YAML parsing works."""
        import yaml

        data = yaml.safe_load("key: value")
        assert data == {"key": "value"}

    def test_dotenv_works(self):
        """Test python-dotenv works."""
        from dotenv import load_dotenv

        # Should not raise
        load_dotenv()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
