"""
Integration Tests for Existing Project Support Workflow

Tests the complete end-to-end workflow:
1. Review project (analyze)
2. Restructure .claude folder (fix)
3. Pick agents (copy from claude-force)

These tests verify the three commands work together seamlessly.
"""

import pytest
import tempfile
import json
from pathlib import Path

from claude_force.commands.review import ReviewCommand
from claude_force.commands.restructure import RestructureCommand
from claude_force.commands.pick_agent import PickAgentCommand


class TestExistingProjectWorkflow:
    """Test complete workflow for existing project integration"""

    def test_complete_workflow_on_new_project(self):
        """
        Test the complete workflow on a brand new project:
        1. Create a new project with some code
        2. Review it (should detect technologies)
        3. Restructure it (should create .claude folder)
        4. Pick agents (should copy agents)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup: Create a new project with Python code
            project_path = Path(tmpdir) / "my-app"
            project_path.mkdir()

            # Create some Python files
            (project_path / "main.py").write_text("print('Hello, World!')")
            (project_path / "requirements.txt").write_text("flask==2.0.0\npytest==7.0.0")
            src_dir = project_path / "src"
            src_dir.mkdir()
            (src_dir / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")

            # Step 1: Review the project
            review_cmd = ReviewCommand(project_path)
            review_result = review_cmd.execute()

            # Verify review found Python files
            assert review_result.stats.total_files >= 3
            assert "python" in [lang.lower() for lang in review_result.tech_stack.languages]

            # Step 2: Restructure (create .claude folder)
            restructure_cmd = RestructureCommand(project_path)
            restructure_result = restructure_cmd.execute(auto_approve=True)

            # Verify restructure created .claude folder
            assert restructure_result["success"] is True
            assert restructure_result["fixes_applied"] > 0
            assert (project_path / ".claude").exists()
            assert (project_path / ".claude" / "claude.json").exists()
            assert (project_path / ".claude" / "README.md").exists()

            # Step 3: Pick agents from claude-force
            # Get claude-force path (assume tests run from project root)
            claude_force_path = Path(__file__).parent.parent.parent

            # Verify claude-force has .claude folder
            if not (claude_force_path / ".claude").exists():
                pytest.skip("claude-force .claude folder not found")

            pick_cmd = PickAgentCommand(
                source_project=claude_force_path,
                target_project=project_path
            )

            # List available agents
            available_agents = pick_cmd.list_available_agents()
            assert len(available_agents) > 0, "Should have some agents available"

            # Copy first agent
            first_agent = available_agents[0]
            pick_result = pick_cmd.execute([first_agent])

            # Verify agent was copied
            assert pick_result["success"] is True
            assert pick_result["agents_copied"] == 1
            assert (project_path / ".claude" / "agents" / f"{first_agent}.md").exists()
            assert (project_path / ".claude" / "contracts" / f"{first_agent}.contract").exists()

            # Verify config was updated
            config_path = project_path / ".claude" / "claude.json"
            config = json.loads(config_path.read_text())
            assert first_agent in config["agents"]

    def test_workflow_on_project_with_existing_claude_folder(self):
        """
        Test workflow on project that already has .claude folder
        (may be incomplete or invalid)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup: Create project with partial .claude folder
            project_path = Path(tmpdir) / "existing-app"
            project_path.mkdir()

            # Create some code
            (project_path / "app.py").write_text("import flask")

            # Create partial .claude folder (missing some files)
            claude_path = project_path / ".claude"
            claude_path.mkdir()
            (claude_path / "README.md").write_text("# My Project")
            # Missing: claude.json, task.md, scorecard.md, and directories

            # Step 1: Review
            review_cmd = ReviewCommand(project_path)
            review_result = review_cmd.execute()
            assert review_result.stats.total_files >= 1

            # Step 2: Restructure (should fix missing files)
            restructure_cmd = RestructureCommand(project_path)
            restructure_result = restructure_cmd.execute(auto_approve=True)

            # Should have fixed missing files
            assert restructure_result["success"] is True
            assert restructure_result["fixes_applied"] > 0
            assert (claude_path / "claude.json").exists()
            assert (claude_path / "task.md").exists()
            assert (claude_path / "scorecard.md").exists()
            assert (claude_path / "agents").exists()

            # Verify original README.md was not overwritten
            assert (claude_path / "README.md").read_text() == "# My Project"

    def test_workflow_review_suggests_agents_then_pick_them(self):
        """
        Test that review recommendations can be used with pick-agent
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup: Create Python/React project
            project_path = Path(tmpdir) / "fullstack-app"
            project_path.mkdir()

            # Python backend
            (project_path / "app.py").write_text("from flask import Flask")
            (project_path / "requirements.txt").write_text("flask==2.0.0")

            # React frontend
            frontend_dir = project_path / "frontend"
            frontend_dir.mkdir()
            (frontend_dir / "package.json").write_text('{"dependencies": {"react": "18.0.0"}}')
            src_dir = frontend_dir / "src"
            src_dir.mkdir()
            (src_dir / "App.tsx").write_text("import React from 'react'")

            # Step 1: Review to get recommendations
            review_cmd = ReviewCommand(project_path)
            review_result = review_cmd.execute()

            # Should recommend both Python and frontend agents
            assert len(review_result.recommended_agents) > 0

            # Step 2: Setup .claude folder
            restructure_cmd = RestructureCommand(project_path)
            restructure_result = restructure_cmd.execute(auto_approve=True)
            assert restructure_result["success"] is True

            # Step 3: Try to pick recommended agents
            claude_force_path = Path(__file__).parent.parent.parent
            if not (claude_force_path / ".claude").exists():
                pytest.skip("claude-force .claude folder not found")

            pick_cmd = PickAgentCommand(
                source_project=claude_force_path,
                target_project=project_path
            )

            # Get list of available agents
            available = pick_cmd.list_available_agents()

            # Try to pick agents that match recommendations
            recommended_names = [agent["agent"] for agent in review_result.recommended_agents]

            # Find agents that exist in both recommendations and available
            to_copy = [name for name in recommended_names if name in available]

            if len(to_copy) > 0:
                # Copy recommended agents
                pick_result = pick_cmd.execute(to_copy[:2])  # Copy first 2
                assert pick_result["success"] is True
                assert pick_result["agents_copied"] > 0


class TestWorkflowOutputFormats:
    """Test that all commands support multiple output formats"""

    def test_all_commands_support_markdown_output(self):
        """Verify all commands can output markdown"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test-project"
            project_path.mkdir()
            (project_path / "main.py").write_text("print('hello')")

            # Review markdown
            review_cmd = ReviewCommand(project_path)
            result = review_cmd.execute()
            markdown = review_cmd.format_markdown(result)
            assert isinstance(markdown, str)
            assert "# Project Analysis" in markdown

            # Restructure markdown
            restructure_cmd = RestructureCommand(project_path)
            result = restructure_cmd.execute(auto_approve=True)
            markdown = restructure_cmd.format_markdown(result)
            assert isinstance(markdown, str)
            assert "# Project Restructure" in markdown

    def test_all_commands_support_json_output(self):
        """Verify all commands can output JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test-project"
            project_path.mkdir()
            (project_path / "main.py").write_text("print('hello')")

            # Review JSON
            review_cmd = ReviewCommand(project_path)
            result = review_cmd.execute()
            json_output = review_cmd.format_json(result)
            parsed = json.loads(json_output)
            assert "stats" in parsed
            assert "total_files" in parsed["stats"]

            # Restructure JSON
            restructure_cmd = RestructureCommand(project_path)
            result = restructure_cmd.execute(auto_approve=True)
            json_output = restructure_cmd.format_json(result)
            parsed = json.loads(json_output)
            assert "success" in parsed


class TestWorkflowErrorHandling:
    """Test error handling across the workflow"""

    def test_restructure_handles_readonly_directory(self):
        """Test restructure handles permission errors gracefully"""
        # This test would require OS-specific permission handling
        # Skipping for now as it's environment-dependent
        pytest.skip("Readonly directory test requires OS-specific setup")

    def test_pick_agent_handles_missing_source_agents(self):
        """Test pick-agent handles missing source agents"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup minimal .claude folders
            for path in [source_path, target_path]:
                claude = path / ".claude"
                claude.mkdir()
                (claude / "agents").mkdir()
                (claude / "contracts").mkdir()
                config = {"agents": {}}
                (claude / "claude.json").write_text(json.dumps(config))

            # Try to copy non-existent agent
            pick_cmd = PickAgentCommand(source_path, target_path)
            result = pick_cmd.execute(["nonexistent-agent"])

            # Should fail gracefully
            assert result["success"] is False
            assert result["agents_copied"] == 0
            assert result["agents_failed"] == 1

    def test_review_handles_empty_directory(self):
        """Test review handles empty directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "empty-project"
            project_path.mkdir()

            # Review empty project
            review_cmd = ReviewCommand(project_path)
            result = review_cmd.execute()

            # Should succeed with 0 files
            assert result.stats.total_files == 0
            assert len(result.tech_stack.languages) == 0


class TestWorkflowSecurityBoundaries:
    """Test that security boundaries are maintained across workflow"""

    def test_commands_reject_system_directories(self):
        """Test all commands reject system directories"""
        system_paths = [Path("/etc"), Path("/sys"), Path("/proc")]

        for sys_path in system_paths:
            if not sys_path.exists():
                continue

            # Review should reject
            with pytest.raises(ValueError):
                ReviewCommand(sys_path)

            # Restructure should reject
            with pytest.raises(ValueError):
                RestructureCommand(sys_path)

            # Pick-agent should reject (both source and target)
            with tempfile.TemporaryDirectory() as tmpdir:
                valid_path = Path(tmpdir)

                with pytest.raises(ValueError):
                    PickAgentCommand(sys_path, valid_path)

                with pytest.raises(ValueError):
                    PickAgentCommand(valid_path, sys_path)

    def test_commands_reject_nonexistent_paths(self):
        """Test all commands reject non-existent paths"""
        fake_path = Path("/nonexistent/fake/path")

        with pytest.raises(ValueError):
            ReviewCommand(fake_path)

        with pytest.raises(ValueError):
            RestructureCommand(fake_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = Path(tmpdir)

            with pytest.raises(ValueError):
                PickAgentCommand(fake_path, valid_path)
