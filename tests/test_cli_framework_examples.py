"""
Example tests demonstrating the CLI testing framework.

These tests show how to use the CLI testing framework for various scenarios.
"""

import json
from pathlib import Path
from tests.cli_test_framework import (
    CLITestCase,
    CLITestTemplate,
    CLIFixtures,
    CLIMockHelpers,
    quick_cli_test
)


class TestCLIFrameworkBasics(CLITestCase):
    """Examples of basic CLI testing patterns."""

    def test_simple_command_success(self):
        """Test a simple successful command."""
        result = self.run_cli("--help")
        self.assert_success(result)
        self.assert_in_output(result, "usage:")

    def test_command_failure(self):
        """Test a command that should fail."""
        result = self.run_cli("nonexistent-command")
        self.assert_failure(result)

    def test_json_output_parsing(self):
        """Test parsing JSON output."""
        # This would be a real command that outputs JSON
        # For example: run_cli("list", "agents", "--json")
        # For this example, we'll create a mock scenario
        pass

    def test_error_messages(self):
        """Test helpful error messages."""
        result = self.run_cli("init", "/nonexistent/path")
        self.assert_error_message(result, "Error")


class TestCLIWithTemporaryProject(CLITestTemplate):
    """Examples using CLITestTemplate with automatic temp directory."""

    def test_init_command(self):
        """Test init command in temporary directory."""
        result = self.run_cli(
            "init",
            str(self.temp_dir),
            "--name", "test-project",
            "--description", "Test project"
        )

        self.assert_success(result)
        self.assert_file_exists(self.claude_dir / "claude.json")

        # Verify configuration
        config = self.assert_valid_json_file(self.claude_dir / "claude.json")
        self.assertEqual(config["name"], "test-project")

    def test_list_agents_empty(self):
        """Test listing agents in empty project."""
        # Create minimal config
        CLIFixtures.create_minimal_config(self.claude_dir)

        result = self.run_cli("list", "agents")
        self.assert_success(result)
        self.assert_in_output(result, "Total: 0 agents")


class TestCLIWithFixtures(CLITestTemplate):
    """Examples using CLIFixtures for test data."""

    def test_list_agents_with_fixtures(self):
        """Test listing agents using fixtures."""
        # Create project with 5 agents
        config = CLIFixtures.create_full_project(self.temp_dir, num_agents=5)

        result = self.run_cli("list", "agents")
        self.assert_success(result)
        self.assert_in_output(result, "Total: 5 agents")

        for i in range(1, 6):
            self.assert_in_output(result, f"test-agent-{i}")

    def test_list_agents_json_format(self):
        """Test listing agents with JSON output."""
        CLIFixtures.create_full_project(self.temp_dir, num_agents=3)

        result = self.run_cli("list", "agents", "--json")
        self.assert_success(result)

        # Parse and validate JSON
        data = self.assert_json_output(result)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

        # Check first agent structure
        agent = data[0]
        self.assertIn("name", agent)
        self.assertIn("priority", agent)
        self.assertIn("domains", agent)

    def test_agent_creation_flow(self):
        """Test complete agent creation flow."""
        CLIFixtures.create_minimal_config(self.claude_dir)

        # Create test agent
        agent_path = CLIFixtures.create_test_agent(
            self.claude_dir,
            "custom-agent",
            ["domain1", "domain2"]
        )

        self.assert_file_exists(agent_path)

        # Verify agent file content
        content = agent_path.read_text()
        self.assertIn("custom-agent", content)
        self.assertIn("domain1", content)
        self.assertIn("domain2", content)


