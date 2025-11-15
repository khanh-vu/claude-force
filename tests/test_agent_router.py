"""
Agent Router Tests for claude-force.

Tests intelligent agent routing and recommendation functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

from claude_force.agent_router import AgentRouter, AgentMatch, get_agent_router


class TestAgentMatch(unittest.TestCase):
    """Test AgentMatch dataclass."""

    def test_agent_match_creation(self):
        """AgentMatch should be creatable with required fields."""
        match = AgentMatch(
            agent_id="test-agent",
            agent_name="Test Agent",
            confidence=0.85,
            source="builtin",
            installed=True,
        )

        self.assertEqual(match.agent_id, "test-agent")
        self.assertEqual(match.agent_name, "Test Agent")
        self.assertEqual(match.confidence, 0.85)
        self.assertEqual(match.source, "builtin")
        self.assertTrue(match.installed)
        self.assertIsNone(match.plugin_id)
        self.assertEqual(match.expertise, [])

    def test_agent_match_with_optional_fields(self):
        """AgentMatch should handle optional fields."""
        match = AgentMatch(
            agent_id="test",
            agent_name="Test",
            confidence=0.9,
            source="marketplace",
            installed=False,
            plugin_id="test-plugin",
            description="Test description",
            expertise=["python", "api"],
            reason="Matches keywords",
        )

        self.assertEqual(match.plugin_id, "test-plugin")
        self.assertEqual(match.description, "Test description")
        self.assertEqual(match.expertise, ["python", "api"])
        self.assertEqual(match.reason, "Matches keywords")


class TestAgentRouterInit(unittest.TestCase):
    """Test AgentRouter initialization."""

    def test_router_initialization(self):
        """Router should initialize with default settings."""
        router = AgentRouter()

        self.assertTrue(router.include_marketplace)
        self.assertIsNotNone(router._builtin_agents)

    def test_router_without_marketplace(self):
        """Router should work without marketplace."""
        router = AgentRouter(include_marketplace=False)

        self.assertFalse(router.include_marketplace)

    def test_builtin_agents_loaded(self):
        """Router should load builtin agent definitions."""
        router = AgentRouter(include_marketplace=False)

        agents = router._builtin_agents

        self.assertIsInstance(agents, dict)
        self.assertGreater(len(agents), 0)

        # Verify structure
        for agent_id, info in agents.items():
            self.assertIn("keywords", info)
            self.assertIn("description", info)
            self.assertIsInstance(info["keywords"], list)


class TestRecommendAgents(unittest.TestCase):
    """Test agent recommendation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = AgentRouter(include_marketplace=False)

    def test_recommend_frontend_agents(self):
        """Should recommend frontend agents for frontend tasks."""
        matches = self.router.recommend_agents(
            task="Build a React component with state management", top_k=5
        )

        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)

        # Should recommend frontend-architect
        agent_ids = [m.agent_id for m in matches]
        self.assertIn("frontend-architect", agent_ids)

        # Top match should have high confidence
        if matches:
            self.assertGreater(matches[0].confidence, 0.0)

    def test_recommend_backend_agents(self):
        """Should recommend backend agents for backend tasks."""
        matches = self.router.recommend_agents(
            task="Design REST API with microservices architecture", top_k=5
        )

        self.assertGreater(len(matches), 0)

        agent_ids = [m.agent_id for m in matches]
        self.assertIn("backend-architect", agent_ids)

    def test_recommend_ai_agents(self):
        """Should recommend AI agents for AI/ML tasks."""
        matches = self.router.recommend_agents(
            task="Train machine learning model for classification", top_k=5
        )

        self.assertGreater(len(matches), 0)

        agent_ids = [m.agent_id for m in matches]
        self.assertIn("ai-engineer", agent_ids)

    def test_recommend_database_agents(self):
        """Should recommend database agents for database tasks."""
        matches = self.router.recommend_agents(
            task="Design PostgreSQL schema with migrations", top_k=5
        )

        self.assertGreater(len(matches), 0)

        agent_ids = [m.agent_id for m in matches]
        self.assertIn("database-architect", agent_ids)

    def test_recommend_security_agents(self):
        """Should recommend security agents for security tasks."""
        matches = self.router.recommend_agents(
            task="Security audit for authentication vulnerability", top_k=5
        )

        self.assertGreater(len(matches), 0)

        agent_ids = [m.agent_id for m in matches]
        self.assertIn("security-specialist", agent_ids)

    def test_recommend_top_k_limit(self):
        """Should respect top_k limit."""
        matches = self.router.recommend_agents(task="Build a web application", top_k=3)

        self.assertLessEqual(len(matches), 3)

    def test_recommend_min_confidence(self):
        """Should filter by minimum confidence."""
        matches = self.router.recommend_agents(task="Build something", min_confidence=0.5)

        for match in matches:
            self.assertGreaterEqual(match.confidence, 0.5)

    def test_recommend_sorted_by_confidence(self):
        """Recommendations should be sorted by confidence."""
        matches = self.router.recommend_agents(task="Build React frontend with API", top_k=5)

        if len(matches) > 1:
            for i in range(len(matches) - 1):
                self.assertGreaterEqual(matches[i].confidence, matches[i + 1].confidence)


