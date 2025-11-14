# CLI Testing Framework

## Quick Start

```python
from tests.cli_test_framework import CLITestTemplate, CLIFixtures

class TestMyCommand(CLITestTemplate):
    def test_command(self):
        # Automatic temp directory setup
        CLIFixtures.create_full_project(self.temp_dir, num_agents=3)

        result = self.run_cli("my-command", "--option", "value")
        self.assert_success(result)
        self.assert_in_output(result, "Expected output")
```

## What's Included

### Core Classes
- **CLITestCase** - Base test class with assertion helpers
- **CLITestTemplate** - Pre-configured with temp directory
- **CLIFixtures** - Test data generators
- **CLIMockHelpers** - Mock utilities

### Assertion Helpers
- `assert_success(result)` - Assert exit code 0
- `assert_failure(result)` - Assert non-zero exit code
- `assert_in_output(result, text)` - Assert text in stdout
- `assert_json_output(result)` - Parse and validate JSON
- `assert_error_message(result, text)` - Assert error in stderr
- `assert_file_exists(path)` - Assert file exists
- And many more...

### Fixtures
- `create_temp_project()` - Create temporary directory
- `create_minimal_config()` - Create basic claude.json
- `create_test_agent()` - Create test agent file
- `create_full_project(num_agents=N)` - Full project setup

### Mock Helpers
- `mock_anthropic_client()` - Mock API client
- `mock_env_vars(**vars)` - Set environment variables
- `no_api_key()` - Remove API key for testing errors

## Examples

### Test Command with JSON Output
```python
class TestListCommand(CLITestTemplate):
    def test_list_json(self):
        CLIFixtures.create_full_project(self.temp_dir, num_agents=5)

        result = self.run_cli("list", "agents", "--json")
        data = self.assert_json_output(result)
        self.assertEqual(len(data), 5)
```

### Test Error Handling
```python
class TestErrors(CLITestTemplate):
    def test_missing_config(self):
        result = self.run_cli("list", "agents")
        self.assert_helpful_error(result, [
            "Configuration",
            "not found",
            "claude-force init"
        ])
```

### Test with Mocks
```python
class TestWithMocks(CLITestTemplate):
    def test_no_api_key(self):
        with CLIMockHelpers.no_api_key():
            result = self.run_cli("run", "agent", "test")
            self.assert_error_message(result, "API key")
```

## Documentation

See [docs/CLI_TESTING_FRAMEWORK.md](/docs/CLI_TESTING_FRAMEWORK.md) for:
- Complete API reference
- Usage patterns
- Best practices
- Advanced examples

## Example Tests

See `test_cli_framework_examples.py` for comprehensive examples.

## Running Tests

```bash
# Run all CLI tests
pytest tests/integration/

# Run with coverage
pytest tests/ --cov=claude_force --cov-report=html

# Run specific test
pytest tests/test_my_command.py::TestMyCommand::test_specific -v
```

## Adding New Tests

1. Create test file in `tests/`
2. Import framework: `from tests.cli_test_framework import CLITestTemplate`
3. Extend `CLITestCase` or `CLITestTemplate`
4. Use assertion helpers
5. Run with pytest

Happy testing! 🧪
