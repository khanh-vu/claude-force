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
    """Test workflow composer with actual goal-based composition."""

    def test_compose_workflow_from_goal(self):
        """Test composing a workflow from a goal description."""
        composer = WorkflowComposer(include_marketplace=True)

        # Compose workflow for a backend development goal
        workflow = composer.compose_workflow(
            goal="Build a REST API with authentication and testing",
            max_agents=5,
            prefer_builtin=False,
        )

        # Verify workflow structure
        self.assertIsInstance(workflow, ComposedWorkflow)
        self.assertIsNotNone(workflow.name)
        self.assertGreater(len(workflow.steps), 0)
        self.assertLessEqual(len(workflow.steps), 5)

        # Should include relevant agents for API development
        agent_names_str = " ".join([step.agent.agent_id for step in workflow.steps]).lower()
        self.assertTrue(
            any(
                keyword in agent_names_str
                for keyword in ["backend", "api", "developer", "engineer"]
            ),
            f"Expected backend/API related agents, got: {agent_names_str}",
        )

    def test_compose_workflow_prefer_builtin(self):
        """Test workflow composition preferring builtin agents."""
        composer = WorkflowComposer(include_marketplace=False)

        workflow = composer.compose_workflow(
            goal="Review code for security issues", max_agents=3, prefer_builtin=True
        )

        self.assertIsInstance(workflow, ComposedWorkflow)
        self.assertGreater(len(workflow.steps), 0)

    def test_compose_workflow_max_agents(self):
        """Test that max_agents limit is respected."""
        composer = WorkflowComposer(include_marketplace=True)

        workflow = composer.compose_workflow(
            goal="Complete full-stack application development", max_agents=3, prefer_builtin=False
        )

        self.assertLessEqual(len(workflow.steps), 3)

    def test_compose_workflow_simple_goal(self):
        """Test workflow composition for a simple goal."""
        composer = WorkflowComposer(include_marketplace=True)

        workflow = composer.compose_workflow(goal="Review Python code", max_agents=2)

        self.assertIsInstance(workflow, ComposedWorkflow)
        self.assertGreater(len(workflow.steps), 0)


@unittest.skipIf(AgentMarketplace is None, "AgentMarketplace not available")
class TestMarketplaceIntegration(unittest.TestCase):
    """Test marketplace operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.marketplace_dir = Path(self.temp_dir) / "marketplace"
        self.marketplace_dir.mkdir()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_marketplace_init(self):
        """Test marketplace initialization."""
        marketplace = AgentMarketplace(marketplace_dir=str(self.marketplace_dir))
        self.assertIsNotNone(marketplace)

    def test_list_marketplace_agents(self):
        """Test listing agents from marketplace."""
        marketplace = AgentMarketplace(marketplace_dir=str(self.marketplace_dir))

        # Should return list (may be empty if no agents installed)
        agents = marketplace.list_agents()
        self.assertIsInstance(agents, list)

    def test_search_marketplace(self):
        """Test searching marketplace by domain."""
        marketplace = AgentMarketplace(marketplace_dir=str(self.marketplace_dir))

        # Search by domain
        results = marketplace.search(domain="backend")
        self.assertIsInstance(results, list)

    def test_agent_availability_check(self):
        """Test checking if an agent is available."""
        marketplace = AgentMarketplace(marketplace_dir=str(self.marketplace_dir))

        # Check for a common agent
        is_available = marketplace.is_agent_available("code-reviewer")
        self.assertIsInstance(is_available, bool)


@unittest.skipIf(
    WorkflowComposer is None or AgentMarketplace is None,
    "WorkflowComposer or AgentMarketplace not available",
)
class TestWorkflowMarketplaceIntegration(unittest.TestCase):
    """Test integration between workflow composer and marketplace."""

    def test_compose_with_marketplace_agents(self):
        """Test composing workflows that may include marketplace agents."""
        composer = WorkflowComposer(include_marketplace=True)

        workflow = composer.compose_workflow(
            goal="Deploy infrastructure and monitor performance", max_agents=4
        )

        self.assertIsInstance(workflow, ComposedWorkflow)
        self.assertGreater(len(workflow.steps), 0)

    def test_compose_without_marketplace(self):
        """Test composing workflows excluding marketplace."""
        composer = WorkflowComposer(include_marketplace=False)

        workflow = composer.compose_workflow(goal="Review and test code", max_agents=3)

        self.assertIsInstance(workflow, ComposedWorkflow)
        self.assertGreater(len(workflow.steps), 0)


if __name__ == "__main__":
    unittest.main()
