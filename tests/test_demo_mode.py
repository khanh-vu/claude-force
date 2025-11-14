"""
Tests for demo mode functionality.
"""

import unittest
import tempfile
import json
from pathlib import Path
from claude_force.demo_mode import DemoOrchestrator


class TestDemoMode(unittest.TestCase):
    """Test demo mode orchestrator."""

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
                    "domains": ["code-review", "quality"]
                },
                "test-writer": {
                    "file": "test-writer.md",
                    "priority": 2,
                    "domains": ["testing", "qa"]
                },
                "doc-writer": {
                    "file": "doc-writer.md",
                    "priority": 3,
                    "domains": ["documentation"]
                },
                "security-auditor": {
                    "file": "security-auditor.md",
                    "priority": 1,
                    "domains": ["security", "audit"]
                }
            },
            "workflows": {
                "full-review": ["code-reviewer", "test-writer"],
                "security-check": ["code-reviewer", "security-auditor"]
            }
        }

        self.config_path = self.config_dir / "claude.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

    def test_demo_orchestrator_init(self):
        """Test demo orchestrator initialization."""
        demo = DemoOrchestrator(config_path=str(self.config_path))
        self.assertIsNotNone(demo)
        self.assertEqual(demo.config, self.config)

    def test_run_agent_code_review(self):
        """Test running code review agent in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        result = demo.run_agent(
            agent_name="code-reviewer",
            task="Review this function"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.agent_name, "code-reviewer")
        self.assertIn("Code Review", result.output)
        self.assertTrue(result.metadata['demo_mode'])
        self.assertTrue(result.errors is None or len(result.errors) == 0)

    def test_run_agent_test_writer(self):
        """Test running test writer agent in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        result = demo.run_agent(
            agent_name="test-writer",
            task="Write tests for this module"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.agent_name, "test-writer")
        self.assertIn("Test Suite", result.output)
        self.assertIn("unittest", result.output)
        self.assertTrue(result.metadata['demo_mode'])

    def test_run_agent_doc_writer(self):
        """Test running doc writer agent in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        result = demo.run_agent(
            agent_name="doc-writer",
            task="Document this API"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.agent_name, "doc-writer")
        self.assertIn("API Documentation", result.output)
        self.assertTrue(result.metadata['demo_mode'])

    def test_run_agent_security_auditor(self):
        """Test running security auditor agent in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        result = demo.run_agent(
            agent_name="security-auditor",
            task="Audit this code for security issues"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.agent_name, "security-auditor")
        self.assertIn("Security", result.output)
        self.assertTrue(result.metadata['demo_mode'])

    def test_run_agent_invalid(self):
        """Test running non-existent agent raises error."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        with self.assertRaises(ValueError) as context:
            demo.run_agent(
                agent_name="nonexistent-agent",
                task="Do something"
            )

        self.assertIn("not found", str(context.exception))

    def test_run_workflow(self):
        """Test running workflow in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        results = demo.run_workflow(
            workflow_name="full-review",
            task="Review and test this code"
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].agent_name, "code-reviewer")
        self.assertEqual(results[1].agent_name, "test-writer")

        for result in results:
            self.assertTrue(result.success)
            self.assertTrue(result.metadata['demo_mode'])

    def test_run_workflow_invalid(self):
        """Test running non-existent workflow raises error."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        with self.assertRaises(ValueError) as context:
            demo.run_workflow(
                workflow_name="nonexistent-workflow",
                task="Do something"
            )

        self.assertIn("not found", str(context.exception))

    def test_list_agents(self):
        """Test listing agents in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        agents = demo.list_agents()

        self.assertEqual(len(agents), 4)
        agent_names = [a['name'] for a in agents]
        self.assertIn("code-reviewer", agent_names)
        self.assertIn("test-writer", agent_names)

    def test_list_workflows(self):
        """Test listing workflows in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        workflows = demo.list_workflows()

        self.assertEqual(len(workflows), 2)
        self.assertIn("full-review", workflows)
        self.assertIn("security-check", workflows)

    def test_get_agent_info(self):
        """Test getting agent info in demo mode."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        info = demo.get_agent_info("code-reviewer")

        self.assertEqual(info['name'], "code-reviewer")
        self.assertEqual(info['priority'], 1)
        self.assertEqual(info['domains'], ["code-review", "quality"])

    def test_get_agent_info_invalid(self):
        """Test getting info for non-existent agent raises error."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        with self.assertRaises(ValueError) as context:
            demo.get_agent_info("nonexistent-agent")

        self.assertIn("not found", str(context.exception))

    def test_demo_metadata(self):
        """Test demo mode metadata is included in results."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        result = demo.run_agent(
            agent_name="code-reviewer",
            task="Review this code",
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=0.7
        )

        metadata = result.metadata
        self.assertTrue(metadata['demo_mode'])
        self.assertEqual(metadata['model'], "claude-3-5-sonnet-20241022")
        self.assertIn('simulated_tokens', metadata)
        self.assertIn('simulated_duration_ms', metadata)
        self.assertGreater(metadata['simulated_tokens'], 0)
        self.assertGreater(metadata['simulated_duration_ms'], 0)

    def test_different_task_types(self):
        """Test demo responses vary based on task content."""
        demo = DemoOrchestrator(config_path=str(self.config_path))

        result1 = demo.run_agent(
            agent_name="code-reviewer",
            task="Review authentication logic"
        )

        result2 = demo.run_agent(
            agent_name="code-reviewer",
            task="Review database queries"
        )

        # Both should be code reviews
        self.assertIn("Code Review", result1.output)
        self.assertIn("Code Review", result2.output)

        # Both should be successful
        self.assertTrue(result1.success)
        self.assertTrue(result2.success)


if __name__ == "__main__":
    unittest.main()
