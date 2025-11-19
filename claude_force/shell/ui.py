"""
UI Enhancements for Interactive Shell.

This module provides rich UI components including:
- Progress bars for long-running tasks
- Better error formatting with context
- Command suggestions on typos
- Rich formatting for tables and lists
- Interactive multi-step command prompts
"""

import sys
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box


# Global console instance for rich output
console = Console()


# =============================================================================
# Progress Bars
# =============================================================================


class TaskProgress:
    """
    Progress bar manager for long-running tasks.

    Usage:
        with TaskProgress("Running agent...") as progress:
            # Do work
            progress.update(50)  # Update to 50%
            # More work
            progress.update(100)  # Complete
    """

    def __init__(self, description: str, total: int = 100):
        """
        Initialize progress tracker.

        Args:
            description: Task description to display
            total: Total units of work (default: 100 for percentage)
        """
        self.description = description
        self.total = total
        self.progress = None
        self.task_id = None

    def __enter__(self):
        """Start progress display."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        )
        self.progress.__enter__()
        self.task_id = self.progress.add_task(self.description, total=self.total)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop progress display."""
        if self.progress:
            self.progress.__exit__(exc_type, exc_val, exc_tb)

    def update(self, completed: int):
        """Update progress to completed amount."""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, completed=completed)

    def advance(self, amount: int = 1):
        """Advance progress by amount."""
        if self.progress and self.task_id is not None:
            self.progress.advance(self.task_id, advance=amount)


# =============================================================================
# Error Formatting
# =============================================================================


@dataclass
class ErrorContext:
    """Context information for an error."""

    error_type: str
    message: str
    suggestions: List[str]
    details: Optional[str] = None
    code_snippet: Optional[str] = None


class ErrorFormatter:
    """Formats errors with rich context and suggestions."""

    @staticmethod
    def format_error(context: ErrorContext) -> None:
        """
        Display a formatted error with context and suggestions.

        Args:
            context: Error context to display
        """
        # Create error panel
        error_content = f"[bold red]{context.error_type}[/bold red]\n\n"
        error_content += f"{context.message}\n"

        if context.details:
            error_content += f"\n[dim]{context.details}[/dim]\n"

        if context.code_snippet:
            error_content += "\n"
            syntax = Syntax(context.code_snippet, "python", theme="monokai", line_numbers=True)
            console.print(syntax)

        # Display error panel
        console.print(Panel(error_content, title="❌ Error", border_style="red", box=box.ROUNDED))

        # Display suggestions
        if context.suggestions:
            console.print("\n💡 [bold yellow]Suggestions:[/bold yellow]")
            for i, suggestion in enumerate(context.suggestions, 1):
                console.print(f"  {i}. {suggestion}")
            console.print()

    @staticmethod
    def format_simple_error(message: str) -> None:
        """Display a simple error message."""
        console.print(f"[bold red]✗[/bold red] {message}", file=sys.stderr)

    @staticmethod
    def format_warning(message: str) -> None:
        """Display a warning message."""
        console.print(f"[bold yellow]⚠[/bold yellow]  {message}")


# =============================================================================
# Command Suggestions
# =============================================================================


class CommandSuggester:
    """Provides intelligent command suggestions on typos."""

    def __init__(self, available_commands: List[str]):
        """
        Initialize suggester with available commands.

        Args:
            available_commands: List of valid commands
        """
        self.commands = available_commands

    def suggest(self, input_command: str, max_suggestions: int = 3) -> List[str]:
        """
        Suggest similar commands based on input.

        Args:
            input_command: The command that was not found
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested commands
        """
        import difflib

        # Get close matches
        suggestions = difflib.get_close_matches(
            input_command, self.commands, n=max_suggestions, cutoff=0.6
        )

        return suggestions

    def display_suggestions(self, input_command: str, suggestions: List[str]) -> None:
        """
        Display command suggestions in a friendly format.

        Args:
            input_command: The command that was not found
            suggestions: List of suggested commands
        """
        console.print(f"\n[bold red]Command not found:[/bold red] '{input_command}'")

        if suggestions:
            console.print("\n💡 [bold yellow]Did you mean:[/bold yellow]")
            for suggestion in suggestions:
                console.print(f"  • [cyan]{suggestion}[/cyan]")
        else:
            console.print("\n💡 Type [cyan]/help[/cyan] to see all available commands")

        console.print()


# =============================================================================
# Rich Formatting for Tables and Lists
# =============================================================================