class TestMatchBuiltinAgents(unittest.TestCase):
    """Test builtin agent matching."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = AgentRouter(include_marketplace=False)

    def test_match_builtin_agents(self):
        """Should match builtin agents correctly."""
        matches = self.router._match_builtin_agents("Build React frontend with API integration")

        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)

        # All should be builtin
        for match in matches:
            self.assertEqual(match.source, "builtin")
            self.assertTrue(match.installed)

    def test_match_includes_reason(self):
        """Matches should include reason."""
        matches = self.router._match_builtin_agents("Build React frontend")

        if matches:
            first_match = matches[0]
            self.assertIsNotNone(first_match.reason)
            self.assertGreater(len(first_match.reason), 0)


class TestCalculateConfidence(unittest.TestCase):
    """Test confidence calculation."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = AgentRouter(include_marketplace=False)

    def test_calculate_confidence_single_match(self):
        """Should calculate confidence for single keyword match."""
        keywords = ["react", "frontend", "ui"]
        confidence = self.router._calculate_confidence("build react component", keywords)

        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_confidence_multiple_matches(self):
        """Should boost confidence for multiple matches."""
        keywords = ["react", "frontend", "ui"]

        single_match = self.router._calculate_confidence("build react component", keywords)

        multi_match = self.router._calculate_confidence(
            "build react frontend ui component", keywords
        )

        self.assertGreater(multi_match, single_match)

    def test_calculate_confidence_no_match(self):
        """Should return 0 for no matches."""
        keywords = ["python", "backend"]
        confidence = self.router._calculate_confidence("javascript frontend", keywords)

        self.assertEqual(confidence, 0.0)

    def test_calculate_confidence_empty_keywords(self):
        """Should handle empty keywords."""
        confidence = self.router._calculate_confidence("some task", [])

        self.assertEqual(confidence, 0.0)


