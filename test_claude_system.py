#!/usr/bin/env python3
"""
Unit tests for Claude Multi-Agent System
Tests all agents, contracts, validators, and system integrity.
"""

import os
import json
import pytest
from pathlib import Path
from typing import Dict, List, Set

# Base path for tests
CLAUDE_DIR = Path(__file__).parent / ".claude"


class TestSystemStructure:
    """Test the overall system structure and file presence."""
    
    def test_required_directories_exist(self):
        """Verify all required directories are present."""
        required_dirs = [
            "agents",
            "contracts",
            "hooks",
            "hooks/validators",
            "macros",
            "tasks",
            "skills"
        ]
        
        for dir_name in required_dirs:
            dir_path = CLAUDE_DIR / dir_name
            assert dir_path.exists(), f"Required directory missing: {dir_name}"
            assert dir_path.is_dir(), f"Path exists but is not a directory: {dir_name}"
    
    def test_required_files_exist(self):
        """Verify all required root files are present."""
        required_files = [
            "README.md",
            "claude.json",
            "commands.md",
            "workflows.md",
            "scorecard.md",
            "task.md"
        ]
        
        for file_name in required_files:
            file_path = CLAUDE_DIR / file_name
            assert file_path.exists(), f"Required file missing: {file_name}"
            assert file_path.is_file(), f"Path exists but is not a file: {file_name}"
    
    def test_hooks_structure(self):
        """Verify hooks directory has all required files."""
        required_hooks = [
            "hooks/README.md",
            "hooks/pre-run.md",
            "hooks/post-run.md"
        ]
        
        for hook in required_hooks:
            hook_path = CLAUDE_DIR / hook
            assert hook_path.exists(), f"Required hook missing: {hook}"


class TestClaudeJSON:
    """Test the claude.json configuration file."""
    
    @pytest.fixture
    def claude_config(self) -> Dict:
        """Load claude.json configuration."""
        config_path = CLAUDE_DIR / "claude.json"
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def test_claude_json_valid(self, claude_config):
        """Verify claude.json is valid JSON."""
        assert isinstance(claude_config, dict), "claude.json must be a valid JSON object"
    
    def test_required_sections_present(self, claude_config):
        """Verify all required sections exist in claude.json."""
        required_sections = [
            "version",
            "name",
            "description",
            "agents",
            "workflows",
            "governance",
            "skills_integration",
            "paths",
            "rules"
        ]
        
        for section in required_sections:
            assert section in claude_config, f"Required section missing: {section}"
    
    def test_agents_section(self, claude_config):
        """Verify agents section is properly configured."""
        agents = claude_config.get("agents", {})
        assert len(agents) > 0, "At least one agent must be defined"
        
        required_agent_fields = ["file", "contract", "domains", "priority"]
        
        for agent_name, agent_config in agents.items():
            for field in required_agent_fields:
                assert field in agent_config, f"Agent {agent_name} missing field: {field}"
            
            # Verify priority is valid
            assert isinstance(agent_config["priority"], int), \
                f"Agent {agent_name} priority must be an integer"
            assert 1 <= agent_config["priority"] <= 3, \
                f"Agent {agent_name} priority must be 1-3"
    
    def test_workflows_section(self, claude_config):
        """Verify workflows reference valid agents."""
        workflows = claude_config.get("workflows", {})
        agents = claude_config.get("agents", {})
        
        assert len(workflows) > 0, "At least one workflow must be defined"
        
        for workflow_name, agent_list in workflows.items():
            assert isinstance(agent_list, list), \
                f"Workflow {workflow_name} must be a list of agents"
            
            for agent in agent_list:
                assert agent in agents, \
                    f"Workflow {workflow_name} references undefined agent: {agent}"
    
    def test_governance_section(self, claude_config):
        """Verify governance configuration."""
        governance = claude_config.get("governance", {})
        
        assert governance.get("hooks_enabled") is True, \
            "Hooks must be enabled for proper governance"
        
        validators = governance.get("validators", [])
        assert len(validators) > 0, "At least one validator must be defined"
        
        expected_validators = [
            "scorecard-validator",
            "write-zone-guard",
            "secret-scan",
            "diff-discipline",
            "format-lint",
            "hierarchy-governance"
        ]
        
        for validator in expected_validators:
            assert validator in validators, \
                f"Required validator missing: {validator}"
    
    def test_skills_integration(self, claude_config):
        """Verify skills integration is configured."""
        skills = claude_config.get("skills_integration", {})
        
        assert skills.get("enabled") is True, \
            "Skills integration should be enabled"
        
        available_skills = skills.get("available_skills", [])
        expected_skills = ["docx", "xlsx", "pptx", "pdf"]
        
        for skill in expected_skills:
            assert skill in available_skills, \
                f"Expected skill missing: {skill}"


