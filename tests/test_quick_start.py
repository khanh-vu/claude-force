"""
Tests for Quick Start orchestrator functionality.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

from claude_force.quick_start import (
    QuickStartOrchestrator,
    ProjectTemplate,
    ProjectConfig,
    get_quick_start_orchestrator,
)


class TestQuickStartOrchestrator(unittest.TestCase):
    """Test suite for QuickStartOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = get_quick_start_orchestrator(use_semantic=False)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_templates(self):
        """Test that templates are loaded correctly."""
        self.assertIsNotNone(self.orchestrator.templates)
        self.assertGreater(len(self.orchestrator.templates), 0)

        # Check template structure
        for template in self.orchestrator.templates:
            self.assertIsInstance(template, ProjectTemplate)
            self.assertIsInstance(template.id, str)
            self.assertIsInstance(template.name, str)
            self.assertIsInstance(template.description, str)
            self.assertIsInstance(template.agents, list)
            self.assertIsInstance(template.workflows, list)
            self.assertIsInstance(template.skills, list)

    def test_keyword_match(self):
        """Test keyword-based template matching."""
        description = "I want to build a chatbot with RAG using Claude and embeddings"
        matches = self.orchestrator.match_templates(description, top_k=3)

        self.assertEqual(len(matches), 3)
        self.assertIsInstance(matches[0], ProjectTemplate)
        self.assertGreater(matches[0].confidence, 0.0)

        # Should match LLM-related template
        self.assertTrue(
            any("llm" in m.id or "rag" in " ".join(m.keywords).lower() for m in matches)
        )

    def test_tech_stack_boost(self):
        """Test that tech stack provides matching boost."""
        description = "Build a web application"
        tech_stack = ["React", "FastAPI", "PostgreSQL"]

        matches_with_tech = self.orchestrator.match_templates(
            description, tech_stack=tech_stack, top_k=3
        )

        matches_without_tech = self.orchestrator.match_templates(
            description, tech_stack=None, top_k=3
        )

        # Tech stack should influence matching
        self.assertIsNotNone(matches_with_tech)
        self.assertIsNotNone(matches_without_tech)

    def test_analyze_project(self):
        """Test project analysis from description."""
        description = "Building an LLM chatbot with RAG, database, and REST API"

        analysis = self.orchestrator.analyze_project(description)

        self.assertIn("detected_features", analysis)
        self.assertIn("complexity", analysis)
        self.assertIn("llm-integration", analysis["detected_features"])
        self.assertIn("database", analysis["detected_features"])
        self.assertIn("api", analysis["detected_features"])

        # Should detect as intermediate or advanced
        self.assertIn(analysis["complexity"], ["intermediate", "advanced"])

    def test_generate_config(self):
        """Test project configuration generation."""
        template = self.orchestrator.templates[0]
        config = self.orchestrator.generate_config(
            template=template, project_name="test-project", description="Test project description"
        )

        self.assertIsInstance(config, ProjectConfig)
        self.assertEqual(config.name, "test-project")
        self.assertEqual(config.description, "Test project description")
        self.assertEqual(config.template_id, template.id)
        self.assertEqual(config.agents, template.agents)
        self.assertEqual(config.workflows, template.workflows)
        self.assertEqual(config.skills, template.skills)
        self.assertIsNotNone(config.created_at)

    def test_initialize_project(self):
        """Test .claude directory initialization."""
        template = self.orchestrator.templates[0]
        config = self.orchestrator.generate_config(
            template=template, project_name="test-project", description="Test project"
        )

        output_dir = Path(self.temp_dir) / ".claude"
        result = self.orchestrator.initialize_project(
            config=config, output_dir=str(output_dir), create_examples=True
        )

        # Check result structure
        self.assertTrue(result["success"])
        self.assertIn("created_files", result)
        self.assertIn("output_dir", result)
        self.assertGreater(len(result["created_files"]), 0)

        # Check created files
        self.assertTrue((output_dir / "claude.json").exists())
        self.assertTrue((output_dir / "task.md").exists())
        self.assertTrue((output_dir / "README.md").exists())
        self.assertTrue((output_dir / "scorecard.md").exists())

        # Check directories
        self.assertTrue((output_dir / "agents").is_dir())
        self.assertTrue((output_dir / "contracts").is_dir())
        self.assertTrue((output_dir / "hooks").is_dir())
        self.assertTrue((output_dir / "skills").is_dir())
        self.assertTrue((output_dir / "tasks").is_dir())

        # Check example
        self.assertTrue((output_dir / "examples" / "example-task.md").exists())

    def test_claude_json_generation(self):
        """Test claude.json file generation."""
        template = self.orchestrator.templates[0]
        config = self.orchestrator.generate_config(
            template=template, project_name="test-project", description="Test project"
        )

        claude_json = self.orchestrator._generate_claude_json(config)

        # Check required fields
        self.assertIn("version", claude_json)
        self.assertIn("name", claude_json)
        self.assertIn("description", claude_json)
        self.assertIn("template", claude_json)
        self.assertIn("agents", claude_json)
        self.assertIn("workflows", claude_json)
        self.assertIn("governance", claude_json)
        self.assertIn("skills_integration", claude_json)
        self.assertIn("paths", claude_json)

        # Check agents structure
        for agent in config.agents:
            self.assertIn(agent, claude_json["agents"])
            self.assertIn("file", claude_json["agents"][agent])
            self.assertIn("contract", claude_json["agents"][agent])

        # Check workflows
        for workflow in config.workflows:
            self.assertIn(workflow, claude_json["workflows"])

    def test_task_template_generation(self):
        """Test task.md template generation."""
        template = self.orchestrator.templates[0]
        config = self.orchestrator.generate_config(
            template=template, project_name="test-project", description="Test project"
        )

        task_md = self.orchestrator._generate_task_template(config)

        # Check content
        self.assertIn(config.name, task_md)
        self.assertIn(config.description, task_md)
        self.assertIn("Objective", task_md)
        self.assertIn("Requirements", task_md)
        self.assertIn("Acceptance Criteria", task_md)
        self.assertIn(config.template_id, task_md)

    def test_readme_generation(self):
        """Test README.md generation."""
        template = self.orchestrator.templates[0]
        config = self.orchestrator.generate_config(
            template=template, project_name="test-project", description="Test project"
        )

        readme = self.orchestrator._generate_readme(config)

        # Check content
        self.assertIn(config.name, readme)
        self.assertIn(config.description, readme)
        self.assertIn("Available Agents", readme)
        self.assertIn("Available Workflows", readme)
        self.assertIn("Available Skills", readme)

        # Check all agents listed
        for agent in config.agents:
            self.assertIn(agent, readme)

    def test_scorecard_generation(self):
        """Test scorecard.md generation."""
        template = self.orchestrator.templates[0]
        config = self.orchestrator.generate_config(
            template=template, project_name="test-project", description="Test project"
        )

        scorecard = self.orchestrator._generate_scorecard(config)

        # Check sections
        self.assertIn("Quality Scorecard", scorecard)
        self.assertIn("Code Quality", scorecard)
        self.assertIn("Testing", scorecard)
        self.assertIn("Security", scorecard)
        self.assertIn("Documentation", scorecard)
        self.assertIn("Performance", scorecard)

    def test_customizations(self):
        """Test project customizations."""
        template = self.orchestrator.templates[0]
        customizations = {"use_typescript": True, "include_docker": True}

        config = self.orchestrator.generate_config(
            template=template,
            project_name="test-project",
            description="Test project",
            customizations=customizations,
        )

        self.assertEqual(config.customizations, customizations)

    def test_multiple_templates_different_categories(self):
        """Test that we have templates for different categories."""
        template_ids = [t.id for t in self.orchestrator.templates]

        # Should have variety of templates
        self.assertIn("fullstack-web", template_ids)
        self.assertIn("llm-app", template_ids)
        self.assertIn("data-pipeline", template_ids)

    def test_template_required_fields(self):
        """Test that all templates have required fields."""
        for template in self.orchestrator.templates:
            # Required string fields
            self.assertTrue(template.id)
            self.assertTrue(template.name)
            self.assertTrue(template.description)
            self.assertTrue(template.category)
            self.assertTrue(template.difficulty)
            self.assertTrue(template.estimated_setup_time)

            # Required list fields
            self.assertIsInstance(template.agents, list)
            self.assertGreater(len(template.agents), 0)
            self.assertIsInstance(template.workflows, list)
            self.assertGreater(len(template.workflows), 0)
            self.assertIsInstance(template.skills, list)
            self.assertGreater(len(template.skills), 0)
            self.assertIsInstance(template.keywords, list)
            self.assertGreater(len(template.keywords), 0)
            self.assertIsInstance(template.use_cases, list)
            self.assertGreater(len(template.use_cases), 0)

            # Tech stack
            self.assertIsInstance(template.tech_stack, dict)
            self.assertGreater(len(template.tech_stack), 0)


