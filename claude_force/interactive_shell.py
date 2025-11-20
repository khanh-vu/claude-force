"""
Interactive Shell for Claude Force.

Provides a REPL (Read-Eval-Print Loop) interface for executing commands
without typing 'claude-force' prefix each time.

Features:
- Command history with arrow keys
- Tab completion (to be implemented in Phase 3)
- Built-in commands (help, exit, quit, clear)
- Session management
- Error handling
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Tuple
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from .shell.executor import CommandExecutor, ExecutionResult
from .shell.completer import ClaudeForceCompleter
from .shell.ui import (
    console,
    ErrorFormatter,
    ErrorContext,
    CommandSuggester,
    RichFormatter,
    InteractivePrompt,
    SuccessFormatter,
)
from .orchestrator import AgentOrchestrator


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    @staticmethod
    def success(text: str) -> str:
        """Format text as success (green)."""
        return f"{Colors.GREEN}{text}{Colors.RESET}"

    @staticmethod
    def error(text: str) -> str:
        """Format text as error (red)."""
        return f"{Colors.RED}{text}{Colors.RESET}"

    @staticmethod
    def warning(text: str) -> str:
        """Format text as warning (yellow)."""
        return f"{Colors.YELLOW}{text}{Colors.RESET}"

    @staticmethod
    def info(text: str) -> str:
        """Format text as info (blue)."""
        return f"{Colors.BLUE}{text}{Colors.RESET}"

    @staticmethod
    def dim(text: str) -> str:
        """Format text as dimmed."""
        return f"{Colors.DIM}{text}{Colors.RESET}"


class ProgressSpinner:
    """Simple spinner for showing progress during long operations."""

    def __init__(self, message: str = "Working"):
        self.message = message
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._stop = False
        self._thread = None

    def _spin(self):
        """Spinner animation loop."""
        idx = 0
        while not self._stop:
            sys.stderr.write(f"\r{self.spinner_chars[idx]} {self.message}...")
            sys.stderr.flush()
            idx = (idx + 1) % len(self.spinner_chars)
            time.sleep(0.1)
        sys.stderr.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stderr.flush()

    def start(self):
        """Start the spinner."""
        self._stop = False
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the spinner."""
        self._stop = True
        if self._thread:
            self._thread.join(timeout=0.5)


