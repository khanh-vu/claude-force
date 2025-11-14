"""
Import/Export Tests for claude-force.

Tests agent porting between claude-force and external formats like wshobson/agents.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from claude_force.import_export import (
    AgentPortingTool,
    AgentMetadata,
    ContractMetadata,
    get_porting_tool
)
from claude_force.path_validator import PathValidationError


class TestAgentMetadataDataclass(unittest.TestCase):
    """Test AgentMetadata dataclass."""

    def test_metadata_creation(self):
        """AgentMetadata should be creatable with required fields."""
        metadata = AgentMetadata(
            name="test-agent",
            description="A test agent",
            content="# Test Agent\n\nThis is a test agent."
        )

        self.assertEqual(metadata.name, "test-agent")
        self.assertEqual(metadata.description, "A test agent")
        self.assertIsNotNone(metadata.content)
        self.assertEqual(metadata.expertise, [])
        self.assertEqual(metadata.tools, [])

    def test_metadata_with_optional_fields(self):
        """AgentMetadata should handle optional fields."""
        metadata = AgentMetadata(
            name="test-agent",
            description="Test",
            content="Content",
            expertise=["python", "api"],
            tools=["pytest", "black"],
            model="claude-3-haiku",
            source="custom"
        )

        self.assertEqual(metadata.expertise, ["python", "api"])
        self.assertEqual(metadata.tools, ["pytest", "black"])
        self.assertEqual(metadata.model, "claude-3-haiku")
        self.assertEqual(metadata.source, "custom")


class TestAgentPortingToolInit(unittest.TestCase):
    """Test AgentPortingTool initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_initialization(self):
        """Tool should initialize with default or custom agents dir."""
        tool = AgentPortingTool()
        self.assertIsNotNone(tool.agents_dir)

        custom_dir = Path(self.temp_dir) / ".claude/agents"
        tool = AgentPortingTool(agents_dir=custom_dir)
        self.assertEqual(tool.agents_dir, custom_dir)


class TestImportFromWshobson(unittest.TestCase):
    """Test importing agents from wshobson/agents format."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.agents_dir = Path(self.temp_dir) / ".claude/agents"
        self.tool = AgentPortingTool(agents_dir=self.agents_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_import_simple_agent(self):
        """Should import a simple wshobson-format agent."""
        # Create test agent file
        agent_content = """# Python Developer

Expert Python developer with focus on clean code and best practices.

## Expertise
- Python 3.x development
- Async programming
- Testing with pytest

## Capabilities
- Write idiomatic Python code
- Implement async patterns
- Create comprehensive tests
"""

        agent_file = Path(self.temp_dir) / "python-developer.md"
        agent_file.write_text(agent_content)

        # Import agent
        result = self.tool.import_from_wshobson(
            agent_file=agent_file,
            generate_contract=True
        )

        # Verify import
        self.assertEqual(result["name"], "python-developer")
        self.assertIsNotNone(result["agent_path"])
        self.assertIsNotNone(result["contract_path"])

        # Verify agent file created
        agent_md = Path(result["agent_path"])
        self.assertTrue(agent_md.exists())
        self.assertEqual(agent_md.read_text(), agent_content)

    def test_import_without_contract(self):
        """Should import agent without generating contract."""
        agent_content = "# Test Agent\n\nSimple test agent."
        agent_file = Path(self.temp_dir) / "test-agent.md"
        agent_file.write_text(agent_content)

        result = self.tool.import_from_wshobson(
            agent_file=agent_file,
            generate_contract=False
        )

        self.assertIsNone(result["contract_path"])

    def test_import_with_custom_name(self):
        """Should import agent with custom name override."""
        agent_content = "# Original Name\n\nAgent content."
        agent_file = Path(self.temp_dir) / "original.md"
        agent_file.write_text(agent_content)

        result = self.tool.import_from_wshobson(
            agent_file=agent_file,
            target_name="custom-name"
        )

        self.assertEqual(result["name"], "custom-name")

        # Verify directory uses custom name
        agent_dir = self.agents_dir / "custom-name"
        self.assertTrue(agent_dir.exists())

    def test_import_nonexistent_file(self):
        """Should raise error for nonexistent file."""
        with self.assertRaises(PathValidationError):
            self.tool.import_from_wshobson(
                agent_file=Path("/nonexistent/agent.md")
            )

    def test_import_extracts_expertise(self):
        """Should extract expertise from agent content."""
        agent_content = """# Expert Agent

Description of the agent.