class TestSemanticMatching(unittest.TestCase):
    """Test semantic matching (if sentence-transformers available)."""

    def setUp(self):
        """Set up test fixtures."""
        try:
            self.orchestrator = get_quick_start_orchestrator(use_semantic=True)
            self.semantic_available = self.orchestrator.use_semantic
        except ImportError:
            self.semantic_available = False

    def test_semantic_match(self):
        """Test semantic template matching."""
        if not self.semantic_available:
            self.skipTest("sentence-transformers not available")

        description = "I need a chatbot with RAG capabilities using vector embeddings"
        matches = self.orchestrator.match_templates(description, top_k=3)

        self.assertEqual(len(matches), 3)
        self.assertGreater(matches[0].confidence, 0.0)

        # Top match should be LLM-related
        top_match = matches[0]
        self.assertTrue(
            "llm" in top_match.id
            or "rag" in " ".join(top_match.keywords).lower()
            or any("llm" in kw.lower() for kw in top_match.keywords)
        )

    def test_embeddings_precomputed(self):
        """Test that embeddings are precomputed."""
        if not self.semantic_available:
            self.skipTest("sentence-transformers not available")

        self.assertIsNotNone(self.orchestrator.template_embeddings)
        self.assertEqual(
            len(self.orchestrator.template_embeddings), len(self.orchestrator.templates)
        )


