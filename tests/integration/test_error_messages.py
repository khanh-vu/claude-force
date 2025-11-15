"""
Integration tests for enhanced error messages.

Tests that error messages are helpful and include suggestions when appropriate.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile
import json


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestEnhancedErrorMessages(unittest.TestCase):
    """Test enhanced error messages in real scenarios."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory with test configuration
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir) / ".claude"
        self.config_dir.mkdir()

        # Create a test configuration
        self.config = {
            "agents": {
                "code-reviewer": {
                    "file": "code-reviewer.md",
                    "priority": 1,
                    "domains": ["code-review", "quality"],
                },
                "test-writer": {
                    "file": "test-writer.md",
                    "priority": 2,
                    "domains": ["testing", "qa"],
                },
                "doc-writer": {
                    "file": "doc-writer.md",
                    "priority": 3,
                    "domains": ["documentation"],
                },
            },
            "workflows": {
                "full-review": ["code-reviewer", "test-writer"],
                "quick-check": ["code-reviewer"],
            },
        }

        self.config_path = self.config_dir / "claude.json"
        with open(self.config_path, "w") as f:
            json.dump(self.config, f)

        # Create dummy agent files
        for agent_name in self.config["agents"].keys():
            agent_file = self.config_dir / f"{agent_name}.md"
            agent_file.write_text(f"# {agent_name}\n\nTest agent")

    def test_agent_not_found_with_typo(self):
        """Test agent not found error suggests correct name for typo."""
        from claude_force.orchestrator import AgentOrchestrator

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            orchestrator = AgentOrchestrator(
                config_path=str(self.config_path), enable_tracking=False
            )

            # Try to get info for misspelled agent
            with self.assertRaises(ValueError) as context:
                orchestrator.get_agent_info("code-reviwer")  # typo

            error_msg = str(context.exception)
            self.assertIn("code-reviwer", error_msg)
            self.assertIn("not found", error_msg)
            self.assertIn("Did you mean?", error_msg)
            self.assertIn("code-reviewer", error_msg)

    def test_agent_not_found_without_match(self):
        """Test agent not found error shows available agents when no match."""
        from claude_force.orchestrator import AgentOrchestrator

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            orchestrator = AgentOrchestrator(
                config_path=str(self.config_path), enable_tracking=False
            )

            # Try to get info for non-existent agent
            with self.assertRaises(ValueError) as context:
                orchestrator.get_agent_info("xyz-agent")

            error_msg = str(context.exception)
            self.assertIn("xyz-agent", error_msg)
            self.assertIn("not found", error_msg)
            self.assertIn("Available agents:", error_msg)

    def test_workflow_not_found_with_typo(self):
        """Test workflow not found error suggests correct name for typo."""
        from claude_force.orchestrator import AgentOrchestrator

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("anthropic.Client") as mock_client:
                orchestrator = AgentOrchestrator(
                    config_path=str(self.config_path), enable_tracking=False
                )

                # Try to run workflow with typo
                with self.assertRaises(ValueError) as context:
                    orchestrator.run_workflow("full-reveiw", task="test")  # typo

                error_msg = str(context.exception)
                self.assertIn("full-reveiw", error_msg)
                self.assertIn("not found", error_msg)
                self.assertIn("Did you mean?", error_msg)
                self.assertIn("full-review", error_msg)

    def test_api_key_error_message(self):
        """Test API key error provides helpful setup instructions."""
        from claude_force.orchestrator import AgentOrchestrator

        # Clear any existing API key
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as context:
                AgentOrchestrator(
                    config_path=str(self.config_path),
                    anthropic_api_key=None,
                    validate_api_key=True,  # Force validation for testing
                )

            error_msg = str(context.exception)
            self.assertIn("API key", error_msg)
            self.assertIn("ANTHROPIC_API_KEY", error_msg)
            self.assertIn("export", error_msg)
            self.assertIn("https://console.anthropic.com", error_msg)

    def test_config_not_found_error_message(self):
        """Test config not found error provides helpful setup instructions."""
        from claude_force.orchestrator import AgentOrchestrator

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with self.assertRaises(FileNotFoundError) as context:
                AgentOrchestrator(config_path="/nonexistent/claude.json")

            error_msg = str(context.exception)
            self.assertIn("not found", error_msg)
            self.assertIn("claude-force init", error_msg)

    def test_tracking_not_enabled_error_message(self):
        """Test tracking disabled error provides helpful instructions."""
        from claude_force.orchestrator import AgentOrchestrator

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            orchestrator = AgentOrchestrator(
                config_path=str(self.config_path), enable_tracking=False  # Disable tracking
            )

            # Try to get performance summary when tracking disabled
            with self.assertRaises(RuntimeError) as context:
                orchestrator.get_performance_summary()

            error_msg = str(context.exception)
            self.assertIn("Performance tracking", error_msg)
            self.assertIn("not enabled", error_msg)
            self.assertIn("enable_tracking=True", error_msg)


if __name__ == "__main__":
    unittest.main()
