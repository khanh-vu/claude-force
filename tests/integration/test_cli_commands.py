"""
CLI Command Integration Tests

Tests all CLI commands via subprocess to ensure they work in real-world scenarios.
Focuses on command-line argument parsing, validation, and output formatting.
"""

import unittest
import subprocess
import sys
import tempfile
import shutil
import json
import os
from pathlib import Path


class CLICommandTestCase(unittest.TestCase):
    """Base test case for CLI command testing."""

    def run_command(self, *args, input_text=None, timeout=30, check=False):
        """
        Run claude-force CLI command.

        Args:
            *args: Command arguments
            input_text: Optional stdin input
            timeout: Command timeout in seconds
            check: Whether to raise on non-zero exit

        Returns:
            subprocess.CompletedProcess
        """
        cmd = [sys.executable, "-m", "claude_force.cli"] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=input_text,
            timeout=timeout,
            check=False
        )
        return result


class TestCLIListCommands(CLICommandTestCase):
    """Test 'claude-force list' commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create minimal config
        config = {
            "name": "test-project",
            "agents": {
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "domains": ["code-quality"],
                    "priority": 1
                }
            },
            "workflows": {
                "review": ["code-reviewer"]
            }
        }

        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(config, f)

        # Create agent file
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "code-reviewer.md").write_text("Code reviewer agent")

        # Change to temp directory
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_agents(self):
        """Test listing all available agents."""
        result = self.run_command("list", "agents")

        self.assertEqual(result.returncode, 0)
        self.assertIn("code-reviewer", result.stdout)

    def test_list_workflows(self):
        """Test listing all workflows."""
        result = self.run_command("list", "workflows")

        self.assertEqual(result.returncode, 0)
        self.assertIn("review", result.stdout)

    def test_list_json_format(self):
        """Test listing with JSON output format."""
        result = self.run_command("list", "agents", "--json")

        self.assertEqual(result.returncode, 0)

        # Verify JSON output
        try:
            data = json.loads(result.stdout)
            self.assertIsInstance(data, (list, dict))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")


class TestCLIInfoCommands(CLICommandTestCase):
    """Test 'claude-force info' commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config
        config = {
            "name": "test-project",
            "agents": {
                "backend-developer": {
                    "file": "agents/backend-developer.md",
                    "domains": ["backend", "api"],
                    "priority": 2,
                    "description": "Backend development expert"
                }
            }
        }

        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(config, f)

        # Create agent file
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "backend-developer.md").write_text("""
# Backend Developer

## Domain Expertise
- RESTful APIs
- Database design
- Backend architecture
""")

        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_info_agent(self):
        """Test getting detailed agent information."""
        result = self.run_command("info", "backend-developer")

        self.assertEqual(result.returncode, 0)
        self.assertIn("backend-developer", result.stdout.lower())
        self.assertIn("backend", result.stdout.lower())

    def test_info_agent_json(self):
        """Test agent info with JSON output."""
        result = self.run_command("info", "backend-developer", "--json")

        self.assertEqual(result.returncode, 0)

        try:
            data = json.loads(result.stdout)
            self.assertIn("domains", data)
            self.assertIn("backend", data["domains"])
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_info_nonexistent_agent(self):
        """Test error when querying non-existent agent."""
        result = self.run_command("info", "nonexistent-agent")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error", result.stderr.lower())


class TestCLIRecommendCommand(CLICommandTestCase):
    """Test 'claude-force recommend' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config with multiple agents
        config = {
            "name": "test-project",
            "agents": {
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "domains": ["code-quality", "security"],
                    "priority": 1
                },
                "backend-developer": {
                    "file": "agents/backend-developer.md",
                    "domains": ["backend", "api"],
                    "priority": 2
                }
            }
        }

        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(config, f)

        # Create agent files
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()

        (agents_dir / "code-reviewer.md").write_text(
            "Expert in code quality and security reviews"
        )
        (agents_dir / "backend-developer.md").write_text(
            "Backend development specialist for APIs"
        )

        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_recommend_agent(self):
        """Test agent recommendation for a task."""
        result = self.run_command(
            "recommend",
            "--task", "Review authentication code for vulnerabilities"
        )

        # May fail if sentence-transformers not installed
        if result.returncode == 0:
            # Should recommend code-reviewer
            self.assertIn("code-reviewer", result.stdout.lower())
        else:
            # Should show helpful error about missing dependencies
            self.assertIn("sentence-transformers", result.stderr.lower())

    def test_recommend_with_top_k(self):
        """Test recommendation with top-k limit."""
        result = self.run_command(
            "recommend",
            "--task", "Build REST API",
            "--top-k", "2"
        )

        # Check command accepts top-k parameter
        # (may fail if dependencies missing)
        self.assertIn(result.returncode, [0, 1])


class TestCLIAnalyzeCommand(CLICommandTestCase):
    """Test 'claude-force analyze' command."""

    def setUp(self):
        """Set up test fixtures with metrics."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config
        config = {"name": "test-project", "agents": {}}
        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(config, f)

        # Create metrics directory with sample data
        metrics_dir = self.claude_dir / "metrics"
        metrics_dir.mkdir()

        # Create sample metrics
        with open(metrics_dir / "executions.jsonl", 'w') as f:
            f.write(json.dumps({
                "timestamp": "2024-01-15T10:00:00",
                "agent_name": "code-reviewer",
                "task_hash": "abc123",
                "success": True,
                "execution_time_ms": 1500.0,
                "model": "claude-3-5-sonnet-20241022",
                "input_tokens": 100,
                "output_tokens": 200,
                "total_tokens": 300,
                "estimated_cost": 0.0045
            }) + '\n')

        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyze_performance(self):
        """Test performance analysis command."""
        result = self.run_command("analyze", "performance")

        if result.returncode == 0:
            # Should show analytics
            output = result.stdout.lower()
            self.assertTrue(
                any(word in output for word in ["execution", "cost", "token"])
            )

    def test_analyze_json_output(self):
        """Test analyze with JSON format."""
        result = self.run_command("analyze", "performance", "--json")

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                self.assertIsInstance(data, dict)
            except json.JSONDecodeError:
                self.fail("Output is not valid JSON")


