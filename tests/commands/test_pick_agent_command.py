"""
Tests for /pick-agent CLI command (TDD - Step by Step)

Following strict TDD: Write tests first, then make them pass.
"""

import pytest
from pathlib import Path
import tempfile
import json

from claude_force.commands.pick_agent import PickAgentCommand


class TestPickAgentCommandBasics:
    """Step 1: Test command basics"""

    def test_command_can_be_imported(self):
        """
        RED: Step 1 - Can we import PickAgentCommand?
        """
        assert PickAgentCommand is not None

    def test_command_can_be_initialized(self):
        """
        RED: Step 2 - Can we create a command instance?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            command = PickAgentCommand(
                source_project=source_path,
                target_project=target_path
            )

            assert command.source_project == source_path
            assert command.target_project == target_path


class TestPickAgentCommandListAgents:
    """Step 2: Test listing available agents"""

    def test_command_lists_available_agents(self):
        """
        RED: Step 3 - Can it list available agents?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Create source .claude folder with agents
            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()

            # Create some test agents
            (source_claude / "agents" / "python-expert.md").write_text("# Python Expert")
            (source_claude / "agents" / "code-reviewer.md").write_text("# Code Reviewer")
            (source_claude / "contracts" / "python-expert.contract").write_text("# Contract")
            (source_claude / "contracts" / "code-reviewer.contract").write_text("# Contract")

            command = PickAgentCommand(source_path, target_path)
            agents = command.list_available_agents()

            # Should return list of agent names
            assert isinstance(agents, list)
            assert "python-expert" in agents
            assert "code-reviewer" in agents

    def test_list_only_includes_agents_with_contracts(self):
        """
        RED: Step 4 - Does it only list agents that have both file and contract?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()

            # Create agent with contract
            (source_claude / "agents" / "complete-agent.md").write_text("# Complete")
            (source_claude / "contracts" / "complete-agent.contract").write_text("# Contract")

            # Create agent without contract
            (source_claude / "agents" / "incomplete-agent.md").write_text("# Incomplete")

            command = PickAgentCommand(source_path, target_path)
            agents = command.list_available_agents()

            # Should only include complete-agent
            assert "complete-agent" in agents
            assert "incomplete-agent" not in agents


class TestPickAgentCommandCopyAgent:
    """Step 3: Test copying individual agents"""

    def test_command_copies_agent_files(self):
        """
        RED: Step 5 - Can it copy an agent?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup source
            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()
            (source_claude / "agents" / "python-expert.md").write_text("# Python Expert Agent")
            (source_claude / "contracts" / "python-expert.contract").write_text("# Python Expert Contract")

            # Setup target
            target_claude = target_path / ".claude"
            target_claude.mkdir()
            (target_claude / "agents").mkdir()
            (target_claude / "contracts").mkdir()

            command = PickAgentCommand(source_path, target_path)
            result = command.copy_agent("python-expert")

            # Should copy both files
            assert result["success"] is True
            assert (target_claude / "agents" / "python-expert.md").exists()
            assert (target_claude / "contracts" / "python-expert.contract").exists()

    def test_copy_preserves_content(self):
        """
        RED: Step 6 - Does it preserve file content?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup source with specific content
            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()

            agent_content = "# Python Expert\n\nThis is the agent definition."
            contract_content = "# Contract\n\nThis is the contract."

            (source_claude / "agents" / "python-expert.md").write_text(agent_content)
            (source_claude / "contracts" / "python-expert.contract").write_text(contract_content)

            # Setup target
            target_claude = target_path / ".claude"
            target_claude.mkdir()
            (target_claude / "agents").mkdir()
            (target_claude / "contracts").mkdir()

            command = PickAgentCommand(source_path, target_path)
            command.copy_agent("python-expert")

            # Verify content matches
            copied_agent = (target_claude / "agents" / "python-expert.md").read_text()
            copied_contract = (target_claude / "contracts" / "python-expert.contract").read_text()

            assert copied_agent == agent_content
            assert copied_contract == contract_content


class TestPickAgentCommandBulkCopy:
    """Step 4: Test copying multiple agents"""

    def test_command_copies_multiple_agents(self):
        """
        RED: Step 7 - Can it copy multiple agents at once?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup source with multiple agents
            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()

            for agent in ["python-expert", "code-reviewer", "database-architect"]:
                (source_claude / "agents" / f"{agent}.md").write_text(f"# {agent}")
                (source_claude / "contracts" / f"{agent}.contract").write_text(f"# {agent} contract")

            # Setup target
            target_claude = target_path / ".claude"
            target_claude.mkdir()
            (target_claude / "agents").mkdir()
            (target_claude / "contracts").mkdir()

            command = PickAgentCommand(source_path, target_path)
            result = command.copy_agents(["python-expert", "code-reviewer"])

            # Should copy both agents
            assert result["copied"] == 2
            assert result["failed"] == 0
            assert (target_claude / "agents" / "python-expert.md").exists()
            assert (target_claude / "agents" / "code-reviewer.md").exists()


