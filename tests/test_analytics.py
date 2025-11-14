"""
Cross-Repository Analytics Tests for claude-force.

Tests analytics and agent performance comparison functionality.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from claude_force.analytics import (
    CrossRepoAnalytics,
    AgentPerformanceMetrics,
    ComparisonReport,
    get_analytics_manager
)


class TestAgentPerformanceMetrics(unittest.TestCase):
    """Test AgentPerformanceMetrics dataclass."""

    def test_metrics_creation(self):
        """AgentPerformanceMetrics should be creatable."""
        metrics = AgentPerformanceMetrics(
            agent_id="test-agent",
            agent_name="Test Agent",
            source="builtin",
            duration_seconds=45.5,
            tokens_used=12000,
            cost_usd=0.045,
            quality_score=8.5,
            model_used="claude-3-5-sonnet-20241022"
        )

        self.assertEqual(metrics.agent_id, "test-agent")
        self.assertEqual(metrics.duration_seconds, 45.5)
        self.assertEqual(metrics.tokens_used, 12000)
        self.assertEqual(metrics.quality_score, 8.5)

    def test_metrics_with_optional_fields(self):
        """AgentPerformanceMetrics should handle optional fields."""
        metrics = AgentPerformanceMetrics(
            agent_id="test",
            agent_name="Test",
            source="marketplace",
            duration_seconds=20.0,
            tokens_used=5000,
            cost_usd=0.01,
            quality_score=7.0,
            model_used="claude-3-haiku-20240307",
            strengths=["Fast", "Cheap"],
            weaknesses=["Less detailed"],
            task_suitability="good"
        )

        self.assertEqual(len(metrics.strengths), 2)
        self.assertEqual(len(metrics.weaknesses), 1)
        self.assertEqual(metrics.task_suitability, "good")


class TestComparisonReport(unittest.TestCase):
    """Test ComparisonReport dataclass."""

    def test_report_creation(self):
        """ComparisonReport should be creatable."""
        metrics = AgentPerformanceMetrics(
            agent_id="test",
            agent_name="Test",
            source="builtin",
            duration_seconds=30.0,
            tokens_used=8000,
            cost_usd=0.03,
            quality_score=8.0,
            model_used="claude-3-5-sonnet-20241022"
        )

        report = ComparisonReport(
            task_description="Test task",
            agents_compared=1,
            results=[metrics],
            winner="test"
        )

        self.assertEqual(report.task_description, "Test task")
        self.assertEqual(report.agents_compared, 1)
        self.assertEqual(len(report.results), 1)
        self.assertEqual(report.winner, "test")

    def test_report_to_dict(self):
        """ComparisonReport should convert to dictionary."""
        metrics = AgentPerformanceMetrics(
            agent_id="test",
            agent_name="Test",
            source="builtin",
            duration_seconds=30.0,
            tokens_used=8000,
            cost_usd=0.03,
            quality_score=8.0,
            model_used="claude-3-5-sonnet-20241022"
        )

        report = ComparisonReport(
            task_description="Test task",
            agents_compared=1,
            results=[metrics]
        )

        result = report.to_dict()

        self.assertIsInstance(result, dict)
        self.assertIn("task_description", result)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)


class TestCrossRepoAnalyticsInit(unittest.TestCase):
    """Test CrossRepoAnalytics initialization."""

    def test_analytics_initialization(self):
        """Analytics should initialize with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_dir = Path(tmpdir) / "metrics"

            analytics = CrossRepoAnalytics(metrics_dir=metrics_dir)

            self.assertEqual(analytics.metrics_dir, metrics_dir)
            self.assertTrue(analytics.metrics_dir.exists())

    def test_analytics_creates_metrics_dir(self):
        """Analytics should create metrics directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_dir = Path(tmpdir) / "metrics"

            analytics = CrossRepoAnalytics(metrics_dir=metrics_dir)

            self.assertTrue(analytics.metrics_dir.exists())
            self.assertTrue(analytics.metrics_dir.is_dir())


class TestCompareAgents(unittest.TestCase):
    """Test agent comparison."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.metrics_dir = Path(self.tmpdir) / "metrics"
        self.analytics = CrossRepoAnalytics(metrics_dir=self.metrics_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.tmpdir)

    def test_compare_single_agent(self):
        """Should compare single agent."""
        report = self.analytics.compare_agents(
            task="Review code",
            agents=["code-reviewer"],
            simulate=True
        )

        self.assertEqual(report.agents_compared, 1)
        self.assertEqual(len(report.results), 1)
        self.assertIsNotNone(report.winner)

    def test_compare_multiple_agents(self):
        """Should compare multiple agents."""
        report = self.analytics.compare_agents(
            task="Review code",
            agents=["code-reviewer", "quick-frontend"],
            simulate=True
        )

        self.assertEqual(report.agents_compared, 2)
        self.assertEqual(len(report.results), 2)
        self.assertIsNotNone(report.winner)

    def test_compare_generates_metrics(self):
        """Should generate performance metrics."""
        report = self.analytics.compare_agents(
            task="Build app",
            agents=["frontend-architect"],
            simulate=True
        )

        result = report.results[0]
        self.assertGreater(result.duration_seconds, 0)
        self.assertGreater(result.tokens_used, 0)
        self.assertGreater(result.cost_usd, 0.0)
        self.assertGreater(result.quality_score, 0.0)

    def test_compare_determines_winner(self):
        """Should determine winner based on quality-to-cost ratio."""
        report = self.analytics.compare_agents(
            task="Test task",
            agents=["frontend-architect", "backend-architect"],
            simulate=True
        )

        self.assertIsNotNone(report.winner)
        self.assertIn(report.winner, ["frontend-architect", "backend-architect"])

    def test_compare_generates_recommendation(self):
        """Should generate recommendation text."""
        report = self.analytics.compare_agents(
            task="Test task",
            agents=["code-reviewer"],
            simulate=True
        )

        self.assertIsNotNone(report.recommendation)
        self.assertGreater(len(report.recommendation), 0)

    def test_compare_saves_report(self):
        """Should save report to metrics directory."""
        report = self.analytics.compare_agents(
            task="Test task",
            agents=["code-reviewer"],
            simulate=True
        )

        # Check report was saved
        report_files = list(self.metrics_dir.glob("comparison_*.json"))
        self.assertGreater(len(report_files), 0)