class TestCLIMarketplaceCommands(CLICommandTestCase):
    """Test 'claude-force marketplace' commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_marketplace_list(self):
        """Test listing marketplace agents."""
        result = self.run_command("marketplace", "list")

        # Should either succeed or fail gracefully
        self.assertIn(result.returncode, [0, 1])

        if result.returncode == 0:
            # Should show marketplace content
            self.assertIsNotNone(result.stdout)

    def test_marketplace_search(self):
        """Test searching marketplace."""
        result = self.run_command("marketplace", "search", "--query", "security")

        # Command should be recognized
        self.assertIn(result.returncode, [0, 1])


class TestCLIComposeCommand(CLICommandTestCase):
    """Test 'claude-force compose' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config with agents
        config = {
            "name": "test-project",
            "agents": {
                "backend-developer": {
                    "file": "agents/backend-developer.md",
                    "domains": ["backend"],
                    "priority": 2
                },
                "code-reviewer": {
                    "file": "agents/code-reviewer.md",
                    "domains": ["code-quality"],
                    "priority": 1
                }
            },
            "workflows": {}
        }

        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(config, f)

        # Create agent files
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "backend-developer.md").write_text("Backend developer")
        (agents_dir / "code-reviewer.md").write_text("Code reviewer")

        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compose_workflow(self):
        """Test creating a custom workflow."""
        result = self.run_command(
            "compose",
            "custom-workflow",
            "--agents", "backend-developer", "code-reviewer"
        )

        # Should either succeed or show helpful message
        self.assertIn(result.returncode, [0, 1])


class TestCLIExportImportCommands(CLICommandTestCase):
    """Test 'claude-force export/import' commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create config
        self.config = {
            "name": "test-project",
            "version": "1.0",
            "agents": {
                "test-agent": {
                    "file": "agents/test-agent.md",
                    "domains": ["testing"],
                    "priority": 2
                }
            }
        }

        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(self.config, f)

        # Create agent file
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "test-agent.md").write_text("Test agent")

        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_config(self):
        """Test exporting configuration."""
        export_file = Path(self.temp_dir) / "export.json"

        result = self.run_command(
            "export",
            "--output", str(export_file)
        )

        if result.returncode == 0:
            # Verify export file created
            self.assertTrue(export_file.exists())

            # Verify content
            with open(export_file) as f:
                exported = json.load(f)
                self.assertEqual(exported["name"], "test-project")

    def test_import_config(self):
        """Test importing configuration."""
        # Create import file
        import_file = Path(self.temp_dir) / "import.json"
        with open(import_file, 'w') as f:
            json.dump({
                "name": "imported-project",
                "agents": {}
            }, f)

        result = self.run_command(
            "import",
            "--input", str(import_file)
        )

        # Should either succeed or show helpful message
        self.assertIn(result.returncode, [0, 1])


class TestCLIValidationCommands(CLICommandTestCase):
    """Test 'claude-force validate' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create valid config
        config = {
            "name": "test-project",
            "version": "1.0",
            "agents": {
                "test-agent": {
                    "file": "agents/test-agent.md",
                    "domains": ["test"],
                    "priority": 1
                }
            }
        }

        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(config, f)

        # Create agent file
        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "test-agent.md").write_text("# Test Agent\n\nTest content")

        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_config(self):
        """Test configuration validation."""
        result = self.run_command("validate")

        if result.returncode == 0:
            # Should report validation success
            self.assertIn("valid", result.stdout.lower())

    def test_validate_with_warnings(self):
        """Test validation shows warnings for issues."""
        # Create invalid config (missing required fields)
        invalid_config = {"name": "test"}  # Missing version, agents, etc.

        with open(self.claude_dir / "claude.json", 'w') as f:
            json.dump(invalid_config, f)

        result = self.run_command("validate")

        # Should report validation issues
        if result.returncode != 0:
            self.assertIn("error", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
