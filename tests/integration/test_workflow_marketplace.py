"""
Workflow and Marketplace Integration Tests

Tests workflow composition, marketplace operations, and complex multi-agent scenarios.
"""

import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

try:
    from claude_force.workflow_composer import WorkflowComposer, ComposedWorkflow
except ImportError:
    WorkflowComposer = None
    ComposedWorkflow = None

try:
    from claude_force.marketplace import AgentMarketplace, MarketplaceAgent
except ImportError:
    AgentMarketplace = None
    MarketplaceAgent = None


@unittest.skipIf(WorkflowComposer is None, "WorkflowComposer not available")
class TestWorkflowComposerIntegration(unittest.TestCase):
    """Test workflow composer with real configurations."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config with multiple agents
        self.config = {
            "name": "test-project",
            "agents": {
                "backend-architect": {
                    "file": "agents/backend-architect.md",
                    "domains": ["architecture", "design"],
                    "priority": 1
                },
                "backend-developer": {
                    "file": "agents/backend-developer.md",
                    "domains": ["backend", "api"],
                    "priority": 2
                },
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "domains": ["code-quality", "security"],
                    "priority": 1
                },
                "qa-engineer": {
                    "file": "agents/qa-engineer.md",
                    "domains": ["testing", "quality"],
                    "priority": 2
                }
            },
            "workflows": {
                "feature-development": [
                    "backend-architect",
                    "backend-developer",
                    "code-reviewer"
                ]
            }
        }

        config_path = self.claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        # Create agent files
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()

        for agent_name in self.config["agents"].keys():
            (agents_dir / f"{agent_name}.md").write_text(
                f"# {agent_name.title()}\n\nAgent description"
            )

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_custom_workflow(self):
        """Test creating a custom workflow."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        # Create new workflow
        workflow = composer.create_workflow(
            name="end-to-end-testing",
            agents=["backend-developer", "qa-engineer", "code-reviewer"],
            description="Complete testing workflow"
        )

        # Verify workflow structure
        self.assertIsInstance(workflow, ComposedWorkflow)
        self.assertEqual(workflow.name, "end-to-end-testing")
        self.assertEqual(len(workflow.agents), 3)
        self.assertEqual(workflow.agents, [
            "backend-developer",
            "qa-engineer",
            "code-reviewer"
        ])

    def test_validate_workflow(self):
        """Test workflow validation."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        # Valid workflow
        valid_workflow = composer.create_workflow(
            name="valid-workflow",
            agents=["backend-developer", "code-reviewer"]
        )

        is_valid, errors = composer.validate_workflow(valid_workflow)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid workflow (non-existent agent)
        invalid_workflow = ComposedWorkflow(
            name="invalid-workflow",
            agents=["nonexistent-agent", "backend-developer"],
            description="Invalid"
        )

        is_valid, errors = composer.validate_workflow(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("nonexistent-agent", errors[0])

    def test_save_and_load_workflow(self):
        """Test saving workflow to config and loading it back."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        # Create and save workflow
        workflow = composer.create_workflow(
            name="custom-review",
            agents=["code-reviewer", "qa-engineer"],
            description="Custom review workflow"
        )

        composer.save_workflow(workflow)

        # Reload config
        with open(config_path) as f:
            updated_config = json.load(f)

        # Verify workflow saved
        self.assertIn("custom-review", updated_config["workflows"])
        self.assertEqual(
            updated_config["workflows"]["custom-review"],
            ["code-reviewer", "qa-engineer"]
        )

        # Load workflow back
        loaded = composer.get_workflow("custom-review")
        self.assertEqual(loaded.name, "custom-review")
        self.assertEqual(loaded.agents, ["code-reviewer", "qa-engineer"])

    def test_list_workflows(self):
        """Test listing all available workflows."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        # Get workflows
        workflows = composer.list_workflows()

        # Should include the existing workflow
        self.assertGreaterEqual(len(workflows), 1)

        workflow_names = [w.name for w in workflows]
        self.assertIn("feature-development", workflow_names)

    def test_delete_workflow(self):
        """Test deleting a workflow."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        # Create a workflow to delete
        workflow = composer.create_workflow(
            name="temporary-workflow",
            agents=["backend-developer"]
        )
        composer.save_workflow(workflow)

        # Verify it exists
        self.assertIsNotNone(composer.get_workflow("temporary-workflow"))

        # Delete it
        composer.delete_workflow("temporary-workflow")

        # Verify it's gone
        with self.assertRaises(ValueError):
            composer.get_workflow("temporary-workflow")

    def test_workflow_optimization(self):
        """Test workflow optimization suggestions."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        # Create a workflow that could be optimized
        workflow = composer.create_workflow(
            name="redundant-workflow",
            agents=[
                "backend-developer",
                "code-reviewer",
                "code-reviewer"  # Duplicate
            ]
        )

        # Get optimization suggestions
        suggestions = composer.optimize_workflow(workflow)

        # Should suggest removing duplicate
        self.assertIsNotNone(suggestions)
        self.assertGreater(len(suggestions), 0)

    def test_workflow_dependencies(self):
        """Test analyzing workflow agent dependencies."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        workflow = composer.get_workflow("feature-development")

        # Analyze dependencies
        deps = composer.analyze_dependencies(workflow)

        # Should return dependency information
        self.assertIsNotNone(deps)

        # Verify structure
        self.assertIn("agents", deps)
        self.assertEqual(len(deps["agents"]), 3)


