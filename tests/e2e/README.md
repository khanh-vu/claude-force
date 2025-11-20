# End-to-End (E2E) Test Suite

## Overview

The E2E test suite simulates real end-user scenarios with fresh package installations. These tests ensure that:

- ✅ Package installs correctly with all dependencies
- ✅ All modules can be imported without errors
- ✅ Core features work from end-user perspective
- ✅ CLI commands execute properly
- ✅ Interactive shell functions as expected
- ✅ No missing dependencies at runtime

## Why E2E Tests?

Unit tests verify individual components, but E2E tests verify the **complete user experience**:

1. **Installation Testing** - Catches missing dependencies in `requirements.txt` or `pyproject.toml`
2. **Integration Testing** - Verifies all components work together
3. **Real-world Scenarios** - Tests actual user workflows
4. **Fresh Environment** - Simulates first-time installation
5. **Cross-platform** - Works on Linux, macOS, and Windows

## Test Categories

### 1. Fresh Installation Tests (`test_fresh_install.py`)

Tests that verify the package installs correctly:

- Package can be installed via pip
- All modules are importable
- Required dependencies are available
- No import errors occur

### 2. Interactive Shell Tests (`test_interactive_shell_e2e.py`)

Tests that verify the interactive shell works:

- Executor can execute commands
- Tab completion functions correctly
- Slash commands work (e.g., `/list`, `/run`)
- UI components display properly
- Error handling shows helpful messages
- Streaming output works

### 3. CLI Tests (`test_cli_e2e.py`)

Tests that verify CLI commands work:

- CLI can be run as module (`python -m claude_force`)
- Help command displays correctly
- Version command works
- CLI entry points are functional

## Running E2E Tests

### Quick Run (Current Environment)

Run tests in your current Python environment:

```bash
# Run all E2E tests (without coverage requirement)
pytest tests/e2e/ -v --no-cov

# Run specific test file
pytest tests/e2e/test_fresh_install.py -v --no-cov

# Note: E2E tests run with --no-cov because they test user workflows,
# not code coverage. They naturally achieve low coverage (~6%) since
# they verify end-to-end functionality, not individual code paths.
```

### Full E2E Test Suite (Fresh Install Simulation)

Use the test runner script for a complete fresh installation test:

#### Linux/macOS:

```bash
# Run with automatic cleanup
./scripts/run_e2e_tests.sh --clean

# Run and preserve test environment
./scripts/run_e2e_tests.sh
```

#### Windows/Cross-platform:

```bash
# Run with automatic cleanup
python scripts/run_e2e_tests.py --clean

# Run in current environment (no venv)
python scripts/run_e2e_tests.py --no-venv

# Run and preserve test environment
python scripts/run_e2e_tests.py
```

## Test Runner Features

The E2E test runner (`run_e2e_tests.py`):

1. ✅ Creates a fresh virtual environment
2. ✅ Installs the package from source
3. ✅ Verifies all dependencies are installed
4. ✅ Runs all E2E tests
5. ✅ Tests critical imports
6. ✅ Verifies CLI execution
7. ✅ Provides detailed output
8. ✅ Optionally cleans up after itself

## Adding New E2E Tests

When adding new features, add corresponding E2E tests:

1. **Create test file** in `tests/e2e/`
2. **Test from user perspective** - What would a user do?
3. **Test fresh installation** - Assume clean environment
4. **Test complete workflows** - Not just individual functions
5. **Document the test** - Clear docstrings

### Example E2E Test

```python
def test_user_lists_and_runs_agent(self):
    """
    E2E Test: User lists agents and runs one.

    Simulates typical user workflow:
    1. User types 'list agents'
    2. User sees available agents
    3. User runs an agent with a task
    """
    mock_orchestrator = Mock()
    mock_orchestrator.list_agents.return_value = ["code-reviewer"]
    mock_orchestrator.run_agent.return_value = {"status": "success"}

    executor = CommandExecutor(mock_orchestrator)

    # Step 1: List agents
    result = executor.execute("list agents")
    assert result.success is True
    assert "code-reviewer" in result.output

    # Step 2: Run agent
    result = executor.execute('run agent code-reviewer --task "Test"')
    assert result.success is True
```

## CI/CD Integration

Add E2E tests to your CI/CD pipeline:

### GitHub Actions Example

```yaml
- name: Run E2E Tests
  run: |
    python scripts/run_e2e_tests.py --clean
```

### GitLab CI Example

```yaml
e2e_tests:
  script:
    - python scripts/run_e2e_tests.py --clean
```

## Test Requirements

E2E tests require:

- Python 3.8+
- pytest
- pytest-cov (optional, for coverage)
- All package dependencies

## Troubleshooting

### Test fails with "ModuleNotFoundError"

This means a dependency is missing from `requirements.txt`:

1. Check which module is missing
2. Add it to `requirements.txt`
3. Add it to `pyproject.toml` dependencies
4. Verify with `pip install -e .`

### Test fails with "Command not found"

This means the CLI entry point isn't configured:

1. Check `pyproject.toml` `[project.scripts]`
2. Check `setup.py` `entry_points`
3. Reinstall package: `pip install -e .`

### Virtual environment issues

If virtual environment creation fails:

1. Use `--no-venv` flag
2. Check Python venv module is installed
3. Try manual venv: `python -m venv test-env`

## Best Practices

1. **Run before every PR** - Catch issues early
2. **Test fresh install** - Don't assume dependencies
3. **Test user workflows** - Not just functions
4. **Keep tests fast** - Use mocks for external services
5. **Document tests** - Clear purpose and steps
6. **Update after features** - Add E2E tests for new features

## Related

- Unit tests: `tests/shell/`
- Integration tests: `tests/`
- Test documentation: `tests/README.md` (if exists)
