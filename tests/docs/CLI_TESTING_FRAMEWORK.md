# CLI Testing Framework

Comprehensive testing framework for claude-force CLI commands with enhanced helpers, fixtures, and utilities.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Usage Guide](#usage-guide)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The CLI Testing Framework provides a robust set of tools for testing command-line interfaces:

- **CLITestCase**: Enhanced base test class with comprehensive assertions
- **CLITestTemplate**: Pre-configured test class with temporary project setup
- **CLIFixtures**: Reusable test data and project generators
- **CLIMockHelpers**: Utilities for mocking external dependencies
- **Assertion Helpers**: CLI-specific validation methods

### Benefits

✅ **Comprehensive** - Covers exit codes, output, JSON, errors, and file system
✅ **Reusable** - Pre-built fixtures and templates reduce boilerplate
✅ **Isolated** - Mock helpers prevent actual API calls
✅ **Readable** - Descriptive assertion methods improve test clarity
✅ **Maintainable** - Centralized utilities simplify updates

## Installation

The framework is included in the test suite. No additional installation required.

```python
from tests.cli_test_framework import CLITestCase, CLIFixtures, CLIMockHelpers
```

## Quick Start

### Basic Test

```python
from tests.cli_test_framework import CLITestCase

class TestMyCommand(CLITestCase):
    def test_help_command(self):
        result = self.run_cli("--help")
        self.assert_success(result)
        self.assert_in_output(result, "usage:")
```

### Test with Temporary Project

```python
from tests.cli_test_framework import CLITestTemplate, CLIFixtures

class TestListCommand(CLITestTemplate):
    def test_list_agents(self):
        # self.temp_dir and self.claude_dir are automatically set up
        CLIFixtures.create_full_project(self.temp_dir, num_agents=3)

        result = self.run_cli("list", "agents")
        self.assert_success(result)
        self.assert_in_output(result, "Total: 3 agents")
```

## Core Components

### CLITestCase

Base test class providing CLI execution and assertion methods.

#### Running Commands

```python
# Basic command
result = self.run_cli("list", "agents")

# With input (for interactive commands)
result = self.run_cli("init", input_text="myproject\n")

# With environment variables
result = self.run_cli("list", "agents", env={"DEBUG": "1"})

# With timeout
result = self.run_cli("long-command", timeout=60)
```

#### Exit Code Assertions

```python
# Assert success (exit code 0)
self.assert_success(result)

# Assert failure (non-zero exit code)
self.assert_failure(result)

# Assert specific exit code
self.assert_exit_code(result, 2)
```

#### Output Assertions

```python
# Assert text in stdout
self.assert_in_output(result, "Expected text")

# Assert text in stderr
self.assert_in_output(result, "Error message", check_stderr=True)

# Assert text NOT in output
self.assert_not_in_output(result, "Unexpected text")

# Assert multiple texts present
self.assert_output_contains_all(result, ["text1", "text2", "text3"])

# Assert regex pattern
self.assert_output_matches_regex(result, r"Total: \d+ agents")
```

#### JSON Assertions

```python
# Parse and validate JSON output
data = self.assert_json_output(result)

# Assert JSON has specific keys
self.assert_json_has_keys(result, ["name", "version", "agents"])

# Assert specific JSON value
self.assert_json_value(result, "name", "my-project")
```

#### Error Assertions

```python
# Assert error message in stderr
self.assert_error_message(result, "API key not found")

# Assert helpful error with keywords
self.assert_helpful_error(result, ["API key", "export", "ANTHROPIC_API_KEY"])
```

#### File System Assertions

```python
# Assert file exists
self.assert_file_exists(Path(".claude/claude.json"))

# Assert file doesn't exist
self.assert_file_not_exists(Path(".claude/old.json"))

# Assert directory structure
self.assert_directory_structure(temp_dir, [
    ".claude/claude.json",
    ".claude/agents",
    ".claude/workflows"
])

# Assert valid JSON file
config = self.assert_valid_json_file(Path(".claude/claude.json"))
```

### CLITestTemplate

Pre-configured test class with automatic setup/teardown.

**Automatically provides:**
- `self.temp_dir` - Temporary project directory
- `self.claude_dir` - `.claude` subdirectory
- `self.original_cwd` - Original working directory
- Automatic cleanup after each test

```python
class TestWithTemplate(CLITestTemplate):
    def test_something(self):
        # temp_dir is ready to use
        CLIFixtures.create_minimal_config(self.claude_dir)
        result = self.run_cli("list", "agents")
        self.assert_success(result)
```

### CLIFixtures

Reusable test data generators.

#### Create Temporary Project

```python
temp_dir = CLIFixtures.create_temp_project("my-project")
```

#### Create Minimal Config

```python
claude_dir = Path(".claude")
config = CLIFixtures.create_minimal_config(
    claude_dir,
    name="test-project",
    version="1.0.0"
)
```

#### Create Test Agent

```python
agent_path = CLIFixtures.create_test_agent(
    claude_dir,
    "my-agent",
    domains=["domain1", "domain2"]
)
```

#### Create Full Project

```python
# Creates project with agents, workflows, and config
config = CLIFixtures.create_full_project(temp_dir, num_agents=5)
```

### CLIMockHelpers

Utilities for mocking external dependencies.

#### Mock Anthropic Client

```python
with CLIMockHelpers.mock_anthropic_client():
    result = self.run_cli("run", "agent", "test-agent", "--task", "test")
    # No actual API call made
```

#### Mock Environment Variables

```python
with CLIMockHelpers.mock_env_vars(ANTHROPIC_API_KEY="test-key", DEBUG="1"):
    result = self.run_cli("list", "agents")
```

#### Remove API Key

```python
with CLIMockHelpers.no_api_key():
    result = self.run_cli("run", "agent", "test")
    self.assert_error_message(result, "API key")
```

## Usage Guide

### Testing a New Command

1. **Create test file** (e.g., `test_my_command.py`)
2. **Choose base class**:
   - Use `CLITestCase` for simple tests
   - Use `CLITestTemplate` if you need a temp project
3. **Write tests** using assertion helpers
4. **Run tests**: `pytest tests/test_my_command.py`

Example:

```python
from tests.cli_test_framework import CLITestTemplate, CLIFixtures

class TestAnalyzeCommand(CLITestTemplate):
    def setUp(self):
        super().setUp()
        # Create project with test data
        CLIFixtures.create_full_project(self.temp_dir, num_agents=3)

    def test_analyze_agents(self):
        result = self.run_cli("analyze", "agents")
        self.assert_success(result)
        self.assert_in_output(result, "Analysis")

    def test_analyze_json_output(self):
        result = self.run_cli("analyze", "agents", "--json")
        data = self.assert_json_output(result)
        self.assertIn("summary", data)
```

### Testing Error Scenarios

```python
class TestErrorHandling(CLITestTemplate):
    def test_missing_required_arg(self):
        result = self.run_cli("command-without-args")
        self.assert_failure(result)
        self.assert_in_output(result, "required", check_stderr=True)

    def test_invalid_input(self):
        CLIFixtures.create_minimal_config(self.claude_dir)
        result = self.run_cli("run", "agent", "nonexistent")
        self.assert_error_message(result, "Agent not found")

    def test_helpful_suggestions(self):
        CLIFixtures.create_minimal_config(self.claude_dir)
        result = self.run_cli("run", "agent", "cod-reviewer")  # typo
        self.assert_helpful_error(result, ["not found", "Did you mean", "code-reviewer"])
```

### Testing JSON Output

```python
class TestJSONOutput(CLITestTemplate):
    def test_agents_json_format(self):
        CLIFixtures.create_full_project(self.temp_dir, num_agents=3)

        result = self.run_cli("list", "agents", "--json")
        self.assert_success(result)

        # Validate JSON structure
        data = self.assert_json_output(result)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

        # Check required keys
        self.assert_json_has_keys(result, ["name", "priority", "domains"])

        # Validate specific values
        for agent in data:
            self.assertIn("name", agent)
            self.assertIn("test-agent", agent["name"])
```

### Testing Interactive Commands

```python
class TestInteractiveCommands(CLITestTemplate):
    def test_init_interactive(self):
        # Simulate user input
        user_input = "myproject\nMy Description\nPython, FastAPI\n1\n"

        result = self.run_cli(
            "init",
            str(self.temp_dir),
            "--interactive",
            input_text=user_input
        )

        self.assert_success(result)
        self.assert_in_output(result, "Project name")
        self.assert_file_exists(self.claude_dir / "claude.json")
```

### Testing with Mocks

```python
class TestWithMocks(CLITestTemplate):
    def test_no_api_key_error(self):
        CLIFixtures.create_full_project(self.temp_dir, num_agents=1)

        with CLIMockHelpers.no_api_key():
            result = self.run_cli("run", "agent", "test-agent-1", "--task", "test")
            self.assert_helpful_error(result, [
                "API key",
                "ANTHROPIC_API_KEY",
                "https://console.anthropic.com"
            ])

    def test_with_test_api_key(self):
        CLIFixtures.create_minimal_config(self.claude_dir)

        with CLIMockHelpers.mock_env_vars(ANTHROPIC_API_KEY="sk-test-key"):
            result = self.run_cli("list", "agents")
            self.assert_success(result)
```

## Best Practices

### 1. Use Appropriate Base Class

```python
# ✅ Good: Simple test, no project needed
class TestHelpCommand(CLITestCase):
    def test_help(self):
        result = self.run_cli("--help")
        self.assert_success(result)

# ✅ Good: Needs temp project
class TestProjectCommands(CLITestTemplate):
    def test_list(self):
        CLIFixtures.create_minimal_config(self.claude_dir)
        result = self.run_cli("list", "agents")
        self.assert_success(result)

# ❌ Avoid: Manual setup when template exists
class TestBad(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()  # Use CLITestTemplate instead!
```

### 2. Use Descriptive Assertion Methods

```python
# ✅ Good: Clear and specific
self.assert_json_has_keys(result, ["name", "version"])
self.assert_helpful_error(result, ["API key", "required"])

# ❌ Avoid: Generic assertions
self.assertIn("name", json.loads(result.stdout))
self.assertTrue("API key" in result.stderr)
```

### 3. Test Both Success and Failure

```python
class TestCommand(CLITestTemplate):
    def test_success_case(self):
        CLIFixtures.create_full_project(self.temp_dir, num_agents=1)
        result = self.run_cli("analyze", "agents")
        self.assert_success(result)

    def test_failure_no_agents(self):
        CLIFixtures.create_minimal_config(self.claude_dir)
        result = self.run_cli("analyze", "agents")
        self.assert_failure(result)
        self.assert_error_message(result, "No agents found")
```

### 4. Use Fixtures for Test Data

```python
# ✅ Good: Reusable fixtures
CLIFixtures.create_full_project(self.temp_dir, num_agents=5)

# ❌ Avoid: Manual test data creation in each test
agents_dir = self.claude_dir / "agents"
agents_dir.mkdir()
(agents_dir / "agent1.md").write_text("...")
(agents_dir / "agent2.md").write_text("...")
# ... repetitive code
```

### 5. Mock External Dependencies

```python
# ✅ Good: No actual API calls
with CLIMockHelpers.mock_anthropic_client():
    result = self.run_cli("run", "agent", "test", "--task", "test")

# ❌ Avoid: Real API calls in tests
result = self.run_cli("run", "agent", "test", "--task", "test")
# Slow, expensive, requires API key
```

## Examples

See `tests/test_cli_framework_examples.py` for comprehensive examples including:

- Basic command testing
- JSON output validation
- Error message testing
- Interactive command testing
- Mock usage
- Advanced assertions
- Directory structure validation

## Running Tests

```bash
# Run all CLI tests
pytest tests/integration/

# Run specific test file
pytest tests/test_my_command.py

# Run with verbose output
pytest tests/test_my_command.py -v

# Run specific test
pytest tests/test_my_command.py::TestMyCommand::test_specific
```

## Contributing

When adding new CLI commands:

1. Create corresponding test file in `tests/`
2. Use the CLI testing framework
3. Test success, failure, and edge cases
4. Test both normal and JSON output
5. Test error messages are helpful
6. Add examples to documentation

## Support

For issues or questions:
- Check existing tests in `tests/integration/`
- Review examples in `tests/test_cli_framework_examples.py`
- See framework source in `tests/cli_test_framework.py`

---

**Version**: 1.0.0
**Last Updated**: 2025-11-14
**Maintained By**: Claude Force Team
