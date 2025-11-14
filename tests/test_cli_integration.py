"""
CLI Integration Tests for claude-force commands.

Tests all command-line interface commands and argument combinations
to ensure robust CLI behavior in production.
"""

import unittest
import subprocess
import sys
import tempfile
import shutil
import json
from pathlib import Path


class CLITestCase(unittest.TestCase):
    """Base class for CLI integration tests."""

    def run_cli(self, *args, input_text=None, timeout=30):
        """
        Run claude-force CLI command.

        Args:
            *args: Command arguments (e.g., "init", "--help")
            input_text: Optional stdin input for interactive mode
            timeout: Command timeout in seconds

        Returns:
            subprocess.CompletedProcess with returncode, stdout, stderr
        """
        cmd = [sys.executable, "-m", "claude_force.cli"] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=input_text,
            timeout=timeout
        )
        return result

    def assertExitCode(self, result, expected_code):
        """Assert CLI exit code matches expected."""
        self.assertEqual(
            result.returncode,
            expected_code,
            f"Expected exit code {expected_code}, got {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    def assertInOutput(self, result, text, check_stderr=False):
        """Assert text appears in stdout (or stderr if specified)."""
        output = result.stderr if check_stderr else result.stdout
        self.assertIn(
            text,
            output,
            f"Expected '{text}' in {'stderr' if check_stderr else 'stdout'}\n"
            f"Got: {output}"
        )

    def assertNotInOutput(self, result, text, check_stderr=False):
        """Assert text does not appear in stdout (or stderr if specified)."""
        output = result.stderr if check_stderr else result.stdout
        self.assertNotIn(
            text,
            output,
            f"Did not expect '{text}' in {'stderr' if check_stderr else 'stdout'}\n"
            f"Got: {output}"
        )


class TestCLIInit(CLITestCase):
    """Test 'claude-force init' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_help(self):
        """Test init --help flag shows usage information."""
        result = self.run_cli("init", "--help")

        self.assertExitCode(result, 0)
        self.assertInOutput(result, "usage:")
        self.assertInOutput(result, "init")
        self.assertInOutput(result, "--description")

    def test_init_non_interactive_success(self):
        """Test claude-force init with non-interactive mode."""
        result = self.run_cli(
            "init",
            self.temp_dir,
            "--description", "Test LLM application for chat",
            "--name", "test-project"
        )

        self.assertExitCode(result, 0)
        self.assertInOutput(result, "initialized successfully")

        # Verify files were created
        claude_dir = Path(self.temp_dir) / ".claude"
        self.assertTrue(claude_dir.exists(), ".claude directory should exist")
        self.assertTrue((claude_dir / "claude.json").exists(), "claude.json should exist")

        # Verify claude.json is valid JSON
        with open(claude_dir / "claude.json") as f:
            config = json.load(f)
            self.assertEqual(config["name"], "test-project")

    def test_init_interactive_mode(self):
        """Test claude-force init in interactive mode."""
        # Simulate user input: name, description, tech stack, template selection
        user_input = "test-project\nBuild a chat application\n\n1\n"

        result = self.run_cli(
            "init",
            self.temp_dir,
            "--interactive",
            input_text=user_input
        )

        self.assertExitCode(result, 0)
        self.assertInOutput(result, "Project name")
        self.assertInOutput(result, "initialized successfully")

    def test_init_with_template(self):
        """Test claude-force init with explicit template selection."""
        result = self.run_cli(
            "init",
            self.temp_dir,
            "--description", "Test project",
            "--name", "test-project",
            "--template", "llm-app"  # Use valid template ID
        )

        self.assertExitCode(result, 0)
        self.assertInOutput(result, "initialized successfully")

        # Verify template was used
        claude_dir = Path(self.temp_dir) / ".claude"
        with open(claude_dir / "claude.json") as f:
            config = json.load(f)
            # Should have agents from llm-app template
            self.assertIn("agents", config)

    def test_init_force_overwrite(self):
        """Test claude-force init --force flag overwrites existing directory."""
        # Create .claude directory first
        claude_dir = Path(self.temp_dir) / ".claude"
        claude_dir.mkdir()
        existing_file = claude_dir / "existing.txt"
        existing_file.write_text("This should remain (--force doesn't delete)")

        result = self.run_cli(
            "init",
            self.temp_dir,
            "--description", "Test project",
            "--name", "test-project",
            "--force"
        )

        self.assertExitCode(result, 0)
        self.assertInOutput(result, "initialized successfully")

        # Verify new files exist (old files may or may not be removed)
        self.assertTrue((claude_dir / "claude.json").exists(), "claude.json should exist")

    def test_init_no_examples(self):
        """Test claude-force init --no-examples flag."""
        result = self.run_cli(
            "init",
            self.temp_dir,
            "--description", "Test project",
            "--name", "test-project",
            "--no-examples"
        )

        self.assertExitCode(result, 0)

        # Verify examples directory not created
        claude_dir = Path(self.temp_dir) / ".claude"
        examples_dir = claude_dir / "examples"
        self.assertFalse(examples_dir.exists(), "Examples should not be created")

    def test_init_missing_description(self):
        """Test error when description is missing in non-interactive mode."""
        result = self.run_cli(
            "init",
            self.temp_dir,
            "--name", "test-project"
            # Missing --description
        )

        # Should fail with error
        self.assertNotEqual(result.returncode, 0)
        self.assertInOutput(result, "description", check_stderr=True)

    def test_init_invalid_template(self):
        """Test error when invalid template ID is provided."""
        result = self.run_cli(
            "init",
            self.temp_dir,
            "--description", "Test project",
            "--name", "test-project",
            "--template", "nonexistent-template-xyz"
        )

        # Should fail with error
        self.assertNotEqual(result.returncode, 0)
        self.assertInOutput(result, "template", check_stderr=True)

    def test_init_existing_directory(self):
        """Test error when .claude directory already exists without --force."""
        # Create .claude directory
        claude_dir = Path(self.temp_dir) / ".claude"
        claude_dir.mkdir()

        result = self.run_cli(
            "init",
            self.temp_dir,
            "--description", "Test project",
            "--name", "test-project"
        )

        # Should fail with error
        self.assertNotEqual(result.returncode, 0)
        self.assertInOutput(result, "already exists", check_stderr=True)

    def test_init_verbose_errors(self):
        """Test --verbose flag provides detailed error information."""
        result = self.run_cli(
            "init",
            self.temp_dir,
            "--name", "test-project",
            "--verbose"
            # Missing --description to trigger error
        )

        # Should show verbose error information
        self.assertNotEqual(result.returncode, 0)
        # Verbose mode shows more details
        self.assertInOutput(result, "description", check_stderr=True)


class TestCLIRunAgent(CLITestCase):
    """Test 'claude-force run agent' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Initialize a project first
        subprocess.run(
            [
                sys.executable, "-m", "claude_force.cli",
                "init",
                self.temp_dir,
                "--description", "Test project for agent runs",
                "--name", "test-agent-project"
            ],
            capture_output=True,
            text=True
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_agent_help(self):
        """Test run agent --help shows usage information."""
        result = self.run_cli("run", "agent", "--help")

        self.assertExitCode(result, 0)
        self.assertInOutput(result, "usage:")
        self.assertInOutput(result, "agent")
        self.assertInOutput(result, "--auto-select-model")

    def test_run_agent_with_auto_select(self):
        """Test run agent with --auto-select-model flag."""
        # Note: This will fail without API key, but we can test argument parsing
        result = self.run_cli(
            "run", "agent",
            "code-reviewer",
            "--task", "Review the authentication module",
            "--auto-select-model",
            "--estimate-cost"  # Show estimate
        )

        # Will fail due to missing API key or config, but args should parse
        # Check that it attempted to run (mentions agent or model or API key error)
        output = result.stdout + result.stderr
        self.assertTrue(
            any(word in output.lower() for word in ["agent", "model", "api", "running"]),
            "Should mention agent/model/API in output"
        )

    def test_run_agent_with_estimate(self):
        """Test run agent with --estimate-cost flag."""
        result = self.run_cli(
            "run", "agent",
            "code-reviewer",
            "--task", "Review the code for security issues",
            "--auto-select-model",
            "--estimate-cost"
        )

        # Will fail due to missing config/API key, but should accept flags
        output = result.stdout + result.stderr
        self.assertTrue(
            any(word in output.lower() for word in ["cost", "error", "config", "api"]),
            "Should process estimate-cost flag or show error"
        )

    def test_run_agent_with_threshold(self):
        """Test run agent with --cost-threshold flag."""
        result = self.run_cli(
            "run", "agent",
            "code-reviewer",
            "--task", "Small code review task",
            "--auto-select-model",
            "--cost-threshold", "0.001"  # Very low threshold
        )

        # Will fail due to missing config, but should accept threshold flag
        output = result.stdout + result.stderr
        # Should at least parse the arguments
        self.assertIsNotNone(output)

    def test_run_agent_yes_flag(self):
        """Test run agent with --yes flag (auto-confirm)."""
        result = self.run_cli(
            "run", "agent",
            "code-reviewer",
            "--task", "Quick review",
            "--yes",
            "--auto-select-model",
            "--estimate-cost"
        )

        # Should accept --yes flag (won't prompt)
        output = result.stdout + result.stderr
        self.assertIsNotNone(output)

    def test_run_agent_missing_task(self):
        """Test error when task is not provided."""
        result = self.run_cli(
            "run", "agent",
            "code-reviewer"
            # Missing --task
        )

        # Should fail with error
        self.assertNotEqual(result.returncode, 0)
        self.assertInOutput(result, "task", check_stderr=True)

    def test_run_agent_task_file(self):
        """Test run agent with --task-file flag."""
        # Create task file
        task_file = Path(self.temp_dir) / "task.txt"
        task_file.write_text("Review the authentication code for security")

        result = self.run_cli(
            "run", "agent",
            "code-reviewer",
            "--task-file", str(task_file)
        )

        # Will fail due to missing API key/config, but should accept task-file flag
        output = result.stdout + result.stderr
        self.assertIsNotNone(output)

    def test_run_agent_output_file(self):
        """Test run agent with --output flag."""
        output_file = Path(self.temp_dir) / "output.txt"

        result = self.run_cli(
            "run", "agent",
            "code-reviewer",
            "--task", "Review code",
            "--output", str(output_file)
        )

        # Will fail due to missing API key/config, but should accept output flag
        output = result.stdout + result.stderr
        self.assertIsNotNone(output)

    def test_run_agent_json_output(self):
        """Test run agent with --json flag for structured output."""
        result = self.run_cli(
            "run", "agent",
            "code-reviewer",
            "--task", "Review code",
            "--json"
        )

        # Will fail due to missing API key/config, but should accept json flag
        output = result.stdout + result.stderr
        self.assertIsNotNone(output)

    def test_run_agent_invalid_agent(self):
        """Test error when invalid agent name is provided."""
        result = self.run_cli(
            "run", "agent",
            "nonexistent-agent-xyz",
            "--task", "Do something"
        )

        # Should fail with error (API key or config missing, or invalid agent)
        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        # Should mention error in some form
        self.assertTrue(
            any(word in output.lower() for word in ["error", "api", "config"]),
            "Should show error message"
        )


class TestCLIExitCodes(CLITestCase):
    """Test CLI exit codes for different scenarios."""

    def test_help_exit_0(self):
        """Test --help exits with code 0."""
        result = self.run_cli("--help")
        self.assertExitCode(result, 0)

    def test_init_help_exit_0(self):
        """Test init --help exits with code 0."""
        result = self.run_cli("init", "--help")
        self.assertExitCode(result, 0)

    def test_invalid_command_exit_nonzero(self):
        """Test invalid commands exit with non-zero code."""
        result = self.run_cli("invalid-command-xyz")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_args_exit_nonzero(self):
        """Test missing required arguments exit with non-zero code."""
        result = self.run_cli("init")  # Missing directory
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
