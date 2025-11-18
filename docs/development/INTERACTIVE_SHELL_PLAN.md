# Interactive Shell Mode - Development Plan

**Feature Branch**: `claude/interactive-shell-01CCQfKdkGfUkdJBR6kw5Hnp`
**Target Version**: v1.3.0
**Timeline**: 3-4 weeks
**Status**: Planning

---

## Overview

Add an interactive REPL (Read-Eval-Print Loop) shell mode to claude-force, allowing users to run commands without typing `claude-force` prefix each time.

### User Experience Goal

**Before** (Current):
```bash
$ claude-force run agent code-reviewer --task "Review PR"
$ claude-force list agents
$ claude-force workflow run full-stack --task "Build feature"
```

**After** (Interactive Shell):
```bash
$ claude-force shell
claude-force> run agent code-reviewer --task "Review PR"
✓ Agent executed successfully

claude-force> list agents
📋 Available Agents (19):
  • frontend-architect
  • backend-architect
  ...

claude-force> workflow run full-stack --task "Build feature"
🚀 Running workflow: full-stack-feature

claude-force> exit
Goodbye! 👋
```

---

## Key Features

### 1. **Interactive REPL Environment**
- Enter with `claude-force shell` or `claude-force interactive`
- Custom prompt: `claude-force>`
- Command history (arrow keys)
- Exit with `exit`, `quit`, or Ctrl+D

### 2. **Tab Completion**
- Agent names: `run agent code-<TAB>` → `run agent code-reviewer`
- Workflow names: `workflow run full-<TAB>` → `workflow run full-stack-feature`
- Commands: `work<TAB>` → `workflow`
- File paths for `--task-file` arguments

### 3. **Multi-line Input**
- For long tasks, support multi-line entry:
  ```
  claude-force> run agent frontend-architect --task \
  ... "Build a dashboard with:
  ... - User metrics
  ... - Charts and graphs
  ... - Export functionality"
  ```

### 4. **Session Context**
- Maintain orchestrator instance across commands (faster)
- Track command history for session
- Display session statistics on exit

### 5. **Enhanced UX**
- Color-coded output (success=green, error=red, info=blue)
- Progress indicators for long-running operations
- Inline help: `help`, `help run`, `help workflow`
- Clear screen: `clear` or `cls`

### 6. **Shortcuts & Aliases**
- `la` → `list agents`
- `lw` → `list workflows`
- `r` → `run`
- `w` → `workflow`
- User-configurable aliases in `.claude/shell-config.yaml`

---

## Technical Design

### Architecture

```
┌─────────────────────────────────────────┐
│  CLI Entry Point (cli.py)              │
│  - Add 'shell' command                 │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  InteractiveShell (NEW)                 │
│  claude_force/interactive_shell.py      │
│                                         │
│  - REPL loop                           │
│  - Command parsing                     │
│  - History management                  │
│  - Tab completion                      │
│  - Session context                     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  CommandExecutor (NEW)                  │
│  claude_force/shell/executor.py         │
│                                         │
│  - Reuse existing CLI commands         │
│  - Parse shell input                   │
│  - Handle errors gracefully            │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Existing Components                    │
│  - AgentOrchestrator                   │
│  - WorkflowComposer                    │
│  - PerformanceTracker                  │
└─────────────────────────────────────────┘
```

### Technology Stack

**Primary Library**: `prompt_toolkit`
- Rich REPL features
- Tab completion
- Syntax highlighting
- Multi-line editing
- Command history
- Cross-platform

**Alternative**: `cmd2` (if prompt_toolkit is overkill)

**Dependencies to add**:
```toml
dependencies = [
    "prompt-toolkit>=3.0.0",  # Interactive shell
    "pygments>=2.0.0",        # Syntax highlighting
]
```

---

## Implementation Phases

### Phase 1: Basic REPL (Week 1)

**Goal**: Working interactive shell with basic commands