## Expertise
- Area 1
- Area 2
- Area 3
"""

        agent_file = Path(self.temp_dir) / "expert.md"
        agent_file.write_text(agent_content)

        result = self.tool.import_from_wshobson(agent_file)

        metadata = result["metadata"]
        self.assertEqual(len(metadata.expertise), 3)
        self.assertIn("Area 1", metadata.expertise)


class TestExportToWshobson(unittest.TestCase):
    """Test exporting agents to wshobson/agents format."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.agents_dir = Path(self.temp_dir) / ".claude/agents"
        self.tool = AgentPortingTool(agents_dir=self.agents_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_simple_agent(self):
        """Should export agent to wshobson format."""
        # Create test agent
        agent_name = "test-agent"
        agent_dir = self.agents_dir / agent_name
        agent_dir.mkdir(parents=True)

        agent_content = """# Test Agent

A test agent for export testing.

## Capabilities
- Task 1
- Task 2
"""

        (agent_dir / "AGENT.md").write_text(agent_content)

        # Export agent
        output_dir = Path(self.temp_dir) / "exported"
        output_file = self.tool.export_to_wshobson(
            agent_name=agent_name,
            output_dir=output_dir
        )

        # Verify export
        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.name, f"{agent_name}.md")

        exported_content = output_file.read_text()
        self.assertIn("Test Agent", exported_content)

    def test_export_nonexistent_agent(self):
        """Should raise error for nonexistent agent."""
        output_dir = Path(self.temp_dir) / "exported"

        with self.assertRaises(FileNotFoundError):
            self.tool.export_to_wshobson(
                agent_name="nonexistent-agent",
                output_dir=output_dir
            )

    def test_export_without_metadata(self):
        """Should export without metadata header."""
        # Create test agent
        agent_name = "simple-agent"
        agent_dir = self.agents_dir / agent_name
        agent_dir.mkdir(parents=True)
        (agent_dir / "AGENT.md").write_text("# Simple Agent\n\nContent.")

        # Export without metadata
        output_dir = Path(self.temp_dir) / "exported"
        output_file = self.tool.export_to_wshobson(
            agent_name=agent_name,
            output_dir=output_dir,
            include_metadata=False
        )

        content = output_file.read_text()
        self.assertNotIn("Exported from claude-force", content)

    def test_export_with_metadata(self):
        """Should export with metadata header."""
        # Create test agent
        agent_name = "meta-agent"
        agent_dir = self.agents_dir / agent_name
        agent_dir.mkdir(parents=True)
        (agent_dir / "AGENT.md").write_text("# Meta Agent\n\nContent.")

        # Export with metadata
        output_dir = Path(self.temp_dir) / "exported"
        output_file = self.tool.export_to_wshobson(
            agent_name=agent_name,
            output_dir=output_dir,
            include_metadata=True
        )

        content = output_file.read_text()
        self.assertIn("Exported from claude-force", content)


class TestContractGeneration(unittest.TestCase):
    """Test automatic contract generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.agents_dir = Path(self.temp_dir) / ".claude/agents"
        self.tool = AgentPortingTool(agents_dir=self.agents_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_contract_generation_creates_file(self):
        """Should generate contract file."""
        agent_content = "# Test Agent\n\nTest agent for contract generation."
        agent_file = Path(self.temp_dir) / "test.md"
        agent_file.write_text(agent_content)

        result = self.tool.import_from_wshobson(
            agent_file=agent_file,
            generate_contract=True
        )

        # Verify contract created
        contract_path = Path(result["contract_path"])
        self.assertTrue(contract_path.exists())
        self.assertEqual(contract_path.name, "CONTRACT.md")

    def test_contract_contains_required_sections(self):
        """Contract should contain all required sections."""
        agent_content = "# Test Agent\n\nTest."
        agent_file = Path(self.temp_dir) / "test.md"
        agent_file.write_text(agent_content)

        result = self.tool.import_from_wshobson(agent_file, generate_contract=True)

        contract_path = Path(result["contract_path"])
        contract_content = contract_path.read_text()

        # Verify sections
        self.assertIn("## Inputs", contract_content)
        self.assertIn("## Expected Outputs", contract_content)
        self.assertIn("## Constraints", contract_content)
        self.assertIn("## Quality Metrics", contract_content)
        self.assertIn("## Validation", contract_content)

    def test_contract_infers_security_constraints(self):
        """Should infer security constraints from content."""
        agent_content = """# Security Specialist

Expert in application security and vulnerability assessment.

