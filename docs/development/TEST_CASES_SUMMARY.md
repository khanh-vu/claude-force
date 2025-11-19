# Interactive Shell - Comprehensive Test Cases Summary

**Branch**: `claude/interactive-shell-01CCQfKdkGfUkdJBR6kw5Hnp`
**TDD Approach**: All tests written BEFORE implementation
**Total Test Cases**: 200+ tests across 4 files

---

## Overview

This document summarizes all test cases created for the Interactive Shell feature. Tests are organized by component and follow Test-Driven Development (TDD) principles.

### Test Files Created

1. `tests/test_interactive_shell.py` - **Main shell tests** (100+ tests)
2. `tests/shell/test_executor.py` - **CommandExecutor tests** (40+ tests)
3. `tests/shell/test_completer.py` - **Tab completion tests** (40+ tests)
4. `tests/shell/test_edge_cases_security.py` - **Edge cases & security** (50+ tests)

---

## Test Coverage Matrix

| Component | Unit Tests | Integration Tests | Security Tests | Edge Cases | Performance Tests |
|-----------|-----------|-------------------|----------------|------------|-------------------|
| InteractiveShell | ✅ | ✅ | ✅ | ✅ | ✅ |
| CommandExecutor | ✅ | ✅ | ✅ | ✅ | ✅ |
| Completer | ✅ | ✅ | ✅ | ✅ | ✅ |
| Config | ✅ | ✅ | ❌ | ✅ | ❌ |
| Session | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## File 1: `tests/test_interactive_shell.py`

### Test Classes (10 classes, 100+ tests)

#### 1. TestInteractiveShellInitialization (8 tests)
- ✅ Shell creates successfully
- ✅ Loads default config
- ✅ Creates config if missing
- ✅ Loads custom config
- ✅ Initializes orchestrator
- ✅ Creates history file
- ✅ Fails gracefully without .claude dir
- ✅ Validates API key on start

**Focus**: Proper initialization and configuration loading

---

#### 2. TestCommandExecution (10 tests)
- ✅ Execute `list agents`
- ✅ Execute `list workflows`
- ✅ Execute `run agent`
- ✅ Execute `workflow run`
- ✅ Invalid command returns error
- ✅ Missing required arg returns error
- ✅ Command with quoted task
- ✅ Command with escaped quotes
- ✅ Command with multiline task
- ✅ Preserves orchestrator state

**Focus**: Command parsing and routing

---

#### 3. TestBuiltInCommands (6 tests)
- ✅ `exit` command stops shell
- ✅ `quit` command stops shell
- ✅ `help` shows help text
- ✅ `help <command>` shows specific help
- ✅ `clear` clears screen
- ✅ `history` shows command history

**Focus**: Shell-specific built-in commands

---

#### 4. TestAliasSystem (4 tests)
- ✅ Alias expands to full command
- ✅ Alias with arguments
- ✅ Undefined alias treated as command
- ✅ Alias doesn't recurse

**Focus**: Alias expansion and execution

---

#### 5. TestErrorHandling (8 tests)
- ✅ Invalid agent name returns error
- ✅ Invalid workflow name returns error
- ✅ API error handled gracefully
- ✅ Malformed command returns parsing error
- ✅ Empty command ignored
- ✅ Task size limit enforced
- ✅ Missing API key returns error
- ✅ Keyboard interrupt during execution

**Focus**: Robust error handling

---

#### 6. TestSessionManagement (6 tests)
- ✅ Session tracks command count
- ✅ Session tracks execution time
- ✅ Session tracks successful/failed commands
- ✅ Session persists history to file
- ✅ Session loads history on start
- ✅ Session recovery after crash

**Focus**: Session state persistence

---

#### 7. TestInputProcessing (7 tests)
- ✅ Strips leading/trailing whitespace
- ✅ Handles tab characters
- ✅ Handles special characters in task
- ✅ Handles Unicode in task
- ✅ Handles very long command line
- ✅ Prevents command injection
- ✅ Handles path traversal attempts

**Focus**: Input sanitization and validation

---

#### 8. TestOutputFormatting (6 tests)
- ✅ Success output formatted correctly
- ✅ Error output formatted correctly
- ✅ Long output truncated appropriately
- ✅ JSON output mode works
- ✅ Quiet mode suppresses output
- ✅ Color disabled for non-TTY

**Focus**: Output display and formatting

---

#### 9. TestTabCompletion (6 tests)
- ✅ Completer suggests commands
- ✅ Completer suggests agent names
- ✅ Completer suggests workflow names
- ✅ Completer suggests flags
- ✅ Completer handles partial matches
- ✅ Completer case-insensitive