**Tasks**:
- [ ] Create `claude_force/interactive_shell.py`
- [ ] Implement basic REPL loop with prompt_toolkit
- [ ] Add `shell` command to CLI (`cli.py`)
- [ ] Support basic commands: `list agents`, `list workflows`
- [ ] Implement `exit`/`quit`/Ctrl+D
- [ ] Command history (arrow keys)
- [ ] Basic error handling

**Files**:
- `claude_force/interactive_shell.py` (NEW)
- `claude_force/cli.py` (MODIFY - add shell command)
- `pyproject.toml` (MODIFY - add prompt_toolkit)

**Test**:
```bash
claude-force shell
claude-force> list agents
claude-force> list workflows
claude-force> exit
```

---

### Phase 2: Command Execution (Week 2)

**Goal**: Execute all existing commands in shell mode

**Tasks**:
- [ ] Create `claude_force/shell/executor.py`
- [ ] Parse shell input and route to existing CLI functions
- [ ] Support `run agent` command
- [ ] Support `workflow run` command
- [ ] Support `metrics` commands
- [ ] Maintain orchestrator instance for session
- [ ] Add loading indicators

**Files**:
- `claude_force/shell/executor.py` (NEW)
- `claude_force/shell/__init__.py` (NEW)
- `claude_force/interactive_shell.py` (MODIFY)

**Test**:
```bash
claude-force shell
claude-force> run agent code-reviewer --task "Review this code"
claude-force> metrics summary
```

---

### Phase 3: Tab Completion (Week 2-3)

**Goal**: Smart auto-completion for all inputs

**Tasks**:
- [ ] Create `claude_force/shell/completer.py`
- [ ] Implement agent name completion
- [ ] Implement workflow name completion
- [ ] Implement command completion
- [ ] Implement flag/option completion (`--task`, `--output`)
- [ ] File path completion for `--task-file`
- [ ] Context-aware completion (complete based on partial command)

**Files**:
- `claude_force/shell/completer.py` (NEW)
- `claude_force/interactive_shell.py` (MODIFY - integrate completer)

**Test**:
```bash
claude-force> run agent code-<TAB>
  code-reviewer
claude-force> run agent code-reviewer --task-<TAB>
  --task  --task-file
```

---

### Phase 4: Enhanced UX (Week 3)

**Goal**: Polish user experience

**Tasks**:
- [ ] Color-coded output (rich library)
- [ ] Multi-line input support
- [ ] Inline help system (`help`, `help run`)
- [ ] Clear screen command
- [ ] Session statistics tracking
- [ ] Welcome banner on shell start
- [ ] Goodbye message on exit

**Files**:
- `claude_force/shell/formatter.py` (NEW - output formatting)
- `claude_force/shell/help.py` (NEW - inline help)
- `claude_force/interactive_shell.py` (MODIFY)

**Test**:
```bash
claude-force shell

╔══════════════════════════════════════════╗
║   Claude Force Interactive Shell v1.3.0  ║
║   Type 'help' for commands               ║
║   Type 'exit' to quit                    ║
╚══════════════════════════════════════════╝

claude-force> help
Available commands:
  run agent <name> --task <task>
  workflow run <name> --task <task>
  list agents
  ...
```

---

### Phase 5: Advanced Features (Week 4)

**Goal**: Power-user features

**Tasks**:
- [ ] Shortcuts and aliases (`la`, `lw`, `r`, `w`)
- [ ] User-configurable aliases (`.claude/shell-config.yaml`)
- [ ] Session history export
- [ ] Shell configuration file
- [ ] Script execution mode (`claude-force shell --script commands.txt`)
- [ ] Shell variables (e.g., `$agent = code-reviewer`)

**Files**:
- `claude_force/shell/config.py` (NEW - config management)
- `claude_force/shell/aliases.py` (NEW - alias system)
- `.claude/shell-config.yaml` (NEW - user config template)

**Example config**:
```yaml
# .claude/shell-config.yaml
aliases:
  la: list agents
  lw: list workflows
  r: run agent
  review: run agent code-reviewer --task

prompt: "🤖 cf> "
colors:
  success: green
  error: red
  info: blue
```

---

### Phase 6: Testing & Documentation (Week 4)

