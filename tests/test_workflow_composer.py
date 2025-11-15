"""
Smart Workflow Composer Tests for claude-force.

Tests intelligent workflow composition and agent selection.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from claude_force.workflow_composer import (
    WorkflowComposer,
    WorkflowStep,
    ComposedWorkflow,
    get_workflow_composer,
)
from claude_force.agent_router import AgentMatch


class TestWorkflowStep(unittest.TestCase):
    """Test WorkflowStep dataclass."""

    def test_step_creation(self):
        """WorkflowStep should be creatable."""
        agent = AgentMatch(
            agent_id="test-agent",
            agent_name="Test Agent",
            confidence=0.9,
            source="builtin",
            installed=True,
        )

        step = WorkflowStep(
            step_number=1, step_type="architecture", agent=agent, description="Design system"
        )

        self.assertEqual(step.step_number, 1)
        self.assertEqual(step.step_type, "architecture")
        self.assertEqual(step.agent.agent_id, "test-agent")
        self.assertEqual(step.description, "Design system")
        self.assertEqual(step.estimated_duration_min, 15)
        self.assertEqual(step.estimated_cost, 0.50)


class TestComposedWorkflow(unittest.TestCase):
    """Test ComposedWorkflow dataclass."""

    def test_workflow_creation(self):
        """ComposedWorkflow should be creatable."""
        agent = AgentMatch(
            agent_id="test-agent",
            agent_name="Test Agent",
            confidence=0.9,
            source="builtin",
            installed=True,
        )

        step = WorkflowStep(
            step_number=1, step_type="architecture", agent=agent, description="Design"
        )

        workflow = ComposedWorkflow(
            name="test-workflow",
            description="Test workflow",
            goal="Test goal",
            steps=[step],
            total_estimated_duration_min=15,
            total_estimated_cost=0.50,
            agents_count=1,
            builtin_count=1,
            marketplace_count=0,
            requires_installation=False,
        )

        self.assertEqual(workflow.name, "test-workflow")
        self.assertEqual(len(workflow.steps), 1)
        self.assertEqual(workflow.agents_count, 1)
        self.assertFalse(workflow.requires_installation)

    def test_workflow_to_dict(self):
        """ComposedWorkflow should convert to dictionary."""
        agent = AgentMatch(
            agent_id="test-agent",
            agent_name="Test Agent",
            confidence=0.9,
            source="builtin",
            installed=True,
        )

        step = WorkflowStep(
            step_number=1, step_type="architecture", agent=agent, description="Design"
        )

        workflow = ComposedWorkflow(
            name="test-workflow",
            description="Test",
            goal="Goal",
            steps=[step],
            total_estimated_duration_min=15,
            total_estimated_cost=0.50,
            agents_count=1,
            builtin_count=1,
            marketplace_count=0,
            requires_installation=False,
        )

        result = workflow.to_dict()

        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("steps", result)
        self.assertEqual(len(result["steps"]), 1)


class TestWorkflowComposerInit(unittest.TestCase):
    """Test WorkflowComposer initialization."""

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_composer_initialization(self, mock_get_router):
        """Composer should initialize with defaults."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router

        composer = WorkflowComposer()

        self.assertTrue(composer.include_marketplace)
        mock_get_router.assert_called_once_with(include_marketplace=True)

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_composer_without_marketplace(self, mock_get_router):
        """Composer should work without marketplace."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router

        composer = WorkflowComposer(include_marketplace=False)

        self.assertFalse(composer.include_marketplace)
        mock_get_router.assert_called_once_with(include_marketplace=False)


class TestAnalyzeGoal(unittest.TestCase):
    """Test goal analysis."""

    @patch("claude_force.workflow_composer.get_agent_router")
    def setUp(self, mock_get_router):
        """Set up test fixtures."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router
        self.composer = WorkflowComposer()

    def test_analyze_architecture_goal(self):
        """Should identify architecture step."""
        steps = self.composer._analyze_goal("Design system architecture")

        step_types = [s[0] for s in steps]
        self.assertIn("architecture", step_types)

    def test_analyze_implementation_goal(self):
        """Should identify implementation step."""
        steps = self.composer._analyze_goal("Implement REST API")

        step_types = [s[0] for s in steps]
        self.assertIn("implementation", step_types)

    def test_analyze_testing_goal(self):
        """Should identify testing step."""
        steps = self.composer._analyze_goal("Write tests for authentication")

        step_types = [s[0] for s in steps]
        self.assertIn("testing", step_types)

    def test_analyze_deployment_goal(self):
        """Should identify deployment step."""
        steps = self.composer._analyze_goal("Deploy to Kubernetes production")

        step_types = [s[0] for s in steps]
        self.assertIn("deployment", step_types)

    def test_analyze_complex_goal(self):
        """Should identify multiple steps for complex goal."""
        steps = self.composer._analyze_goal("Build and deploy ML model with monitoring")

        step_types = [s[0] for s in steps]
        self.assertGreater(len(step_types), 1)
        self.assertTrue("deployment" in step_types or "implementation" in step_types)

    def test_analyze_generic_goal(self):
        """Should provide default steps for generic goal."""
        # Use truly generic goal that won't match any keywords
        steps = self.composer._analyze_goal("Do the thing")

        self.assertGreater(len(steps), 0)
        # Should have architecture, implementation, testing
        step_types = [s[0] for s in steps]
        self.assertIn("architecture", step_types)
        self.assertIn("implementation", step_types)
        self.assertIn("testing", step_types)

    def test_analyze_steps_sorted(self):
        """Steps should be sorted in logical workflow order."""
        steps = self.composer._analyze_goal("Test, deploy, and design architecture")

        step_types = [s[0] for s in steps]
        # Architecture should come before testing and deployment
        if "architecture" in step_types:
            arch_index = step_types.index("architecture")
            if "testing" in step_types:
                test_index = step_types.index("testing")
                self.assertLess(arch_index, test_index)


