"""
Tests for quiet mode and JSON output format in CLI commands.

This module tests the --quiet and --format flags added for CI/CD integration.
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace
from io import StringIO
import sys

from claude_force.cli import cmd_list_agents, cmd_list_workflows, cmd_run_agent


class TestQuietMode(unittest.TestCase):
    """Test quiet mode functionality."""

    @patch("claude_force.cli.AgentOrchestrator")
    @patch("sys.stdout", new_callable=StringIO)
    def test_list_agents_quiet_mode(self, mock_stdout, mock_orch_class):
        """Test list agents with --quiet flag produces no output."""
        # Setup mock
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch
        mock_orch.list_agents.return_value = [
            {"name": "test-agent", "priority": 1, "domains": ["test"]}
        ]

        # Create args with quiet=True
        args = Namespace(config=None, demo=False, quiet=True, format="text", json=False)

        # Execute
        cmd_list_agents(args)

        # Verify no output
        output = mock_stdout.getvalue()
        self.assertEqual(output, "", "Quiet mode should produce no output")

    @patch("claude_force.cli.AgentOrchestrator")
    @patch("sys.stdout", new_callable=StringIO)
    def test_list_workflows_quiet_mode(self, mock_stdout, mock_orch_class):
        """Test list workflows with --quiet flag produces no output."""
        # Setup mock
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch
        mock_orch.list_workflows.return_value = {"test-workflow": ["agent1", "agent2"]}

        # Create args with quiet=True
        args = Namespace(config=None, demo=False, quiet=True, format="text", json=False)

        # Execute
        cmd_list_workflows(args)

        # Verify no output
        output = mock_stdout.getvalue()
        self.assertEqual(output, "", "Quiet mode should produce no output")


class TestJSONFormat(unittest.TestCase):
    """Test JSON output format."""

    @patch("claude_force.cli.AgentOrchestrator")
    @patch("sys.stdout", new_callable=StringIO)
    def test_list_agents_json_format(self, mock_stdout, mock_orch_class):
        """Test list agents with --format json produces valid JSON."""
        # Setup mock
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch
        expected_agents = [{"name": "test-agent", "priority": 1, "domains": ["test", "domain"]}]
        mock_orch.list_agents.return_value = expected_agents

        # Create args with format=json
        args = Namespace(config=None, demo=False, quiet=False, format="json", json=False)

        # Execute
        cmd_list_agents(args)

        # Verify JSON output
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        self.assertEqual(parsed, expected_agents)

    @patch("claude_force.cli.AgentOrchestrator")
    @patch("sys.stdout", new_callable=StringIO)
    def test_list_workflows_json_format(self, mock_stdout, mock_orch_class):
        """Test list workflows with --format json produces valid JSON."""
        # Setup mock
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch
        workflows = {"test-workflow": ["agent1", "agent2"]}
        mock_orch.list_workflows.return_value = workflows

        # Create args with format=json
        args = Namespace(config=None, demo=False, quiet=False, format="json", json=False)

        # Execute
        cmd_list_workflows(args)

        # Verify JSON output
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["name"], "test-workflow")
        self.assertEqual(parsed[0]["agents"], ["agent1", "agent2"])

    @patch("sys.stdin.isatty", return_value=True)
    @patch("claude_force.cli.AgentOrchestrator")
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_agent_json_format_success(self, mock_stdout, mock_orch_class, mock_isatty):
        """Test run agent with --format json on success."""
        # Setup mock
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch

        mock_result = Mock()
        mock_result.success = True
        mock_result.output = "Test output"
        mock_result.errors = []
        mock_result.metadata = {"tokens": 100}
        mock_orch.run_agent.return_value = mock_result

        # Create args with format=json
        args = Namespace(
            config=None,
            demo=False,
            quiet=False,
            format="json",
            json=False,
            agent="test-agent",
            task="test task",
            task_file=None,
            output=None,
            model=None,
            max_tokens=4096,
            temperature=1.0,
            auto_select_model=False,
            api_key=None,
        )

        # Execute (expect sys.exit)
        with self.assertRaises(SystemExit) as cm:
            cmd_run_agent(args)

        # Verify exit code
        self.assertEqual(cm.exception.code, 0)

        # Verify JSON output
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["agent"], "test-agent")
        self.assertEqual(parsed["output"], "Test output")
        self.assertEqual(parsed["errors"], [])

    @patch("sys.stdin.isatty", return_value=True)
    @patch("claude_force.cli.AgentOrchestrator")
    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_agent_json_format_failure(
        self, mock_stdout, mock_stderr, mock_orch_class, mock_isatty
    ):
        """Test run agent with --format json on failure."""
        # Setup mock
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch

        mock_result = Mock()
        mock_result.success = False
        mock_result.output = ""
        mock_result.errors = ["Error message"]
        mock_result.metadata = {}
        mock_orch.run_agent.return_value = mock_result

        # Create args with format=json
        args = Namespace(
            config=None,
            demo=False,
            quiet=False,
            format="json",
            json=False,
            agent="test-agent",
            task="test task",
            task_file=None,
            output=None,
            model=None,
            max_tokens=4096,
            temperature=1.0,
            auto_select_model=False,
            api_key=None,
        )

        # Execute (expect sys.exit with error code)
        with self.assertRaises(SystemExit) as cm:
            cmd_run_agent(args)

        # Verify exit code
        self.assertEqual(cm.exception.code, 1)

        # Verify JSON output
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        self.assertFalse(parsed["success"])
        self.assertEqual(parsed["errors"], ["Error message"])


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing --json flag."""

    @patch("claude_force.cli.AgentOrchestrator")
    @patch("sys.stdout", new_callable=StringIO)
    def test_json_flag_still_works(self, mock_stdout, mock_orch_class):
        """Test that old --json flag still works for list commands."""
        # Setup mock
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch
        expected_agents = [{"name": "test", "priority": 1, "domains": []}]
        mock_orch.list_agents.return_value = expected_agents

        # Create args with old json=True flag
        args = Namespace(config=None, demo=False, quiet=False, format="text", json=True)

        # Execute
        cmd_list_agents(args)

        # Verify JSON output (backward compatibility)
        output = mock_stdout.getvalue()
        parsed = json.loads(output)
        self.assertEqual(parsed, expected_agents)


