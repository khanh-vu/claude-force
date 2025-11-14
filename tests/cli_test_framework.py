"""
CLI Testing Framework for claude-force

Provides comprehensive test utilities for CLI command testing including:
- Base test classes with enhanced helpers
- Fixtures for common test scenarios
- Assertion helpers for CLI-specific validations
- Mock helpers for isolated testing

Usage:
    from tests.cli_test_framework import CLITestCase, CLIFixtures

    class TestMyCommand(CLITestCase):
        def test_command(self):
            result = self.run_cli("my-command", "--option", "value")
            self.assert_success(result)
            self.assert_json_output(result)
"""

import unittest
import subprocess
import sys
import tempfile
import shutil
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from unittest.mock import patch, MagicMock
from contextlib import contextmanager


class CLITestCase(unittest.TestCase):
    """
    Enhanced base class for CLI integration tests.

    Provides comprehensive helpers for running and validating CLI commands.
    """

    def run_cli(self, *args, input_text: Optional[str] = None,
                timeout: int = 30, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        """
        Run claude-force CLI command.

        Args:
            *args: Command arguments (e.g., "init", "--help")
            input_text: Optional stdin input for interactive mode
            timeout: Command timeout in seconds
            env: Optional environment variables to set/override

        Returns:
            subprocess.CompletedProcess with returncode, stdout, stderr

        Example:
            result = self.run_cli("list", "agents", "--json")
            result = self.run_cli("init", input_text="myproject\\n", env={"DEBUG": "1"})
        """
        cmd = [sys.executable, "-m", "claude_force"] + list(args)

        # Merge environment variables
        test_env = os.environ.copy()
        if env:
            test_env.update(env)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=input_text,
            timeout=timeout,
            env=test_env
        )
        return result

    # Exit Code Assertions

    def assert_success(self, result: subprocess.CompletedProcess, msg: Optional[str] = None):
        """Assert CLI command succeeded (exit code 0)."""
        self.assertEqual(
            result.returncode,
            0,
            msg or f"Expected success (exit code 0), got {result.returncode}\n"
                   f"STDOUT: {result.stdout}\n"
                   f"STDERR: {result.stderr}"
        )

    def assert_failure(self, result: subprocess.CompletedProcess, msg: Optional[str] = None):
        """Assert CLI command failed (non-zero exit code)."""
        self.assertNotEqual(
            result.returncode,
            0,
            msg or f"Expected failure (non-zero exit code), got {result.returncode}\n"
                   f"STDOUT: {result.stdout}"
        )

    def assert_exit_code(self, result: subprocess.CompletedProcess, expected_code: int,
                        msg: Optional[str] = None):
        """Assert CLI exit code matches expected value."""
        self.assertEqual(
            result.returncode,
            expected_code,
            msg or f"Expected exit code {expected_code}, got {result.returncode}\n"
                   f"STDOUT: {result.stdout}\n"
                   f"STDERR: {result.stderr}"
        )

    # Output Assertions

    def assert_in_output(self, result: subprocess.CompletedProcess, text: str,
                        check_stderr: bool = False, msg: Optional[str] = None):
        """Assert text appears in stdout (or stderr if specified)."""
        output = result.stderr if check_stderr else result.stdout
        self.assertIn(
            text,
            output,
            msg or f"Expected '{text}' in {'stderr' if check_stderr else 'stdout'}\n"
                   f"Got: {output}"
        )

    def assert_not_in_output(self, result: subprocess.CompletedProcess, text: str,
                            check_stderr: bool = False, msg: Optional[str] = None):
        """Assert text does not appear in stdout (or stderr if specified)."""
        output = result.stderr if check_stderr else result.stdout
        self.assertNotIn(
            text,
            output,
            msg or f"Did not expect '{text}' in {'stderr' if check_stderr else 'stdout'}\n"
                   f"Got: {output}"
        )

    def assert_output_contains_all(self, result: subprocess.CompletedProcess,
                                   texts: List[str], check_stderr: bool = False):
        """Assert all texts appear in output."""
        output = result.stderr if check_stderr else result.stdout
        for text in texts:
            self.assertIn(
                text,
                output,
                f"Expected '{text}' in {'stderr' if check_stderr else 'stdout'}\n"
                f"Got: {output}"
            )

    def assert_output_matches_regex(self, result: subprocess.CompletedProcess,
                                   pattern: str, check_stderr: bool = False):
        """Assert output matches regex pattern."""
        import re
        output = result.stderr if check_stderr else result.stdout
        self.assertRegex(
            output,
            pattern,
            f"Output did not match pattern '{pattern}'\n"
            f"Got: {output}"
        )

    # JSON Output Assertions

    def assert_json_output(self, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """
        Assert output is valid JSON and return parsed data.

        Returns:
            Parsed JSON data
        """
        try:
            data = json.loads(result.stdout)
            return data
        except json.JSONDecodeError as e:
            self.fail(
                f"Expected valid JSON output, got JSONDecodeError: {e}\n"
                f"Output: {result.stdout}"
            )

    def assert_json_has_keys(self, result: subprocess.CompletedProcess, keys: List[str]):
        """Assert JSON output contains expected keys."""
        data = self.assert_json_output(result)
        for key in keys:
            self.assertIn(
                key,
                data,
                f"Expected key '{key}' in JSON output\n"
                f"Got: {json.dumps(data, indent=2)}"
            )

    def assert_json_value(self, result: subprocess.CompletedProcess,
                         key: str, expected_value: Any):
        """Assert specific JSON key has expected value."""
        data = self.assert_json_output(result)
        self.assertEqual(
            data.get(key),
            expected_value,
            f"Expected {key}={expected_value}, got {key}={data.get(key)}\n"
            f"Full output: {json.dumps(data, indent=2)}"
        )

    # Error Message Assertions

    def assert_error_message(self, result: subprocess.CompletedProcess, error_text: str):
        """Assert error message appears in stderr."""
        self.assert_failure(result)
        self.assert_in_output(result, error_text, check_stderr=True)

    def assert_helpful_error(self, result: subprocess.CompletedProcess,
                            error_keywords: List[str]):
        """Assert error message contains helpful keywords."""
        self.assert_failure(result)
        self.assert_output_contains_all(result, error_keywords, check_stderr=True)

    # File System Assertions

    def assert_file_exists(self, filepath: Path, msg: Optional[str] = None):
        """Assert file exists."""
        self.assertTrue(
            filepath.exists(),
            msg or f"Expected file to exist: {filepath}"
        )

    def assert_file_not_exists(self, filepath: Path, msg: Optional[str] = None):
        """Assert file does not exist."""
        self.assertFalse(
            filepath.exists(),
            msg or f"Expected file to not exist: {filepath}"
        )

    def assert_directory_structure(self, base_dir: Path, expected_paths: List[str]):
        """Assert expected directory structure exists."""
        for path in expected_paths:
            full_path = base_dir / path
            self.assert_file_exists(
                full_path,
                f"Expected path in directory structure: {path}"
            )

    def assert_valid_json_file(self, filepath: Path) -> Dict[str, Any]:
        """Assert file exists and contains valid JSON. Returns parsed data."""
        self.assert_file_exists(filepath)
        try:
            with open(filepath) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.fail(f"File {filepath} contains invalid JSON: {e}")


class CLIFixtures:
    """
    Reusable test fixtures for CLI testing.

    Provides common test data, configurations, and setup patterns.
    """

    @staticmethod
    def create_temp_project(project_name: str = "test-project") -> Path:
        """
        Create a temporary project directory.

        Returns:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp())
        return temp_dir

    @staticmethod
    def create_minimal_config(claude_dir: Path, **kwargs) -> Dict[str, Any]:
        """
        Create minimal valid claude.json config.

        Args:
            claude_dir: Path to .claude directory
            **kwargs: Additional config fields to override

        Returns:
            Config dictionary
        """
        config = {
            "name": kwargs.get("name", "test-project"),
            "version": kwargs.get("version", "1.0.0"),
            "agents": kwargs.get("agents", {}),
            "workflows": kwargs.get("workflows", {})
        }

        claude_dir.mkdir(parents=True, exist_ok=True)
        config_path = claude_dir / "claude.json"

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        return config

    @staticmethod
    def create_test_agent(claude_dir: Path, agent_name: str,
                         domains: Optional[List[str]] = None) -> Path:
        """
        Create a test agent file.

        Args:
            claude_dir: Path to .claude directory
            agent_name: Name of agent
            domains: Optional list of domains

        Returns:
            Path to created agent file
        """
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        agent_file = agents_dir / f"{agent_name}.md"
        agent_content = f"""# {agent_name.replace('-', ' ').title()}

## Role
Test agent for {agent_name}

## Domain Expertise
{chr(10).join(f'- {d}' for d in (domains or ['testing']))}

## Skills & Specializations
- Test skill 1
- Test skill 2
"""
        agent_file.write_text(agent_content)
        return agent_file

    @staticmethod
    def create_full_project(temp_dir: Path, num_agents: int = 3) -> Dict[str, Any]:
        """
        Create a full test project with agents and workflows.

        Args:
            temp_dir: Base directory for project
            num_agents: Number of test agents to create

        Returns:
            Project configuration dictionary
        """
        claude_dir = temp_dir / ".claude"
        claude_dir.mkdir()

        # Create agents
        agents_config = {}
        agent_names = []
        for i in range(num_agents):
            agent_name = f"test-agent-{i+1}"
            agent_names.append(agent_name)
            CLIFixtures.create_test_agent(claude_dir, agent_name, [f"domain-{i+1}"])
            agents_config[agent_name] = {
                "file": f"agents/{agent_name}.md",
                "domains": [f"domain-{i+1}"],
                "priority": i + 1
            }

        # Create config
        config = CLIFixtures.create_minimal_config(
            claude_dir,
            agents=agents_config,
            workflows={"test-workflow": agent_names}
        )

        return config


class CLIMockHelpers:
    """
    Mock helpers for isolated CLI testing.

    Provides context managers and utilities for mocking external dependencies.
    """

    @staticmethod
    @contextmanager
    def mock_anthropic_client(return_value: Optional[Any] = None):
        """
        Mock Anthropic client to avoid actual API calls.

        Usage:
            with CLIMockHelpers.mock_anthropic_client():
                result = self.run_cli("run", "agent", "test-agent", "--task", "test")
        """
        mock_client = MagicMock()
        if return_value:
            mock_client.return_value = return_value

        with patch('anthropic.Client', return_value=mock_client):
            yield mock_client

    @staticmethod
    @contextmanager
    def mock_env_vars(**env_vars):
        """
        Temporarily set environment variables.

        Usage:
            with CLIMockHelpers.mock_env_vars(ANTHROPIC_API_KEY="test-key"):
                result = self.run_cli("list", "agents")
        """
        with patch.dict(os.environ, env_vars, clear=False):
            yield

    @staticmethod
    @contextmanager
    def no_api_key():
        """
        Remove API key from environment for testing error messages.

        Usage:
            with CLIMockHelpers.no_api_key():
                result = self.run_cli("run", "agent", "test")
                self.assert_error_message(result, "API key")
        """
        with patch.dict(os.environ, {}, clear=True):
            yield


class CLITestTemplate(CLITestCase):
    """
    Template test class with common setup/teardown.

    Extend this class for tests that need a temporary project directory.

    Example:
        class TestMyCommand(CLITestTemplate):
            def test_command(self):
                # self.temp_dir and self.claude_dir are available
                result = self.run_cli("my-command")
                self.assert_success(result)
    """

    def setUp(self):
        """Set up temporary project directory."""
        self.temp_dir = CLIFixtures.create_temp_project()
        self.claude_dir = self.temp_dir / ".claude"
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# Convenience functions for quick testing

def quick_cli_test(command: str, *args, expected_exit_code: int = 0) -> subprocess.CompletedProcess:
    """
    Quick CLI command test without full test class setup.

    Args:
        command: CLI command to run
        *args: Additional arguments
        expected_exit_code: Expected exit code (default: 0)

    Returns:
        subprocess.CompletedProcess

    Example:
        result = quick_cli_test("list", "agents", "--json")
        data = json.loads(result.stdout)
    """
    test = CLITestCase()
    result = test.run_cli(command, *args)
    test.assert_exit_code(result, expected_exit_code)
    return result
