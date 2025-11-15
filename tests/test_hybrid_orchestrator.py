"""
Tests for Hybrid Model Orchestrator functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from claude_force.hybrid_orchestrator import (
    HybridOrchestrator,
    ModelPricing,
    CostEstimate,
    get_hybrid_orchestrator,
)


class TestModelPricing(unittest.TestCase):
    """Test model pricing dataclass."""

    def test_default_pricing(self):
        """Test default pricing values."""
        pricing = ModelPricing()

        # Haiku pricing
        self.assertEqual(pricing.haiku_input, 0.25)
        self.assertEqual(pricing.haiku_output, 1.25)

        # Sonnet pricing
        self.assertEqual(pricing.sonnet_input, 3.00)
        self.assertEqual(pricing.sonnet_output, 15.00)

        # Opus pricing
        self.assertEqual(pricing.opus_input, 15.00)
        self.assertEqual(pricing.opus_output, 75.00)


class TestCostEstimate(unittest.TestCase):
    """Test cost estimate dataclass."""

    def test_cost_estimate_structure(self):
        """Test cost estimate structure."""
        estimate = CostEstimate(
            model="claude-3-haiku-20240307",
            estimated_input_tokens=1000,
            estimated_output_tokens=500,
            estimated_cost=0.001,
            breakdown={"input_cost": 0.0005, "output_cost": 0.0005},
        )

        self.assertEqual(estimate.model, "claude-3-haiku-20240307")
        self.assertEqual(estimate.estimated_input_tokens, 1000)
        self.assertEqual(estimate.estimated_output_tokens, 500)
        self.assertEqual(estimate.estimated_cost, 0.001)
        self.assertIn("input_cost", estimate.breakdown)


class TestHybridOrchestrator(unittest.TestCase):
    """Test suite for HybridOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the config file
        self.mock_config = {
            "agents": {
                "test-agent": {
                    "file": "agents/test-agent.md",
                    "contract": "contracts/test-agent.contract",
                },
                "document-writer-expert": {
                    "file": "agents/document-writer-expert.md",
                    "contract": "contracts/document-writer-expert.contract",
                },
                "frontend-architect": {
                    "file": "agents/frontend-architect.md",
                    "contract": "contracts/frontend-architect.contract",
                },
            }
        }

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_initialization(self, mock_init):
        """Test HybridOrchestrator initialization."""
        mock_init.return_value = None

        orchestrator = HybridOrchestrator(
            config_path=".claude/claude.json",
            auto_select_model=True,
            prefer_cheaper=True,
            cost_threshold=1.0,
        )

        self.assertTrue(orchestrator.auto_select_model)
        self.assertTrue(orchestrator.prefer_cheaper)
        self.assertEqual(orchestrator.cost_threshold, 1.0)
        self.assertIsInstance(orchestrator.pricing, ModelPricing)

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_model_strategy_classification(self, mock_init):
        """Test that agents are classified correctly."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        # Check Haiku agents
        self.assertIn("document-writer-expert", orchestrator.MODEL_STRATEGY["haiku"])
        self.assertIn("api-documenter", orchestrator.MODEL_STRATEGY["haiku"])

        # Check Sonnet agents
        self.assertIn("frontend-architect", orchestrator.MODEL_STRATEGY["sonnet"])
        self.assertIn("backend-architect", orchestrator.MODEL_STRATEGY["sonnet"])
        self.assertIn("ai-engineer", orchestrator.MODEL_STRATEGY["sonnet"])

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_analyze_task_complexity_critical(self, mock_init):
        """Test critical task detection."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        critical_tasks = [
            "Deploy to production",
            "Delete all user data",
            "Run database migration",
            "Security audit for authentication",
            "Drop table from production",
        ]

        for task in critical_tasks:
            complexity = orchestrator._analyze_task_complexity(task, "test-agent")
            self.assertEqual(complexity, "critical", f"Task '{task}' should be critical")

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_analyze_task_complexity_simple(self, mock_init):
        """Test simple task detection."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        simple_tasks = [
            "Format the code",
            "Generate docs for this function",
            "Create readme",
            "Fix typo in README",
            "Add comments to code",
        ]

        for task in simple_tasks:
            complexity = orchestrator._analyze_task_complexity(task, "test-agent")
            self.assertEqual(complexity, "simple", f"Task '{task}' should be simple")

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_analyze_task_complexity_complex(self, mock_init):
        """Test complex task detection."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        complex_tasks = [
            "Design the frontend application architecture",
            "Implement user dashboard with real-time updates",
            "Refactor the entire API layer",
            "Build a RAG system with vector database",
        ]

        for task in complex_tasks:
            complexity = orchestrator._analyze_task_complexity(task, "test-agent")
            self.assertEqual(complexity, "complex", f"Task '{task}' should be complex")

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_select_model_for_agent_haiku(self, mock_init):
        """Test model selection for Haiku agents."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        task = "Generate documentation"
        model = orchestrator.select_model_for_agent(
            "document-writer-expert", task, task_complexity="auto"
        )

        self.assertEqual(model, orchestrator.MODELS["haiku"])

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_select_model_for_agent_sonnet(self, mock_init):
        """Test model selection for Sonnet agents."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        task = "Design the frontend architecture"
        model = orchestrator.select_model_for_agent(
            "frontend-architect", task, task_complexity="auto"
        )

        self.assertEqual(model, orchestrator.MODELS["sonnet"])

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_select_model_for_agent_opus(self, mock_init):
        """Test model selection for critical tasks."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        task = "Deploy to production"
        model = orchestrator.select_model_for_agent("test-agent", task, task_complexity="critical")

        self.assertEqual(model, orchestrator.MODELS["opus"])

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_select_model_manual_override(self, mock_init):
        """Test manual complexity override."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        # Override to simple
        model = orchestrator.select_model_for_agent(
            "frontend-architect", "Some task", task_complexity="simple"  # Normally Sonnet
        )
        self.assertEqual(model, orchestrator.MODELS["haiku"])

        # Override to complex
        model = orchestrator.select_model_for_agent(
            "document-writer-expert", "Some task", task_complexity="complex"  # Normally Haiku
        )
        self.assertEqual(model, orchestrator.MODELS["sonnet"])

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_estimate_cost_haiku(self, mock_init):
        """Test cost estimation for Haiku."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        task = "Format this code"
        estimate = orchestrator.estimate_cost(
            task, "document-writer-expert", model="claude-3-haiku-20240307"
        )

        self.assertEqual(estimate.model, "claude-3-haiku-20240307")
        self.assertGreater(estimate.estimated_input_tokens, 0)
        self.assertGreater(estimate.estimated_output_tokens, 0)
        self.assertGreater(estimate.estimated_cost, 0)
        self.assertIn("input_cost", estimate.breakdown)
        self.assertIn("output_cost", estimate.breakdown)

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_estimate_cost_sonnet(self, mock_init):
        """Test cost estimation for Sonnet."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        task = "Design a complex architecture"
        estimate = orchestrator.estimate_cost(
            task, "frontend-architect", model="claude-3-5-sonnet-20241022"
        )

        self.assertEqual(estimate.model, "claude-3-5-sonnet-20241022")
        self.assertGreater(estimate.estimated_cost, 0)

        # Sonnet should be more expensive than Haiku
        haiku_estimate = orchestrator.estimate_cost(
            task, "frontend-architect", model="claude-3-haiku-20240307"
        )
        self.assertGreater(estimate.estimated_cost, haiku_estimate.estimated_cost)

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_estimate_cost_auto_select(self, mock_init):
        """Test cost estimation with auto model selection."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        task = "Generate documentation"
        estimate = orchestrator.estimate_cost(
            task, "document-writer-expert", model=None  # Auto-select
        )

        # Should select Haiku for document-writer-expert
        self.assertIn("haiku", estimate.model.lower())

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_estimate_cost_varies_by_complexity(self, mock_init):
        """Test that cost estimates vary by task complexity."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        model = "claude-3-5-sonnet-20241022"

        # Simple task
        simple_estimate = orchestrator.estimate_cost("Fix typo", "test-agent", model=model)

        # Complex task
        complex_estimate = orchestrator.estimate_cost(
            "Design and implement a complete microservices architecture", "test-agent", model=model
        )

        # Complex should estimate more output tokens
        self.assertGreater(
            complex_estimate.estimated_output_tokens, simple_estimate.estimated_output_tokens
        )


class TestGetHybridOrchestrator(unittest.TestCase):
    """Test the factory function."""

    @patch("claude_force.hybrid_orchestrator.AgentOrchestrator.__init__")
    def test_factory_function(self, mock_init):
        """Test factory function creates orchestrator correctly."""
        mock_init.return_value = None

        orchestrator = get_hybrid_orchestrator(
            config_path=".claude/claude.json",
            auto_select_model=True,
            prefer_cheaper=True,
            cost_threshold=5.0,
        )

        self.assertIsInstance(orchestrator, HybridOrchestrator)
        self.assertTrue(orchestrator.auto_select_model)
        self.assertTrue(orchestrator.prefer_cheaper)
        self.assertEqual(orchestrator.cost_threshold, 5.0)


if __name__ == "__main__":
    unittest.main()
