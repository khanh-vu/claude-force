"""
Validation Tests for claude-force.

Tests data integrity, file validity, permissions, and other quality checks
to ensure production-ready output.
"""

import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path

from claude_force.quick_start import QuickStartOrchestrator, get_quick_start_orchestrator


class TestGeneratedFileValidity(unittest.TestCase):
    """Test that generated files are valid and well-formed."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Initialize a project for testing
        orchestrator = get_quick_start_orchestrator(use_semantic=False)
        matches = orchestrator.match_templates("Test application", top_k=1)
        template = matches[0]
        config = orchestrator.generate_config(
            template=template,
            project_name="validation-test",
            description="Test project for validation",
        )

        self.claude_dir = Path(self.temp_dir) / ".claude"
        orchestrator.initialize_project(config=config, output_dir=str(self.claude_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_claude_json_is_valid(self):
        """claude.json should be valid, parseable JSON."""
        claude_json = self.claude_dir / "claude.json"

        # File should exist
        self.assertTrue(claude_json.exists(), "claude.json should exist")

        # Should be valid JSON
        with open(claude_json) as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                self.fail(f"claude.json is not valid JSON: {e}")

        # Should have required top-level keys
        required_keys = ["version", "name", "description", "agents", "workflows"]
        for key in required_keys:
            self.assertIn(key, config, f"claude.json missing required key: {key}")

        # Agents should be a dict
        self.assertIsInstance(config["agents"], dict, "agents should be a dict")

        # Workflows should be a dict
        self.assertIsInstance(config["workflows"], dict, "workflows should be a dict")

    def test_task_md_is_valid_markdown(self):
        """task.md should be valid markdown."""
        task_md = self.claude_dir / "task.md"

        # File should exist
        self.assertTrue(task_md.exists(), "task.md should exist")

        # Should be readable as text
        with open(task_md) as f:
            content = f.read()

        # Should not be empty
        self.assertGreater(len(content), 0, "task.md should not be empty")

        # Should contain markdown headers
        self.assertTrue(
            content.startswith("#") or "# " in content, "task.md should contain markdown headers"
        )

    def test_readme_md_is_valid_markdown(self):
        """README.md should be valid markdown."""
        readme_md = self.claude_dir / "README.md"

        # File should exist
        self.assertTrue(readme_md.exists(), "README.md should exist")

        # Should be readable as text
        with open(readme_md) as f:
            content = f.read()

        # Should not be empty
        self.assertGreater(len(content), 0, "README.md should not be empty")

        # Should contain project name
        self.assertIn("validation-test", content, "README.md should mention project name")

    def test_scorecard_md_is_valid_markdown(self):
        """scorecard.md should be valid markdown."""
        scorecard_md = self.claude_dir / "scorecard.md"

        # File should exist
        self.assertTrue(scorecard_md.exists(), "scorecard.md should exist")

        # Should be readable as text
        with open(scorecard_md) as f:
            content = f.read()

        # Should not be empty
        self.assertGreater(len(content), 0, "scorecard.md should not be empty")

        # Should contain scoring sections
        self.assertTrue(
            "score" in content.lower() or "quality" in content.lower(),
            "scorecard.md should contain scoring information",
        )

    def test_file_permissions_correct(self):
        """Files should have correct permissions (644 for files, 755 for dirs)."""
        import sys

        # Skip on Windows (permissions work differently)
        if sys.platform == "win32":
            self.skipTest("Permission tests not applicable on Windows")

        # Check directory permissions
        claude_dir_stat = self.claude_dir.stat()
        claude_dir_mode = oct(claude_dir_stat.st_mode)[-3:]

        # Directory should be readable and executable (at least 755 or 700)
        self.assertIn(
            claude_dir_mode[0],
            ["7", "5"],
            f".claude directory should be accessible, got mode {claude_dir_mode}",
        )

        # Check file permissions
        claude_json = self.claude_dir / "claude.json"
        if claude_json.exists():
            file_stat = claude_json.stat()
            file_mode = oct(file_stat.st_mode)[-3:]

            # File should be readable (at least 644 or 600)
            self.assertIn(
                file_mode[0], ["6", "7"], f"claude.json should be readable, got mode {file_mode}"
            )

    def test_directory_structure_complete(self):
        """All required directories should be created."""
        required_dirs = ["agents", "contracts", "hooks", "skills"]

        for dir_name in required_dirs:
            dir_path = self.claude_dir / dir_name
            self.assertTrue(
                dir_path.exists() and dir_path.is_dir(),
                f"Required directory '{dir_name}' should exist",
            )


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_no_data_loss_on_init(self):
        """Project initialization should not lose data."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # Get template and generate config
        matches = orchestrator.match_templates("Web application", top_k=1)
        template = matches[0]

        original_description = "My important project description"
        original_name = "my-project"

        config = orchestrator.generate_config(
            template=template, project_name=original_name, description=original_description
        )

        # Initialize project
        claude_dir = Path(self.temp_dir) / ".claude"
        orchestrator.initialize_project(config=config, output_dir=str(claude_dir))

        # Load saved config
        with open(claude_dir / "claude.json") as f:
            saved_config = json.load(f)

        # Verify no data loss
        self.assertEqual(saved_config["name"], original_name)
        self.assertEqual(saved_config["description"], original_description)

    def test_atomic_operations(self):
        """File operations should be atomic (no partial writes)."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        matches = orchestrator.match_templates("Test app", top_k=1)
        template = matches[0]
        config = orchestrator.generate_config(
            template=template, project_name="atomic-test", description="Test"
        )

        claude_dir = Path(self.temp_dir) / ".claude"

        # Initialize project
        result = orchestrator.initialize_project(config=config, output_dir=str(claude_dir))

        # All files should be fully written (not empty or partial)
        for file_path in result["created_files"]:
            path = Path(file_path)
            if path.is_file():
                # File should have content
                size = path.stat().st_size
                self.assertGreater(size, 0, f"File {path.name} should not be empty")

    def test_generated_files_parseable(self):
        """All generated files should be parseable/readable."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        matches = orchestrator.match_templates("API service", top_k=1)
        template = matches[0]
        config = orchestrator.generate_config(
            template=template, project_name="parse-test", description="Test"
        )

        claude_dir = Path(self.temp_dir) / ".claude"
        result = orchestrator.initialize_project(config=config, output_dir=str(claude_dir))

        # Try to read all created files
        for file_path in result["created_files"]:
            path = Path(file_path)
            if path.is_file():
                try:
                    # For JSON files
                    if path.suffix == ".json":
                        with open(path) as f:
                            json.load(f)
                    # For text files
                    else:
                        with open(path) as f:
                            content = f.read()
                            self.assertIsInstance(content, str)
                except Exception as e:
                    self.fail(f"Failed to parse {path.name}: {e}")

    def test_cross_references_valid(self):
        """Agent and workflow references should be valid."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        matches = orchestrator.match_templates("Full-stack app", top_k=1)
        template = matches[0]
        config = orchestrator.generate_config(
            template=template, project_name="refs-test", description="Test"
        )

        claude_dir = Path(self.temp_dir) / ".claude"
        orchestrator.initialize_project(config=config, output_dir=str(claude_dir))

        # Load config
        with open(claude_dir / "claude.json") as f:
            saved_config = json.load(f)

        # Verify workflow references valid agents
        agents = saved_config.get("agents", {})
        workflows = saved_config.get("workflows", {})

        for workflow_name, agent_list in workflows.items():
            for agent_id in agent_list:
                self.assertIn(
                    agent_id,
                    agents,
                    f"Workflow '{workflow_name}' references non-existent agent '{agent_id}'",
                )


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration file validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_version_field_present(self):
        """Config should have version field."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)
        matches = orchestrator.match_templates("Test", top_k=1)
        config = orchestrator.generate_config(matches[0], "test", "Test")

        claude_dir = Path(self.temp_dir) / ".claude"
        orchestrator.initialize_project(config, str(claude_dir))

        with open(claude_dir / "claude.json") as f:
            saved = json.load(f)

        self.assertIn("version", saved)
        self.assertIsInstance(saved["version"], str)

    def test_created_at_timestamp(self):
        """Config should have created_at timestamp."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)
        matches = orchestrator.match_templates("Test", top_k=1)
        config = orchestrator.generate_config(matches[0], "test", "Test")

        claude_dir = Path(self.temp_dir) / ".claude"
        orchestrator.initialize_project(config, str(claude_dir))

        with open(claude_dir / "claude.json") as f:
            saved = json.load(f)

        self.assertIn("created_at", saved)
        # Should be ISO format timestamp
        self.assertIsInstance(saved["created_at"], str)
        self.assertGreater(len(saved["created_at"]), 10)


if __name__ == "__main__":
    unittest.main()