class TestAgents:
    """Test all agent files."""
    
    @pytest.fixture
    def claude_config(self) -> Dict:
        """Load claude.json configuration."""
        with open(CLAUDE_DIR / "claude.json", 'r') as f:
            return json.load(f)
    
    def test_all_agents_have_files(self, claude_config):
        """Verify every agent in claude.json has a corresponding file."""
        agents = claude_config.get("agents", {})
        
        for agent_name, agent_config in agents.items():
            agent_file = CLAUDE_DIR / agent_config["file"]
            assert agent_file.exists(), \
                f"Agent file missing for {agent_name}: {agent_file}"
            assert agent_file.is_file(), \
                f"Agent path exists but is not a file: {agent_file}"
    
    def test_agent_files_not_empty(self, claude_config):
        """Verify agent files have content."""
        agents = claude_config.get("agents", {})
        
        for agent_name, agent_config in agents.items():
            agent_file = CLAUDE_DIR / agent_config["file"]
            content = agent_file.read_text()
            
            assert len(content) > 100, \
                f"Agent file {agent_name} seems too short (< 100 chars)"
    
    def test_agent_files_have_required_sections(self, claude_config):
        """Verify agent files contain required sections."""
        agents = claude_config.get("agents", {})
        required_sections = [
            "# ",  # Title
            "## Role",
            "## Domain Expertise",
            "## Responsibilities",
            "## Input Requirements",
            "## Reads",
            "## Writes",
            "## Tools Available",
            "## Guardrails",
            "## Output Format"
        ]
        
        for agent_name, agent_config in agents.items():
            agent_file = CLAUDE_DIR / agent_config["file"]
            content = agent_file.read_text()
            
            for section in required_sections:
                assert section in content, \
                    f"Agent {agent_name} missing required section: {section}"


class TestContracts:
    """Test all contract files."""
    
    @pytest.fixture
    def claude_config(self) -> Dict:
        """Load claude.json configuration."""
        with open(CLAUDE_DIR / "claude.json", 'r') as f:
            return json.load(f)
    
    def test_all_contracts_exist(self, claude_config):
        """Verify every agent has a contract file."""
        agents = claude_config.get("agents", {})
        
        for agent_name, agent_config in agents.items():
            contract_file = CLAUDE_DIR / agent_config["contract"]
            assert contract_file.exists(), \
                f"Contract file missing for {agent_name}: {contract_file}"
    
    def test_contract_files_have_required_sections(self, claude_config):
        """Verify contract files contain required sections."""
        agents = claude_config.get("agents", {})
        required_sections = [
            "# ",  # Title
            "## Agent Identity",
            "## Scope of Authority",
            "## Core Responsibilities",
            "## Deliverables",
            "## Boundaries",
            "## Dependencies",
            "## Input Requirements",
            "## Output Requirements",
            "## Quality Gates"
        ]
        
        for agent_name, agent_config in agents.items():
            contract_file = CLAUDE_DIR / agent_config["contract"]
            content = contract_file.read_text()
            
            for section in required_sections:
                assert section in content, \
                    f"Contract for {agent_name} missing section: {section}"


class TestValidators:
    """Test all validator files."""
    
    @pytest.fixture
    def claude_config(self) -> Dict:
        """Load claude.json configuration."""
        with open(CLAUDE_DIR / "claude.json", 'r') as f:
            return json.load(f)
    
    def test_all_validators_exist(self, claude_config):
        """Verify all validators in claude.json have files."""
        validators = claude_config.get("governance", {}).get("validators", [])
        
        for validator_name in validators:
            validator_file = CLAUDE_DIR / "hooks" / "validators" / f"{validator_name}.md"
            assert validator_file.exists(), \
                f"Validator file missing: {validator_name}"
    
    def test_validator_files_have_structure(self, claude_config):
        """Verify validator files have proper structure."""
        validators = claude_config.get("governance", {}).get("validators", [])
        required_sections = [
            "# ",  # Title
            "## Purpose",
            "## Validation Rules",
            "## Pass Criteria",
            "## Fail Criteria"
        ]
        
        for validator_name in validators:
            validator_file = CLAUDE_DIR / "hooks" / "validators" / f"{validator_name}.md"
            content = validator_file.read_text()
            
            for section in required_sections:
                assert section in content, \
                    f"Validator {validator_name} missing section: {section}"


