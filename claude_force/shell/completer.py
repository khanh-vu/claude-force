"""
Tab Completion for Interactive Shell.

Provides context-aware tab completion for:
- Command names (run, list, workflow, metrics, etc.)
- Agent names (code-reviewer, frontend-architect, etc.)
- Workflow names (full-stack-feature, bug-fix, etc.)
- Flags and options (--task, --output, --json, etc.)
- File paths (for --task-file, --output, etc.)
"""

from typing import Iterable, List, Optional
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


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

        # Top-level commands
        self.commands = [
            'list', 'info', 'recommend', 'run', 'metrics',
            'setup', 'init', 'marketplace', 'review',
            'restructure', 'pick-agent', 'compose', 'analyze',
            'help', 'exit', 'quit', 'clear', 'history'
        ]

        # Subcommands
        self.subcommands = {
            'list': ['agents', 'workflows'],
            'run': ['agent', 'workflow'],
            'metrics': ['summary', 'agents', 'costs', 'export', 'analyze'],
            'marketplace': ['list', 'search', 'install', 'uninstall'],
            'analyze': ['compare', 'recommend'],
        }

        # Common flags
        self.common_flags = [
            '--task', '--task-file', '--output', '--json',
            '--quiet', '--format', '--help', '--config',
            '--demo', '--verbose'
        ]

        # Agent-specific flags
        self.agent_flags = [
            '--model', '--max-tokens', '--temperature',
            '--auto-select-model', '--estimate-cost',
            '--cost-threshold', '--yes'
        ]

    def _get_agents(self) -> List[str]:
        """Get list of agent names (cached)."""
        if self._agent_cache is None and self.orchestrator:
            try:
                agents = self.orchestrator.list_agents()
                self._agent_cache = [a['name'] if isinstance(a, dict) else a for a in agents]
            except Exception:
                # If listing agents fails, return empty list (completion still works for commands)
                self._agent_cache = []
        return self._agent_cache or []

    def _get_workflows(self) -> List[str]:
        """Get list of workflow names (cached)."""
        if self._workflow_cache is None and self.orchestrator:
            try:
                workflows = self.orchestrator.list_workflows()
                self._workflow_cache = [w['name'] if isinstance(w, dict) else w for w in workflows]
            except Exception:
                # If listing workflows fails, return empty list (completion still works for commands)
                self._workflow_cache = []
        return self._workflow_cache or []

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        """
        Generate completions based on current input.

        Args:
            document: Current document (text before cursor)
            complete_event: Completion event

        Yields:
            Completion objects for matching items
        """
        text = document.text_before_cursor
        words = text.split()

        # Empty input - show all commands
        if not words:
            for cmd in self.commands:
                yield Completion(cmd, start_position=0)
            return

        # Get current word being completed
        current_word = words[-1] if not text.endswith(' ') else ''

        # One word - complete command name
        if len(words) == 1 and not text.endswith(' '):
            for cmd in self.commands:
                if cmd.startswith(current_word.lower()):
                    yield Completion(
                        cmd,
                        start_position=-len(current_word),
                        display_meta="command"
                    )
            return

        # Two words - complete subcommand
        if len(words) <= 2:
            first_word = words[0].lower()
            if first_word in self.subcommands:
                for subcmd in self.subcommands[first_word]:
                    if subcmd.startswith(current_word.lower()):
                        yield Completion(
                            subcmd,
                            start_position=-len(current_word),
                            display_meta="subcommand"
                        )
                return

        # Context-aware completion
        if len(words) >= 2:
            first_word = words[0].lower()
            second_word = words[1].lower()

            # Complete agent names after 'run agent'
            if first_word == 'run' and second_word == 'agent':
                if len(words) == 2 or (len(words) == 3 and not text.endswith(' ')):
                    for agent in self._get_agents():
                        if agent.lower().startswith(current_word.lower()):
                            yield Completion(
                                agent,
                                start_position=-len(current_word),
                                display_meta="agent"
                            )
                    return
                # After agent name, complete flags
                else:
                    for flag in self.common_flags + self.agent_flags:
                        if flag.startswith(current_word):
                            yield Completion(
                                flag,
                                start_position=-len(current_word),
                                display_meta="option"
                            )
                    return

            # Complete workflow names after 'run workflow'
            if first_word == 'run' and second_word == 'workflow':
                if len(words) == 2 or (len(words) == 3 and not text.endswith(' ')):
                    for workflow in self._get_workflows():
                        if workflow.lower().startswith(current_word.lower()):
                            yield Completion(
                                workflow,
                                start_position=-len(current_word),
                                display_meta="workflow"
                            )
                    return
                # After workflow name, complete flags
                else:
                    for flag in self.common_flags:
                        if flag.startswith(current_word):
                            yield Completion(
                                flag,
                                start_position=-len(current_word),
                                display_meta="option"
                            )
                    return

        # Default: complete flags
        if current_word.startswith('--'):
            for flag in self.common_flags:
                if flag.startswith(current_word):
                    yield Completion(
                        flag,
                        start_position=-len(current_word),
                        display_meta="option"
                    )
