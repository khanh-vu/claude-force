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
from pathlib import Path
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from .shell.executor import CommandExecutor, ExecutionResult
from .shell.completer import ClaudeForceCompleter
from .orchestrator import AgentOrchestrator


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

        # Initialize orchestrator for completer
        try:
            orchestrator = AgentOrchestrator()
        except Exception as e:
            # If orchestrator fails to initialize, completer will work without agent/workflow lists
            orchestrator = None

        # Create completer
        self.completer = ClaudeForceCompleter(orchestrator=orchestrator)

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            completer=self.completer,
            complete_while_typing=False,  # Only complete on TAB
        )

        # Built-in commands (handled by shell, not CLI)
        self.builtin_commands = {
            'exit': self._cmd_exit,
            'quit': self._cmd_exit,
            'help': self._cmd_help,
            'clear': self._cmd_clear,
            'history': self._cmd_history,
            'meta-prompt': self._cmd_meta_prompt,
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
                command = self.session.prompt('claude-force> ')

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

        self.command_count += 1

        # Check if this is a slash command (starts with /)
        if command.startswith('/'):
            # Remove the forward slash and execute as command
            command = command[1:].strip()

            # Check for built-in commands first
            cmd_parts = command.split()
            if cmd_parts[0] in self.builtin_commands:
                self.builtin_commands[cmd_parts[0]](cmd_parts[1:])
                return

            # Execute CLI command via executor
            result = self.executor.execute(command)

            # Display result
            if result.success:
                self.success_count += 1
                if result.output:
                    print(result.output, end='')
            else:
                self.failure_count += 1
                if result.error:
                    print(f"❌ {result.error}", file=sys.stderr)
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
        """Print goodbye message with session statistics."""
        print()
        print("Goodbye! 👋")
        print()
        print(f"Session statistics:")
        print(f"  Commands executed: {self.command_count}")
        print(f"  Successful: {self.success_count}")
        print(f"  Failed: {self.failure_count}")
        print()

    def _handle_prompt(self, prompt: str):
        """
        Handle prompt input (text without forward slash).

        Currently provides guidance on how to run the prompt as a task.
        Future enhancement: Could integrate with meta-prompt or recommend agent.

        Args:
            prompt: User's prompt text
        """
        print(f"\n💡 Did you mean to run a command?")
        print(f"   Your input: \"{prompt}\"\n")
        print(f"   To run commands, start with / like:")
        print(f"   • /run agent <agent-name> --task \"{prompt}\"")
        print(f"   • /recommend --task \"{prompt}\"")
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

        prompt = ' '.join(args)
        print(f"\n💡 Meta-prompt feature is planned for future release.")
        print(f"   Your prompt: \"{prompt}\"\n")
        print(f"   Try these alternatives:")
        print(f"   • /recommend --task \"{prompt}\" --explain")
        print(f"   • /run agent <agent-name> --task \"{prompt}\"")
        print(f"   • /list agents  (to see available agents)\n")

    def _cmd_help(self, args):
        """Show help for commands."""
        if args:
            # Help for specific command
            command = args[0]
            print(f"\nHelp for '/{command}':")
            print(f"  (Detailed help to be implemented)")
            print()
        else:
            # General help
            print("\nClaude Force Interactive Shell - Available Commands\n")
            print("💡 Usage:")
            print("  • All commands start with / (forward slash)")
            print("  • Press Tab for auto-completion")
            print("  • Use arrow keys to navigate command history")
            print()
            print("Built-in Commands:")
            print("  /help [command]      Show this help or help for specific command")
            print("  /exit, /quit         Exit the shell")
            print("  /clear               Clear the screen")
            print("  /history             Show command history")
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
        os.system('clear' if os.name != 'nt' else 'cls')

    def _cmd_history(self, args):
        """Show command history."""
        print("\nCommand History:\n")
        for i, entry in enumerate(self.executor.history[-20:], 1):
            command = entry['command']
            result = entry['result']
            status = "✓" if result.success else "✗"
            print(f"  {i}. {status} {command}")
        print()


def run_interactive_shell(config_path: Optional[Path] = None):
    """
    Entry point for interactive shell.

    Args:
        config_path: Optional path to shell configuration
    """
    shell = InteractiveShell(config_path=config_path)
    shell.start()
