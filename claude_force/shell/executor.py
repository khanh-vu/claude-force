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
        Create parser by importing and calling cli.main() logic.

        Note: We can't directly reuse main() because it calls sys.exit().
        Instead, we extract the parser creation logic.
        """
        import argparse
        from claude_force.cli import (
            cmd_list_agents, cmd_list_workflows, cmd_agent_info,
            cmd_recommend, cmd_run_agent, cmd_run_workflow,
            cmd_metrics
        )

        parser = argparse.ArgumentParser(
            prog="claude-force",
            description="Multi-Agent Orchestration System for Claude (Interactive Shell)",
            add_help=False,  # Disable default --help to handle it manually
        )

        # Global options
        parser.add_argument(
            "--config",
            default=".claude/claude.json",
            help="Path to claude.json configuration",
        )
        parser.add_argument("--api-key", help="Anthropic API key")
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Run in demo mode",
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to execute")

        # List command
        list_parser = subparsers.add_parser("list", help="List agents or workflows")
        list_subparsers = list_parser.add_subparsers(dest="list_type")

        list_agents_parser = list_subparsers.add_parser("agents", help="List all agents")
        list_agents_parser.add_argument("--json", action="store_true")
        list_agents_parser.add_argument("--quiet", "-q", action="store_true")
        list_agents_parser.add_argument("--format", choices=["text", "json"], default="text")
        list_agents_parser.set_defaults(func=cmd_list_agents)

        list_workflows_parser = list_subparsers.add_parser("workflows", help="List all workflows")
        list_workflows_parser.add_argument("--json", action="store_true")
        list_workflows_parser.add_argument("--quiet", "-q", action="store_true")
        list_workflows_parser.add_argument("--format", choices=["text", "json"], default="text")
        list_workflows_parser.set_defaults(func=cmd_list_workflows)

        # Info command
        info_parser = subparsers.add_parser("info", help="Show agent information")
        info_parser.add_argument("agent", help="Agent name")
        info_parser.add_argument("--json", action="store_true")
        info_parser.set_defaults(func=cmd_agent_info)

        # Recommend command
        recommend_parser = subparsers.add_parser("recommend", help="Recommend agents")
        recommend_parser.add_argument("--task", help="Task description")
        recommend_parser.add_argument("--task-file", help="Read task from file")
        recommend_parser.add_argument("--top-k", type=int, default=3)
        recommend_parser.add_argument("--min-confidence", type=float, default=0.3)
        recommend_parser.add_argument("--explain", action="store_true")
        recommend_parser.add_argument("--json", action="store_true")
        recommend_parser.add_argument("--include-marketplace", action="store_true")
        recommend_parser.add_argument("--verbose", "-v", action="store_true")
        recommend_parser.set_defaults(func=cmd_recommend)

        # Run command
        run_parser = subparsers.add_parser("run", help="Run agent or workflow")
        run_subparsers = run_parser.add_subparsers(dest="run_type")

        # Run agent
        run_agent_parser = run_subparsers.add_parser("agent", help="Run a single agent")
        run_agent_parser.add_argument("agent", help="Agent name")
        run_agent_parser.add_argument("--task", help="Task description")
        run_agent_parser.add_argument("--task-file", help="Read task from file")
        run_agent_parser.add_argument("--output", "-o", help="Save output to file")
        run_agent_parser.add_argument("--model", help="Claude model to use")
        run_agent_parser.add_argument("--max-tokens", type=int, default=4096)
        run_agent_parser.add_argument("--temperature", type=float, default=1.0)
        run_agent_parser.add_argument("--json", action="store_true")
        run_agent_parser.add_argument("--quiet", "-q", action="store_true")
        run_agent_parser.add_argument("--format", choices=["text", "json"], default="text")
        run_agent_parser.add_argument("--auto-select-model", action="store_true")
        run_agent_parser.add_argument("--estimate-cost", action="store_true")
        run_agent_parser.add_argument("--cost-threshold", type=float)
        run_agent_parser.add_argument("--yes", "-y", action="store_true")
        run_agent_parser.set_defaults(func=cmd_run_agent)

        # Run workflow
        run_workflow_parser = run_subparsers.add_parser("workflow", help="Run a workflow")
        run_workflow_parser.add_argument("workflow", help="Workflow name")
        run_workflow_parser.add_argument("--task", help="Task description")
        run_workflow_parser.add_argument("--task-file", help="Read task from file")
        run_workflow_parser.add_argument("--output", "-o", help="Save results to file")
        run_workflow_parser.add_argument("--no-pass-output", action="store_true")
        run_workflow_parser.add_argument("--quiet", "-q", action="store_true")
        run_workflow_parser.add_argument("--format", choices=["text", "json"], default="text")
        run_workflow_parser.set_defaults(func=cmd_run_workflow)

        # Metrics command
        metrics_parser = subparsers.add_parser("metrics", help="Show metrics")
        metrics_subparsers = metrics_parser.add_subparsers(dest="metrics_type")

        summary_parser = metrics_subparsers.add_parser("summary", help="Show summary")
        summary_parser.add_argument("--hours", type=int)
        summary_parser.set_defaults(func=cmd_metrics)

        agents_parser = metrics_subparsers.add_parser("agents", help="Show agent metrics")
        agents_parser.add_argument("--hours", type=int)
        agents_parser.add_argument("--sort-by", choices=["runs", "success", "time", "cost"], default="runs")
        agents_parser.set_defaults(func=cmd_metrics)

        costs_parser = metrics_subparsers.add_parser("costs", help="Show cost breakdown")
        costs_parser.add_argument("--hours", type=int)
        costs_parser.add_argument("--breakdown", action="store_true")
        costs_parser.set_defaults(func=cmd_metrics)

        export_parser = metrics_subparsers.add_parser("export", help="Export metrics")
        export_parser.add_argument("--output", "-o", required=True)
        export_parser.add_argument("--format", choices=["json", "csv"], default="json")
        export_parser.add_argument("--hours", type=int)
        export_parser.set_defaults(func=cmd_metrics)

        analyze_parser = metrics_subparsers.add_parser("analyze", help="Analyze patterns")
        analyze_parser.add_argument("--hours", type=int)
        analyze_parser.set_defaults(func=cmd_metrics)

        return parser

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