class InteractiveShell:
    """
    Interactive REPL shell for Claude Force.

    Provides a command-line shell interface with:
    - Command history persistence
    - Built-in commands (exit, quit, help, clear)
    - Integration with existing CLI commands
    - Session statistics tracking
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize interactive shell.

        Args:
            config_path: Path to shell config (optional)
        """
        self.config_path = config_path
        self.running = False
        self.executor = CommandExecutor()

        # Session statistics
        self.command_count = 0
        self.success_count = 0
        self.failure_count = 0

        # Setup prompt session with history and completion
        history_file = Path(".claude/.shell-history")
        history_file.parent.mkdir(parents=True, exist_ok=True)

        # Create history file with secure permissions (owner read/write only)
        if not history_file.exists():
            history_file.touch(mode=0o600)
        else:
            # Fix permissions on existing file
            history_file.chmod(0o600)

        # Initialize orchestrator for completer
        try:
            orchestrator = AgentOrchestrator()
        except Exception as e:
            # If orchestrator fails to initialize, completer will work without agent/workflow lists
            orchestrator = None

        # Create completer
        self.completer = ClaudeForceCompleter(orchestrator=orchestrator)

        # Create command suggester for typo detection
        all_commands = self.completer.commands + [
            f"{cmd} {subcmd}"
            for cmd, subcmds in self.completer.subcommands.items()
            for subcmd in subcmds
        ]
        self.suggester = CommandSuggester(all_commands)

        # Create custom style for rich completions
        completion_style = Style.from_dict({
            # Completion menu styling
            'completion-menu': 'bg:#1e1e1e #ffffff',
            'completion-menu.completion': 'bg:#1e1e1e #ffffff',
            'completion-menu.completion.current': 'bg:#0078d4 #ffffff bold',
            'completion-menu.meta.completion': 'bg:#1e1e1e #888888',
            'completion-menu.meta.completion.current': 'bg:#0078d4 #ffffff',

            # Command completion styling
            'completion-command': '#4ec9b0 bold',  # Teal for commands
            'completion-meta': '#888888 italic',    # Gray for descriptions

            # Scrollbar styling
            'scrollbar.background': 'bg:#1e1e1e',
            'scrollbar.button': 'bg:#555555',
        })

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            completer=self.completer,
            complete_while_typing=True,  # Show completions while typing (like Claude!)
            style=completion_style,
            # Make completion menu larger and more visible
            reserve_space_for_menu=10,  # Reserve space for completion menu
        )

        # Command aliases for convenience
        self.command_aliases = {
            "q": "quit",
            "h": "help",
            "ls": "list",
            "?": "help",
            "cls": "clear",
        }

        # Built-in commands (handled by shell, not CLI)
        self.builtin_commands = {
            "exit": self._cmd_exit,
            "quit": self._cmd_exit,
            "help": self._cmd_help,
            "clear": self._cmd_clear,
            "history": self._cmd_history,
            "meta-prompt": self._cmd_meta_prompt,
            "reload": self._cmd_reload,
            "version": self._cmd_version,
            "interactive-demo": self._cmd_interactive_demo,
        }

    def start(self):
        """
        Start the interactive shell.

        Main REPL loop:
        1. Display prompt
        2. Read user input
        3. Execute command
        4. Print result
        5. Repeat until exit
        """
        self._print_welcome()
        self.running = True

        while self.running:
            try:
                # Get user input
                command = self.session.prompt("claude-force> ")

                # Execute command
                self._execute_command(command)

            except KeyboardInterrupt:
                # Ctrl+C pressed - don't exit, just show new prompt
                print("^C")
                continue

            except EOFError:
                # Ctrl+D pressed - exit gracefully
                print()
                self.running = False
                break

            except Exception as e:
                print(f"❌ Shell error: {e}")
                continue

        self._print_goodbye()

    def _validate_input(self, command: str) -> Tuple[bool, str]:
        """
        Validate and sanitize user input.

        Args:
            command: Raw command string

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for null bytes (security risk)
        if "\x00" in command:
            return False, "Invalid input: null bytes not allowed"

        # Check maximum length (prevent memory issues)
        MAX_COMMAND_LENGTH = 10000
        if len(command) > MAX_COMMAND_LENGTH:
            return False, f"Command too long (max {MAX_COMMAND_LENGTH} characters)"

        # Check for control characters (except common ones like \n, \t)
        import unicodedata

        for char in command:
            if unicodedata.category(char) == "Cc" and char not in "\n\t\r":
                return False, f"Invalid control character in input"

        return True, ""

    def _execute_command(self, command: str):
        """
        Execute a command (slash command or prompt).

        Behavior:
        - Commands starting with '/' are executed as CLI commands
        - Commands without '/' are treated as prompts (sent to meta-prompt)

        Args:
            command: Command string to execute
        """
        command = command.strip()

        # Ignore empty commands
        if not command:
            return

        # Validate input
        is_valid, error_msg = self._validate_input(command)
        if not is_valid:
            print(Colors.error(f"✗ {error_msg}"), file=sys.stderr)
            return

        self.command_count += 1

        # Check if this is a slash command (starts with /)
        if command.startswith("/"):
            # Remove the forward slash and execute as command
            command = command[1:].strip()

            # Expand command aliases
            cmd_parts = command.split(maxsplit=1)
            if cmd_parts and cmd_parts[0] in self.command_aliases:
                alias_expanded = self.command_aliases[cmd_parts[0]]
                command = alias_expanded + (" " + cmd_parts[1] if len(cmd_parts) > 1 else "")
                cmd_parts = command.split()

            # Check for built-in commands first
            cmd_parts = command.split()
            if cmd_parts[0] in self.builtin_commands:
                self.builtin_commands[cmd_parts[0]](cmd_parts[1:])
                return

            # Show spinner for potentially long-running commands (only if not streaming)
            # When streaming is enabled, real-time output is shown instead
            show_spinner = not self.executor.streaming and any(
                command.startswith(cmd)
                for cmd in [
                    "run agent",
                    "run workflow",
                    "recommend",
                    "marketplace install",
                    "import",
                    "export",
                    "compose",
                    "analyze",
                ]
            )

            spinner = None
            if show_spinner:
                spinner = ProgressSpinner("Executing")
                spinner.start()

            # Track execution time
            start_time = time.time()

            try:
                # Execute CLI command via executor
                result = self.executor.execute(command)
            finally:
                if spinner:
                    spinner.stop()

            elapsed_time = time.time() - start_time

            # Display result with rich formatting
            if result.success:
                self.success_count += 1
                # With streaming enabled, output is already displayed in real-time
                # Only print if streaming is disabled OR if there's no output yet
                if not self.executor.streaming and result.output:
                    print(result.output, end="")
                # Show elapsed time for longer commands (>1 second)
                if elapsed_time > 1.0:
                    SuccessFormatter.format_success(f"Completed in {elapsed_time:.2f}s")
            else:
                self.failure_count += 1
                # Handle errors with better formatting
                if result.error:
                    # Check if this is a command not found error
                    if result.metadata.get("no_handler") or result.metadata.get("parse_error"):
                        # Extract command from error for suggestions
                        cmd_parts = command.split()
                        if cmd_parts:
                            suggestions = self.suggester.suggest(cmd_parts[0])
                            if suggestions:
                                self.suggester.display_suggestions(cmd_parts[0], suggestions)
                            else:
                                ErrorFormatter.format_simple_error(result.error)
                    else:
                        # Regular error
                        ErrorFormatter.format_simple_error(result.error)

                if elapsed_time > 0.5:
                    print(Colors.dim(f"Failed after {elapsed_time:.2f}s"), file=sys.stderr)
        else:
            # No backslash - treat as prompt input
            self._handle_prompt(command)

    def _print_welcome(self):
        """Print welcome banner."""
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║   Claude Force Interactive Shell v1.3.0             ║")
        print("║   • All commands start with / (e.g., /help)         ║")
        print("║   • Type /help to see available commands            ║")
        print("║   • Press Tab for auto-completion                   ║")
        print("║   • Use Ctrl+D or /exit to quit                     ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()

    def _print_goodbye(self):
        """Print goodbye message with session statistics using rich formatting."""
        console.print("\n[bold blue]Goodbye! 👋[/bold blue]\n")

        # Display session statistics in a nice table
        stats_data = {
            "Commands executed": str(self.command_count),
            "✓ Successful": f"[green]{self.success_count}[/green]",
            "✗ Failed": f"[red]{self.failure_count}[/red]",
        }

        RichFormatter.format_key_value(stats_data, title="Session Statistics")
        console.print()

    def _handle_prompt(self, prompt: str):
        """
        Handle prompt input (text without forward slash).

        Currently provides guidance on how to run the prompt as a task.
        Future enhancement: Could integrate with meta-prompt or recommend agent.

        Args:
            prompt: User's prompt text
        """
        print(f"\n💡 Did you mean to run a command?")
        print(f'   Your input: "{prompt}"\n')
        print(f"   To run commands, start with / like:")
        print(f'   • /run agent <agent-name> --task "{prompt}"')
        print(f'   • /recommend --task "{prompt}"')
        print(f"   • /help for all commands\n")

    # =========================================================================
    # Built-in Commands
    # =========================================================================

    def _cmd_exit(self, args):
        """Exit the shell."""
        self.running = False

    def _cmd_meta_prompt(self, args):
        """
        Generate meta-prompt from user input (placeholder).

        This is a placeholder for future meta-prompt functionality.
        Currently suggests using the recommend command instead.
        """
        if not args:
            print("❌ Usage: /meta-prompt <your prompt here>")
            return

        prompt = " ".join(args)
        print(f"\n💡 Meta-prompt feature is planned for future release.")
        print(f'   Your prompt: "{prompt}"\n')
        print(f"   Try these alternatives:")
        print(f'   • /recommend --task "{prompt}" --explain')
        print(f'   • /run agent <agent-name> --task "{prompt}"')
        print(f"   • /list agents  (to see available agents)\n")

    def _cmd_help(self, args):
        """Show help for commands with rich formatting."""
        if args:
            # Help for specific command
            command = args[0]
            console.print(f"\n[bold cyan]Help for /{command}[/bold cyan]")
            console.print("  (Detailed help to be implemented)\n")
        else:
            # General help with rich table
            console.print(
                "\n[bold cyan]Claude Force Interactive Shell - Available Commands[/bold cyan]\n"
            )

            console.print("💡 [bold]Usage:[/bold]")
            console.print("  • All commands start with / (forward slash)")
            console.print("  • Press [cyan]Tab[/cyan] for auto-completion")
            console.print("  • Use arrow keys to navigate command history\n")

            # Built-in commands table
            RichFormatter.format_table(
                title="Built-in Commands",
                columns=["Command", "Description"],
                rows=[
                    ["/help [command]", "Show this help or help for specific command"],
                    ["/exit, /quit", "Exit the shell (alias: /q)"],
                    ["/clear", "Clear the screen (alias: /cls)"],
                    ["/history", "Show command history"],
                    ["/reload", "Refresh agent/workflow lists"],
                    ["/version", "Show version information"],
                ],
                show_lines=False,
            )

            console.print("\n[bold]Command Aliases:[/bold]")
            console.print("  /h, /?    →  /help")
            console.print("  /q        →  /quit")
            console.print("  /ls       →  /list")
            console.print("  /cls      →  /clear")
            print()
            print("Keyboard Shortcuts:")
            print("  Tab              Auto-complete commands/agents/workflows")
            print("  ↑/↓              Navigate command history")
            print("  Ctrl+C           Cancel current input")
            print("  Ctrl+D           Exit shell")
            print("  Ctrl+L           Clear screen (most terminals)")
            print()
            print("Agent Commands:")
            print("  /list agents         List all available agents")
            print("  /list workflows      List all workflows")
            print("  /info <agent>        Show agent information")
            print("  /recommend --task    Recommend agents for task")
            print()
            print("Execution Commands:")
            print("  /run agent <name> --task <task>      Run an agent")
            print("  /run workflow <name> --task <task>   Run a workflow")
            print()
            print("Metrics Commands:")
            print("  /metrics summary     Show metrics summary")
            print("  /metrics agents      Show agent performance")
            print("  /metrics costs       Show cost breakdown")
            print()
            print("Examples:")
            print("  /list agents")
            print("  /run agent code-reviewer --task 'Review this code'")
            print("  /recommend --task 'Design a REST API' --explain")
            print("  /info code-reviewer")
            print()

    def _cmd_clear(self, args):
        """Clear the screen."""
        os.system("clear" if os.name != "nt" else "cls")

    def _cmd_reload(self, args):
        """
        Reload agent and workflow lists.

        Useful after installing new agents or workflows during a session.
        """
        print("\n🔄 Reloading agent and workflow lists...")
        self.completer.invalidate_cache()
        print(Colors.success("✓ Cache cleared. Tab completion will refresh on next use.\n"))

    def _cmd_version(self, args):
        """Show version information."""
        print("\n" + Colors.info("Claude Force Interactive Shell"))
        print(f"Version: {Colors.success('v1.3.0')}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Platform: {sys.platform}\n")

    def _cmd_history(self, args):
        """Show command history."""
        print("\nCommand History:\n")
        for i, entry in enumerate(self.executor.history[-20:], 1):
            command = entry["command"]
            result = entry["result"]
            status = "✓" if result.success else "✗"
            print(f"  {i}. {status} {command}")
        print()

    def _cmd_interactive_demo(self, args):
        """
        Demonstrate interactive multi-step command capabilities.

        This is an example of how to create interactive commands that
        prompt users for input step by step.
        """
        console.print("\n[bold cyan]Interactive Command Demo[/bold cyan]\n")
        console.print("This demonstrates the interactive multi-step command feature.\n")

        # Define multi-step prompts
        steps = [
            {
                "name": "task_type",
                "question": "What type of task do you want to run?",
                "type": "choice",
                "choices": ["agent", "workflow", "analysis"],
                "default": "agent",
            },
            {
                "name": "task_description",
                "question": "Describe your task",
                "type": "text",
            },
            {
                "name": "enable_verbose",
                "question": "Enable verbose output?",
                "type": "confirm",
                "default": False,
            },
        ]

        # Run interactive prompts
        results = InteractivePrompt.multi_step(steps)

        # Display results
        console.print("[bold green]✓ Configuration Complete![/bold green]\n")

        RichFormatter.format_key_value(
            {
                "Task Type": results["task_type"],
                "Description": results["task_description"],
                "Verbose Mode": "Enabled" if results["enable_verbose"] else "Disabled",
            },
            title="Your Configuration",
        )

        console.print("\n[dim]This is a demo - no actual task was executed.[/dim]\n")


def run_interactive_shell(config_path: Optional[Path] = None):
    """
    Entry point for interactive shell.

    Args:
        config_path: Optional path to shell configuration
    """
    shell = InteractiveShell(config_path=config_path)
    shell.start()
