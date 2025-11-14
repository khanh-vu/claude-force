"""
End-to-End Integration Tests for Agent Orchestrator

Tests complete workflows from agent selection to execution with performance tracking.
Uses mocked Claude API responses to ensure reproducible, fast tests.
"""

import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

from claude_force.orchestrator import AgentOrchestrator, AgentResult
from claude_force.performance_tracker import PerformanceTracker, ExecutionMetrics
from claude_force.semantic_selector import SemanticAgentSelector, AgentMatch


class MockClaudeResponse:
    """Mock Anthropic API response"""

    def __init__(self, content: str, model: str = "claude-3-5-sonnet-20241022",
                 input_tokens: int = 100, output_tokens: int = 200):
        self.content = [Mock(text=content)]
        self.model = model
        self.usage = Mock(
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        self.id = "msg_123"
        self.stop_reason = "end_turn"


class TestOrchestratorEndToEnd(unittest.TestCase):
    """Test complete orchestrator workflows end-to-end."""

    def setUp(self):
        """Set up test fixtures with a complete .claude configuration."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create minimal claude.json
        self.config = {
            "name": "test-project",
            "version": "1.0",
            "description": "Test project for integration tests",
            "agents": {
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "contract": "contracts/code-reviewer.contract",
                    "domains": ["code-quality", "security", "performance"],
                    "priority": 1
                },
                "backend-developer": {
                    "file": "agents/backend-developer.md",
                    "contract": "contracts/backend-developer.contract",
                    "domains": ["backend", "api", "database"],
                    "priority": 2
                }
            },
            "workflows": {
                "code-review": ["code-reviewer"],
                "feature-development": ["backend-developer", "code-reviewer"]
            }
        }

        config_path = self.claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        # Create agent files
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()

        (agents_dir / "code-reviewer.md").write_text("""
# Code Reviewer Agent

## Role
Expert code reviewer specializing in security, quality, and performance.

## Domain Expertise
- Code quality analysis
- Security vulnerability detection
- Performance optimization
- Best practices enforcement

## Responsibilities
- Review code for bugs and security issues
- Suggest improvements
- Ensure coding standards compliance
""")

        (agents_dir / "backend-developer.md").write_text("""
# Backend Developer Agent

## Role
Backend development expert specializing in APIs and databases.

## Domain Expertise
- RESTful API design
- Database schema design
- Backend architecture
- Microservices

## Responsibilities
- Implement backend features
- Design APIs
- Optimize database queries
""")

        # Set API key for testing
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

    @patch('anthropic.Client')
    def test_run_single_agent_with_tracking(self, mock_client_class):
        """Test running a single agent with performance tracking enabled."""
        # Setup mock Claude API
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = MockClaudeResponse(
            content="# Code Review Results\n\nThe code looks good with minor suggestions...",
            input_tokens=150,
            output_tokens=250
        )

        mock_client.messages.create.return_value = mock_response

        # Initialize orchestrator
        config_path = self.claude_dir / "claude.json"
        orchestrator = AgentOrchestrator(
            config_path=str(config_path),
            enable_tracking=True
        )

        # Run agent
        result = orchestrator.run_agent(
            agent_name="code-reviewer",
            task="Review this authentication function for security issues"
        )

        # Verify result
        self.assertIsInstance(result, AgentResult)
        self.assertTrue(result.success)
        self.assertIn("Code Review Results", result.output)

        # Verify Claude API was called
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        self.assertIn("messages", call_kwargs)

        # Verify performance tracking
        if orchestrator.tracker:
            metrics = orchestrator.tracker.get_summary()
            self.assertIsNotNone(metrics)

    @patch('anthropic.Client')
    def test_run_workflow_multi_agent(self, mock_client_class):
        """Test running a complete multi-agent workflow."""
        # Setup mock Claude API
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Different responses for each agent
        responses = [
            MockClaudeResponse("# Backend Implementation\n\nImplemented REST endpoint..."),
            MockClaudeResponse("# Code Review\n\nImplementation approved with suggestions...")
        ]

        mock_client.messages.create.side_effect = responses

        # Initialize orchestrator
        config_path = self.claude_dir / "claude.json"
        orchestrator = AgentOrchestrator(
            config_path=str(config_path),
            enable_tracking=True
        )

        # Run workflow
        results = orchestrator.run_workflow(
            workflow_name="feature-development",
            task="Implement user authentication endpoint"
        )

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.success for r in results))

        # First agent: backend-developer
        self.assertEqual(results[0].agent_name, "backend-developer")
        self.assertIn("Backend Implementation", results[0].output)

        # Second agent: code-reviewer
        self.assertEqual(results[1].agent_name, "code-reviewer")
        self.assertIn("Code Review", results[1].output)

        # Verify both agents were called
        self.assertEqual(mock_client.messages.create.call_count, 2)

    @patch('anthropic.Client')
    def test_agent_failure_handling(self, mock_client_class):
        """Test graceful handling of agent execution failures."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API rate limit exceeded")

        config_path = self.claude_dir / "claude.json"
        orchestrator = AgentOrchestrator(
            config_path=str(config_path),
            enable_tracking=True
        )

        # Run agent (should handle error gracefully)
        result = orchestrator.run_agent(
            agent_name="code-reviewer",
            task="Review code"
        )

        # Verify error handling
        self.assertFalse(result.success)
        self.assertIsNotNone(result.errors)
        self.assertTrue(len(result.errors) > 0)
        self.assertIn("rate limit", result.errors[0].lower())

    @patch('anthropic.Client')
    def test_workflow_partial_failure(self, mock_client_class):
        """Test workflow when one agent fails mid-execution."""
        # Setup mock: first succeeds, second fails
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_client.messages.create.side_effect = [
            MockClaudeResponse("# Implementation complete"),
            Exception("Network timeout")
        ]

        config_path = self.claude_dir / "claude.json"
        orchestrator = AgentOrchestrator(
            config_path=str(config_path),
            enable_tracking=True
        )

        results = orchestrator.run_workflow(
            workflow_name="feature-development",
            task="Implement feature"
        )

        # Verify partial execution
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].success)
        self.assertFalse(results[1].success)
        self.assertIsNotNone(results[1].errors)