class TestPickAgentCommandUpdateConfig:
    """Step 5: Test updating target claude.json"""

    def test_command_updates_claude_json(self):
        """
        RED: Step 8 - Does it update claude.json with new agents?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup source
            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()
            (source_claude / "agents" / "python-expert.md").write_text("# Python Expert")
            (source_claude / "contracts" / "python-expert.contract").write_text("# Contract")

            # Setup source claude.json with agent config
            source_config = {
                "agents": {
                    "python-expert": {
                        "file": "agents/python-expert.md",
                        "contract": "contracts/python-expert.contract",
                        "domains": ["python", "testing"],
                        "priority": 2
                    }
                }
            }
            (source_claude / "claude.json").write_text(json.dumps(source_config))

            # Setup target with existing claude.json
            target_claude = target_path / ".claude"
            target_claude.mkdir()
            (target_claude / "agents").mkdir()
            (target_claude / "contracts").mkdir()

            target_config = {
                "version": "1.0.0",
                "name": "Target Project",
                "agents": {},
                "workflows": {},
                "governance": {},
                "paths": {},
                "rules": {}
            }
            (target_claude / "claude.json").write_text(json.dumps(target_config))

            command = PickAgentCommand(source_path, target_path)
            command.copy_agent("python-expert")
            command.update_config(["python-expert"])

            # Verify claude.json was updated
            updated_config = json.loads((target_claude / "claude.json").read_text())
            assert "python-expert" in updated_config["agents"]
            assert updated_config["agents"]["python-expert"]["file"] == "agents/python-expert.md"


class TestPickAgentCommandExecute:
    """Step 6: Test end-to-end execution"""

    def test_command_execute_copies_and_updates_config(self):
        """
        RED: Step 9 - Does execute() perform complete workflow?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup source
            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()
            (source_claude / "agents" / "python-expert.md").write_text("# Python")
            (source_claude / "contracts" / "python-expert.contract").write_text("# Contract")

            source_config = {
                "agents": {
                    "python-expert": {
                        "file": "agents/python-expert.md",
                        "contract": "contracts/python-expert.contract",
                        "domains": ["python"],
                        "priority": 2
                    }
                }
            }
            (source_claude / "claude.json").write_text(json.dumps(source_config))

            # Setup target
            target_claude = target_path / ".claude"
            target_claude.mkdir()
            (target_claude / "agents").mkdir()
            (target_claude / "contracts").mkdir()

            target_config = {
                "version": "1.0.0",
                "name": "Target",
                "agents": {},
                "workflows": {},
                "governance": {},
                "paths": {},
                "rules": {}
            }
            (target_claude / "claude.json").write_text(json.dumps(target_config))

            command = PickAgentCommand(source_path, target_path)
            result = command.execute(["python-expert"])

            # Should copy files and update config
            assert result["success"] is True
            assert result["agents_copied"] == 1
            assert (target_claude / "agents" / "python-expert.md").exists()

            # Verify config updated
            updated_config = json.loads((target_claude / "claude.json").read_text())
            assert "python-expert" in updated_config["agents"]


class TestPickAgentCommandFormatting:
    """Step 7: Test output formatting"""

    def test_command_formats_result_as_markdown(self):
        """
        RED: Step 10 - Can it format result as markdown?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup minimal structure
            for path in [source_path, target_path]:
                claude = path / ".claude"
                claude.mkdir()
                (claude / "agents").mkdir()
                (claude / "contracts").mkdir()
                config = {"agents": {}, "workflows": {}, "governance": {}, "paths": {}, "rules": {}}
                (claude / "claude.json").write_text(json.dumps(config))

            command = PickAgentCommand(source_path, target_path)
            result = command.execute([])

            # Should format as markdown
            markdown = command.format_markdown(result)
            assert isinstance(markdown, str)
            assert "# Agent Pick Report" in markdown or "# Pick Agent" in markdown

    def test_command_formats_result_as_json(self):
        """
        RED: Step 11 - Can it format result as JSON?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup minimal structure
            for path in [source_path, target_path]:
                claude = path / ".claude"
                claude.mkdir()
                (claude / "agents").mkdir()
                (claude / "contracts").mkdir()
                config = {"agents": {}, "workflows": {}, "governance": {}, "paths": {}, "rules": {}}
                (claude / "claude.json").write_text(json.dumps(config))

            command = PickAgentCommand(source_path, target_path)
            result = command.execute([])

            # Should format as JSON
            json_output = command.format_json(result)
            assert isinstance(json_output, str)
            parsed = json.loads(json_output)
            assert "success" in parsed


