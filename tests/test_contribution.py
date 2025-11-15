"""
Community Contribution Tests for claude-force.

Tests contribution validation, export, and packaging functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from claude_force.contribution import (
    ContributionManager,
    ValidationResult,
    ContributionPackage,
    get_contribution_manager,
)


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """ValidationResult should be creatable."""
        result = ValidationResult(
            valid=True, errors=[], warnings=["Warning 1"], passed_checks=["Check 1", "Check 2"]
        )

        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(len(result.passed_checks), 2)

    def test_validation_result_with_errors(self):
        """ValidationResult with errors should be invalid."""
        result = ValidationResult(
            valid=False, errors=["Error 1", "Error 2"], warnings=[], passed_checks=[]
        )

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 2)


class TestContributionPackage(unittest.TestCase):
    """Test ContributionPackage dataclass."""

    def test_package_creation(self):
        """ContributionPackage should be creatable."""
        validation = ValidationResult(valid=True, errors=[], warnings=[], passed_checks=["Test"])

        package = ContributionPackage(
            agent_name="test-agent", export_path=Path("/tmp/test"), validation=validation
        )

        self.assertEqual(package.agent_name, "test-agent")
        self.assertIsNotNone(package.validation)
        self.assertIsNone(package.pr_template_path)


class TestContributionManagerInit(unittest.TestCase):
    """Test ContributionManager initialization."""

    def test_manager_initialization(self):
        """Manager should initialize with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / ".claude" / "agents"
            agents_dir.mkdir(parents=True)

            manager = ContributionManager(agents_dir=agents_dir)

            self.assertEqual(manager.agents_dir, agents_dir)
            self.assertEqual(manager.export_dir, Path("./exported"))

    def test_manager_custom_export_dir(self):
        """Manager should accept custom export directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / ".claude" / "agents"
            export_dir = Path(tmpdir) / "exports"

            manager = ContributionManager(agents_dir=agents_dir, export_dir=export_dir)

            self.assertEqual(manager.export_dir, export_dir)


class TestValidateAgent(unittest.TestCase):
    """Test agent validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.agents_dir = Path(self.tmpdir) / ".claude" / "agents"
        self.agents_dir.mkdir(parents=True)

        self.manager = ContributionManager(agents_dir=self.agents_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.tmpdir)

    def test_validate_nonexistent_agent(self):
        """Should fail for nonexistent agent."""
        result = self.manager.validate_agent_for_contribution("nonexistent")

        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("not found", result.errors[0].lower())

    def test_validate_agent_without_md(self):
        """Should fail for agent without AGENT.md."""
        agent_dir = self.agents_dir / "test-agent"
        agent_dir.mkdir()

        result = self.manager.validate_agent_for_contribution("test-agent")

        self.assertFalse(result.valid)
        self.assertIn("AGENT.md not found", result.errors)

    def test_validate_agent_with_short_content(self):
        """Should fail for agent with too short content."""
        agent_dir = self.agents_dir / "test-agent"
        agent_dir.mkdir()

        agent_md = agent_dir / "AGENT.md"
        agent_md.write_text("# Test\n\nShort")

        result = self.manager.validate_agent_for_contribution("test-agent")

        self.assertFalse(result.valid)
        self.assertIn("too short", result.errors[0].lower())

    def test_validate_valid_agent(self):
        """Should pass for valid agent."""
        agent_dir = self.agents_dir / "test-agent"
        agent_dir.mkdir()

        agent_md = agent_dir / "AGENT.md"
        content = """# Test Agent

This is a comprehensive description of the test agent with sufficient content
to pass validation. It includes examples and detailed documentation.

## Examples

Example 1: Test task

## Capabilities

- Feature 1
- Feature 2
"""
        agent_md.write_text(content)

        result = self.manager.validate_agent_for_contribution("test-agent")

        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
        self.assertGreater(len(result.passed_checks), 0)

    def test_validate_warns_for_builtin_name(self):
        """Should warn if agent name matches builtin."""
        agent_dir = self.agents_dir / "frontend-architect"
        agent_dir.mkdir()

        agent_md = agent_dir / "AGENT.md"
        agent_md.write_text("# Frontend\n\n" + "x" * 200)

        result = self.manager.validate_agent_for_contribution("frontend-architect")

        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)
        self.assertTrue(any("builtin" in w.lower() for w in result.warnings))