class TestCLIWithMocks(CLITestTemplate):
    """Examples using CLIMockHelpers for isolated testing."""

    def test_command_without_api_key(self):
        """Test command behavior without API key."""
        CLIFixtures.create_full_project(self.temp_dir, num_agents=1)

        with CLIMockHelpers.no_api_key():
            result = self.run_cli("run", "agent", "test-agent-1", "--task", "test")
            # Command should fail or show API key error
            self.assert_failure(result)

    def test_command_with_env_vars(self):
        """Test command with specific environment variables."""
        CLIFixtures.create_minimal_config(self.claude_dir)

        with CLIMockHelpers.mock_env_vars(DEBUG="1", ANTHROPIC_API_KEY="test-key"):
            result = self.run_cli("list", "agents")
            # Command should succeed with test API key
            # (actual behavior depends on implementation)

    def test_command_with_mocked_client(self):
        """Test command with mocked Anthropic client."""
        CLIFixtures.create_full_project(self.temp_dir, num_agents=1)

        with CLIMockHelpers.mock_anthropic_client():
            # This would prevent actual API calls
            # result = self.run_cli("run", "agent", "test-agent-1")
            pass


class TestCLIAdvancedAssertions(CLITestTemplate):
    """Examples of advanced assertion patterns."""

    def test_output_contains_all_keywords(self):
        """Test output contains multiple keywords."""
        CLIFixtures.create_full_project(self.temp_dir, num_agents=2)

        result = self.run_cli("list", "agents")
        self.assert_success(result)

        # Check for multiple expected strings
        self.assert_output_contains_all(result, [
            "test-agent-1",
            "test-agent-2",
            "Total: 2 agents"
        ])

    def test_output_regex_matching(self):
        """Test output matches regex pattern."""
        CLIFixtures.create_minimal_config(self.claude_dir)

        result = self.run_cli("list", "agents")
        self.assert_success(result)

        # Match pattern like "Total: X agents"
        self.assert_output_matches_regex(result, r"Total: \d+ agents")

    def test_directory_structure_validation(self):
        """Test complete directory structure."""
        result = self.run_cli(
            "init",
            str(self.temp_dir),
            "--name", "test-project",
            "--description", "Test project"
        )
        self.assert_success(result)

        # Verify expected directory structure
        self.assert_directory_structure(self.temp_dir, [
            ".claude/claude.json",
            ".claude/agents"
        ])

    def test_json_value_assertions(self):
        """Test specific JSON values."""
        config = CLIFixtures.create_minimal_config(
            self.claude_dir,
            name="my-project",
            version="2.0.0"
        )

        result = self.run_cli("list", "agents", "--json")
        # In a real test, we'd parse the config or output
        # self.assert_json_value(result, "name", "my-project")


class TestCLIQuickTesting(CLITestCase):
    """Examples using quick_cli_test helper."""

    def test_quick_help_command(self):
        """Quick test of help command."""
        result = quick_cli_test("--help")
        self.assertIn("usage:", result.stdout)

    def test_quick_version_command(self):
        """Quick test of version command (if exists)."""
        # result = quick_cli_test("--version")
        # self.assertIn("claude-force", result.stdout)
        pass


class TestCLIErrorHandling(CLITestTemplate):
    """Examples of testing error scenarios."""

    def test_helpful_error_for_missing_config(self):
        """Test error message when config is missing."""
        result = self.run_cli("list", "agents")
        self.assert_helpful_error(result, [
            "Configuration",
            "not found",
            "claude-force init"
        ])

    def test_helpful_error_for_invalid_agent(self):
        """Test error message for nonexistent agent."""
        CLIFixtures.create_minimal_config(self.claude_dir)

        result = self.run_cli("info", "nonexistent-agent")
        self.assert_failure(result)
        # Error could be in stdout or stderr depending on implementation
        error_output = result.stdout + result.stderr
        self.assertIn("not found", error_output.lower())

    def test_helpful_error_for_missing_required_arg(self):
        """Test error for missing required argument."""
        result = self.run_cli("compose")  # Missing --goal
        self.assert_failure(result)
        self.assert_in_output(result, "required", check_stderr=True)


if __name__ == "__main__":
    import unittest
    unittest.main()
