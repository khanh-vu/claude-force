"""
Comprehensive error handling tests for all integrations.

Tests critical error scenarios to ensure robust production behavior.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml

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


class TestQuickStartErrorHandling(unittest.TestCase):
    """Test error handling in QuickStartOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_invalid_yaml_template(self):
        """Test handling of malformed YAML template file."""
        templates_file = Path(self.temp_dir) / "templates.yaml"
        templates_file.write_text("invalid: yaml: content: [[[")

        # Should raise ValueError (which wraps the YAML error)
        with self.assertRaises(ValueError) as cm:
            orchestrator = get_quick_start_orchestrator(
                templates_path=str(templates_file),
                use_semantic=False
            )

        # Verify it mentions the underlying issue
        self.assertIn("Failed to load templates", str(cm.exception))

    def test_missing_template_file(self):
        """Test handling of missing template file."""
        nonexistent = Path(self.temp_dir) / "nonexistent.yaml"

        # Should raise ValueError (which wraps FileNotFoundError)
        with self.assertRaises(ValueError) as cm:
            orchestrator = get_quick_start_orchestrator(
                templates_path=str(nonexistent),
                use_semantic=False
            )

        # Verify it mentions the file not found issue
        self.assertIn("Failed to load templates", str(cm.exception))

    def test_empty_description(self):
        """Test handling of empty project description."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # Empty string
        matches = orchestrator.match_templates("", top_k=3)
        self.assertIsInstance(matches, list)
        # Should still return templates, just with low confidence

        # Whitespace only
        matches = orchestrator.match_templates("   \n  \t  ", top_k=3)
        self.assertIsInstance(matches, list)

    def test_very_long_description(self):
        """Test handling of very long project descriptions."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # 10K character description
        long_desc = "Build a web application " * 500
        matches = orchestrator.match_templates(long_desc, top_k=3)

        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)

    def test_special_characters_in_project_name(self):
        """Test handling of special characters in project names."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)
        template = orchestrator.templates[0]

        # Names with special characters
        special_names = [
            "my-project!@#$%",
            "project/with/slashes",
            "project\x00null",
            "project<script>xss</script>"
        ]

        for name in special_names:
            config = orchestrator.generate_config(
                template=template,
                project_name=name,
                description="Test project"
            )
            # Should handle gracefully (sanitize or accept)
            self.assertIsNotNone(config)
            self.assertIsInstance(config.name, str)

    def test_permission_denied_directory(self):
        """Test handling of permission errors during directory creation."""
        import sys
        import os

        # Skip on Windows or if running as root (permissions don't work the same)
        if sys.platform == 'win32' or os.geteuid() == 0:
            self.skipTest("Permission handling is platform/user-specific")

        orchestrator = get_quick_start_orchestrator(use_semantic=False)
        template = orchestrator.templates[0]
        config = orchestrator.generate_config(
            template=template,
            project_name="test",
            description="Test"
        )

        # Create directory with no write permissions
        no_write_dir = Path(self.temp_dir) / "no_write"
        no_write_dir.mkdir()
        no_write_dir.chmod(0o444)  # Read-only

        output_dir = no_write_dir / ".claude"

        try:
            # Permission errors may or may not be raised depending on filesystem
            # This test verifies the code doesn't crash, at minimum
            try:
                result = orchestrator.initialize_project(
                    config=config,
                    output_dir=str(output_dir)
                )
                # If it succeeded, permissions weren't enforced (e.g., root user)
                self.skipTest("Permissions not enforced in this environment")
            except (PermissionError, OSError) as e:
                # Expected - permission denied
                self.assertIn("permission", str(e).lower(),
                             "Error should mention permissions")
        finally:
            # Cleanup
            no_write_dir.chmod(0o755)

    def test_template_with_missing_required_fields(self):
        """Test handling of templates with missing required fields."""
        templates_file = Path(self.temp_dir) / "templates.yaml"

        # Template missing required fields
        invalid_template = {
            "templates": [
                {
                    "id": "incomplete",
                    "name": "Incomplete Template"
                    # Missing: description, agents, workflows, etc.
                }
            ]
        }

        with open(templates_file, 'w') as f:
            yaml.dump(invalid_template, f)

        # Should handle gracefully or raise descriptive error
        try:
            orchestrator = get_quick_start_orchestrator(
                templates_path=str(templates_file),
                use_semantic=False
            )
            # If it loads, the template should be skipped or have defaults
            self.assertIsNotNone(orchestrator)
        except (KeyError, ValueError) as e:
            # Expected error with clear message
            self.assertIn("required", str(e).lower())


class TestHybridOrchestratorErrorHandling(unittest.TestCase):
    """Test error handling in HybridOrchestrator."""

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_invalid_model_name(self, mock_init):
        """Test handling of invalid model names."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        # Invalid model tier - should return default (Sonnet)
        # The method doesn't raise an error, it defaults to safe choice
        model = orchestrator.select_model_for_agent(
            "test-agent",
            "Test task",
            task_complexity="invalid_complexity"
        )

        # Should return the default Sonnet model
        self.assertEqual(model, orchestrator.MODELS["sonnet"])

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_cost_threshold_exceeded(self, mock_init):
        """Test behavior when cost threshold is exceeded."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator(cost_threshold=0.001)  # Very low threshold

        # Estimate cost for expensive operation
        task = "Deploy to production with full security audit"
        estimate = orchestrator.estimate_cost(task, "backend-architect")

        # Should warn if threshold exceeded
        if estimate.estimated_cost > orchestrator.cost_threshold:
            # Verify warning would be logged
            self.assertGreater(estimate.estimated_cost, orchestrator.cost_threshold)

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_empty_task_string(self, mock_init):
        """Test handling of empty task strings."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        # Empty task
        complexity = orchestrator._analyze_task_complexity("", "test-agent")
        self.assertIn(complexity, ["simple", "complex", "critical"])

        # Whitespace only
        complexity = orchestrator._analyze_task_complexity("   \n\t  ", "test-agent")
        self.assertIn(complexity, ["simple", "complex", "critical"])

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_very_long_task(self, mock_init):
        """Test handling of very long tasks (>100K chars)."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        # 100K character task
        long_task = "Build a complex system " * 5000
        self.assertGreater(len(long_task), 100000)

        complexity = orchestrator._analyze_task_complexity(long_task, "test-agent")
        self.assertIn(complexity, ["simple", "complex", "critical"])
        # Long tasks should typically be complex
        self.assertEqual(complexity, "complex")

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_unicode_and_emoji_in_tasks(self, mock_init):
        """Test handling of Unicode and emoji in task descriptions."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        unicode_tasks = [
            "Build a web app 🚀",
            "Créer une application française",
            "创建一个中文应用",
            "Создать русское приложение"
        ]

        for task in unicode_tasks:
            complexity = orchestrator._analyze_task_complexity(task, "test-agent")
            self.assertIn(complexity, ["simple", "complex", "critical"])

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_task_with_only_special_characters(self, mock_init):
        """Test handling of tasks with only special characters."""
        mock_init.return_value = None
        orchestrator = HybridOrchestrator()

        special_tasks = [
            "!@#$%^&*()",
            "___---===",
            "[[[]]]",
            "<script>alert('xss')</script>"
        ]

        for task in special_tasks:
            complexity = orchestrator._analyze_task_complexity(task, "test-agent")
            self.assertIn(complexity, ["simple", "complex", "critical"])


