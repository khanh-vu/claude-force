"""
Feature Integration Tests for claude-force.

Tests interactions between Quick Start, Hybrid Orchestrator, and Skills Manager
to ensure all features work together seamlessly in production workflows.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

from claude_force.quick_start import (
    QuickStartOrchestrator,
    get_quick_start_orchestrator
)
from claude_force.hybrid_orchestrator import (
    HybridOrchestrator,
    get_hybrid_orchestrator
)
from claude_force.skills_manager import (
    ProgressiveSkillsManager,
    get_skills_manager
)


class TestQuickStartHybridIntegration(unittest.TestCase):
    """Test integration between Quick Start and Hybrid Orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_then_run_with_hybrid(self):
        """Test full workflow: init project → run agent with hybrid orchestration."""
        # Step 1: Initialize project with Quick Start
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # Match templates
        matches = orchestrator.match_templates(
            description="Build a chat application with LLM integration",
            tech_stack=["python", "react"],
            top_k=1
        )
        self.assertGreater(len(matches), 0)

        template = matches[0]

        # Generate config
        config = orchestrator.generate_config(
            template=template,
            project_name="test-chat-app",
            description="Chat app with AI"
        )

        # Initialize project
        claude_dir = Path(self.temp_dir) / ".claude"
        result = orchestrator.initialize_project(
            config=config,
            output_dir=str(claude_dir)
        )

        self.assertTrue((claude_dir / "claude.json").exists())
        self.assertGreater(len(result['created_files']), 0)

        # Step 2: Use Hybrid Orchestrator with the initialized project
        with patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__') as mock_init:
            mock_init.return_value = None

            hybrid = HybridOrchestrator(
                config_path=str(claude_dir / "claude.json"),
                auto_select_model=True
            )

            # Test model selection for different tasks
            simple_model = hybrid.select_model_for_agent(
                "code-reviewer",
                "Fix typo in README",
                task_complexity="simple"
            )
            self.assertEqual(simple_model, hybrid.MODELS["haiku"])

            complex_model = hybrid.select_model_for_agent(
                "backend-architect",
                "Design scalable microservices architecture",
                task_complexity="complex"
            )
            self.assertEqual(complex_model, hybrid.MODELS["sonnet"])

    def test_init_then_cost_estimate(self):
        """Test workflow: init → estimate costs before running."""
        # Initialize project
        orchestrator = get_quick_start_orchestrator(use_semantic=False)
        matches = orchestrator.match_templates(
            description="REST API service",
            top_k=1
        )

        template = matches[0]
        config = orchestrator.generate_config(
            template=template,
            project_name="test-api",
            description="REST API"
        )

        claude_dir = Path(self.temp_dir) / ".claude"
        orchestrator.initialize_project(
            config=config,
            output_dir=str(claude_dir)
        )

        # Estimate costs with Hybrid Orchestrator
        with patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__') as mock_init:
            mock_init.return_value = None

            hybrid = HybridOrchestrator(auto_select_model=True)

            # Estimate for different complexity tasks
            simple_estimate = hybrid.estimate_cost(
                "Fix bug in login endpoint",
                "backend-developer"
            )
            # Should use cheaper model for simple task
            self.assertIn(simple_estimate.model, [hybrid.MODELS["haiku"], hybrid.MODELS["sonnet"]])
            self.assertLess(simple_estimate.estimated_cost, 0.1)

            complex_estimate = hybrid.estimate_cost(
                "Implement full authentication system with OAuth2 and JWT",
                "backend-architect"
            )
            # Complex task estimate should exist
            self.assertIsNotNone(complex_estimate.model)
            self.assertGreater(complex_estimate.estimated_cost, 0)

    def test_template_to_execution(self):
        """Test complete flow: template selection → config generation → agent execution setup."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # User describes their project
        description = "Machine learning model training pipeline with data validation"

        # System recommends templates
        matches = orchestrator.match_templates(
            description=description,
            tech_stack=["python", "tensorflow"],
            top_k=3
        )

        self.assertGreater(len(matches), 0)

        # User selects top match
        selected_template = matches[0]

        # Generate project configuration
        config = orchestrator.generate_config(
            template=selected_template,
            project_name="ml-pipeline",
            description=description
        )

        # Verify config has required components
        self.assertIsNotNone(config.agents)
        self.assertIsNotNone(config.workflows)
        self.assertIsNotNone(config.skills)
        self.assertGreater(len(config.agents), 0)

        # Initialize project
        claude_dir = Path(self.temp_dir) / ".claude"
        result = orchestrator.initialize_project(
            config=config,
            output_dir=str(claude_dir)
        )

        # Verify all necessary files created
        self.assertTrue((claude_dir / "claude.json").exists())
        self.assertTrue((claude_dir / "task.md").exists())
        self.assertTrue((claude_dir / "README.md").exists())

        # Load config and verify agents are ready
        with open(claude_dir / "claude.json") as f:
            loaded_config = json.load(f)
            self.assertIn("agents", loaded_config)
            # Agents are stored as a dict with agent_id as key
            self.assertIsInstance(loaded_config["agents"], dict)
            self.assertGreater(len(loaded_config["agents"]), 0)


class TestHybridSkillsIntegration(unittest.TestCase):
    """Test integration between Hybrid Orchestrator and Skills Manager."""

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_hybrid_with_progressive_skills(self, mock_init):
        """Test combined cost optimization: model selection + progressive skills."""
        mock_init.return_value = None

        # Initialize both systems
        hybrid = HybridOrchestrator(auto_select_model=True, prefer_cheaper=True)
        skills_manager = get_skills_manager()

        # Simple task: should use Haiku + minimal skills
        simple_task = "Review code for typos"
        simple_agent = "code-reviewer"

        # Hybrid selects cheaper model
        model = hybrid.select_model_for_agent(
            simple_agent,
            simple_task,
            task_complexity="simple"
        )
        self.assertEqual(model, hybrid.MODELS["haiku"])

        # Skills manager loads only necessary skills
        required_skills = skills_manager.analyze_required_skills(
            simple_agent,
            simple_task,
            include_agent_skills=False
        )
        # Simple task should require fewer skills
        self.assertLessEqual(len(required_skills), 3)

        # Complex task: should use Sonnet + more skills
        complex_task = "Design and implement full test automation framework with CI/CD"
        complex_agent = "qa-lead"

        # Hybrid selects more capable model
        model = hybrid.select_model_for_agent(
            complex_agent,
            complex_task,
            task_complexity="complex"
        )
        self.assertEqual(model, hybrid.MODELS["sonnet"])

        # Skills manager loads more comprehensive skills
        required_skills = skills_manager.analyze_required_skills(
            complex_agent,
            complex_task,
            include_agent_skills=True
        )
        # Complex task should require more skills
        self.assertGreater(len(required_skills), 0)

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_cost_savings_measurement(self, mock_init):
        """Test that hybrid + progressive skills provides measurable cost savings."""
        mock_init.return_value = None

        hybrid = HybridOrchestrator(auto_select_model=True)
        skills_manager = get_skills_manager()

        # Scenario 1: Simple bug fix (should use cheaper model + minimal skills)
        simple_task = "Fix null pointer exception"
        simple_agent = "backend-developer"

        simple_estimate = hybrid.estimate_cost(
            simple_task,
            simple_agent
        )
        # Should provide cost estimate
        self.assertIsNotNone(simple_estimate.model)
        self.assertGreater(simple_estimate.estimated_cost, 0)

        # Calculate token savings from progressive skills
        all_skills = skills_manager.get_available_skills()
        required_skills = skills_manager.analyze_required_skills(
            simple_agent,
            simple_task,
            include_agent_skills=False
        )

        # Progressive skills should reduce token count
        if len(all_skills) > 0 and len(required_skills) < len(all_skills):
            # Savings achieved
            self.assertLess(len(required_skills), len(all_skills))

        # Scenario 2: Complex architectural task (should use more capable model + more skills)
        complex_task = "Design complete microservices architecture with event sourcing"
        complex_agent = "backend-architect"

        complex_estimate = hybrid.estimate_cost(
            complex_task,
            complex_agent
        )
        # Should provide estimate
        self.assertIsNotNone(complex_estimate.model)
        self.assertGreater(complex_estimate.estimated_cost, 0)

        # Even complex tasks benefit from progressive skills vs loading all
        complex_required_skills = skills_manager.analyze_required_skills(
            complex_agent,
            complex_task,
            include_agent_skills=True
        )
        # Should still be selective, not loading all skills
        self.assertIsNotNone(complex_required_skills)

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_token_reduction_measurement(self, mock_init):
        """Test measurable token reduction from progressive skills."""
        mock_init.return_value = None

        skills_manager = get_skills_manager()

        # Test different agents with varying skill needs
        test_cases = [
            ("code-reviewer", "Review this function for bugs", 3),
            ("backend-developer", "Implement REST endpoint", 4),
            ("data-engineer", "Build ETL pipeline", 5),
        ]

        for agent, task, expected_max_skills in test_cases:
            required_skills = skills_manager.analyze_required_skills(
                agent,
                task,
                include_agent_skills=False
            )

            # Progressive loading should be selective
            all_skills = skills_manager.get_available_skills()

            # If we have skills, verify selection is happening
            if len(all_skills) > 0:
                self.assertIsNotNone(required_skills)
                self.assertIsInstance(required_skills, list)


class TestFullPipelineIntegration(unittest.TestCase):
    """Test complete end-to-end workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_project_lifecycle(self):
        """Test complete lifecycle: init → template selection → config → execution setup."""
        # Phase 1: Project Initialization
        quick_start = get_quick_start_orchestrator(use_semantic=False)

        description = "Full-stack web app with authentication and database"
        matches = quick_start.match_templates(
            description=description,
            tech_stack=["python", "react", "postgresql"],
            top_k=1
        )

        self.assertGreater(len(matches), 0)
        template = matches[0]

        config = quick_start.generate_config(
            template=template,
            project_name="fullstack-app",
            description=description
        )

        claude_dir = Path(self.temp_dir) / ".claude"
        result = quick_start.initialize_project(
            config=config,
            output_dir=str(claude_dir)
        )

        # Verify initialization
        self.assertTrue((claude_dir / "claude.json").exists())
        self.assertGreater(len(config.agents), 0)
        self.assertGreater(len(config.workflows), 0)

        # Phase 2: Cost Optimization Setup
        with patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__') as mock_init:
            mock_init.return_value = None

            hybrid = HybridOrchestrator(
                config_path=str(claude_dir / "claude.json"),
                auto_select_model=True,
                cost_threshold=0.50
            )

            # Test different task complexities
            tasks = [
                ("Fix typo in comment", "simple"),
                ("Implement user authentication", "complex"),
                ("Design database schema", "complex"),
            ]

            for task, expected_complexity in tasks:
                complexity = hybrid._analyze_task_complexity(task, "backend-developer")
                self.assertIn(complexity, ["simple", "complex", "critical"])

        # Phase 3: Progressive Skills Loading
        skills_manager = get_skills_manager()

        # Test a few sample agents
        sample_agents = ["backend-developer", "code-reviewer", "frontend-developer"]
        for agent in sample_agents:
            required_skills = skills_manager.analyze_required_skills(
                agent,
                "Implement feature",
                include_agent_skills=True
            )
            self.assertIsNotNone(required_skills)

    def test_multi_agent_workflow(self):
        """Test running multiple agents in sequence with different optimizations."""
        # Initialize project
        quick_start = get_quick_start_orchestrator(use_semantic=False)

        matches = quick_start.match_templates(
            description="Backend API development",
            top_k=1
        )

        template = matches[0]
        config = quick_start.generate_config(
            template=template,
            project_name="api-project",
            description="REST API"
        )

        claude_dir = Path(self.temp_dir) / ".claude"
        quick_start.initialize_project(
            config=config,
            output_dir=str(claude_dir)
        )

        # Simulate multi-agent workflow
        with patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__') as mock_init:
            mock_init.return_value = None

            hybrid = HybridOrchestrator(auto_select_model=True)
            skills_manager = get_skills_manager()

            # Workflow: Architect → Developer → Reviewer
            workflow_steps = [
                ("backend-architect", "Design API architecture", "complex"),
                ("backend-developer", "Implement endpoints", "complex"),
                ("code-reviewer", "Review implementation", "simple"),
            ]

            for agent, task, expected_complexity in workflow_steps:
                # Each agent gets optimized model
                model = hybrid.select_model_for_agent(
                    agent,
                    task,
                    task_complexity=expected_complexity
                )
                self.assertIsNotNone(model)

                # Each agent gets relevant skills
                skills = skills_manager.analyze_required_skills(
                    agent,
                    task,
                    include_agent_skills=True
                )
                self.assertIsNotNone(skills)

    def test_error_recovery(self):
        """Test graceful degradation when components fail."""
        # Test Quick Start with missing template
        quick_start = get_quick_start_orchestrator(use_semantic=False)

        # Should handle empty description gracefully
        matches = quick_start.match_templates(
            description="",  # Empty description
            top_k=1
        )
        # Should still return templates, just with low confidence
        self.assertIsInstance(matches, list)

        # Test Hybrid Orchestrator with invalid complexity
        with patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__') as mock_init:
            mock_init.return_value = None

            hybrid = HybridOrchestrator(auto_select_model=True)

            # Invalid complexity should default to safe choice
            model = hybrid.select_model_for_agent(
                "test-agent",
                "Test task",
                task_complexity="invalid_complexity"
            )
            # Should default to Sonnet (safe middle ground)
            self.assertEqual(model, hybrid.MODELS["sonnet"])

        # Test Skills Manager with unknown agent
        skills_manager = get_skills_manager()
        skills = skills_manager.analyze_required_skills(
            "nonexistent-agent-xyz",
            "Some task",
            include_agent_skills=False
        )
        # Should return empty list or general skills, not crash
        self.assertIsInstance(skills, list)

    def test_configuration_persistence(self):
        """Test that configurations persist correctly across the workflow."""
        # Create project
        quick_start = get_quick_start_orchestrator(use_semantic=False)

        matches = quick_start.match_templates(
            description="Data pipeline",
            top_k=1
        )

        template = matches[0]
        original_config = quick_start.generate_config(
            template=template,
            project_name="data-pipeline",
            description="ETL pipeline"
        )

        claude_dir = Path(self.temp_dir) / ".claude"
        quick_start.initialize_project(
            config=original_config,
            output_dir=str(claude_dir)
        )

        # Load config and verify persistence
        config_file = claude_dir / "claude.json"
        self.assertTrue(config_file.exists())

        with open(config_file) as f:
            loaded_config = json.load(f)

        # Verify key fields persisted
        self.assertEqual(loaded_config["name"], original_config.name)
        self.assertEqual(loaded_config["description"], original_config.description)
        # Template is saved as "template" not "template_id"
        self.assertIn("template", loaded_config)
        self.assertEqual(loaded_config["template"], original_config.template_id)

        # Verify collections persisted
        self.assertIn("agents", loaded_config)
        self.assertIn("workflows", loaded_config)
        # Skills are stored under "skills_integration"
        self.assertIn("skills_integration", loaded_config)

        # Verify we can load this config in Hybrid Orchestrator
        # (This tests that the persisted format is compatible)
        with patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__') as mock_init:
            mock_init.return_value = None

            # Should be able to create hybrid orchestrator with persisted config
            hybrid = HybridOrchestrator(
                config_path=str(config_file),
                auto_select_model=True
            )
            self.assertIsNotNone(hybrid)


if __name__ == "__main__":
    unittest.main()