class TestSimulateAgentPerformance(unittest.TestCase):
    """Test agent performance simulation."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = CrossRepoAnalytics()

    def test_simulate_known_agent(self):
        """Should simulate metrics for known agent."""
        metrics = self.analytics._simulate_agent_performance(
            "frontend-architect",
            "Build React app"
        )

        self.assertEqual(metrics.agent_id, "frontend-architect")
        self.assertGreater(metrics.duration_seconds, 0)
        self.assertGreater(metrics.tokens_used, 0)
        self.assertGreater(metrics.cost_usd, 0.0)
        self.assertGreaterEqual(metrics.quality_score, 0.0)
        self.assertLessEqual(metrics.quality_score, 10.0)

    def test_simulate_unknown_agent(self):
        """Should simulate metrics for unknown agent with defaults."""
        metrics = self.analytics._simulate_agent_performance(
            "unknown-agent",
            "Do something"
        )

        self.assertEqual(metrics.agent_id, "unknown-agent")
        self.assertGreater(metrics.duration_seconds, 0)

    def test_simulate_includes_strengths_weaknesses(self):
        """Should include strengths and weaknesses."""
        metrics = self.analytics._simulate_agent_performance(
            "code-reviewer",
            "Review code"
        )

        self.assertIsInstance(metrics.strengths, list)
        self.assertIsInstance(metrics.weaknesses, list)


class TestDetermineWinner(unittest.TestCase):
    """Test winner determination."""

    def setUp(self):
        """Set up test fixtures."""
        self.analytics = CrossRepoAnalytics()

    def test_determine_winner_empty_list(self):
        """Should return None for empty results."""
        winner = self.analytics._determine_winner([])

        self.assertIsNone(winner)

    def test_determine_winner_single_agent(self):
        """Should return single agent as winner."""
        metrics = AgentPerformanceMetrics(
            agent_id="test",
            agent_name="Test",
            source="builtin",
            duration_seconds=30.0,
            tokens_used=8000,
            cost_usd=0.03,
            quality_score=8.0,
            model_used="claude-3-5-sonnet-20241022"
        )

        winner = self.analytics._determine_winner([metrics])

        self.assertEqual(winner, "test")

    def test_determine_winner_quality_to_cost_ratio(self):
        """Should select winner based on quality-to-cost ratio."""
        high_quality_expensive = AgentPerformanceMetrics(
            agent_id="expensive",
            agent_name="Expensive",
            source="builtin",
            duration_seconds=60.0,
            tokens_used=15000,
            cost_usd=0.10,
            quality_score=9.5,
            model_used="claude-3-5-sonnet-20241022"
        )

        medium_quality_cheap = AgentPerformanceMetrics(
            agent_id="cheap",
            agent_name="Cheap",
            source="marketplace",
            duration_seconds=20.0,
            tokens_used=4000,
            cost_usd=0.005,
            quality_score=7.0,
            model_used="claude-3-haiku-20240307"
        )

        winner = self.analytics._determine_winner([
            high_quality_expensive,
            medium_quality_cheap
        ])

        # Winner should be determined by quality/cost ratio
        self.assertIn(winner, ["expensive", "cheap"])


class TestRecommendAgentForTask(unittest.TestCase):
    """Test task-based agent recommendation."""

    @patch('claude_force.agent_router.get_agent_router')
    def test_recommend_returns_agent(self, mock_get_router):
        """Should recommend agent for task."""
        from claude_force.agent_router import AgentMatch

        mock_router = Mock()
        mock_agent = AgentMatch(
            agent_id="test-agent",
            agent_name="Test Agent",
            confidence=0.9,
            source="builtin",
            installed=True
        )
        mock_router.recommend_agents.return_value = [mock_agent]
        mock_get_router.return_value = mock_router

        analytics = CrossRepoAnalytics()
        recommendation = analytics.recommend_agent_for_task(
            task="Build app",
            priority="balanced"
        )

        self.assertIn("recommendation", recommendation)
        self.assertEqual(recommendation["recommendation"], "test-agent")

    @patch('claude_force.agent_router.get_agent_router')
    def test_recommend_no_agents_found(self, mock_get_router):
        """Should handle no agents found."""
        mock_router = Mock()
        mock_router.recommend_agents.return_value = []
        mock_get_router.return_value = mock_router

        analytics = CrossRepoAnalytics()
        recommendation = analytics.recommend_agent_for_task(
            task="Unknown task",
            priority="balanced"
        )

        self.assertIsNone(recommendation["recommendation"])

    @patch('claude_force.agent_router.get_agent_router')
    def test_recommend_different_priorities(self, mock_get_router):
        """Should handle different priority options."""
        from claude_force.agent_router import AgentMatch

        mock_router = Mock()
        mock_agent = AgentMatch(
            agent_id="test",
            agent_name="Test",
            confidence=0.9,
            source="builtin",
            installed=True
        )
        mock_router.recommend_agents.return_value = [mock_agent]
        mock_get_router.return_value = mock_router

        analytics = CrossRepoAnalytics()

        for priority in ["speed", "cost", "quality", "balanced"]:
            recommendation = analytics.recommend_agent_for_task(
                task="Test",
                priority=priority
            )

            self.assertEqual(recommendation["priority"], priority)
            self.assertIn("guidance", recommendation)


class TestGetAnalyticsManager(unittest.TestCase):
    """Test get_analytics_manager function."""

    def test_get_manager_creates_instance(self):
        """get_analytics_manager should create instance."""
        manager = get_analytics_manager()

        self.assertIsInstance(manager, CrossRepoAnalytics)

    def test_get_manager_with_custom_dir(self):
        """get_analytics_manager should accept custom directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_dir = Path(tmpdir) / "metrics"

            manager = get_analytics_manager(metrics_dir=metrics_dir)

            self.assertEqual(manager.metrics_dir, metrics_dir)


if __name__ == "__main__":
    unittest.main()