class TestExitCodes(unittest.TestCase):
    """Test proper exit codes for CI/CD integration."""

    @patch("sys.stdin.isatty", return_value=True)
    @patch("claude_force.cli.AgentOrchestrator")
    def test_successful_agent_exits_zero(self, mock_orch_class, mock_isatty):
        """Test successful agent execution exits with code 0."""
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch

        mock_result = Mock()
        mock_result.success = True
        mock_result.output = "Success"
        mock_result.errors = []
        mock_result.metadata = {}
        mock_orch.run_agent.return_value = mock_result

        args = Namespace(
            config=None,
            demo=False,
            quiet=True,
            format="json",
            json=False,
            agent="test",
            task="task",
            task_file=None,
            output=None,
            model=None,
            max_tokens=4096,
            temperature=1.0,
            auto_select_model=False,
            api_key=None,
        )

        with self.assertRaises(SystemExit) as cm:
            cmd_run_agent(args)

        self.assertEqual(cm.exception.code, 0)

    @patch("sys.stdin.isatty", return_value=True)
    @patch("claude_force.cli.AgentOrchestrator")
    def test_failed_agent_exits_one(self, mock_orch_class, mock_isatty):
        """Test failed agent execution exits with code 1."""
        mock_orch = Mock()
        mock_orch_class.return_value = mock_orch

        mock_result = Mock()
        mock_result.success = False
        mock_result.output = ""
        mock_result.errors = ["Failed"]
        mock_result.metadata = {}
        mock_orch.run_agent.return_value = mock_result

        args = Namespace(
            config=None,
            demo=False,
            quiet=True,
            format="json",
            json=False,
            agent="test",
            task="task",
            task_file=None,
            output=None,
            model=None,
            max_tokens=4096,
            temperature=1.0,
            auto_select_model=False,
            api_key=None,
        )

        with self.assertRaises(SystemExit) as cm:
            cmd_run_agent(args)

        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
