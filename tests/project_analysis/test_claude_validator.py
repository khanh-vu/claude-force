"""
Tests for ClaudeValidator (TDD - Step by Step)

Following strict TDD: Write tests first, then make them pass.
"""

import pytest
from pathlib import Path
import tempfile
import json
import os

from claude_force.project_analysis.claude_validator import (
    ClaudeValidator,
    ValidationResult,
    ValidationIssue,
)


class TestClaudeValidatorBasics:
    """Step 1: Test validator initialization"""

    def test_validator_can_be_imported(self):
        """
        RED: Step 1 - Can we import ClaudeValidator?
        """
        assert ClaudeValidator is not None

    def test_validator_can_be_initialized(self):
        """
        RED: Step 2 - Can we create a validator instance?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            validator = ClaudeValidator(project_path)

            assert validator.project_path == project_path
            assert validator.claude_path == project_path / ".claude"


class TestClaudeValidatorMissingFolder:
    """Step 2: Test validation when .claude folder doesn't exist"""

    def test_validates_missing_claude_folder(self):
        """
        RED: Step 3 - Does it detect missing .claude folder?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            validator = ClaudeValidator(project_path)

            result = validator.validate()

            # Should return invalid result
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False

            # Should have error about missing .claude folder
            errors = result.errors()
            assert len(errors) >= 1
            assert any(".claude folder does not exist" in e.message for e in errors)

    def test_missing_folder_has_fix_available(self):
        """
        RED: Step 4 - Is fix available for missing .claude folder?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            validator = ClaudeValidator(project_path)

            result = validator.validate()

            # Should have fixable issue
            fixable = result.fixable_issues()
            assert len(fixable) >= 1
            assert any(".claude folder" in f.message for f in fixable)


class TestClaudeValidatorRequiredFiles:
    """Step 3: Test validation of required files"""

    def test_detects_missing_required_files(self):
        """
        RED: Step 5 - Does it detect all missing required files?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should have errors for missing required files
            errors = result.errors()

            # Check for each required file
            assert any("README.md" in e.message for e in errors)
            assert any("claude.json" in e.message for e in errors)
            assert any("task.md" in e.message for e in errors)
            assert any("scorecard.md" in e.message for e in errors)

    def test_validates_when_required_files_exist(self):
        """
        RED: Step 6 - Does it pass when required files exist?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create required files
            (claude_path / "README.md").write_text("# README")
            (claude_path / "task.md").write_text("# Task")
            (claude_path / "scorecard.md").write_text("# Scorecard")

            # Create minimal valid claude.json
            config = {
                "version": "1.0.0",
                "name": "Test",
                "agents": {},
                "workflows": {},
                "governance": {},
                "paths": {},
                "rules": {}
            }
            (claude_path / "claude.json").write_text(json.dumps(config))

            # Create required directories
            (claude_path / "agents").mkdir()
            (claude_path / "contracts").mkdir()
            (claude_path / "hooks").mkdir()
            (claude_path / "macros").mkdir()
            (claude_path / "tasks").mkdir()

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should not have errors for missing required files
            errors = result.errors()
            missing_file_errors = [e for e in errors if e.category == "missing_file"]
            assert len(missing_file_errors) == 0


class TestClaudeValidatorRequiredDirectories:
    """Step 4: Test validation of required directories"""

    def test_detects_missing_required_directories(self):
        """
        RED: Step 7 - Does it detect missing required directories?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should have errors for missing directories
            errors = result.errors()

            assert any("agents" in e.message for e in errors)
            assert any("contracts" in e.message for e in errors)
            assert any("hooks" in e.message for e in errors)
            assert any("macros" in e.message for e in errors)
            assert any("tasks" in e.message for e in errors)

    def test_validates_when_required_directories_exist(self):
        """
        RED: Step 8 - Does it pass when required directories exist?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create required directories
            (claude_path / "agents").mkdir()
            (claude_path / "contracts").mkdir()
            (claude_path / "hooks").mkdir()
            (claude_path / "macros").mkdir()
            (claude_path / "tasks").mkdir()

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should not have errors for missing required directories
            errors = result.errors()
            missing_dir_errors = [e for e in errors if e.category == "missing_directory" and "Required" in e.message]
            assert len(missing_dir_errors) == 0