class TestPickAgentCommandBackup:
    """Test backup functionality for file safety"""

    def test_backup_created_before_overwriting_existing_agent(self):
        """
        TDD: Backup should be created before overwriting existing agent files
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup source project with agent
            source_claude = source_path / ".claude"
            source_claude.mkdir()
            (source_claude / "agents").mkdir()
            (source_claude / "contracts").mkdir()

            # Create source agent
            (source_claude / "agents" / "test-agent.md").write_text("# New Agent\n\nNew version")
            (source_claude / "contracts" / "test-agent.contract").write_text("contract: new")

            source_config = {
                "agents": {"test-agent": {"skills": ["test"]}},
                "workflows": {},
                "governance": {},
                "paths": {},
                "rules": {}
            }
            (source_claude / "claude.json").write_text(json.dumps(source_config))

            # Setup target project with EXISTING agent (custom version)
            target_claude = target_path / ".claude"
            target_claude.mkdir()
            (target_claude / "agents").mkdir()
            (target_claude / "contracts").mkdir()

            # Create existing agent with custom content
            original_agent_content = "# My Custom Agent\n\nDon't overwrite this!"
            original_contract_content = "contract: custom"
            (target_claude / "agents" / "test-agent.md").write_text(original_agent_content)
            (target_claude / "contracts" / "test-agent.contract").write_text(original_contract_content)

            target_config = {
                "agents": {},
                "workflows": {},
                "governance": {},
                "paths": {},
                "rules": {}
            }
            (target_claude / "claude.json").write_text(json.dumps(target_config))

            # Copy agent (should overwrite and create backup)
            command = PickAgentCommand(source_path, target_path)
            result = command.copy_agent("test-agent")

            # Should succeed
            assert result["success"] is True

            # Backups should exist
            agent_backup = target_claude / "agents" / "test-agent.md.bak"
            contract_backup = target_claude / "contracts" / "test-agent.contract.bak"

            assert agent_backup.exists(), "Agent backup should be created"
            assert contract_backup.exists(), "Contract backup should be created"

            # Backups should contain original content
            assert agent_backup.read_text() == original_agent_content
            assert contract_backup.read_text() == original_contract_content

            # New files should have new content
            assert (target_claude / "agents" / "test-agent.md").read_text() == "# New Agent\n\nNew version"
            assert (target_claude / "contracts" / "test-agent.contract").read_text() == "contract: new"

    def test_no_backup_for_new_agents(self):
        """
        TDD: No backup should be created when copying to new location
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source"
            target_path = Path(tmpdir) / "target"
            source_path.mkdir()
            target_path.mkdir()

            # Setup both projects
            for path in [source_path, target_path]:
                claude = path / ".claude"
                claude.mkdir()
                (claude / "agents").mkdir()
                (claude / "contracts").mkdir()
                config = {"agents": {}, "workflows": {}, "governance": {}, "paths": {}, "rules": {}}
                (claude / "claude.json").write_text(json.dumps(config))

            # Add agent to source only
            source_claude = source_path / ".claude"
            (source_claude / "agents" / "new-agent.md").write_text("# New Agent")
            (source_claude / "contracts" / "new-agent.contract").write_text("contract: v1")

            source_config = json.loads((source_claude / "claude.json").read_text())
            source_config["agents"]["new-agent"] = {"skills": ["test"]}
            (source_claude / "claude.json").write_text(json.dumps(source_config))

            # Copy agent
            command = PickAgentCommand(source_path, target_path)
            result = command.copy_agent("new-agent")

            assert result["success"] is True

            # No backups should exist (agent didn't exist before)
            target_claude = target_path / ".claude"
            agent_backup = target_claude / "agents" / "new-agent.md.bak"
            contract_backup = target_claude / "contracts" / "new-agent.contract.bak"

            assert not agent_backup.exists(), "No backup for new agent file"
            assert not contract_backup.exists(), "No backup for new contract file"