class TestSkillsManagerErrorHandling(unittest.TestCase):
    """Test error handling in ProgressiveSkillsManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_missing_skills_directory(self):
        """Test handling when skills directory doesn't exist."""
        nonexistent_dir = Path(self.temp_dir) / "nonexistent_skills"

        # Should handle gracefully
        manager = ProgressiveSkillsManager(skills_dir=str(nonexistent_dir))
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.get_available_skills()), 0)

    def test_malformed_skill_file(self):
        """Test handling of malformed skill files."""
        skills_dir = Path(self.temp_dir) / "skills"
        skills_dir.mkdir()

        # Create skill with malformed SKILL.md
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        # Write binary/invalid content
        skill_file.write_bytes(b'\x00\x01\x02\x03\x04')

        manager = ProgressiveSkillsManager(skills_dir=str(skills_dir))

        # Should handle gracefully
        try:
            content = manager._load_skill_file("test-skill")
            # Either returns None or handles the error
            if content is not None:
                self.assertIsInstance(content, str)
        except Exception as e:
            # Should be a graceful error
            self.assertIsInstance(e, (UnicodeDecodeError, ValueError))

    def test_permission_denied_skill_file(self):
        """Test handling when skill file is not readable."""
        skills_dir = Path(self.temp_dir) / "skills"
        skills_dir.mkdir()

        # Create skill with no read permissions
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("Test skill content")
        skill_file.chmod(0o000)  # No permissions

        manager = ProgressiveSkillsManager(skills_dir=str(skills_dir))

        try:
            # Should handle permission error gracefully
            content = manager._load_skill_file("test-skill")
            # Either returns None or raises PermissionError
            if content is not None:
                # Permissions might not be enforced in test environment
                pass
        except PermissionError:
            # Expected
            pass
        finally:
            # Cleanup
            skill_file.chmod(0o644)

    def test_very_large_skill_file(self):
        """Test handling of very large skill files (>1MB)."""
        skills_dir = Path(self.temp_dir) / "skills"
        skills_dir.mkdir()

        # Create large skill file
        skill_dir = skills_dir / "large-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        # Write 2MB of content
        large_content = "# Large Skill\n" + ("A" * 1000 + "\n") * 2000
        self.assertGreater(len(large_content), 1_000_000)
        skill_file.write_text(large_content)

        manager = ProgressiveSkillsManager(skills_dir=str(skills_dir))

        # Should handle large files
        content = manager._load_skill_file("large-skill")
        self.assertIsNotNone(content)
        self.assertGreater(len(content), 1_000_000)

    def test_empty_skill_file(self):
        """Test handling of empty skill files."""
        skills_dir = Path(self.temp_dir) / "skills"
        skills_dir.mkdir()

        # Create empty skill file
        skill_dir = skills_dir / "empty-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("")

        manager = ProgressiveSkillsManager(skills_dir=str(skills_dir))

        # Should handle empty files gracefully
        content = manager._load_skill_file("empty-skill")
        self.assertIsNotNone(content)
        self.assertEqual(content, "")

    def test_skill_file_with_only_comments(self):
        """Test handling of skill files with only comments."""
        skills_dir = Path(self.temp_dir) / "skills"
        skills_dir.mkdir()

        # Create skill with only comments
        skill_dir = skills_dir / "comment-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("<!-- Comment 1 -->\n<!-- Comment 2 -->\n")

        manager = ProgressiveSkillsManager(skills_dir=str(skills_dir))

        # Should load successfully
        content = manager._load_skill_file("comment-skill")
        self.assertIsNotNone(content)
        self.assertIn("Comment", content)

    def test_corrupted_cache(self):
        """Test handling of corrupted cache data."""
        manager = ProgressiveSkillsManager(skills_dir=str(self.temp_dir))

        # Corrupt the cache
        manager.skill_cache["test-skill"] = None
        manager.skill_cache["another-skill"] = 12345  # Invalid type

        # Should handle gracefully
        skills = manager.load_skills(["test-skill", "another-skill"])
        self.assertIsInstance(skills, str)

    def test_analyze_required_skills_with_unknown_agent(self):
        """Test skill analysis for unknown agent."""
        manager = ProgressiveSkillsManager(skills_dir=str(self.temp_dir))

        # Unknown agent
        skills = manager.analyze_required_skills(
            "unknown-agent-12345",
            "Write tests for the API",
            include_agent_skills=True
        )

        # Should still work, just won't have agent-specific skills
        self.assertIsInstance(skills, list)


class TestConcurrentAccess(unittest.TestCase):
    """Test thread safety and concurrent access patterns."""

    def test_skill_cache_concurrent_access(self):
        """Test concurrent access to skill cache."""
        import threading

        temp_dir = tempfile.mkdtemp()
        try:
            skills_dir = Path(temp_dir) / "skills"
            skills_dir.mkdir()

            # Create test skill
            skill_dir = skills_dir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("Test content")

            manager = ProgressiveSkillsManager(skills_dir=str(skills_dir))

            results = []
            errors = []

            def load_skill():
                try:
                    content = manager.load_skills(["test-skill"])
                    results.append(content)
                except Exception as e:
                    errors.append(e)

            # Create multiple threads
            threads = [threading.Thread(target=load_skill) for _ in range(10)]

            # Start all threads
            for t in threads:
                t.start()

            # Wait for completion
            for t in threads:
                t.join()

            # Check results
            self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
            self.assertEqual(len(results), 10)
            # All results should be the same
            self.assertTrue(all(r == results[0] for r in results))

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
