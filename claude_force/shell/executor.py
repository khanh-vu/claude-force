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
                        success=True,
                        output="Help text displayed",
                        metadata={"help": True}
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error=f"Invalid command syntax. Try 'help' for usage.",
                        metadata={"parse_error": True}
                    )

            # Check if command has a handler function
            if not hasattr(args, 'func'):
                return ExecutionResult(
                    success=False,
                    error=f"Unknown command. Try 'help' for available commands.",
                    metadata={"no_handler": True}
                )

            # Capture stdout to get command output
            output_buffer = StringIO()
            error_buffer = StringIO()

            with contextlib.redirect_stdout(output_buffer), \
                 contextlib.redirect_stderr(error_buffer):
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
                        metadata={"command": command}
                    )

                except KeyboardInterrupt:
                    result = ExecutionResult(
                        success=False,
                        error="Command interrupted by user (Ctrl+C)",
                        metadata={"interrupted": True}
                    )

                except Exception as e:
                    result = ExecutionResult(
                        success=False,
                        error=f"Error executing command: {str(e)}",
                        metadata={"exception": type(e).__name__}
                    )

            # Store in history
            self.history.append({
                "command": command,
                "result": result,
            })

            # Limit history size
            if len(self.history) > 1000:
                self.history = self.history[-1000:]

            return result

        except ValueError as e:
            # Parse error from shlex
            return ExecutionResult(
                success=False,
                error=str(e),
                metadata={"parse_error": True}
            )

        except Exception as e:
            # Unexpected error
            return ExecutionResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={"exception": type(e).__name__}
            )