class TestPrepareContribution(unittest.TestCase):
    """Test contribution preparation."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.agents_dir = Path(self.tmpdir) / ".claude" / "agents"
        self.export_dir = Path(self.tmpdir) / "exports"
        self.agents_dir.mkdir(parents=True)
        self.export_dir.mkdir(parents=True)

        self.manager = ContributionManager(agents_dir=self.agents_dir, export_dir=self.export_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.tmpdir)

    def _create_valid_agent(self, name: str):
        """Helper to create a valid agent."""
        agent_dir = self.agents_dir / name
        agent_dir.mkdir()

        agent_md = agent_dir / "AGENT.md"
        content = f"""# {name}

This is a comprehensive agent definition with sufficient content.

## Capabilities

- Feature 1
- Feature 2

## Examples

Example usage of {name}.
"""
        agent_md.write_text(content)

    def test_prepare_contribution_invalid_agent(self):
        """Should raise ValueError for invalid agent."""
        agent_dir = self.agents_dir / "invalid-agent"
        agent_dir.mkdir()

        with self.assertRaises(ValueError) as ctx:
            self.manager.prepare_contribution("invalid-agent")

        self.assertIn("validation failed", str(ctx.exception).lower())

    def test_prepare_contribution_skip_validation(self):
        """Should skip validation if requested."""
        self._create_valid_agent("test-agent")

        package = self.manager.prepare_contribution("test-agent", validate=False)

        self.assertIsNone(package.validation)

    def test_prepare_contribution_creates_export(self):
        """Should create export directory and files."""
        self._create_valid_agent("test-agent")

        package = self.manager.prepare_contribution("test-agent")

        # Check export directory created
        self.assertTrue(package.export_path.exists())
        self.assertTrue(package.export_path.is_dir())

        # Check plugin.json created
        plugin_file = package.export_path / "plugin.json"
        self.assertTrue(plugin_file.exists())

        # Check PR template created
        self.assertIsNotNone(package.pr_template_path)
        self.assertTrue(package.pr_template_path.exists())

    def test_prepare_contribution_wshobson_format(self):
        """Should export in wshobson format."""
        self._create_valid_agent("test-agent")

        package = self.manager.prepare_contribution("test-agent", target_repo="wshobson")

        # Check agent markdown file exists
        agent_md = package.export_path / "test-agent.md"
        self.assertTrue(agent_md.exists())

        # Check plugin structure
        self.assertIsNotNone(package.plugin_structure)
        self.assertIn("plugin_id", package.plugin_structure)
        self.assertEqual(package.plugin_structure["source"], "community")

    def test_prepare_contribution_claude_force_format(self):
        """Should export in claude-force format."""
        self._create_valid_agent("test-agent")

        package = self.manager.prepare_contribution("test-agent", target_repo="claude-force")

        # Check agent markdown file exists
        agent_md = package.export_path / "test-agent.md"
        self.assertTrue(agent_md.exists())

        # Check plugin structure
        self.assertIsNotNone(package.plugin_structure)
        self.assertIn("agents", package.plugin_structure)


class TestGeneratePluginStructure(unittest.TestCase):
    """Test plugin structure generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.manager = ContributionManager()

    def tearDown(self):
        """Clean up temporary directory."""
        if Path(self.tmpdir).exists():
            shutil.rmtree(self.tmpdir)

    def test_generate_wshobson_structure(self):
        """Should generate wshobson plugin structure."""
        export_path = Path(self.tmpdir) / "export"
        export_path.mkdir(parents=True)

        structure = self.manager._generate_plugin_structure("test-agent", "wshobson", export_path)

        self.assertIn("plugin_id", structure)
        self.assertEqual(structure["source"], "community")
        self.assertIn("test-agent", structure["agents"])
        self.assertEqual(structure["version"], "1.0.0")

        # Check file created
        plugin_file = export_path / "plugin.json"
        self.assertTrue(plugin_file.exists())

    def test_generate_claude_force_structure(self):
        """Should generate claude-force plugin structure."""
        export_path = Path(self.tmpdir) / "export"
        export_path.mkdir(parents=True)

        structure = self.manager._generate_plugin_structure(
            "test-agent", "claude-force", export_path
        )

        self.assertIn("plugin_id", structure)
        self.assertIn("agents", structure)
        self.assertEqual(len(structure["agents"]), 1)
        self.assertEqual(structure["agents"][0]["id"], "test-agent")