**Goal**: Comprehensive testing and docs

**Tasks**:
- [ ] Unit tests for InteractiveShell
- [ ] Unit tests for CommandExecutor
- [ ] Unit tests for Completer
- [ ] Integration tests (simulate shell sessions)
- [ ] Update README.md with shell mode
- [ ] Create `docs/guides/interactive-shell.md`
- [ ] Update CHANGELOG.md
- [ ] Add examples to `examples/shell/`

**Files**:
- `tests/test_interactive_shell.py` (NEW)
- `tests/shell/test_executor.py` (NEW)
- `tests/shell/test_completer.py` (NEW)
- `docs/guides/interactive-shell.md` (NEW)
- `README.md` (MODIFY)
- `CHANGELOG.md` (MODIFY)

**Target**: 100% test coverage maintained

---

## File Structure

```
claude-force/
├── claude_force/
│   ├── interactive_shell.py         # NEW - Main shell class
│   ├── shell/                       # NEW - Shell subpackage
│   │   ├── __init__.py
│   │   ├── executor.py              # Command execution
│   │   ├── completer.py             # Tab completion
│   │   ├── formatter.py             # Output formatting
│   │   ├── help.py                  # Inline help
│   │   ├── config.py                # Config management
│   │   └── aliases.py               # Alias system
│   └── cli.py                       # MODIFY - add shell command
├── .claude/
│   └── shell-config.yaml            # NEW - User shell config
├── tests/
│   ├── test_interactive_shell.py    # NEW
│   └── shell/                       # NEW
│       ├── test_executor.py
│       ├── test_completer.py
│       └── test_formatter.py
├── docs/
│   └── guides/
│       └── interactive-shell.md     # NEW - Guide
└── examples/
    └── shell/                       # NEW - Shell examples
        ├── basic-session.txt
        └── advanced-workflow.txt
```

---

## API Design

### InteractiveShell Class

```python
# claude_force/interactive_shell.py

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer
from prompt_toolkit.history import FileHistory

class InteractiveShell:
    """
    Interactive REPL shell for claude-force.

    Features:
    - Command history with arrow keys
    - Tab completion for agents/workflows
    - Multi-line input support
    - Session context maintenance
    - Color-coded output
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize shell with optional config."""
        self.session = PromptSession(
            history=FileHistory('.claude/.shell-history'),
            completer=ClaudeForceCompleter(),
            multiline=False,
        )
        self.executor = CommandExecutor()
        self.config = self._load_config(config_path)
        self.running = False

    def start(self):
        """Start the interactive shell."""
        self._print_welcome()
        self.running = True

        while self.running:
            try:
                command = self.session.prompt('claude-force> ')
                self._execute_command(command)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

        self._print_goodbye()

    def _execute_command(self, command: str):
        """Execute a shell command."""
        # Handle built-in commands
        if command in ['exit', 'quit']:
            self.running = False
            return

        if command == 'clear':
            os.system('clear' if os.name != 'nt' else 'cls')
            return

        if command.startswith('help'):
            self._show_help(command)
            return

        # Execute claude-force command
        result = self.executor.execute(command)
        self._print_result(result)

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load shell configuration."""
        # Load from .claude/shell-config.yaml
        pass

    def _print_welcome(self):
        """Print welcome banner."""
        pass

    def _print_goodbye(self):
        """Print goodbye message with session stats."""
        pass
```

### CommandExecutor Class

```python
# claude_force/shell/executor.py

class CommandExecutor:
    """
    Executes claude-force commands in shell context.

    Reuses existing CLI command functions, maintaining
    orchestrator instance for performance.
    """

    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.history = []

    def execute(self, command: str) -> ExecutionResult:
        """
        Parse and execute a command.

        Args:
            command: Shell command (without 'claude-force' prefix)

        Returns:
            ExecutionResult with success status and output
        """
        # Parse command into args
        args = self._parse_command(command)

        # Route to appropriate handler
        if args[0] == 'run' and args[1] == 'agent':
            return self._run_agent(args[2:])
        elif args[0] == 'workflow' and args[1] == 'run':
            return self._run_workflow(args[2:])
        elif args[0] == 'list' and args[1] == 'agents':
            return self._list_agents()
        # ... more commands

    def _parse_command(self, command: str) -> list:
        """Parse shell command into arguments."""
        # Handle quoted strings, flags, etc.
        pass
```