class TestAnalyzeTaskComplexity(unittest.TestCase):
    """Test task complexity analysis."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = AgentRouter(include_marketplace=False)

    def test_analyze_simple_task(self):
        """Should identify simple tasks."""
        analysis = self.router.analyze_task_complexity("Fix bug in login function")

        self.assertEqual(analysis["complexity"], "simple")
        self.assertEqual(analysis["estimated_agents"], 1)
        self.assertFalse(analysis["requires_multiple_agents"])

    def test_analyze_medium_task(self):
        """Should identify medium complexity tasks."""
        analysis = self.router.analyze_task_complexity(
            "Implement user authentication with OAuth2 and JWT tokens"
        )

        self.assertEqual(analysis["complexity"], "medium")
        self.assertGreaterEqual(analysis["estimated_agents"], 2)

    def test_analyze_complex_task(self):
        """Should identify complex tasks."""
        analysis = self.router.analyze_task_complexity(
            "Design and build complete microservices architecture with event sourcing, CQRS, and distributed tracing for production deployment"
        )

        self.assertEqual(analysis["complexity"], "complex")
        self.assertGreaterEqual(analysis["estimated_agents"], 3)
        self.assertTrue(analysis["requires_multiple_agents"])

    def test_analyze_identifies_categories(self):
        """Should identify relevant categories."""
        analysis = self.router.analyze_task_complexity(
            "Build React frontend with FastAPI backend and PostgreSQL database"
        )

        categories = analysis["categories"]
        self.assertIn("frontend", categories)
        self.assertIn("backend", categories)
        self.assertIn("database", categories)

    def test_analyze_includes_recommendations(self):
        """Analysis should include agent recommendations."""
        analysis = self.router.analyze_task_complexity("Build React application")

        self.assertIn("recommendations", analysis)
        self.assertIsInstance(analysis["recommendations"], list)
        self.assertGreater(len(analysis["recommendations"]), 0)


class TestGetInstallationPlan(unittest.TestCase):
    """Test installation plan generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = AgentRouter(include_marketplace=False)

    def test_installation_plan_builtin_only(self):
        """Should identify builtin agents."""
        matches = [
            AgentMatch(
                agent_id="test1",
                agent_name="Test 1",
                confidence=0.9,
                source="builtin",
                installed=True,
            )
        ]

        plan = self.router.get_installation_plan(matches)

        self.assertEqual(len(plan["builtin"]), 1)
        self.assertEqual(len(plan["to_install"]), 0)
        self.assertFalse(plan["requires_installation"])
        self.assertEqual(plan["ready_to_use"], 1)

    def test_installation_plan_marketplace_installed(self):
        """Should identify installed marketplace agents."""
        matches = [
            AgentMatch(
                agent_id="test1",
                agent_name="Test 1",
                confidence=0.9,
                source="marketplace",
                installed=True,
                plugin_id="test-plugin",
            )
        ]

        plan = self.router.get_installation_plan(matches)

        self.assertEqual(len(plan["already_installed"]), 1)
        self.assertEqual(len(plan["to_install"]), 0)
        self.assertFalse(plan["requires_installation"])

    def test_installation_plan_marketplace_not_installed(self):
        """Should identify marketplace agents needing installation."""
        matches = [
            AgentMatch(
                agent_id="test1",
                agent_name="Test 1",
                confidence=0.9,
                source="marketplace",
                installed=False,
                plugin_id="test-plugin",
            )
        ]

        plan = self.router.get_installation_plan(matches)

        self.assertEqual(len(plan["to_install"]), 1)
        self.assertTrue(plan["requires_installation"])
        self.assertEqual(plan["ready_to_use"], 0)

    def test_installation_plan_mixed(self):
        """Should handle mixed agent sources."""
        matches = [
            AgentMatch("a1", "A1", 0.9, "builtin", True),
            AgentMatch("a2", "A2", 0.8, "marketplace", True, plugin_id="p1"),
            AgentMatch("a3", "A3", 0.7, "marketplace", False, plugin_id="p2"),
        ]

        plan = self.router.get_installation_plan(matches)

        self.assertEqual(len(plan["builtin"]), 1)
        self.assertEqual(len(plan["already_installed"]), 1)
        self.assertEqual(len(plan["to_install"]), 1)
        self.assertTrue(plan["requires_installation"])
        self.assertEqual(plan["ready_to_use"], 2)
        self.assertEqual(plan["total_agents"], 3)


class TestMarketplaceIntegration(unittest.TestCase):
    """Test marketplace integration."""

    @patch("claude_force.marketplace.get_marketplace_manager")
    def test_marketplace_lazy_loading(self, mock_get_marketplace):
        """Marketplace should be lazy loaded."""
        mock_marketplace = Mock()
        mock_get_marketplace.return_value = mock_marketplace

        router = AgentRouter(include_marketplace=True)

        # Not loaded yet
        self.assertIsNone(router._marketplace)

        # Access triggers loading
        _ = router.marketplace

        # Now loaded
        self.assertIsNotNone(router._marketplace)

    def test_marketplace_disabled(self):
        """Should work without marketplace."""
        router = AgentRouter(include_marketplace=False)

        matches = router.recommend_agents(task="Build something", include_marketplace=False)

        # Should still get builtin recommendations
        self.assertIsInstance(matches, list)

        # All should be builtin
        for match in matches:
            self.assertEqual(match.source, "builtin")


class TestGetAgentRouter(unittest.TestCase):
    """Test get_agent_router function."""

    def test_get_agent_router_creates_instance(self):
        """get_agent_router should create instance."""
        router = get_agent_router()

        self.assertIsInstance(router, AgentRouter)

    def test_get_agent_router_with_marketplace(self):
        """get_agent_router should accept marketplace flag."""
        router = get_agent_router(include_marketplace=False)

        self.assertFalse(router.include_marketplace)


if __name__ == "__main__":
    unittest.main()