class RichFormatter:
    """Provides rich formatting for tables and lists."""

    @staticmethod
    def format_table(
        title: str,
        columns: List[str],
        rows: List[List[str]],
        show_header: bool = True,
        show_lines: bool = False,
    ) -> None:
        """
        Display a formatted table.

        Args:
            title: Table title
            columns: Column headers
            rows: Table rows
            show_header: Whether to show header row
            show_lines: Whether to show lines between rows
        """
        table = Table(
            title=title,
            show_header=show_header,
            show_lines=show_lines,
            box=box.ROUNDED,
            header_style="bold cyan",
        )

        # Add columns
        for column in columns:
            table.add_column(column)

        # Add rows
        for row in rows:
            table.add_row(*row)

        console.print(table)

    @staticmethod
    def format_list(
        title: str, items: List[str], numbered: bool = False, style: str = "cyan"
    ) -> None:
        """
        Display a formatted list.

        Args:
            title: List title
            items: List items
            numbered: Whether to number items
            style: Color style for items
        """
        console.print(f"\n[bold]{title}[/bold]\n")

        for i, item in enumerate(items, 1):
            if numbered:
                console.print(f"  {i}. [{style}]{item}[/{style}]")
            else:
                console.print(f"  • [{style}]{item}[/{style}]")

        console.print()

    @staticmethod
    def format_key_value(data: Dict[str, Any], title: Optional[str] = None) -> None:
        """
        Display key-value pairs in a formatted panel.

        Args:
            data: Dictionary of key-value pairs
            title: Optional panel title
        """
        content = ""
        for key, value in data.items():
            content += f"[bold cyan]{key}:[/bold cyan] {value}\n"

        if title:
            console.print(Panel(content, title=title, box=box.ROUNDED))
        else:
            console.print(content)


# =============================================================================
# Interactive Multi-Step Commands
# =============================================================================


class InteractivePrompt:
    """Provides interactive prompts for multi-step commands."""

    @staticmethod
    def ask(
        question: str, default: Optional[str] = None, choices: Optional[List[str]] = None
    ) -> str:
        """
        Ask user for input.

        Args:
            question: Question to ask
            default: Default value
            choices: List of valid choices

        Returns:
            User's response
        """
        return Prompt.ask(question, default=default, choices=choices)

    @staticmethod
    def confirm(question: str, default: bool = False) -> bool:
        """
        Ask yes/no question.

        Args:
            question: Question to ask
            default: Default answer

        Returns:
            True if user confirms, False otherwise
        """
        return Confirm.ask(question, default=default)

    @staticmethod
    def multi_step(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run a multi-step interactive command.

        Args:
            steps: List of step configurations, each containing:
                - name: Step name (key for result)
                - question: Question to ask
                - type: 'text', 'confirm', or 'choice'
                - default: Default value (optional)
                - choices: List of choices (for 'choice' type)

        Returns:
            Dictionary of step results
        """
        results = {}

        console.print("\n[bold cyan]Interactive Setup[/bold cyan]\n")

        for i, step in enumerate(steps, 1):
            console.print(f"[dim]Step {i}/{len(steps)}[/dim]")

            step_type = step.get("type", "text")
            name = step["name"]
            question = step["question"]
            default = step.get("default")

            if step_type == "confirm":
                results[name] = Confirm.ask(question, default=default or False)
            elif step_type == "choice":
                choices = step.get("choices", [])
                results[name] = Prompt.ask(question, choices=choices, default=default)
            else:  # text
                results[name] = Prompt.ask(question, default=default)

            console.print()

        return results


# =============================================================================
# Success Messages
# =============================================================================


class SuccessFormatter:
    """Formats success messages."""

    @staticmethod
    def format_success(message: str) -> None:
        """Display a success message."""
        console.print(f"[bold green]✓[/bold green] {message}")

    @staticmethod
    def format_info(message: str) -> None:
        """Display an info message."""
        console.print(f"[bold blue]ℹ[/bold blue]  {message}")

    @staticmethod
    def format_completion(
        title: str, stats: Dict[str, Any], elapsed_time: Optional[float] = None
    ) -> None:
        """
        Display task completion summary.

        Args:
            title: Completion title
            stats: Statistics to display
            elapsed_time: Optional elapsed time in seconds
        """
        content = ""
        for key, value in stats.items():
            content += f"[cyan]{key}:[/cyan] [bold]{value}[/bold]\n"

        if elapsed_time:
            content += f"\n[dim]Completed in {elapsed_time:.2f}s[/dim]"

        console.print(Panel(content, title=f"✓ {title}", border_style="green", box=box.ROUNDED))