class TestComposeWorkflow(unittest.TestCase):
    """Test workflow composition."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_router = Mock()

        # Mock agent matches
        self.mock_agent = AgentMatch(
            agent_id="frontend-architect",
            agent_name="Frontend Architect",
            confidence=0.9,
            source="builtin",
            installed=True,
            description="Frontend expert",
        )

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_compose_simple_workflow(self, mock_get_router):
        """Should compose workflow for simple goal."""
        mock_get_router.return_value = self.mock_router
        self.mock_router.recommend_agents.return_value = [self.mock_agent]

        composer = WorkflowComposer()
        workflow = composer.compose_workflow("Build React app")

        self.assertIsInstance(workflow, ComposedWorkflow)
        self.assertGreater(len(workflow.steps), 0)
        self.assertGreater(workflow.total_estimated_duration_min, 0)
        self.assertGreater(workflow.total_estimated_cost, 0.0)

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_compose_respects_max_agents(self, mock_get_router):
        """Should respect max_agents limit."""
        mock_get_router.return_value = self.mock_router
        self.mock_router.recommend_agents.return_value = [self.mock_agent]

        composer = WorkflowComposer()
        workflow = composer.compose_workflow(
            "Build complete system with all features", max_agents=3
        )

        self.assertLessEqual(workflow.agents_count, 3)

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_compose_calculates_totals(self, mock_get_router):
        """Should calculate total duration and cost."""
        mock_get_router.return_value = self.mock_router
        self.mock_router.recommend_agents.return_value = [self.mock_agent]

        composer = WorkflowComposer()
        workflow = composer.compose_workflow("Build app")

        # Total should equal sum of steps
        expected_duration = sum(s.estimated_duration_min for s in workflow.steps)
        expected_cost = sum(s.estimated_cost for s in workflow.steps)

        self.assertEqual(workflow.total_estimated_duration_min, expected_duration)
        self.assertEqual(workflow.total_estimated_cost, expected_cost)

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_compose_tracks_agent_sources(self, mock_get_router):
        """Should track builtin vs marketplace agents."""
        builtin_agent = AgentMatch(
            agent_id="test1", agent_name="Test 1", confidence=0.9, source="builtin", installed=True
        )

        marketplace_agent = AgentMatch(
            agent_id="test2",
            agent_name="Test 2",
            confidence=0.8,
            source="marketplace",
            installed=True,
            plugin_id="test-plugin",
        )

        mock_get_router.return_value = self.mock_router
        # Return different agents for different calls
        self.mock_router.recommend_agents.side_effect = [[builtin_agent], [marketplace_agent]]

        composer = WorkflowComposer()
        workflow = composer.compose_workflow("Build and deploy")

        self.assertGreater(workflow.builtin_count, 0)

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_compose_identifies_installation_needed(self, mock_get_router):
        """Should identify marketplace agents needing installation."""
        marketplace_agent = AgentMatch(
            agent_id="test",
            agent_name="Test",
            confidence=0.9,
            source="marketplace",
            installed=False,
            plugin_id="test-plugin",
        )

        mock_get_router.return_value = self.mock_router
        self.mock_router.recommend_agents.return_value = [marketplace_agent]

        composer = WorkflowComposer()
        workflow = composer.compose_workflow("Build app")

        self.assertTrue(workflow.requires_installation)
        self.assertIn("test-plugin", workflow.installation_needed)


class TestGenerateWorkflowName(unittest.TestCase):
    """Test workflow name generation."""

    @patch("claude_force.workflow_composer.get_agent_router")
    def setUp(self, mock_get_router):
        """Set up test fixtures."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router
        self.composer = WorkflowComposer()

    def test_generate_name_from_simple_goal(self):
        """Should generate name from simple goal."""
        name = self.composer._generate_workflow_name("Build React app")

        self.assertIn("custom", name)
        self.assertIn("build", name.lower())
        self.assertIn("react", name.lower())
        self.assertNotIn(" ", name)

    def test_generate_name_removes_special_chars(self):
        """Should remove special characters."""
        name = self.composer._generate_workflow_name("Build app (with tests!)")

        self.assertNotIn("(", name)
        self.assertNotIn(")", name)
        self.assertNotIn("!", name)

    def test_generate_name_limits_length(self):
        """Should limit name length."""
        long_goal = "Build a complete enterprise application with microservices architecture and full test coverage"
        name = self.composer._generate_workflow_name(long_goal)

        # custom- prefix + 50 chars max
        self.assertLessEqual(len(name), 60)