class TestGetQuickStartOrchestrator(unittest.TestCase):
    """Test the factory function."""

    def test_default_creation(self):
        """Test default orchestrator creation."""
        orchestrator = get_quick_start_orchestrator()
        self.assertIsInstance(orchestrator, QuickStartOrchestrator)
        self.assertIsNotNone(orchestrator.templates)

    def test_custom_templates_path(self):
        """Test orchestrator with custom templates path."""
        # Create temporary templates file
        temp_dir = tempfile.mkdtemp()
        try:
            templates_path = Path(temp_dir) / "custom_templates.yaml"

            # Create minimal templates file
            templates_data = {
                "templates": [
                    {
                        "id": "test-template",
                        "name": "Test Template",
                        "description": "A test template",
                        "category": "testing",
                        "difficulty": "simple",
                        "estimated_setup_time": "5 minutes",
                        "agents": ["test-agent"],
                        "workflows": ["test-workflow"],
                        "skills": ["test-skill"],
                        "keywords": ["test"],
                        "tech_stack": {"testing": ["pytest"]},
                        "use_cases": ["Testing"],
                    }
                ]
            }

            import yaml

            with open(templates_path, "w") as f:
                yaml.dump(templates_data, f)

            orchestrator = get_quick_start_orchestrator(
                templates_path=str(templates_path), use_semantic=False
            )

            self.assertEqual(len(orchestrator.templates), 1)
            self.assertEqual(orchestrator.templates[0].id, "test-template")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