class TestClaudeValidatorOptionalFiles:
    """Step 5: Test validation of optional files (warnings)"""

    def test_warns_about_missing_optional_files(self):
        """
        RED: Step 9 - Does it warn about missing optional files?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should have warnings for optional files
            warnings = result.warnings()

            # Check for optional files
            assert any("work.md" in w.message for w in warnings)
            assert any("commands.md" in w.message for w in warnings)
            assert any("workflows.md" in w.message for w in warnings)


class TestClaudeValidatorClaudeJson:
    """Step 6: Test claude.json validation"""

    def test_detects_invalid_json(self):
        """
        RED: Step 10 - Does it detect invalid JSON?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create invalid JSON
            (claude_path / "claude.json").write_text("{invalid json")

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should have error about invalid JSON
            errors = result.errors()
            assert any("not valid JSON" in e.message for e in errors)

    def test_detects_missing_required_fields(self):
        """
        RED: Step 11 - Does it detect missing required fields in claude.json?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create JSON with missing fields
            config = {"version": "1.0.0"}
            (claude_path / "claude.json").write_text(json.dumps(config))

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should have errors for missing fields
            errors = result.errors()
            assert any("name" in e.message for e in errors)
            assert any("agents" in e.message for e in errors)
            assert any("workflows" in e.message for e in errors)
            assert any("governance" in e.message for e in errors)
            assert any("paths" in e.message for e in errors)
            assert any("rules" in e.message for e in errors)

    def test_validates_complete_claude_json(self):
        """
        RED: Step 12 - Does it pass with complete claude.json?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create complete config
            config = {
                "version": "1.0.0",
                "name": "Test Project",
                "agents": {},
                "workflows": {},
                "governance": {},
                "paths": {},
                "rules": {}
            }
            (claude_path / "claude.json").write_text(json.dumps(config))

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should not have errors about missing fields
            errors = result.errors()
            config_errors = [e for e in errors if "claude.json missing required field" in e.message]
            assert len(config_errors) == 0


class TestClaudeValidatorAgentReferences:
    """Step 7: Test agent file reference validation"""

    def test_warns_about_missing_agent_files(self):
        """
        RED: Step 13 - Does it warn about missing agent files?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create config with agent reference
            config = {
                "version": "1.0.0",
                "name": "Test",
                "agents": {
                    "test-agent": {
                        "file": "agents/test-agent.md",
                        "contract": "contracts/test-agent.contract"
                    }
                },
                "workflows": {},
                "governance": {},
                "paths": {},
                "rules": {}
            }
            (claude_path / "claude.json").write_text(json.dumps(config))

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            # Should warn about missing agent file
            warnings = result.warnings()
            assert any("test-agent.md" in w.message for w in warnings)
            assert any("test-agent.contract" in w.message for w in warnings)


class TestValidationResultHelpers:
    """Step 8: Test ValidationResult helper methods"""

    def test_errors_method_filters_errors(self):
        """
        RED: Step 14 - Does errors() method work?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            # Don't create .claude folder - will have errors

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            errors = result.errors()
            # All should be severity "error"
            assert all(e.severity == "error" for e in errors)

    def test_warnings_method_filters_warnings(self):
        """
        RED: Step 15 - Does warnings() method work?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            warnings = result.warnings()
            # All should be severity "warning"
            assert all(w.severity == "warning" for w in warnings)

    def test_fixable_issues_method_filters_fixable(self):
        """
        RED: Step 16 - Does fixable_issues() method work?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            # No .claude folder

            validator = ClaudeValidator(project_path)
            result = validator.validate()

            fixable = result.fixable_issues()
            # All should have fix_available = True
            assert all(f.fix_available for f in fixable)