### ClaudeForceCompleter Class

```python
# claude_force/shell/completer.py

from prompt_toolkit.completion import Completer, Completion

class ClaudeForceCompleter(Completer):
    """
    Tab completion for claude-force shell.

    Provides context-aware completions for:
    - Commands (run, workflow, list, etc.)
    - Agent names
    - Workflow names
    - Flags and options
    - File paths
    """

    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.agents = self.orchestrator.list_agents()
        self.workflows = self.orchestrator.list_workflows()

    def get_completions(self, document, complete_event):
        """Generate completions based on current input."""
        text = document.text_before_cursor
        words = text.split()

        # Complete command
        if len(words) == 0 or (len(words) == 1 and not text.endswith(' ')):
            yield from self._complete_command(words[0] if words else '')

        # Complete agent name
        elif len(words) >= 2 and words[0] == 'run' and words[1] == 'agent':
            yield from self._complete_agent(words[-1])

        # Complete workflow name
        elif len(words) >= 2 and words[0] == 'workflow' and words[1] == 'run':
            yield from self._complete_workflow(words[-1])

    def _complete_command(self, partial: str):
        """Complete command names."""
        commands = ['run', 'workflow', 'list', 'metrics', 'help', 'exit']
        for cmd in commands:
            if cmd.startswith(partial):
                yield Completion(cmd, start_position=-len(partial))
```

---

## User Stories

### Story 1: Quick Agent Execution
```
As a developer
I want to run multiple agents without retyping 'claude-force'
So that I can iterate faster on my tasks

Acceptance:
- Can enter shell with `claude-force shell`
- Can run agents with just `run agent <name>`
- Shell maintains context between commands
```

### Story 2: Tab Completion
```
As a developer
I want tab completion for agent and workflow names
So that I don't have to remember exact spellings

Acceptance:
- Pressing TAB shows available completions
- Partial names complete (code-<TAB> → code-reviewer)
- Works for agents, workflows, and commands
```

### Story 3: Multi-line Tasks
```
As a developer
I want to enter long tasks across multiple lines
So that complex prompts are easier to write

Acceptance:
- Can use backslash for line continuation
- Can paste multi-line text
- Shell handles line breaks properly
```

---

## Success Metrics

**Functional**:
- ✅ Shell starts and accepts commands
- ✅ All existing CLI commands work in shell mode
- ✅ Tab completion works for agents/workflows/commands
- ✅ Command history persists between sessions
- ✅ Multi-line input supported

**Technical**:
- ✅ 100% test coverage maintained (331+ tests)
- ✅ No performance regression
- ✅ Works on Linux, macOS, Windows
- ✅ Graceful error handling

**User Experience**:
- ✅ Faster workflow (no repeated typing)
- ✅ Intuitive and discoverable (help system)
- ✅ Pleasant to use (colors, formatting)

---

## Risks & Mitigation

**Risk 1**: Compatibility with existing CLI
- **Impact**: Breaking changes to command structure
- **Mitigation**: Reuse existing CLI functions, don't modify them
- **Fallback**: Keep both modes (shell and traditional CLI)

**Risk 2**: Cross-platform issues (Windows vs Unix)
- **Impact**: Different terminal behaviors
- **Mitigation**: Use prompt_toolkit (handles cross-platform)
- **Testing**: Test on all major platforms

**Risk 3**: Performance overhead from shell
- **Impact**: Slower command execution
- **Mitigation**: Maintain orchestrator instance (only initialize once)
- **Benefit**: Actually faster due to instance reuse

**Risk 4**: Learning curve for users
- **Impact**: Users don't know how to use shell
- **Mitigation**: Excellent inline help and documentation
- **Optional**: Traditional CLI still works

---

## Dependencies