class TestGeneratePRTemplate(unittest.TestCase):
    """Test PR template generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.manager = ContributionManager()

    def tearDown(self):
        """Clean up temporary directory."""
        if Path(self.tmpdir).exists():
            shutil.rmtree(self.tmpdir)

    def test_generate_pr_template(self):
        """Should generate PR template."""
        export_path = Path(self.tmpdir) / "export"
        export_path.mkdir(parents=True)

        pr_path = self.manager._generate_pr_template("test-agent", "wshobson", export_path, None)

        self.assertTrue(pr_path.exists())

        content = pr_path.read_text()
        self.assertIn("test-agent", content)
        self.assertIn("wshobson", content)
        self.assertIn("Checklist", content)

    def test_generate_pr_template_with_validation(self):
        """Should include validation results in PR template."""
        export_path = Path(self.tmpdir) / "export"
        export_path.mkdir(parents=True)

        validation = ValidationResult(
            valid=True, errors=[], warnings=["Warning 1"], passed_checks=["Check 1", "Check 2"]
        )

        pr_path = self.manager._generate_pr_template(
            "test-agent", "wshobson", export_path, validation
        )

        content = pr_path.read_text()
        self.assertIn("✅ Passed", content)
        self.assertIn("Warning 1", content)
        self.assertIn("Check 1", content)


class TestGetContributionInstructions(unittest.TestCase):
    """Test contribution instructions generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = ContributionManager()

    def test_get_instructions_wshobson(self):
        """Should generate instructions for wshobson."""
        validation = ValidationResult(valid=True, errors=[], warnings=[], passed_checks=["Test"])

        package = ContributionPackage(
            agent_name="test-agent",
            export_path=Path("/tmp/test"),
            validation=validation,
            pr_template_path=Path("/tmp/test/PR_TEMPLATE.md"),
        )

        instructions = self.manager.get_contribution_instructions("test-agent", "wshobson", package)

        self.assertIn("test-agent", instructions)
        self.assertIn("wshobson", instructions)
        self.assertIn("Fork", instructions)
        self.assertIn("marketplace.json", instructions)
        self.assertIn("PASSED", instructions)

    def test_get_instructions_with_warnings(self):
        """Should include warnings in instructions."""
        validation = ValidationResult(
            valid=True, errors=[], warnings=["Warning 1", "Warning 2"], passed_checks=["Test"]
        )

        package = ContributionPackage(
            agent_name="test-agent", export_path=Path("/tmp/test"), validation=validation
        )

        instructions = self.manager.get_contribution_instructions("test-agent", "wshobson", package)

        self.assertIn("Warning 1", instructions)
        self.assertIn("Warning 2", instructions)


class TestGetContributionManager(unittest.TestCase):
    """Test get_contribution_manager function."""

    def test_get_manager_creates_instance(self):
        """get_contribution_manager should create instance."""
        manager = get_contribution_manager()

        self.assertIsInstance(manager, ContributionManager)

    def test_get_manager_with_custom_dirs(self):
        """get_contribution_manager should accept custom directories."""
        agents_dir = Path("/tmp/agents")
        export_dir = Path("/tmp/exports")

        manager = get_contribution_manager(agents_dir=agents_dir, export_dir=export_dir)

        self.assertEqual(manager.agents_dir, agents_dir)
        self.assertEqual(manager.export_dir, export_dir)


if __name__ == "__main__":
    unittest.main()