## Expertise
- Security auditing
- Vulnerability scanning
"""

        agent_file = Path(self.temp_dir) / "security.md"
        agent_file.write_text(agent_content)

        result = self.tool.import_from_wshobson(agent_file, generate_contract=True)

        contract_path = Path(result["contract_path"])
        contract_content = contract_path.read_text()

        # Should include security constraint
        self.assertIn("security", contract_content.lower())


class TestBulkImport(unittest.TestCase):
    """Test bulk import functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.agents_dir = Path(self.temp_dir) / ".claude/agents"
        self.source_dir = Path(self.temp_dir) / "source"
        self.source_dir.mkdir()
        self.tool = AgentPortingTool(agents_dir=self.agents_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bulk_import_multiple_agents(self):
        """Should import multiple agents from directory."""
        # Create test agents
        for i in range(3):
            agent_file = self.source_dir / f"agent-{i}.md"
            agent_file.write_text(f"# Agent {i}\n\nTest agent {i}.")

        # Bulk import
        results = self.tool.bulk_import(
            source_dir=self.source_dir,
            pattern="*.md"
        )

        # Verify results
        self.assertEqual(results["total"], 3)
        self.assertEqual(len(results["imported"]), 3)
        self.assertEqual(len(results["failed"]), 0)

    def test_bulk_import_with_pattern(self):
        """Should respect file pattern."""
        # Create mixed files
        (self.source_dir / "agent1.md").write_text("# Agent 1\n\nTest.")
        (self.source_dir / "agent2.txt").write_text("# Agent 2\n\nTest.")
        (self.source_dir / "agent3.md").write_text("# Agent 3\n\nTest.")

        # Import only .md files
        results = self.tool.bulk_import(
            source_dir=self.source_dir,
            pattern="*.md"
        )

        # Should import only .md files
        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["imported"]), 2)

    def test_bulk_import_handles_errors(self):
        """Should handle errors gracefully in bulk import."""
        # Create one valid and one invalid agent
        (self.source_dir / "valid.md").write_text("# Valid Agent\n\nTest.")

        # Create empty file (will cause error in parsing)
        (self.source_dir / "invalid.md").write_text("")

        # Bulk import
        results = self.tool.bulk_import(
            source_dir=self.source_dir,
            pattern="*.md",
            generate_contracts=False  # Simplify test
        )

        # Should continue despite errors
        self.assertEqual(results["total"], 2)
        self.assertGreater(len(results["imported"]), 0)

    def test_bulk_import_nonexistent_directory(self):
        """Should raise error for nonexistent directory."""
        with self.assertRaises(FileNotFoundError):
            self.tool.bulk_import(
                source_dir=Path("/nonexistent/directory")
            )


class TestBulkExport(unittest.TestCase):
    """Test bulk export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.agents_dir = Path(self.temp_dir) / ".claude/agents"
        self.output_dir = Path(self.temp_dir) / "output"
        self.tool = AgentPortingTool(agents_dir=self.agents_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bulk_export_multiple_agents(self):
        """Should export multiple agents."""
        # Create test agents
        for i in range(3):
            agent_dir = self.agents_dir / f"agent-{i}"
            agent_dir.mkdir(parents=True)
            (agent_dir / "AGENT.md").write_text(f"# Agent {i}\n\nTest.")

        # Bulk export
        agent_names = ["agent-0", "agent-1", "agent-2"]
        results = self.tool.bulk_export(
            agent_names=agent_names,
            output_dir=self.output_dir
        )

        # Verify results
        self.assertEqual(results["total"], 3)
        self.assertEqual(len(results["exported"]), 3)
        self.assertEqual(len(results["failed"]), 0)

    def test_bulk_export_handles_errors(self):
        """Should handle export errors gracefully."""
        # Create one valid agent
        agent_dir = self.agents_dir / "valid-agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "AGENT.md").write_text("# Valid\n\nTest.")

        # Try to export valid + nonexistent
        agent_names = ["valid-agent", "nonexistent-agent"]
        results = self.tool.bulk_export(
            agent_names=agent_names,
            output_dir=self.output_dir
        )

        # Should export valid, fail on nonexistent
        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["exported"]), 1)
        self.assertEqual(len(results["failed"]), 1)


class TestFormatConversion(unittest.TestCase):
    """Test format conversion helpers."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tool = AgentPortingTool(agents_dir=Path(self.temp_dir) / "agents")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_slugify_converts_correctly(self):
        """Should convert text to slug format."""
        self.assertEqual(self.tool._slugify("Python Developer"), "python-developer")
        self.assertEqual(self.tool._slugify("API Engineer!"), "api-engineer")
        self.assertEqual(self.tool._slugify("Test  Agent"), "test-agent")

    def test_parse_wshobson_format(self):
        """Should parse wshobson format correctly."""
        agent_content = """# Python Expert

An expert in Python development.

## Expertise
- Python 3.x
- Async programming
"""

        agent_file = Path(self.temp_dir) / "test.md"
        agent_file.write_text(agent_content)

        metadata = self.tool._parse_wshobson_format(agent_file)

        self.assertEqual(metadata.name, "python-expert")
        self.assertIn("Python", metadata.description)
        self.assertEqual(len(metadata.expertise), 2)


class TestGetPortingTool(unittest.TestCase):
    """Test get_porting_tool singleton function."""

    def test_get_porting_tool_creates_instance(self):
        """get_porting_tool should create instance."""
        tool = get_porting_tool()
        self.assertIsInstance(tool, AgentPortingTool)

    def test_get_porting_tool_with_custom_dir(self):
        """get_porting_tool should accept custom directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            custom_dir = Path(temp_dir) / ".claude/agents"
            tool = get_porting_tool(agents_dir=custom_dir)
            self.assertEqual(tool.agents_dir, custom_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
