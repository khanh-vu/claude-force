"""
Command Executor for Interactive Shell.

This module executes shell commands by reusing the existing CLI argument parser.
CRITICAL: Does NOT create a parallel command routing system - reuses argparse from cli.py.

Architecture:
    User Input → shlex.split() → argparse.parse_args() → Existing CLI Functions → ExecutionResult

This ensures:
- Zero code duplication
- Automatic sync with CLI changes
- Proper argument validation
- Consistent error handling
"""

import shlex
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from io import StringIO
import contextlib
import difflib


@dataclass
class ExecutionResult:
    """
    Result of a command execution.

    Attributes:
        success: Whether command executed successfully
        output: Command output (stdout)
        error: Error message if failed
        metadata: Additional metadata (execution time, etc.)
    """

    success: bool
    output: str = ""
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommandExecutor:
    """
    Executes shell commands using existing CLI infrastructure.

    Key Design Decision (from Expert Review):
    - REUSES existing argparse parser from cli.py
    - DOES NOT create new command routing logic
    - Catches SystemExit to prevent shell from exiting

    This ensures zero code duplication and automatic synchronization
    with any CLI changes.
    """

    def __init__(self):
        """Initialize executor."""
        self.history: List[Dict[str, Any]] = []
        self._parser = None  # Lazy-loaded from cli module

        # Common commands for "did you mean" suggestions
        self.all_commands = [
            "list agents",
            "list workflows",
            "info",
            "recommend",
            "run agent",
            "run workflow",
            "metrics summary",
            "metrics agents",
            "metrics costs",
            "setup",
            "init",
            "shell",
            "marketplace list",
            "marketplace search",
            "marketplace install",
            "review",
            "restructure",
            "pick-agent",
            "compose",
            "analyze",
            "diagnose",
            "import",
            "export",
            "contribute",
        ]

    @property
    def parser(self):
        """
        Get argparse parser (lazy-loaded).

        Imports cli module and creates parser on first access.
        This avoids circular import issues.
        """
        if self._parser is None:
            from claude_force import cli

            # Create a fresh parser each time to avoid state issues
            self._parser = self._create_parser_from_cli()
        return self._parser

    def _create_parser_from_cli(self):
        """
        Create parser by importing shared parser creation function from cli.

        This eliminates code duplication and ensures the shell always uses
        the same argument configuration as the main CLI.

        Returns:
            argparse.ArgumentParser: Configured parser from cli module
        """
        from claude_force.cli import create_argument_parser

        return create_argument_parser()

    def _suggest_similar_commands(self, command: str, max_suggestions: int = 3) -> List[str]:
        """
        Suggest similar commands using fuzzy matching.

        Args:
            command: The invalid command that was entered
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of similar command suggestions
        """
        # Get close matches using difflib
        suggestions = difflib.get_close_matches(
            command, self.all_commands, n=max_suggestions, cutoff=0.6  # 60% similarity threshold
        )
        return suggestions

    def _parse_command(self, command: str) -> List[str]:
        """
        Parse command string into argument list using shlex.

        Uses shlex.split() for proper handling of:
        - Quoted strings with spaces
        - Escaped characters
        - Multiple argument formats

        Args:
            command: Raw command string

        Returns:
            List of parsed arguments

        Raises:
            ValueError: If command has unterminated quotes
        """
        try:
            return shlex.split(command)
        except ValueError as e:
            # shlex raises ValueError for unterminated quotes
            raise ValueError(f"Parse error: {e}")

    def execute(self, command: str) -> ExecutionResult:
        """
        Execute a shell command.

        Flow:
        1. Parse command with shlex
        2. Parse arguments with argparse
        3. Call corresponding CLI function
        4. Capture output and return result

        Args:
            command: Command string (without 'claude-force' prefix)

        Returns:
            ExecutionResult with success status and output
        """
        # Handle empty command
        command = command.strip()
        if not command:
            return ExecutionResult(success=True, output="", metadata={"empty": True})

        try:
            # Parse command into arguments
            args_list = self._parse_command(command)

            # Parse arguments with argparse
            # CRITICAL: Catch SystemExit which argparse raises on errors
            try:
                args = self.parser.parse_args(args_list)
            except SystemExit as e:
                # argparse calls sys.exit() on parse errors
                # We catch this to prevent shell from exiting
                if e.code == 0:
                    # Exit code 0 means --help was called
                    return ExecutionResult(
                        success=True, output="Help text displayed", metadata={"help": True}
                    )
                else:
                    # Try to suggest similar commands even for parse errors
                    suggestions = self._suggest_similar_commands(
                        command.split()[0] if command.split() else command
                    )
                    error_msg = f"Invalid command syntax. Try '/help' for usage."
                    if suggestions:
                        error_msg += f"\n\n💡 Did you mean:\n"
                        for suggestion in suggestions:
                            error_msg += f"   • {suggestion}\n"
                    return ExecutionResult(
                        success=False,
                        error=error_msg,
                        metadata={"parse_error": True, "suggestions": suggestions},
                    )

            # Check if command has a handler function
            if not hasattr(args, "func"):
                # Suggest similar commands
                suggestions = self._suggest_similar_commands(command)
                error_msg = f"Unknown command. Try '/help' for available commands."
                if suggestions:
                    error_msg += f"\n\n💡 Did you mean:\n"
                    for suggestion in suggestions:
                        error_msg += f"   • {suggestion}\n"
                return ExecutionResult(
                    success=False,
                    error=error_msg,
                    metadata={"no_handler": True, "suggestions": suggestions},
                )

            # Capture stdout to get command output
            output_buffer = StringIO()
            error_buffer = StringIO()

            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(
                error_buffer
            ):
                try:
                    # Execute the command function
                    args.func(args)

                    # Get captured output
                    output = output_buffer.getvalue()
                    errors = error_buffer.getvalue()

                    result = ExecutionResult(
                        success=True,
                        output=output,
                        error=errors if errors else "",
                        metadata={"command": command},
                    )

                except KeyboardInterrupt:
                    result = ExecutionResult(
                        success=False,
                        error="Command interrupted by user (Ctrl+C)",
                        metadata={"interrupted": True},
                    )

                except SystemExit as e:
                    # CLI commands call sys.exit() on errors - catch this to keep shell running
                    exit_code = e.code if e.code is not None else 1
                    error_msg = f"Command failed with exit code {exit_code}"

                    # Try to get more context from error buffer
                    errors = error_buffer.getvalue()
                    if errors:
                        error_msg = errors.strip()

                    result = ExecutionResult(
                        success=False,
                        error=error_msg,
                        metadata={"exit_code": exit_code, "system_exit": True},
                    )

                except Exception as e:
                    # Provide helpful error messages with recovery suggestions
                    error_msg = f"Error executing command: {str(e)}"
                    exception_type = type(e).__name__

                    # Add recovery suggestions for common errors
                    if "API key" in str(e) or "ANTHROPIC_API_KEY" in str(e):
                        error_msg += "\n\n💡 Recovery suggestions:"
                        error_msg += (
                            "\n   • Set your API key: export ANTHROPIC_API_KEY='your-key-here'"
                        )
                        error_msg += "\n   • Or run: /setup to configure interactively"
                    elif "FileNotFoundError" in exception_type or "No such file" in str(e):
                        error_msg += "\n\n💡 Recovery suggestions:"
                        error_msg += "\n   • Check that the file path is correct"
                        error_msg += (
                            "\n   • Use absolute paths or ensure you're in the right directory"
                        )
                    elif "Agent not found" in str(e) or "agent" in str(e).lower():
                        error_msg += "\n\n💡 Recovery suggestions:"
                        error_msg += "\n   • Run: /list agents (to see available agents)"
                        error_msg += "\n   • Run: /marketplace search (to find more agents)"
                        error_msg += "\n   • Run: /reload (to refresh agent list)"
                    elif "Workflow not found" in str(e) or "workflow" in str(e).lower():
                        error_msg += "\n\n💡 Recovery suggestions:"
                        error_msg += "\n   • Run: /list workflows (to see available workflows)"
                        error_msg += "\n   • Run: /compose (to create a new workflow)"
                    elif "PermissionError" in exception_type:
                        error_msg += "\n\n💡 Recovery suggestions:"
                        error_msg += "\n   • Check file/directory permissions"
                        error_msg += "\n   • You may need to run with different permissions"
                    elif "Network" in str(e) or "Connection" in str(e):
                        error_msg += "\n\n💡 Recovery suggestions:"
                        error_msg += "\n   • Check your internet connection"
                        error_msg += "\n   • Verify API endpoints are accessible"
                        error_msg += "\n   • Try again in a moment"

                    result = ExecutionResult(
                        success=False, error=error_msg, metadata={"exception": exception_type}
                    )

            # Store in history
            self.history.append(
                {
                    "command": command,
                    "result": result,
                }
            )

            # Limit history size
            if len(self.history) > 1000:
                self.history = self.history[-1000:]

            return result

        except ValueError as e:
            # Parse error from shlex
            return ExecutionResult(success=False, error=str(e), metadata={"parse_error": True})

        except Exception as e:
            # Unexpected error
            return ExecutionResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={"exception": type(e).__name__},
            )