**Focus**: Tab completion functionality

---

#### 10. TestDemoMode (3 tests)
- ✅ Demo mode enables simulated responses
- ✅ Demo mode shown in prompt
- ✅ Demo mode toggle during session

**Focus**: Demo mode integration

---

#### 11. TestCrossPlatformCompatibility (6 tests)
- ✅ Shell works on Windows
- ✅ Shell works on Linux
- ✅ Shell works on macOS
- ✅ Path separators handled correctly
- ✅ Line endings handled correctly
- ✅ `clear` works on all platforms

**Focus**: Cross-platform compatibility

---

#### 12. TestPerformance (5 tests)
- ✅ Shell startup time under 200ms
- ✅ Command execution overhead minimal
- ✅ Tab completion response under 100ms
- ✅ Memory stable over long session
- ✅ History file size limited

**Focus**: Performance benchmarks

---

#### 13. TestSecurity (4 tests)
- ✅ Prevents arbitrary code execution
- ✅ Sanitizes file paths
- ✅ API key not logged in history
- ✅ Sensitive data not in error messages

**Focus**: Security vulnerabilities

---

#### 14. TestEdgeCases (12 tests)
- ✅ Empty string command
- ✅ Only whitespace command
- ✅ Extremely long command
- ✅ Null byte in command
- ✅ Rapid command execution
- ✅ Concurrent shell instances
- ✅ Recovery from corrupted history
- ✅ Handles missing permissions
- ✅ Ctrl+C during startup
- ✅ EOF during startup
- ✅ Various boundary conditions

**Focus**: Edge cases and unusual scenarios

---

#### 15. TestIntegration (4 tests)
- ✅ Full agent workflow
- ✅ Full workflow execution
- ✅ Error recovery workflow
- ✅ Session persistence across restarts

**Focus**: End-to-end integration

---

#### 16. TestCommandExecutor (5 tests)
- ✅ Executor initializes with orchestrator
- ✅ Parses command correctly
- ✅ Handles quoted arguments
- ✅ Reuses orchestrator instance
- ✅ Tracks execution history

**Focus**: CommandExecutor unit tests

---

## File 2: `tests/shell/test_executor.py`

### Test Classes (8 classes, 40+ tests)

#### 1. TestArgumentParsing (9 tests)
- ✅ Parse simple command
- ✅ Parse with flags
- ✅ Parse with quoted string
- ✅ Parse with single quotes
- ✅ Parse with escaped quotes
- ✅ Parse with multiple spaces
- ✅ Parse with equals sign
- ✅ Empty command returns empty list
- ✅ Parse with special characters

**Focus**: shlex-based command parsing

**Critical Implementation Notes**:
```python
# Must use shlex for proper parsing
import shlex
args = shlex.split(command_string)
```

---

#### 2. TestCommandRouting (6 tests)
- ✅ Route `list agents` command
- ✅ Route `list workflows` command
- ✅ Route `run agent` command
- ✅ Route `workflow run` command
- ✅ Route `metrics` command
- ✅ Unknown command returns error

**Focus**: Routing to correct handlers

**Critical Implementation Notes**:
```python
# MUST reuse existing argparse parser
# DO NOT create parallel routing system
from .cli import create_parser
parser = create_parser()
args = parser.parse_args(shlex.split(command))
```

---

#### 3. TestArgparseIntegration (4 tests)
- ✅ Reuses existing argparse parser
- ✅ Argparse errors caught and converted
- ✅ --help doesn't exit shell
- ✅ Subcommands work correctly

**Focus**: Integration with CLI's argparse

**Critical Implementation Notes**:
```python
# argparse calls sys.exit() on errors
# Must catch SystemExit and convert to ExecutionResult
try:
    args = parser.parse_args(...)
except SystemExit:
    return ExecutionResult(success=False, error="...")
```

---

#### 4. TestExecutionResults (6 tests)
- ✅ Result has success field
- ✅ Result has output field
- ✅ Result has error field
- ✅ Result has metadata field
- ✅ Successful result has no error
- ✅ Failed result has error message

**Focus**: ExecutionResult data structure

**Implementation**:
```python
@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: str = ""
    metadata: dict = field(default_factory=dict)
```

---

#### 5. TestStateManagement (4 tests)
- ✅ Reuses orchestrator instance
- ✅ Maintains history
- ✅ History includes command and result
- ✅ History limited to max size

**Focus**: State across commands

---

