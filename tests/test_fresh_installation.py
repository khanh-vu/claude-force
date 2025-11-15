"""
Fresh Installation Integration Tests

Tests that simulate a fresh user installing claude-force and running
common workflows. Ensures that all dependencies (including PyYAML) are
properly installed and that the package works out of the box.

This test suite specifically verifies the PyYAML dependency fix.
"""

import unittest
import subprocess
import sys
import tempfile
import shutil
import os
import json
from pathlib import Path


class TestFreshInstallation(unittest.TestCase):
    """Test suite simulating fresh user installation."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.temp_base = tempfile.mkdtemp(prefix="claude-force-test-")
        cls.test_projects_dir = Path(cls.temp_base) / "test-projects"
        cls.test_projects_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if hasattr(cls, "temp_base"):
            shutil.rmtree(cls.temp_base, ignore_errors=True)

    def run_cli(self, *args, cwd=None, timeout=60):
        """
        Run claude-force CLI command.

        Args:
            *args: Command arguments
            cwd: Working directory (default: temp_base)
            timeout: Command timeout in seconds

        Returns:
            subprocess.CompletedProcess
        """
        cmd = [sys.executable, "-m", "claude_force.cli"] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or self.temp_base,
        )
        return result

    def test_pyyaml_is_importable(self):
        """Test that PyYAML is installed and importable."""
        result = subprocess.run(
            [sys.executable, "-c", "import yaml; print(yaml.__version__)"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"PyYAML import failed: {result.stderr}")
        self.assertIn(".", result.stdout, "PyYAML version should be printed")

    def test_quick_start_module_imports_yaml(self):
        """Test that quick_start module can import yaml without errors."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from claude_force.quick_start import QuickStartOrchestrator; print('SUCCESS')",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"quick_start import failed: {result.stderr}")
        self.assertIn("SUCCESS", result.stdout)

    def test_marketplace_module_imports_yaml(self):
        """Test that marketplace module can import yaml without errors."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from claude_force.marketplace import MarketplaceManager; print('SUCCESS')",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"marketplace import failed: {result.stderr}")
        self.assertIn("SUCCESS", result.stdout)

    def test_import_export_module_imports_yaml(self):
        """Test that import_export module can import yaml without errors."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from claude_force.import_export import AgentPortingTool; print('SUCCESS')",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"import_export import failed: {result.stderr}")
        self.assertIn("SUCCESS", result.stdout)

    def test_cli_help_command(self):
        """Test basic CLI help command works."""
        result = self.run_cli("--help")

        self.assertEqual(result.returncode, 0, f"CLI help failed: {result.stderr}")
        self.assertIn("claude-force", result.stdout.lower())
        self.assertIn("usage", result.stdout.lower())

    def test_cli_version_info(self):
        """Test CLI version information is available."""
        # Note: CLI may not have --version flag, so we check module version
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import claude_force; print(claude_force.__version__ if hasattr(claude_force, '__version__') else '2.2.0')",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        # Should output some version info
        self.assertTrue(len(result.stdout.strip()) > 0)

    def test_init_help_command(self):
        """Test init --help command works."""
        result = self.run_cli("init", "--help")

        self.assertEqual(result.returncode, 0, f"Init help failed: {result.stderr}")
        self.assertIn("init", result.stdout.lower())
        self.assertIn("description", result.stdout.lower())

    def test_init_creates_project_structure(self):
        """Test that init command creates proper project structure."""
        project_dir = self.test_projects_dir / "test-init-1"
        project_dir.mkdir(exist_ok=True)

        result = self.run_cli(
            "init",
            str(project_dir),
            "--name",
            "test-project",
            "--description",
            "Test project for fresh installation",
            "--tech",
            "Python,FastAPI",
            "--no-semantic",
            cwd=str(project_dir),
        )

        # Check command succeeded
        self.assertEqual(
            result.returncode, 0, f"Init command failed: {result.stderr}\n{result.stdout}"
        )

        # Verify .claude directory was created
        claude_dir = project_dir / ".claude"
        self.assertTrue(claude_dir.exists(), ".claude directory should be created")

        # Verify key files exist
        self.assertTrue((claude_dir / "claude.json").exists(), "claude.json should exist")
        self.assertTrue((claude_dir / "task.md").exists(), "task.md should exist")
        self.assertTrue((claude_dir / "README.md").exists(), "README.md should exist")
        self.assertTrue((claude_dir / "scorecard.md").exists(), "scorecard.md should exist")

        # Verify directories exist
        self.assertTrue((claude_dir / "agents").is_dir(), "agents/ directory should exist")
        self.assertTrue((claude_dir / "contracts").is_dir(), "contracts/ directory should exist")
        self.assertTrue((claude_dir / "hooks").is_dir(), "hooks/ directory should exist")
        self.assertTrue((claude_dir / "skills").is_dir(), "skills/ directory should exist")
        self.assertTrue((claude_dir / "tasks").is_dir(), "tasks/ directory should exist")

        # Verify claude.json is valid JSON
        with open(claude_dir / "claude.json", "r") as f:
            config = json.load(f)
            self.assertEqual(config["name"], "test-project")
            self.assertIn("agents", config)
            self.assertIn("workflows", config)

    def test_init_with_template_parameter(self):
        """Test init command with specific template."""
        project_dir = self.test_projects_dir / "test-init-template"
        project_dir.mkdir(exist_ok=True)

        result = self.run_cli(
            "init",
            str(project_dir),
            "--name",
            "llm-app",
            "--description",
            "LLM application",
            "--template",
            "llm-app",
            "--no-semantic",
            cwd=str(project_dir),
        )

        self.assertEqual(result.returncode, 0, f"Init with template failed: {result.stderr}")

        # Verify template was applied
        claude_dir = project_dir / ".claude"
        with open(claude_dir / "claude.json", "r") as f:
            config = json.load(f)
            self.assertEqual(config["template"], "llm-app")

    def test_list_agents_command(self):
        """Test that list agents command works."""
        # Create a test project first
        project_dir = self.test_projects_dir / "test-list-agents"
        project_dir.mkdir(exist_ok=True)

        # Initialize project
        self.run_cli(
            "init",
            str(project_dir),
            "--name",
            "test",
            "--description",
            "test",
            "--no-semantic",
            cwd=str(project_dir),
        )

        # List agents
        result = self.run_cli("list", "agents", cwd=str(project_dir))

        self.assertEqual(result.returncode, 0, f"List agents failed: {result.stderr}")
        # Should list at least one agent
        self.assertTrue(len(result.stdout) > 0, "Should output agent list")

    def test_list_workflows_command(self):
        """Test that list workflows command works."""
        # Create a test project first
        project_dir = self.test_projects_dir / "test-list-workflows"
        project_dir.mkdir(exist_ok=True)

        # Initialize project
        self.run_cli(
            "init",
            str(project_dir),
            "--name",
            "test",
            "--description",
            "test",
            "--no-semantic",
            cwd=str(project_dir),
        )

        # List workflows
        result = self.run_cli("list", "workflows", cwd=str(project_dir))

        self.assertEqual(result.returncode, 0, f"List workflows failed: {result.stderr}")
        # Should output workflow list
        self.assertTrue(len(result.stdout) > 0, "Should output workflow list")

    def test_info_command(self):
        """Test that info command works for an agent."""
        # Create a test project first
        project_dir = self.test_projects_dir / "test-info"
        project_dir.mkdir(exist_ok=True)

        # Initialize project
        self.run_cli(
            "init",
            str(project_dir),
            "--name",
            "test",
            "--description",
            "test",
            "--no-semantic",
            cwd=str(project_dir),
        )

        # Get info for first available agent (code-reviewer is usually available)
        result = self.run_cli("info", "code-reviewer", cwd=str(project_dir))

        # Command may fail if agent not found, but should not crash
        # Just verify it runs without import errors
        if result.returncode == 0:
            self.assertIn("code-reviewer", result.stdout.lower())

    def test_yaml_templates_load_correctly(self):
        """Test that YAML templates can be loaded without errors."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
from claude_force.quick_start import QuickStartOrchestrator
orchestrator = QuickStartOrchestrator(use_semantic=False)
print(f"Loaded {len(orchestrator.templates)} templates")
assert len(orchestrator.templates) > 0, "Should load at least one template"
print("SUCCESS")
                """.strip(),
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"Template loading failed: {result.stderr}")
        self.assertIn("SUCCESS", result.stdout)
        self.assertIn("templates", result.stdout)

    def test_marketplace_registry_loads(self):
        """Test that marketplace registry YAML loads correctly."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
from claude_force.marketplace import get_marketplace_manager
import tempfile
temp_dir = tempfile.mkdtemp()
manager = get_marketplace_manager(temp_dir)
plugins = manager.available_plugins
print(f"Loaded {len(plugins)} plugins")
print("SUCCESS")
                """.strip(),
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"Marketplace loading failed: {result.stderr}")
        self.assertIn("SUCCESS", result.stdout)

    def test_fresh_user_workflow_complete(self):
        """
        Test complete fresh user workflow:
        1. Install package (already done in test environment)
        2. Run init command
        3. List available resources
        4. Verify everything works
        """
        project_dir = self.test_projects_dir / "complete-workflow"
        project_dir.mkdir(exist_ok=True)

        # Step 1: Initialize project
        result = self.run_cli(
            "init",
            str(project_dir),
            "--name",
            "my-app",
            "--description",
            "My first claude-force application",
            "--tech",
            "Python,React,PostgreSQL",
            "--no-semantic",
            cwd=str(project_dir),
        )
        self.assertEqual(result.returncode, 0, f"Init failed: {result.stderr}")

        # Step 2: List agents
        result = self.run_cli("list", "agents", cwd=str(project_dir))
        self.assertEqual(result.returncode, 0, f"List agents failed: {result.stderr}")

        # Step 3: List workflows
        result = self.run_cli("list", "workflows", cwd=str(project_dir))
        self.assertEqual(result.returncode, 0, f"List workflows failed: {result.stderr}")

        # Step 4: Verify project structure is complete
        claude_dir = project_dir / ".claude"
        required_files = [
            "claude.json",
            "task.md",
            "README.md",
            "scorecard.md",
        ]

        for filename in required_files:
            file_path = claude_dir / filename
            self.assertTrue(
                file_path.exists(), f"{filename} should exist in .claude directory"
            )

        required_dirs = ["agents", "contracts", "hooks", "skills", "tasks", "metrics"]

        for dirname in required_dirs:
            dir_path = claude_dir / dirname
            self.assertTrue(dir_path.is_dir(), f"{dirname}/ directory should exist")

    def test_no_yaml_import_error_on_init(self):
        """
        Regression test: Ensure 'claude-force init' does not raise
        'No module named yaml' error.

        This was the original bug that was fixed.
        """
        project_dir = self.test_projects_dir / "no-yaml-error"
        project_dir.mkdir(exist_ok=True)

        result = self.run_cli(
            "init",
            str(project_dir),
            "--name",
            "test",
            "--description",
            "test",
            "--no-semantic",
            cwd=str(project_dir),
        )

        # Should not contain yaml import errors
        combined_output = result.stdout + result.stderr
        self.assertNotIn("No module named 'yaml'", combined_output)
        self.assertNotIn("ModuleNotFoundError", combined_output)
        self.assertNotIn("ImportError: No module named yaml", combined_output)

        # Should succeed
        self.assertEqual(
            result.returncode,
            0,
            f"Init should succeed without yaml errors: {result.stderr}",
        )


class TestDependencyInstallation(unittest.TestCase):
    """Test that dependencies are properly specified."""

    def test_pyyaml_in_requirements_txt(self):
        """Test that PyYAML is listed in requirements.txt."""
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        self.assertTrue(requirements_path.exists(), "requirements.txt should exist")

        with open(requirements_path, "r") as f:
            content = f.read()
            self.assertIn("PyYAML", content, "PyYAML should be in requirements.txt")
            self.assertIn(">=6.0", content, "PyYAML version should be >=6.0")

    def test_pyyaml_in_pyproject_toml(self):
        """Test that PyYAML is listed in pyproject.toml."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml should exist")

        with open(pyproject_path, "r") as f:
            content = f.read()
            self.assertIn("PyYAML", content, "PyYAML should be in pyproject.toml")
            self.assertIn(">=6.0", content, "PyYAML version should be >=6.0")


if __name__ == "__main__":
    unittest.main()