**New Python Dependencies**:
```toml
[project]
dependencies = [
    # ... existing ...
    "prompt-toolkit>=3.0.0",  # Interactive shell
    "pygments>=2.0.0",        # Syntax highlighting (optional)
]
```

**Why prompt_toolkit?**
- ✅ Rich REPL features (history, completion, multi-line)
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Well-maintained (used by IPython, pgcli, etc.)
- ✅ Pythonic API
- ✅ Lightweight (~2MB)

---

## Testing Strategy

### Unit Tests

```python
# tests/test_interactive_shell.py

def test_shell_initialization():
    """Test shell initializes correctly."""
    shell = InteractiveShell()
    assert shell.running == False
    assert shell.executor is not None

def test_execute_list_agents():
    """Test listing agents in shell."""
    executor = CommandExecutor()
    result = executor.execute('list agents')
    assert result.success == True
    assert len(result.output) > 0

def test_execute_run_agent():
    """Test running agent in shell."""
    executor = CommandExecutor()
    result = executor.execute('run agent code-reviewer --task "Review"')
    assert result.success == True
```

### Integration Tests

```python
# tests/shell/test_shell_integration.py

def test_full_shell_session():
    """Simulate complete shell session."""
    shell = InteractiveShell()

    # Mock user input
    commands = [
        'list agents',
        'run agent code-reviewer --task "Test"',
        'metrics summary',
        'exit'
    ]

    # Execute session
    results = shell.execute_batch(commands)

    # Verify all succeeded
    assert all(r.success for r in results)
```

---

## Documentation Outline

### docs/guides/interactive-shell.md

```markdown
# Interactive Shell Guide

## Quick Start

Enter shell mode:
bash
$ claude-force shell


## Basic Commands

list agents          - Show all agents
run agent <name>     - Run an agent
workflow run <name>  - Run a workflow
help                 - Show help
exit                 - Exit shell


## Tab Completion

Press TAB to auto-complete:
- Agent names
- Workflow names
- Commands
- File paths


## Advanced Features

### Aliases
### Multi-line Input
### Configuration
### Keyboard Shortcuts


## Examples

### Code Review Workflow
### Full-Stack Development
### Batch Operations


## Troubleshooting

### Shell won't start
### Commands not found
### Performance issues
```

---

## Timeline

| Week | Phase | Deliverables |
|------|-------|-------------|
| 1 | Basic REPL | Working shell with basic commands |
| 2 | Command Execution | All CLI commands working |
| 2-3 | Tab Completion | Smart auto-completion |
| 3 | Enhanced UX | Colors, help, multi-line |
| 4 | Advanced Features | Aliases, config, scripts |
| 4 | Testing & Docs | Tests, documentation, examples |

**Total**: 3-4 weeks (part-time) or 2 weeks (full-time)

---

## Next Steps

1. ✅ Create feature branch: `claude/interactive-shell-01CCQfKdkGfUkdJBR6kw5Hnp`
2. ⏳ Review and approve this plan
3. ⏳ Start Phase 1: Basic REPL
4. ⏳ Implement InteractiveShell class
5. ⏳ Add `shell` command to CLI

---

## Future Enhancements (Post-v1.3.0)

**Shell Plugins**:
- User-extensible commands
- Custom completion providers
- Third-party integrations

**Remote Shell**:
- Connect to remote claude-force instances
- SSH-like session management

**Shell Recording**:
- Record and replay shell sessions
- Share shell session transcripts

**AI-Powered Shell**:
- Natural language command parsing
- Smart suggestions based on history
- Context-aware help

---

## References

**Similar Tools**:
- IPython - Python REPL: https://ipython.org
- pgcli - PostgreSQL CLI: https://www.pgcli.com
- mycli - MySQL CLI: https://www.mycli.net
- aws-shell - AWS CLI: https://github.com/awslabs/aws-shell

**Libraries**:
- prompt_toolkit: https://python-prompt-toolkit.readthedocs.io
- cmd2: https://cmd2.readthedocs.io
- rich: https://rich.readthedocs.io

---

**Status**: Ready for implementation 🚀