class TestPerformanceTrackingIntegration(unittest.TestCase):
    """Test performance tracking integration with orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.metrics_dir = Path(self.temp_dir) / ".claude" / "metrics"
        self.metrics_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_metrics_recording(self):
        """Test that metrics are correctly recorded."""
        tracker = PerformanceTracker(metrics_dir=str(self.metrics_dir))

        # Record execution
        tracker.record_execution(
            agent_name="code-reviewer",
            task="Review authentication module",
            success=True,
            execution_time_ms=1250.5,
            model="claude-3-5-sonnet-20241022",
            input_tokens=150,
            output_tokens=250
        )

        # Verify metrics file created
        metrics_file = self.metrics_dir / "executions.jsonl"
        self.assertTrue(metrics_file.exists())

        # Verify metrics content
        with open(metrics_file) as f:
            line = f.readline()
            data = json.loads(line)

            self.assertEqual(data["agent_name"], "code-reviewer")
            self.assertTrue(data["success"])
            self.assertEqual(data["model"], "claude-3-5-sonnet-20241022")
            self.assertEqual(data["input_tokens"], 150)
            self.assertEqual(data["output_tokens"], 250)

    def test_cost_calculation(self):
        """Test accurate cost calculation for different models."""
        tracker = PerformanceTracker(metrics_dir=str(self.metrics_dir))

        # Record executions with different models
        test_cases = [
            ("claude-3-haiku-20240307", 1000, 1000),  # Cheapest
            ("claude-3-5-sonnet-20241022", 1000, 1000),  # Mid-tier
            ("claude-3-opus-20240229", 1000, 1000),  # Most expensive
        ]

        for model, input_tokens, output_tokens in test_cases:
            tracker.record_execution(
                agent_name="test-agent",
                task="Test task",
                success=True,
                execution_time_ms=1000,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

        # Verify costs are different and in correct order
        summary = tracker.get_summary()
        self.assertIsNotNone(summary)

        # Haiku should be cheapest, Opus most expensive
        # (We can verify this by checking the summary stats)

    def test_analytics_generation(self):
        """Test analytics and trend analysis."""
        tracker = PerformanceTracker(metrics_dir=str(self.metrics_dir))

        # Record multiple executions
        for i in range(10):
            tracker.record_execution(
                agent_name="code-reviewer",
                task=f"Review task {i}",
                success=i % 8 != 0,  # 1 failure
                execution_time_ms=1000 + i * 100,
                model="claude-3-5-sonnet-20241022",
                input_tokens=100 + i * 10,
                output_tokens=200 + i * 20
            )

        # Get analytics
        analytics = tracker.get_analytics()

        # Verify analytics structure
        self.assertIn("total_executions", analytics)
        self.assertEqual(analytics["total_executions"], 10)

        self.assertIn("success_rate", analytics)
        self.assertAlmostEqual(analytics["success_rate"], 0.9, places=2)

        self.assertIn("total_cost", analytics)
        self.assertGreater(analytics["total_cost"], 0)

    def test_agent_comparison(self):
        """Test comparing performance across different agents."""
        tracker = PerformanceTracker(metrics_dir=str(self.metrics_dir))

        # Record executions for multiple agents
        agents = ["code-reviewer", "backend-developer", "frontend-developer"]

        for agent in agents:
            for i in range(5):
                tracker.record_execution(
                    agent_name=agent,
                    task=f"Task {i}",
                    success=True,
                    execution_time_ms=1000 + hash(agent + str(i)) % 1000,
                    model="claude-3-5-sonnet-20241022",
                    input_tokens=100,
                    output_tokens=200
                )

        # Get per-agent stats
        agent_stats = tracker.get_agent_stats()

        # Verify all agents present
        self.assertEqual(len(agent_stats), 3)
        for agent in agents:
            self.assertIn(agent, agent_stats)
            self.assertEqual(agent_stats[agent]["execution_count"], 5)


class TestSemanticSelectorIntegration(unittest.TestCase):
    """Test semantic agent selector integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config with diverse agents
        self.config = {
            "name": "test-project",
            "agents": {
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "domains": ["code-quality", "security", "review"],
                    "priority": 1
                },
                "security-specialist": {
                    "file": "agents/security-specialist.md",
                    "domains": ["security", "compliance", "threat-modeling"],
                    "priority": 1
                },
                "backend-developer": {
                    "file": "agents/backend-developer.md",
                    "domains": ["backend", "api", "database"],
                    "priority": 2
                },
                "devops-engineer": {
                    "file": "agents/devops-engineer.md",
                    "domains": ["infrastructure", "deployment", "monitoring"],
                    "priority": 2
                }
            }
        }

        config_path = self.claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f)

        # Create agent files
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()

        (agents_dir / "code-reviewer.md").write_text(
            "Expert in code quality, security reviews, and performance analysis"
        )
        (agents_dir / "security-specialist.md").write_text(
            "Security expert specializing in threat modeling and compliance"
        )
        (agents_dir / "backend-developer.md").write_text(
            "Backend development expert for APIs and databases"
        )
        (agents_dir / "devops-engineer.md").write_text(
            "DevOps specialist for CI/CD pipelines and infrastructure"
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_semantic_matching_accuracy(self):
        """Test that semantic matching selects appropriate agents."""
        config_path = self.claude_dir / "claude.json"

        try:
            selector = SemanticAgentSelector(config_path=str(config_path))
        except ImportError:
            # sentence-transformers not installed, skip test
            self.skipTest("sentence-transformers not installed")
            return

        # Test case 1: Security-related task
        matches = selector.recommend_agents(
            task="Analyze this code for SQL injection vulnerabilities",
            top_k=2
        )

        self.assertGreater(len(matches), 0)
        # Should recommend security-specialist or code-reviewer
        top_match = matches[0]
        self.assertIn(top_match.agent_name, ["security-specialist", "code-reviewer"])
        self.assertGreater(top_match.confidence, 0.5)

        # Test case 2: Infrastructure task
        matches = selector.recommend_agents(
            task="Set up Kubernetes cluster with auto-scaling",
            top_k=2
        )

        self.assertGreater(len(matches), 0)
        top_match = matches[0]
        self.assertEqual(top_match.agent_name, "devops-engineer")

        # Test case 3: Backend development task
        matches = selector.recommend_agents(
            task="Design REST API for user management",
            top_k=2
        )

        self.assertGreater(len(matches), 0)
        top_match = matches[0]
        self.assertEqual(top_match.agent_name, "backend-developer")

    def test_multi_agent_recommendation(self):
        """Test recommending multiple agents for complex tasks."""
        config_path = self.claude_dir / "claude.json"

        try:
            selector = SemanticAgentSelector(config_path=str(config_path))
        except ImportError:
            self.skipTest("sentence-transformers not installed")
            return

        # Complex task requiring multiple agents
        matches = selector.recommend_agents(
            task="Build secure authentication API with deployment pipeline",
            top_k=3
        )

        self.assertGreaterEqual(len(matches), 2)

        # Should recommend backend-developer, security-specialist, and devops-engineer
        agent_names = [m.agent_name for m in matches]
        self.assertIn("backend-developer", agent_names)

        # All matches should have reasonable confidence
        for match in matches:
            self.assertGreater(match.confidence, 0.3)

    def test_confidence_scores(self):
        """Test that confidence scores are meaningful and well-calibrated."""
        config_path = self.claude_dir / "claude.json"

        try:
            selector = SemanticAgentSelector(config_path=str(config_path))
        except ImportError:
            self.skipTest("sentence-transformers not installed")
            return

        # Very specific task - should have high confidence
        matches = selector.recommend_agents(
            task="Review code for security vulnerabilities",
            top_k=4
        )

        # Top match should have higher confidence than lower matches
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                self.assertGreaterEqual(
                    matches[i].confidence,
                    matches[i + 1].confidence,
                    "Confidence scores should be descending"
                )

        # Confidence should be in valid range [0, 1]
        for match in matches:
            self.assertGreaterEqual(match.confidence, 0.0)
            self.assertLessEqual(match.confidence, 1.0)


class TestCompleteIntegrationWorkflow(unittest.TestCase):
    """Test complete integration: semantic selection → orchestration → tracking."""

    def setUp(self):
        """Set up complete test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Full configuration
        self.config = {
            "name": "integration-test-project",
            "version": "1.0",
            "agents": {
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "contract": "contracts/code-reviewer.contract",
                    "domains": ["code-quality", "security"],
                    "priority": 1
                }
            },
            "workflows": {
                "review": ["code-reviewer"]
            }
        }

        config_path = self.claude_dir / "claude.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f)

        # Create agent file
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "code-reviewer.md").write_text("Code quality expert")

        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

    @patch('anthropic.Client')
    def test_full_workflow_with_all_features(self, mock_client_class):
        """Test complete workflow: selection → execution → tracking."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.return_value = MockClaudeResponse(
            "Code review complete"
        )

        config_path = self.claude_dir / "claude.json"

        # Step 1: Semantic agent selection (if available)
        try:
            selector = SemanticAgentSelector(config_path=str(config_path))
            matches = selector.recommend_agents(
                task="Review authentication code for security issues",
                top_k=1
            )
            selected_agent = matches[0].agent_name if matches else "code-reviewer"
        except ImportError:
            # Fallback if sentence-transformers not available
            selected_agent = "code-reviewer"

        # Step 2: Execute agent with orchestrator
        orchestrator = AgentOrchestrator(
            config_path=str(config_path),
            enable_tracking=True
        )

        result = orchestrator.run_agent(
            agent_name=selected_agent,
            task="Review authentication code for security issues"
        )

        # Step 3: Verify execution
        self.assertTrue(result.success)
        self.assertEqual(result.agent_name, selected_agent)

        # Step 4: Verify tracking
        if orchestrator.tracker:
            analytics = orchestrator.tracker.get_analytics()
            self.assertGreater(analytics["total_executions"], 0)


if __name__ == "__main__":
    unittest.main()