#### 6. TestErrorHandling (5 tests)
- ✅ Handles orchestrator exception
- ✅ Handles parsing exception
- ✅ Handles keyboard interrupt
- ✅ Handles missing API key
- ✅ Handles invalid agent name

**Focus**: Graceful error handling

---

#### 7. TestPerformance (2 tests)
- ✅ Command execution is fast
- ✅ Parsing overhead minimal

**Focus**: Performance benchmarks

---

#### 8. TestEdgeCases (5 tests)
- ✅ Empty command handled
- ✅ Very long command
- ✅ Command with newlines
- ✅ Command with Unicode
- ✅ Command with null bytes

**Focus**: Boundary conditions

---

## File 3: `tests/shell/test_completer.py`

### Test Classes (8 classes, 40+ tests)

#### 1. TestCommandCompletion (7 tests)
- ✅ Complete `ru` → `run`
- ✅ Complete `lis` → `list`
- ✅ Complete `work` → `workflow`
- ✅ Complete `hel` → `help`
- ✅ Complete `ex` → `exit`
- ✅ No completions after complete command + space
- ✅ All commands listed on empty input

**Focus**: Command name completion

---

#### 2. TestAgentCompletion (5 tests)
- ✅ Complete agent after `run agent`
- ✅ Complete partial agent name
- ✅ Case-insensitive completion
- ✅ Prefix match completion
- ✅ No agents in wrong context

**Focus**: Agent name completion

---

#### 3. TestWorkflowCompletion (3 tests)
- ✅ Complete workflow after `workflow run`
- ✅ Complete partial workflow name
- ✅ Case-insensitive workflow completion

**Focus**: Workflow name completion

---

#### 4. TestFlagCompletion (6 tests)
- ✅ Complete `--task` flag
- ✅ Complete `--task-file` flag
- ✅ Complete `--output` flag
- ✅ Complete `--json` flag
- ✅ Complete `--quiet` flag
- ✅ Complete `--help` flag

**Focus**: Flag/option completion

---

#### 5. TestFilePathCompletion (3 tests)
- ✅ Complete task file path
- ✅ Complete directory path
- ✅ Complete path with spaces

**Focus**: File path completion

---

#### 6. TestContextAwareness (5 tests)
- ✅ Completes subcommand after `run`
- ✅ Completes subcommand after `list`
- ✅ Completes subcommand after `workflow`
- ✅ No completions after task value
- ✅ Cursor position affects completion

**Focus**: Context-aware completion

---

#### 7. TestCompletionMetadata (3 tests)
- ✅ Completion has display text
- ✅ Completion has metadata descriptions
- ✅ Completion start_position correct

**Focus**: Completion display metadata

---

#### 8. TestPerformance (3 tests)
- ✅ Completion fast for empty input
- ✅ Completion fast for partial agent
- ✅ Completer caches agent list

**Focus**: Completion performance

**Benchmarks**:
- Empty input: < 100ms
- Partial match: < 100ms
- Caching: Only load agents once

---