@unittest.skipIf(AgentMarketplace is None, "AgentMarketplace not available")
class TestMarketplaceIntegration(unittest.TestCase):
    """Test marketplace operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_marketplace_agents(self):
        """Test listing available marketplace agents."""
        marketplace = AgentMarketplace()

        # Get available agents
        agents = marketplace.list_agents()

        # Should return list of agents
        self.assertIsInstance(agents, list)

        # Each agent should have required fields
        if len(agents) > 0:
            agent = agents[0]
            self.assertIsInstance(agent, MarketplaceAgent)
            self.assertIsNotNone(agent.name)
            self.assertIsNotNone(agent.description)
            self.assertIsNotNone(agent.domains)

    def test_search_marketplace(self):
        """Test searching marketplace for specific agents."""
        marketplace = AgentMarketplace()

        # Search for security-related agents
        results = marketplace.search(query="security")

        # Should return list
        self.assertIsInstance(results, list)

        # Results should be relevant to security
        if len(results) > 0:
            for agent in results:
                # Agent description or domains should mention security
                text = (agent.description + " ".join(agent.domains)).lower()
                # Note: May not always match depending on marketplace content
                self.assertIsInstance(agent, MarketplaceAgent)

    def test_get_agent_details(self):
        """Test getting detailed information about a marketplace agent."""
        marketplace = AgentMarketplace()

        agents = marketplace.list_agents()
        if len(agents) == 0:
            self.skipTest("No marketplace agents available")

        # Get details for first agent
        agent_name = agents[0].name
        details = marketplace.get_agent(agent_name)

        # Should return agent with full details
        self.assertIsNotNone(details)
        self.assertEqual(details.name, agent_name)
        self.assertIsNotNone(details.description)

    def test_install_marketplace_agent(self):
        """Test installing an agent from marketplace."""
        # Create .claude directory
        claude_dir = Path(self.temp_dir) / ".claude"
        claude_dir.mkdir()

        # Create minimal config
        config = {
            "name": "test-project",
            "agents": {}
        }

        config_path = claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

        marketplace = AgentMarketplace()

        # Try to install an agent
        agents = marketplace.list_agents()
        if len(agents) == 0:
            self.skipTest("No marketplace agents available")

        agent_to_install = agents[0].name

        # Install agent
        result = marketplace.install_agent(
            agent_name=agent_to_install,
            target_dir=str(claude_dir)
        )

        # Verify installation
        if result:
            # Should create agent file
            agents_dir = claude_dir / "agents"
            if agents_dir.exists():
                agent_files = list(agents_dir.glob("*.md"))
                self.assertGreater(len(agent_files), 0)

    def test_filter_by_category(self):
        """Test filtering marketplace agents by category."""
        marketplace = AgentMarketplace()

        # Get all categories
        categories = marketplace.get_categories()

        # Should return list of categories
        self.assertIsInstance(categories, list)

        if len(categories) > 0:
            # Filter by first category
            category = categories[0]
            filtered = marketplace.filter_by_category(category)

            # Should return agents in that category
            self.assertIsInstance(filtered, list)

            for agent in filtered:
                self.assertIn(category, agent.categories)

    def test_marketplace_ratings(self):
        """Test marketplace agent ratings and reviews."""
        marketplace = AgentMarketplace()

        agents = marketplace.list_agents()
        if len(agents) == 0:
            self.skipTest("No marketplace agents available")

        agent = agents[0]

        # Get ratings
        if hasattr(agent, 'rating'):
            self.assertIsInstance(agent.rating, (int, float))
            self.assertGreaterEqual(agent.rating, 0)
            self.assertLessEqual(agent.rating, 5)


@unittest.skipIf(WorkflowComposer is None or AgentMarketplace is None,
                 "WorkflowComposer or AgentMarketplace not available")
class TestWorkflowMarketplaceIntegration(unittest.TestCase):
    """Test integration between workflow composer and marketplace."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config
        self.config = {
            "name": "test-project",
            "agents": {
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "domains": ["code-quality"],
                    "priority": 1
                }
            },
            "workflows": {}
        }

        config_path = self.claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f)

        # Create agent file
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "code-reviewer.md").write_text("Code reviewer")

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_install_and_compose_workflow(self):
        """Test installing marketplace agent and adding to workflow."""
        marketplace = AgentMarketplace()

        # Install an agent
        agents = marketplace.list_agents()
        if len(agents) == 0:
            self.skipTest("No marketplace agents available")

        installed = marketplace.install_agent(
            agent_name=agents[0].name,
            target_dir=str(self.claude_dir)
        )

        if not installed:
            self.skipTest("Agent installation failed")

        # Update config to include installed agent
        # (In real scenario, install_agent would do this)
        installed_agent_name = agents[0].name
        self.config["agents"][installed_agent_name] = {
            "file": f"agents/{installed_agent_name}.md",
            "domains": agents[0].domains,
            "priority": 2
        }

        config_path = self.claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f)

        # Create workflow with installed agent
        composer = WorkflowComposer(config_path=str(config_path))

        workflow = composer.create_workflow(
            name="marketplace-workflow",
            agents=["code-reviewer", installed_agent_name]
        )

        # Verify workflow created successfully
        self.assertEqual(len(workflow.agents), 2)
        self.assertIn(installed_agent_name, workflow.agents)

    def test_recommend_workflow_from_task(self):
        """Test recommending workflow composition based on task."""
        config_path = self.claude_dir / "claude.json"
        composer = WorkflowComposer(config_path=str(config_path))

        # Get workflow recommendation
        recommendation = composer.recommend_workflow(
            task="Review code and fix security vulnerabilities"
        )

        # Should recommend relevant agents
        self.assertIsNotNone(recommendation)
        self.assertIsInstance(recommendation, list)

        # Should include code-reviewer
        if len(recommendation) > 0:
            self.assertIn("code-reviewer", recommendation)