class TestSkillsIntegration:
    """Test skills integration."""
    
    def test_skills_readme_exists(self):
        """Verify skills README exists."""
        skills_readme = CLAUDE_DIR / "skills" / "README.md"
        assert skills_readme.exists(), "Skills README.md missing"
    
    def test_skills_readme_documents_all_skills(self):
        """Verify skills README documents expected skills."""
        skills_readme = CLAUDE_DIR / "skills" / "README.md"
        content = skills_readme.read_text()
        
        expected_skills = ["DOCX", "XLSX", "PPTX", "PDF"]
        
        for skill in expected_skills:
            assert skill in content, \
                f"Skills README doesn't document {skill} skill"
    
    def test_skills_readme_has_integration_patterns(self):
        """Verify skills README includes integration patterns."""
        skills_readme = CLAUDE_DIR / "skills" / "README.md"
        content = skills_readme.read_text()
        
        assert "Integration Pattern" in content, \
            "Skills README missing integration patterns"
        assert "file_read" in content, \
            "Skills README doesn't show how to read skill documentation"


class TestSystemIntegrity:
    """Test overall system integrity and consistency."""
    
    @pytest.fixture
    def claude_config(self) -> Dict:
        """Load claude.json configuration."""
        with open(CLAUDE_DIR / "claude.json", 'r') as f:
            return json.load(f)
    
    def test_no_orphaned_agent_files(self, claude_config):
        """Verify no agent files exist that aren't in claude.json."""
        agents_dir = CLAUDE_DIR / "agents"
        defined_agents = set(
            Path(cfg["file"]).name 
            for cfg in claude_config.get("agents", {}).values()
        )
        
        actual_agent_files = set(
            f.name for f in agents_dir.glob("*.md")
        )
        
        orphaned = actual_agent_files - defined_agents
        assert len(orphaned) == 0, \
            f"Orphaned agent files found (not in claude.json): {orphaned}"
    
    def test_no_orphaned_contract_files(self, claude_config):
        """Verify no contract files exist that aren't in claude.json."""
        contracts_dir = CLAUDE_DIR / "contracts"
        defined_contracts = set(
            Path(cfg["contract"]).name 
            for cfg in claude_config.get("agents", {}).values()
        )
        
        actual_contract_files = set(
            f.name for f in contracts_dir.glob("*.contract")
        )
        
        orphaned = actual_contract_files - defined_contracts
        assert len(orphaned) == 0, \
            f"Orphaned contract files found: {orphaned}"
    
    def test_agent_contract_names_match(self, claude_config):
        """Verify agent file names match their contract file names."""
        agents = claude_config.get("agents", {})
        
        for agent_name in agents.keys():
            agent_file = Path(agents[agent_name]["file"]).stem
            contract_file = Path(agents[agent_name]["contract"]).stem
            
            assert agent_file == contract_file, \
                f"Agent {agent_name}: file name '{agent_file}' doesn't match contract '{contract_file}'"
    
    def test_workflow_coverage(self, claude_config):
        """Verify workflows cover all agents appropriately."""
        workflows = claude_config.get("workflows", {})
        agents = set(claude_config.get("agents", {}).keys())
        
        # Get all agents used in workflows
        agents_in_workflows = set()
        for workflow_agents in workflows.values():
            agents_in_workflows.update(workflow_agents)
        
        # Some agents might not be in workflows (like document-writer-expert)
        # but most should be
        coverage = len(agents_in_workflows) / len(agents)
        assert coverage >= 0.7, \
            f"Only {coverage:.0%} of agents are used in workflows (expected >= 70%)"


class TestDocumentation:
    """Test documentation completeness."""
    
    def test_readme_is_comprehensive(self):
        """Verify README has all expected sections."""
        readme = CLAUDE_DIR / "README.md"
        content = readme.read_text()
        
        expected_sections = [
            "Purpose",
            "Directory Structure",
            "Quick Start",
            "Agents",
            "Workflows"
        ]
        
        for section in expected_sections:
            assert section in content, \
                f"README missing section about: {section}"
    
    def test_commands_md_exists(self):
        """Verify commands.md provides command reference."""
        commands = CLAUDE_DIR / "commands.md"
        assert commands.exists(), "commands.md missing"
        
        content = commands.read_text()
        assert len(content) > 200, "commands.md seems incomplete"
    
    def test_workflows_md_exists(self):
        """Verify workflows.md documents workflow patterns."""
        workflows = CLAUDE_DIR / "workflows.md"
        assert workflows.exists(), "workflows.md missing"
        
        content = workflows.read_text()
        assert len(content) > 300, "workflows.md seems incomplete"


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