#### 9. TestEdgeCases (6 tests)
- ✅ Completion with trailing spaces
- ✅ Mixed case input
- ✅ Completion with typo (doesn't crash)
- ✅ Very long input
- ✅ Unicode input
- ✅ Empty agent list

**Focus**: Robustness

---

## File 4: `tests/shell/test_edge_cases_security.py`

### Test Classes (11 classes, 50+ tests)

#### 1. TestCommandInjectionPrevention (6 tests)
- ✅ Prevents shell command injection (`;`)
- ✅ Prevents pipe injection (`|`)
- ✅ Prevents backtick execution (\`)
- ✅ Prevents `$()` expansion
- ✅ Prevents newline injection
- ✅ Prevents null byte injection

**Focus**: Security against command injection

**Critical**: All shell metacharacters must be treated as literals

---

#### 2. TestPathTraversalPrevention (4 tests)
- ✅ Prevents `..` traversal
- ✅ Prevents absolute paths to sensitive files
- ✅ Prevents symlink traversal
- ✅ Task file paths validated

**Focus**: Path traversal attacks

**Critical**: Implement path validation/sanitization

---

#### 3. TestSensitiveDataHandling (4 tests)
- ✅ API key not in history
- ✅ API key not in error messages
- ✅ Passwords not in logs
- ✅ Sensitive files not readable

**Focus**: Sensitive data protection

**Critical**: Must redact/sanitize sensitive data

---

#### 4. TestResourceLimits (4 tests)
- ✅ Task size limit enforced
- ✅ Command length limit enforced
- ✅ History size limit enforced
- ✅ Concurrent execution limit

**Focus**: DoS prevention via resource limits

**Limits**:
- Task size: 10MB max
- History: 1000 entries max
- Concurrent: Reasonable queue

---

#### 5. TestBoundaryConditions (6 tests)
- ✅ Empty string input
- ✅ Only whitespace input
- ✅ Maximum argument count
- ✅ Deeply nested quotes
- ✅ Unicode boundaries
- ✅ Zero-length agent name

**Focus**: Boundary value testing

---

#### 6. TestRaceConditions (3 tests)
- ✅ Concurrent shells same history
- ✅ Config modified during session
- ✅ History deleted during session

**Focus**: Concurrency issues

---

#### 7. TestErrorRecovery (4 tests)
- ✅ Recovery from orchestrator crash
- ✅ Recovery from disk full
- ✅ Recovery from permission denied
- ✅ Recovery from corrupted state

**Focus**: Graceful degradation

---

#### 8. TestStressTesting (4 tests)
- ✅ Rapid-fire 1000 commands
- ✅ Very long session (60 seconds)
- ✅ Memory stable under load
- ✅ Alternating success/failure

**Focus**: Stability under stress

**Benchmarks**:
- Rapid fire: 1000 commands without failure
- Long session: 60s continuous operation
- Memory: < 100MB peak

---

#### 9. TestPlatformSpecificEdgeCases (4 tests)
- ✅ Windows path separators (`\`)
- ✅ Unix path separators (`/`)
- ✅ Windows line endings (CRLF)
- ✅ macOS special paths (`~`)

**Focus**: Cross-platform compatibility

---

#### 10. TestFuzzing (3 tests)
- ✅ Random ASCII input (100 iterations)
- ✅ Random Unicode input (100 iterations)
- ✅ Random binary input (100 iterations)

**Focus**: Robustness against arbitrary input

**Critical**: Shell must NOT crash on any input

---

## Test Execution Strategy

### TDD Workflow

```bash
# 1. Run tests (should FAIL - Red)
pytest tests/test_interactive_shell.py -v
# Expected: All tests fail (code not implemented)

# 2. Implement minimal code to pass ONE test (Green)
# ... write code ...

# 3. Run tests again
pytest tests/test_interactive_shell.py::TestInteractiveShellInitialization::test_shell_creates_successfully -v
# Expected: This test passes

# 4. Refactor (Refactor)
# ... improve code while keeping tests passing ...

# 5. Repeat for next test
```

### Test Execution Order

**Phase 1: Foundation**
1. `TestInteractiveShellInitialization` - Setup and config
2. `TestCommandExecutor` - Basic executor
3. `TestArgumentParsing` - Command parsing

**Phase 2: Core Functionality**
4. `TestCommandExecution` - Command routing
5. `TestBuiltInCommands` - Shell commands
6. `TestErrorHandling` - Error handling

**Phase 3: Advanced Features**
7. `TestTabCompletion` - Completion
8. `TestAliasSystem` - Aliases
9. `TestSessionManagement` - Session state

**Phase 4: Quality & Security**
10. `TestSecurity` - Security tests
11. `TestEdgeCases` - Edge cases
12. `TestPerformance` - Performance benchmarks

**Phase 5: Integration**
13. `TestIntegration` - End-to-end tests
14. `TestCrossPlatformCompatibility` - Platform tests

---

## Test Coverage Goals

### Coverage Targets

| Component | Target | Priority |
|-----------|--------|----------|
| InteractiveShell | 95% | P0 |
| CommandExecutor | 95% | P0 |
| Completer | 90% | P1 |
| Config | 85% | P2 |
| Formatter | 80% | P2 |

### Current Coverage (After Implementation)

```bash
# Run coverage
pytest --cov=claude_force.interactive_shell \
       --cov=claude_force.shell \
       --cov-report=html \
       --cov-report=term

# Expected output:
# Name                                  Stmts   Miss  Cover
# ---------------------------------------------------------
# claude_force/interactive_shell.py      250      12    95%
# claude_force/shell/executor.py         180       9    95%
# claude_force/shell/completer.py        150      15    90%
# claude_force/shell/config.py            80      12    85%
# claude_force/shell/formatter.py         60      12    80%
# ---------------------------------------------------------
# TOTAL                                  720      60    92%
```

---

## Key Testing Patterns

### 1. Mocking Pattern

```python
@pytest.fixture
def mock_orchestrator():
    """Standard mock for AgentOrchestrator."""
    orch = Mock()
    orch.list_agents.return_value = ["code-reviewer"]
    return orch
```

### 2. Temporary Directory Pattern

```python
@pytest.fixture
def temp_claude_dir(tmp_path):
    """Create isolated .claude directory for testing."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    return claude_dir
```

### 3. Document Creation Pattern (Completion)

```python
def create_document(text, cursor_position=None):
    """Helper for creating prompt_toolkit Document."""
    if cursor_position is None:
        cursor_position = len(text)
    return Document(text=text, cursor_position=cursor_position)
```

### 4. Error Testing Pattern

```python
def test_handles_error(shell_instance, mock_orchestrator):
    """Test error is handled gracefully."""
    mock_orchestrator.run_agent.side_effect = Exception("Error")
    result = shell_instance.executor.execute("run agent code-reviewer")
    assert result.success == False
    assert "error" in result.error.lower()
```

---

## Critical Implementation Notes

### From Expert Review

**MUST-DO** (Blockers identified in review):

1. **Reuse Argparse** (NOT create new parser)
   ```python
   # DO THIS
   from .cli import create_parser
   parser = create_parser()
   args = parser.parse_args(shlex.split(command))

   # NOT THIS
   if args[0] == "run" and args[1] == "agent":  # ❌
   ```

2. **Catch SystemExit** (argparse exits on errors)
   ```python
   try:
       args = parser.parse_args(shlex.split(command))
   except SystemExit as e:
       return ExecutionResult(success=False, error="Invalid command")
   ```

3. **Use shlex for Parsing** (NOT manual string splitting)
   ```python
   import shlex
   args = shlex.split(command)  # Handles quotes properly
   ```

4. **Implement Path Validation** (Security critical)
   ```python
   from claude_force.security.path_validator import validate_path
   if not validate_path(task_file):
       raise SecurityError("Invalid path")
   ```

5. **Limit Resource Usage** (DoS prevention)
   ```python
   MAX_TASK_SIZE = 10 * 1024 * 1024  # 10MB
   MAX_HISTORY_SIZE = 1000
   if len(task) > MAX_TASK_SIZE:
       raise ValueError("Task too large")
   ```

---

## Test Maintenance

### Adding New Tests

1. **Choose appropriate test file**:
   - Core shell: `test_interactive_shell.py`
   - Executor: `test_executor.py`
   - Completion: `test_completer.py`
   - Security/Edge: `test_edge_cases_security.py`

2. **Follow naming convention**:
   ```python
   def test_<component>_<scenario>_<expected_behavior>():
       """Test that <component> <expected_behavior> when <scenario>."""
   ```

3. **Use appropriate fixtures**:
   - `mock_orchestrator` - Mock AgentOrchestrator
   - `temp_claude_dir` - Temporary .claude directory
   - `shell_instance` - InteractiveShell instance

4. **Add docstring explaining purpose**

5. **Update this summary document**

### Running Specific Test Subsets

```bash
# All shell tests
pytest tests/test_interactive_shell.py tests/shell/ -v

# Only security tests
pytest tests/shell/test_edge_cases_security.py::TestCommandInjectionPrevention -v

# Only performance tests
pytest tests/test_interactive_shell.py::TestPerformance -v

# Only executor tests
pytest tests/shell/test_executor.py -v

# Only completion tests
pytest tests/shell/test_completer.py -v

# Run with coverage
pytest --cov=claude_force.shell --cov-report=html

# Run fast tests only (exclude slow ones)
pytest -m "not slow" tests/
```

---

## Success Criteria

### Test Suite Must

- ✅ All tests initially FAIL (before implementation)
- ✅ Tests guide implementation (TDD)
- ✅ 90%+ coverage of shell components
- ✅ All security tests pass
- ✅ All edge case tests pass
- ✅ Performance benchmarks met
- ✅ Cross-platform tests pass on all platforms
- ✅ Integration tests demonstrate end-to-end functionality

### Test Execution Time

- Unit tests: < 10 seconds
- Integration tests: < 30 seconds
- All tests: < 60 seconds
- (Excluding fuzz tests which may take longer)

---

## Next Steps

1. ✅ **Expert review complete** - Comprehensive feedback received
2. ✅ **Test cases created** - 200+ tests written
3. ⏳ **Address review feedback** - Update plan based on review
4. ⏳ **Verify tests fail** - Run tests to confirm they fail (Red)
5. ⏳ **Begin implementation** - Phase 1: Basic REPL
6. ⏳ **Make tests pass** - Implement until tests pass (Green)
7. ⏳ **Refactor** - Improve code while keeping tests green

---

**Document Status**: Complete ✅
**Last Updated**: 2025-11-18
**Total Test Cases**: 200+
**Coverage Target**: 90%+
**TDD Ready**: Yes
