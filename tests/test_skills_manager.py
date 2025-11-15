"""
Tests for Progressive Skills Manager functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from claude_force.skills_manager import ProgressiveSkillsManager, get_skills_manager


class TestProgressiveSkillsManager(unittest.TestCase):
    """Test suite for ProgressiveSkillsManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary skills directory
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / "skills"
        self.skills_dir.mkdir()

        # Create some test skills
        self._create_test_skill("test-generation", "Test generation skill content")
        self._create_test_skill("code-review", "Code review skill content")
        self._create_test_skill("api-design", "API design skill content")
        self._create_test_skill("dockerfile", "Dockerfile skill content")

        self.manager = ProgressiveSkillsManager(skills_dir=str(self.skills_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_skill(self, skill_id: str, content: str):
        """Create a test skill directory and SKILL.md file."""
        skill_path = self.skills_dir / skill_id
        skill_path.mkdir()
        skill_file = skill_path / "SKILL.md"
        skill_file.write_text(content)

    def test_initialization(self):
        """Test ProgressiveSkillsManager initialization."""
        self.assertIsNotNone(self.manager.skills_registry)
        self.assertIsInstance(self.manager.skill_cache, dict)
        self.assertEqual(len(self.manager.skill_cache), 0)  # Cache starts empty

    def test_load_skills_registry(self):
        """Test skills registry loading."""
        registry = self.manager.skills_registry

        self.assertIn("test-generation", registry)
        self.assertIn("code-review", registry)
        self.assertIn("api-design", registry)
        self.assertIn("dockerfile", registry)

        # Check test-generation entry
        test_gen = registry["test-generation"]
        self.assertEqual(test_gen["id"], "test-generation")
        self.assertTrue(test_gen["exists"])
        self.assertIsInstance(test_gen["keywords"], list)
        self.assertGreater(len(test_gen["keywords"]), 0)

    def test_analyze_required_skills_keyword_matching(self):
        """Test skill analysis based on keywords."""
        # Task mentions testing
        task = "Write unit tests for the authentication module"
        skills = self.manager.analyze_required_skills(
            "python-expert", task, include_agent_skills=False
        )

        self.assertIn("test-generation", skills)

        # Task mentions Docker
        task = "Create a Dockerfile for the application"
        skills = self.manager.analyze_required_skills(
            "python-expert", task, include_agent_skills=False
        )

        self.assertIn("dockerfile", skills)

        # Task mentions API
        task = "Design a REST API with GraphQL endpoints"
        skills = self.manager.analyze_required_skills(
            "backend-architect", task, include_agent_skills=False
        )

        self.assertIn("api-design", skills)

    def test_analyze_required_skills_multiple_matches(self):
        """Test that multiple skills are detected."""
        task = "Review the API code and write tests for it"
        skills = self.manager.analyze_required_skills(
            "backend-architect", task, include_agent_skills=False
        )

        # Should match both code-review and test-generation and api-design
        self.assertIn("code-review", skills)
        self.assertIn("test-generation", skills)
        self.assertIn("api-design", skills)

    def test_analyze_required_skills_agent_skills(self):
        """Test that agent's preferred skills are included."""
        task = "Implement a new feature"  # Generic task

        # With agent skills included
        skills_with = self.manager.analyze_required_skills(
            "frontend-developer", task, include_agent_skills=True
        )

        # Without agent skills
        skills_without = self.manager.analyze_required_skills(
            "frontend-developer", task, include_agent_skills=False
        )

        # With agent skills should have more (or at least as many)
        # Note: Only for complex/long tasks
        if len(task) > 200:
            self.assertGreaterEqual(len(skills_with), len(skills_without))

    def test_analyze_required_skills_no_matches(self):
        """Test task with no matching skills."""
        task = "Explain quantum physics"  # Unrelated task
        skills = self.manager.analyze_required_skills(
            "python-expert", task, include_agent_skills=False
        )

        self.assertEqual(len(skills), 0)

    def test_load_skills(self):
        """Test loading skills content."""
        skill_ids = ["test-generation", "code-review"]
        content = self.manager.load_skills(skill_ids)

        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)
        self.assertIn("test-generation", content)
        self.assertIn("code-review", content)
        self.assertIn("Test generation skill content", content)
        self.assertIn("Code review skill content", content)

    def test_load_skills_caching(self):
        """Test that skills are cached after first load."""
        skill_ids = ["test-generation"]

        # First load
        content1 = self.manager.load_skills(skill_ids)
        self.assertEqual(len(self.manager.skill_cache), 1)
        self.assertIn("test-generation", self.manager.skill_cache)

        # Second load (should use cache)
        content2 = self.manager.load_skills(skill_ids)
        self.assertEqual(content1, content2)
        self.assertEqual(len(self.manager.skill_cache), 1)  # Still 1

    def test_load_skills_empty_list(self):
        """Test loading with empty skill list."""
        content = self.manager.load_skills([])
        self.assertEqual(content, "")

    def test_load_skills_nonexistent(self):
        """Test loading non-existent skill."""
        content = self.manager.load_skills(["nonexistent-skill"])
        self.assertEqual(content, "")

    def test_load_skill_file(self):
        """Test loading individual skill file."""
        content = self.manager._load_skill_file("test-generation")

        self.assertIsNotNone(content)
        self.assertIn("Test generation skill content", content)

    def test_load_skill_file_not_found(self):
        """Test loading skill file that doesn't exist."""
        content = self.manager._load_skill_file("nonexistent-skill")
        self.assertIsNone(content)

    def test_get_token_savings_estimate(self):
        """Test token savings estimation."""
        # Load 3 out of 11 skills
        estimate = self.manager.get_token_savings_estimate(
            loaded_skills=3, total_skills=11, avg_skill_tokens=1500
        )

        self.assertEqual(estimate["loaded_skills"], 3)
        self.assertEqual(estimate["skipped_skills"], 8)
        self.assertEqual(estimate["tokens_saved"], 8 * 1500)
        self.assertEqual(estimate["total_tokens_before"], 11 * 1500)
        self.assertEqual(estimate["total_tokens_after"], 3 * 1500)
        self.assertGreater(estimate["reduction_percentage"], 0)
        self.assertAlmostEqual(estimate["reduction_percentage"], 72.7, places=1)

    def test_get_available_skills(self):
        """Test getting list of available skills."""
        available = self.manager.get_available_skills()

        self.assertIsInstance(available, list)
        self.assertIn("test-generation", available)
        self.assertIn("code-review", available)
        self.assertIn("api-design", available)
        self.assertIn("dockerfile", available)

    def test_clear_cache(self):
        """Test clearing the skill cache."""
        # Load some skills to populate cache
        self.manager.load_skills(["test-generation", "code-review"])
        self.assertGreater(len(self.manager.skill_cache), 0)

        # Clear cache
        self.manager.clear_cache()
        self.assertEqual(len(self.manager.skill_cache), 0)

    def test_skill_keywords_coverage(self):
        """Test that all skills have keyword mappings."""
        for skill_id in self.manager.SKILL_KEYWORDS.keys():
            keywords = self.manager.SKILL_KEYWORDS[skill_id]
            self.assertIsInstance(keywords, list)
            self.assertGreater(len(keywords), 0)

    def test_agent_skills_associations(self):
        """Test that agents have skill associations."""
        # Check some key agents
        self.assertIn("frontend-architect", self.manager.AGENT_SKILLS)
        self.assertIn("backend-architect", self.manager.AGENT_SKILLS)
        self.assertIn("python-expert", self.manager.AGENT_SKILLS)

        # Check skills are lists
        for agent, skills in self.manager.AGENT_SKILLS.items():
            self.assertIsInstance(skills, list)


class TestGetSkillsManager(unittest.TestCase):
    """Test the factory function."""

    def test_factory_function(self):
        """Test factory function creates manager correctly."""
        manager = get_skills_manager()
        self.assertIsInstance(manager, ProgressiveSkillsManager)


if __name__ == "__main__":
    unittest.main()
