"""
Tests for error helpers and improved error messages.
"""

import unittest
from claude_force.error_helpers import (
    suggest_agents,
    format_agent_not_found_error,
    format_workflow_not_found_error,
    format_api_key_error,
    format_config_not_found_error,
    format_tracking_not_enabled_error,
    format_missing_dependency_error,
)


class TestErrorHelpers(unittest.TestCase):
    """Test error helper functions."""

    def test_suggest_agents_exact_match(self):
        """Test fuzzy matching with close matches."""
        all_agents = [
            "code-reviewer",
            "code-writer",
            "test-writer",
            "doc-writer",
        ]

        # Test close match
        suggestions = suggest_agents("code-reviwer", all_agents)  # typo
        self.assertIn("code-reviewer", suggestions)

        # Test another typo
        suggestions = suggest_agents("test-writter", all_agents)  # typo
        self.assertIn("test-writer", suggestions)

    def test_suggest_agents_no_match(self):
        """Test fuzzy matching with no close matches."""
        all_agents = ["code-reviewer", "test-writer"]

        suggestions = suggest_agents("completely-different", all_agents)
        self.assertEqual(len(suggestions), 0)

    def test_format_agent_not_found_with_suggestions(self):
        """Test agent not found error with suggestions."""
        all_agents = ["code-reviewer", "code-writer", "test-writer"]

        error_msg = format_agent_not_found_error("code-reviwer", all_agents)

        self.assertIn("code-reviwer", error_msg)
        self.assertIn("not found", error_msg)
        self.assertIn("Did you mean?", error_msg)
        self.assertIn("code-reviewer", error_msg)

    def test_format_agent_not_found_without_suggestions(self):
        """Test agent not found error without close matches."""
        all_agents = ["code-reviewer", "test-writer"]

        error_msg = format_agent_not_found_error("xyz", all_agents)

        self.assertIn("xyz", error_msg)
        self.assertIn("not found", error_msg)
        self.assertIn("Available agents:", error_msg)
        self.assertNotIn("Did you mean?", error_msg)

    def test_format_workflow_not_found_with_suggestions(self):
        """Test workflow not found error with suggestions."""
        all_workflows = ["full-stack", "backend-only", "frontend-only"]

        error_msg = format_workflow_not_found_error("full-stck", all_workflows)

        self.assertIn("full-stck", error_msg)
        self.assertIn("not found", error_msg)
        self.assertIn("Did you mean?", error_msg)
        self.assertIn("full-stack", error_msg)

    def test_format_api_key_error(self):
        """Test API key error message."""
        error_msg = format_api_key_error()

        self.assertIn("API key", error_msg)
        self.assertIn("ANTHROPIC_API_KEY", error_msg)
        self.assertIn("export", error_msg)  # Linux/Mac instructions
        self.assertIn("https://console.anthropic.com", error_msg)

    def test_format_config_not_found_error(self):
        """Test config not found error message."""
        config_path = ".claude/claude.json"
        error_msg = format_config_not_found_error(config_path)

        self.assertIn(config_path, error_msg)
        self.assertIn("claude-force init", error_msg)
        self.assertIn("not found", error_msg)

    def test_format_tracking_not_enabled_error(self):
        """Test tracking not enabled error message."""
        error_msg = format_tracking_not_enabled_error()

        self.assertIn("Performance tracking", error_msg)
        self.assertIn("enable_tracking=True", error_msg)
        self.assertIn("not enabled", error_msg)

    def test_format_missing_dependency_error(self):
        """Test missing dependency error message."""
        error_msg = format_missing_dependency_error(
            "anthropic",
            "pip install anthropic"
        )

        self.assertIn("anthropic", error_msg)
        self.assertIn("pip install anthropic", error_msg)
        self.assertIn("not found", error_msg)

    def test_suggest_agents_max_suggestions(self):
        """Test that suggest_agents respects max suggestions parameter."""
        all_agents = [
            "code-reviewer",
            "code-writer",
            "code-analyzer",
            "code-tester",
        ]

        # All start with "code-", should get at most 2 suggestions
        suggestions = suggest_agents("code", all_agents, n=2)
        self.assertLessEqual(len(suggestions), 2)

    def test_format_agent_not_found_many_agents(self):
        """Test agent not found error with many agents."""
        # Create a list of 20 agents
        all_agents = [f"agent-{i}" for i in range(20)]

        error_msg = format_agent_not_found_error("xyz", all_agents)

        # Should show first 10 agents and indicate there are more
        self.assertIn("(20 total)", error_msg)


if __name__ == "__main__":
    unittest.main()