class TestSaveWorkflow(unittest.TestCase):
    """Test workflow saving."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.tmpdir)

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_save_workflow(self, mock_get_router):
        """Should save workflow to file."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router

        composer = WorkflowComposer()

        # Create simple workflow
        agent = AgentMatch(
            agent_id="test", agent_name="Test", confidence=0.9, source="builtin", installed=True
        )

        step = WorkflowStep(
            step_number=1, step_type="architecture", agent=agent, description="Design"
        )

        workflow = ComposedWorkflow(
            name="test-workflow",
            description="Test",
            goal="Test goal",
            steps=[step],
            total_estimated_duration_min=15,
            total_estimated_cost=0.50,
            agents_count=1,
            builtin_count=1,
            marketplace_count=0,
            requires_installation=False,
        )

        output_dir = Path(self.tmpdir) / "workflows"
        workflow_file = composer.save_workflow(workflow, output_dir=output_dir)

        self.assertTrue(workflow_file.exists())
        self.assertEqual(workflow_file.parent, output_dir)

        # Check file content
        import json

        with open(workflow_file) as f:
            data = json.load(f)

        self.assertEqual(data["name"], "test-workflow")
        self.assertEqual(len(data["steps"]), 1)


class TestEstimateWorkflowCost(unittest.TestCase):
    """Test workflow cost estimation."""

    @patch("claude_force.workflow_composer.get_agent_router")
    def setUp(self, mock_get_router):
        """Set up test fixtures."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router
        self.composer = WorkflowComposer()

    def test_estimate_cost_single_run(self):
        """Should estimate cost for single run."""
        workflow = ComposedWorkflow(
            name="test",
            description="Test",
            goal="Test",
            steps=[],
            total_estimated_duration_min=30,
            total_estimated_cost=2.00,
            agents_count=0,
            builtin_count=0,
            marketplace_count=0,
            requires_installation=False,
        )

        estimate = self.composer.estimate_workflow_cost(workflow, runs_per_month=1)

        self.assertEqual(estimate["cost_per_run"], 2.00)
        self.assertEqual(estimate["runs_per_month"], 1)
        self.assertEqual(estimate["monthly_cost"], 2.00)

    def test_estimate_cost_multiple_runs(self):
        """Should estimate cost for multiple runs."""
        workflow = ComposedWorkflow(
            name="test",
            description="Test",
            goal="Test",
            steps=[],
            total_estimated_duration_min=30,
            total_estimated_cost=2.00,
            agents_count=0,
            builtin_count=0,
            marketplace_count=0,
            requires_installation=False,
        )

        estimate = self.composer.estimate_workflow_cost(workflow, runs_per_month=10)

        self.assertEqual(estimate["monthly_cost"], 20.00)
        self.assertEqual(estimate["annual_cost"], 240.00)


class TestGetWorkflowComposer(unittest.TestCase):
    """Test get_workflow_composer function."""

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_get_composer_creates_instance(self, mock_get_router):
        """get_workflow_composer should create instance."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router

        composer = get_workflow_composer()

        self.assertIsInstance(composer, WorkflowComposer)

    @patch("claude_force.workflow_composer.get_agent_router")
    def test_get_composer_with_marketplace(self, mock_get_router):
        """get_workflow_composer should accept marketplace flag."""
        mock_router = Mock()
        mock_get_router.return_value = mock_router

        composer = get_workflow_composer(include_marketplace=False)

        self.assertFalse(composer.include_marketplace)


if __name__ == "__main__":
    unittest.main()