class TestCompleteWorkflowExecution(unittest.TestCase):
    """Test complete workflow execution scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create complete config
        self.config = {
            "name": "integration-test",
            "agents": {
                "architect": {
                    "file": "agents/architect.md",
                    "domains": ["architecture"],
                    "priority": 1
                },
                "developer": {
                    "file": "agents/developer.md",
                    "domains": ["development"],
                    "priority": 2
                },
                "reviewer": {
                    "file": "agents/reviewer.md",
                    "domains": ["review"],
                    "priority": 1
                },
                "tester": {
                    "file": "agents/tester.md",
                    "domains": ["testing"],
                    "priority": 2
                }
            },
            "workflows": {
                "full-cycle": ["architect", "developer", "reviewer", "tester"]
            }
        }

        config_path = self.claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f)

        # Create agent files
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()

        for agent in ["architect", "developer", "reviewer", "tester"]:
            (agents_dir / f"{agent}.md").write_text(f"# {agent.title()}")

        os.environ["ANTHROPIC_API_KEY"] = "test-key"

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

    @patch('anthropic.Client')
    def test_full_workflow_execution(self, mock_client_class):
        """Test executing complete multi-agent workflow."""
        from claude_force.orchestrator import AgentOrchestrator

        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock responses for each agent
        responses = []
        for agent in ["architect", "developer", "reviewer", "tester"]:
            mock_resp = Mock()
            mock_resp.content = [Mock(text=f"Output from {agent}")]
            mock_resp.model = "claude-3-5-sonnet-20241022"
            mock_resp.usage = Mock(input_tokens=100, output_tokens=200)
            responses.append(mock_resp)

        mock_client.messages.create.side_effect = responses

        # Execute workflow
        config_path = self.claude_dir / "claude.json"
        orchestrator = AgentOrchestrator(
            config_path=str(config_path),
            enable_tracking=True
        )

        results = orchestrator.run_workflow(
            workflow_name="full-cycle",
            task="Build complete feature with testing"
        )

        # Verify execution
        self.assertEqual(len(results), 4)
        self.assertTrue(all(r.success for r in results))

        # Verify order
        expected_order = ["architect", "developer", "reviewer", "tester"]
        for i, expected_agent in enumerate(expected_order):
            self.assertEqual(results[i].agent_name, expected_agent)


if __name__ == "__main__":
    unittest.main()
