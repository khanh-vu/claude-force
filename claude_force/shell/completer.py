"""
Tab Completion for Interactive Shell.

Provides context-aware tab completion for:
- Command names (run, list, workflow, metrics, etc.)
- Agent names (code-reviewer, frontend-architect, etc.)
- Workflow names (full-stack-feature, bug-fix, etc.)
- Flags and options (--task, --output, --json, etc.)
- File paths (for --task-file, --output, etc.)
"""

from typing import Iterable, List, Optional, Dict, Tuple
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText


class ClaudeForceCompleter(Completer):
    """
    Tab completion for Claude Force interactive shell.

    Provides context-aware completions based on current input:
    - After empty input: All top-level commands
    - After 'run': Subcommands (agent, workflow)
    - After 'run agent': Agent names
    - After 'workflow run': Workflow names
    - After agent/workflow name: Flags (--task, --output, etc.)
    """

    def __init__(self, orchestrator=None):
        """
        Initialize completer.

        Args:
            orchestrator: Optional AgentOrchestrator for agent/workflow lists
        """
        self.orchestrator = orchestrator
        self._agent_cache = None
        self._workflow_cache = None

        # Command metadata: (description, category, emoji)
        self.command_metadata = {
            "list": ("List available agents or workflows", "📋 Query", "📋"),
            "info": ("Show detailed information about an agent", "📋 Query", "ℹ️"),
            "recommend": ("Get agent recommendations for a task", "🤖 Agent", "💡"),
            "run": ("Execute an agent or workflow", "🤖 Agent", "▶️"),
            "metrics": ("View execution metrics and costs", "📊 Metrics", "📊"),
            "setup": ("Initialize Claude Force in current directory", "⚙️ Setup", "🔧"),
            "init": ("Create a new Claude Force project", "⚙️ Setup", "🆕"),
            "marketplace": ("Browse and install agent packs", "🏪 Marketplace", "🛒"),
            "review": ("Review project for Claude Force integration", "📋 Query", "🔍"),
            "restructure": ("Validate and fix .claude folder structure", "⚙️ Setup", "🔨"),
            "pick-agent": ("Copy agents from another project", "🤖 Agent", "📥"),
            "compose": ("Create custom workflows", "🔄 Workflow", "✨"),
            "analyze": ("Analyze agents and workflows", "📊 Metrics", "🔬"),
            "help": ("Show help information", "❓ Help", "❓"),
            "exit": ("Exit the interactive shell", "❓ Help", "🚪"),
            "quit": ("Exit the interactive shell", "❓ Help", "🚪"),
            "clear": ("Clear the terminal screen", "❓ Help", "🧹"),
            "history": ("Show command history", "❓ Help", "📜"),
        }

        # Top-level commands
        self.commands = list(self.command_metadata.keys())

        # Subcommands with descriptions
        self.subcommand_metadata = {
            "list": {
                "agents": "List all available agents",
                "workflows": "List all available workflows",
            },
            "run": {
                "agent": "Run a single agent",
                "workflow": "Run a complete workflow",
            },
            "metrics": {
                "summary": "Show execution summary",
                "agents": "Show agent usage metrics",
                "costs": "Show cost breakdown",
                "export": "Export metrics to file",
                "analyze": "Analyze metric trends",
            },
            "marketplace": {
                "list": "List available agent packs",
                "search": "Search for agent packs",
                "install": "Install an agent pack",
                "uninstall": "Remove an agent pack",
            },
            "analyze": {
                "compare": "Compare agent performance",
                "recommend": "Get optimization recommendations",
            },
        }

        # Subcommands (simple list for compatibility)
        self.subcommands = {k: list(v.keys()) for k, v in self.subcommand_metadata.items()}

        # Flag descriptions
        self.flag_metadata = {
            "--task": "Task description or prompt",
            "--task-file": "Path to task file",
            "--output": "Output file path",
            "--json": "Output in JSON format",
            "--quiet": "Suppress output",
            "--format": "Output format (table, json, yaml)",
            "--help": "Show help message",
            "--config": "Path to config file",
            "--demo": "Run in demo mode",
            "--verbose": "Verbose output",
            "--model": "AI model to use",
            "--max-tokens": "Maximum tokens for response",
            "--temperature": "Sampling temperature (0.0-1.0)",
            "--auto-select-model": "Automatically select optimal model",
            "--estimate-cost": "Estimate cost before running",
            "--cost-threshold": "Maximum allowed cost",
            "--yes": "Auto-confirm prompts",
        }

        # Common flags
        self.common_flags = [
            "--task",
            "--task-file",
            "--output",
            "--json",
            "--quiet",
            "--format",
            "--help",
            "--config",
            "--demo",
            "--verbose",
        ]

        # Agent-specific flags
        self.agent_flags = [
            "--model",
            "--max-tokens",
            "--temperature",
            "--auto-select-model",
            "--estimate-cost",
            "--cost-threshold",
            "--yes",
        ]

    def invalidate_cache(self):
        """
        Invalidate cached agent and workflow lists.

        Call this after operations that might change available agents/workflows
        (e.g., installing from marketplace, importing agents, etc.)
        """
        self._agent_cache = None
        self._workflow_cache = None

    def _get_agents(self) -> List[str]:
        """Get list of agent names (cached)."""
        if self._agent_cache is None and self.orchestrator:
            try:
                agents = self.orchestrator.list_agents()
                self._agent_cache = [a["name"] if isinstance(a, dict) else a for a in agents]
            except Exception:
                # If listing agents fails, return empty list (completion still works for commands)
                self._agent_cache = []
        return self._agent_cache or []

    def _get_workflows(self) -> List[str]:
        """Get list of workflow names (cached)."""
        if self._workflow_cache is None and self.orchestrator:
            try:
                workflows = self.orchestrator.list_workflows()
                self._workflow_cache = [w["name"] if isinstance(w, dict) else w for w in workflows]
            except Exception:
                # If listing workflows fails, return empty list (completion still works for commands)
                self._workflow_cache = []
        return self._workflow_cache or []

    def _format_display_meta(self, text: str, style: str = "") -> FormattedText:
        """Format display metadata with styling."""
        if style:
            return FormattedText([(style, text)])
        return FormattedText([("", text)])

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        """
        Generate completions based on current input.

        Args:
            document: Current document (text before cursor)
            complete_event: Completion event

        Yields:
            Completion objects for matching items
        """
        text = document.text_before_cursor

        # Handle slash command completion
        has_slash = text.startswith("/")
        text_without_slash = text[1:] if has_slash else text
        words = text_without_slash.split()

        # Just "/" typed - show all commands with slash prefix and descriptions
        if text == "/":
            for cmd in self.commands:
                description, category, emoji = self.command_metadata.get(cmd, ("", "", ""))
                # Create rich display with emoji and description
                display_meta = self._format_display_meta(
                    f"{emoji} {description}" if emoji else description,
                    "class:completion-meta"
                )
                yield Completion(
                    "/" + cmd,
                    start_position=-1,
                    display=FormattedText([
                        ("class:completion-command", "/" + cmd),
                        ("", "  "),
                        ("class:completion-meta", f"{emoji} {description}" if emoji else description),
                    ]),
                    display_meta=f"{emoji} {description}" if emoji else description,
                )
            return

        # Empty input (no slash) - show all commands without slash and descriptions
        if not words and not has_slash:
            for cmd in self.commands:
                description, category, emoji = self.command_metadata.get(cmd, ("", "", ""))
                yield Completion(
                    cmd,
                    start_position=0,
                    display_meta=f"{emoji} {description}" if emoji else description,
                )
            return

        # Get current word being completed
        current_word = words[-1] if not text_without_slash.endswith(" ") else ""

        # One word - complete command name
        if len(words) == 1 and not text_without_slash.endswith(" "):
            for cmd in self.commands:
                if cmd.startswith(current_word.lower()):
                    description, category, emoji = self.command_metadata.get(cmd, ("", "", ""))
                    completion_text = ("/" + cmd) if has_slash else cmd
                    yield Completion(
                        completion_text,
                        start_position=-len(current_word) - (1 if has_slash else 0),
                        display_meta=f"{emoji} {description}" if emoji else description,
                    )
            return

        # One word with trailing space OR two words without trailing space - complete subcommand
        # Examples: "run " or "run a" or "/run " or "/run a"
        if (len(words) == 1 and text_without_slash.endswith(" ")) or (
            len(words) == 2 and not text_without_slash.endswith(" ")
        ):
            first_word = words[0].lower()
            if first_word in self.subcommands:
                for subcmd in self.subcommands[first_word]:
                    if subcmd.startswith(current_word.lower()):
                        # Get description for subcommand
                        description = self.subcommand_metadata.get(first_word, {}).get(subcmd, "")
                        yield Completion(
                            subcmd,
                            start_position=-len(current_word),
                            display_meta=description or "subcommand",
                        )
                return

        # Context-aware completion
        if len(words) >= 2:
            first_word = words[0].lower()
            second_word = words[1].lower()

            # Complete agent names after 'run agent'
            if first_word == "run" and second_word == "agent":
                if len(words) == 2 or (len(words) == 3 and not text.endswith(" ")):
                    for agent in self._get_agents():
                        if agent.lower().startswith(current_word.lower()):
                            yield Completion(
                                agent, start_position=-len(current_word), display_meta="agent"
                            )
                    return
                # After agent name, complete flags
                else:
                    for flag in self.common_flags + self.agent_flags:
                        if flag.startswith(current_word):
                            description = self.flag_metadata.get(flag, "option")
                            yield Completion(
                                flag, start_position=-len(current_word), display_meta=description
                            )
                    return

            # Complete workflow names after 'run workflow'
            if first_word == "run" and second_word == "workflow":
                if len(words) == 2 or (len(words) == 3 and not text.endswith(" ")):
                    for workflow in self._get_workflows():
                        if workflow.lower().startswith(current_word.lower()):
                            yield Completion(
                                workflow, start_position=-len(current_word), display_meta="workflow"
                            )
                    return
                # After workflow name, complete flags
                else:
                    for flag in self.common_flags:
                        if flag.startswith(current_word):
                            description = self.flag_metadata.get(flag, "option")
                            yield Completion(
                                flag, start_position=-len(current_word), display_meta=description
                            )
                    return

        # Default: complete flags
        if current_word.startswith("--"):
            for flag in self.common_flags:
                if flag.startswith(current_word):
                    description = self.flag_metadata.get(flag, "option")
                    yield Completion(flag, start_position=-len(current_word), display_meta=description)
