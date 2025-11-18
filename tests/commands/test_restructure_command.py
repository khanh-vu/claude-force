"""
Tests for /restructure CLI command (TDD - Step by Step)

Following strict TDD: One test at a time.
"""

import pytest
from pathlib import Path
import tempfile
import json

from claude_force.commands.restructure import RestructureCommand
from claude_force.project_analysis.claude_validator import ValidationResult


class TestRestructureCommandBasics:
    """Step 1: Test command basics"""

    def test_command_can_be_imported(self):
        """
        RED: Step 1 - Can we import RestructureCommand?
        """
        assert RestructureCommand is not None

    def test_command_can_be_initialized(self):
        """
        RED: Step 2 - Can we create a command instance?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            assert command.project_path == project_path


class TestRestructureCommandValidation:
    """Step 2: Test validation functionality"""

    def test_command_validates_project(self):
        """
        RED: Step 3 - Can it run validation?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            # Run validation
            result = command.validate()

            # Should return ValidationResult
            assert isinstance(result, ValidationResult)

    def test_command_detects_missing_claude_folder(self):
        """
        RED: Step 4 - Does it detect missing .claude folder?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            result = command.validate()

            # Should detect missing .claude folder
            assert result.is_valid is False
            assert len(result.errors()) > 0


class TestRestructureCommandFixGeneration:
    """Step 3: Test fix plan generation"""

    def test_command_generates_fix_plan(self):
        """
        RED: Step 5 - Can it generate a fix plan?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            # Validate first
            validation = command.validate()

            # Generate fix plan
            fix_plan = command.generate_fix_plan(validation)

            # Should return a list of fixes
            assert isinstance(fix_plan, list)
            assert len(fix_plan) > 0

    def test_fix_plan_contains_fix_details(self):
        """
        RED: Step 6 - Does fix plan contain proper details?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            validation = command.validate()
            fix_plan = command.generate_fix_plan(validation)

            # Each fix should have details
            for fix in fix_plan:
                assert "action" in fix
                assert "description" in fix
                assert "path" in fix


class TestRestructureCommandApplyFixes:
    """Step 4: Test applying fixes"""

    def test_command_can_apply_fixes(self):
        """
        RED: Step 7 - Can it apply fixes?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            # Get validation and fix plan
            validation = command.validate()
            fix_plan = command.generate_fix_plan(validation)

            # Apply fixes (auto mode, no approval needed)
            result = command.apply_fixes(fix_plan, auto_approve=True)

            # Should return result
            assert isinstance(result, dict)
            assert "applied" in result
            assert "skipped" in result

    def test_applying_fixes_creates_claude_folder(self):
        """
        RED: Step 8 - Does it create .claude folder?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"

            # Verify .claude doesn't exist
            assert not claude_path.exists()

            command = RestructureCommand(project_path)
            validation = command.validate()
            fix_plan = command.generate_fix_plan(validation)
            command.apply_fixes(fix_plan, auto_approve=True)

            # Now .claude should exist
            assert claude_path.exists()
            assert claude_path.is_dir()

    def test_applying_fixes_creates_required_files(self):
        """
        RED: Step 9 - Does it create required files?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"

            command = RestructureCommand(project_path)
            # Use execute() which handles iterative fixing
            command.execute(auto_approve=True)

            # Required files should exist
            assert (claude_path / "README.md").exists()
            assert (claude_path / "claude.json").exists()
            assert (claude_path / "task.md").exists()
            assert (claude_path / "scorecard.md").exists()

    def test_applying_fixes_creates_required_directories(self):
        """
        RED: Step 10 - Does it create required directories?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"

            command = RestructureCommand(project_path)
            # Use execute() which handles iterative fixing
            command.execute(auto_approve=True)

            # Required directories should exist
            assert (claude_path / "agents").exists()
            assert (claude_path / "contracts").exists()
            assert (claude_path / "hooks").exists()
            assert (claude_path / "macros").exists()
            assert (claude_path / "tasks").exists()


class TestRestructureCommandExecute:
    """Step 5: Test end-to-end execution"""

    def test_command_execute_validates_and_fixes(self):
        """
        RED: Step 11 - Does execute() run full workflow?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            # Execute (should validate, plan, and apply fixes)
            result = command.execute(auto_approve=True)

            # Should return comprehensive result
            assert isinstance(result, dict)
            assert "validation" in result
            assert "fixes_applied" in result
            assert "success" in result

    def test_execute_creates_valid_claude_folder(self):
        """
        RED: Step 12 - Does execute() create valid .claude folder?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            # Execute
            result = command.execute(auto_approve=True)

            # Re-validate to ensure it's now valid
            validation = command.validate()

            # Should have no errors now
            errors = validation.errors()
            assert len(errors) == 0


class TestRestructureCommandFormattting:
    """Step 6: Test output formatting"""

    def test_command_formats_result_as_markdown(self):
        """
        RED: Step 13 - Can it format result as markdown?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            result = command.execute(auto_approve=True)

            # Should be able to format as markdown
            markdown = command.format_markdown(result)

            assert isinstance(markdown, str)
            assert "# Restructure Report" in markdown or "# Project Restructure" in markdown

    def test_command_formats_result_as_json(self):
        """
        RED: Step 14 - Can it format result as JSON?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            result = command.execute(auto_approve=True)

            # Should be able to format as JSON
            json_output = command.format_json(result)

            assert isinstance(json_output, str)
            parsed = json.loads(json_output)
            assert "success" in parsed


class TestRestructureCommandInteractive:
    """Step 7: Test interactive approval mode"""

    def test_command_skips_unapproved_fixes(self):
        """
        RED: Step 15 - Does it skip fixes when not approved?
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            command = RestructureCommand(project_path)

            validation = command.validate()
            fix_plan = command.generate_fix_plan(validation)

            # Apply with auto_approve=False and no approval callback
            # Should skip all fixes
            result = command.apply_fixes(fix_plan, auto_approve=False)

            # All should be skipped
            assert result["skipped"] > 0
            assert result["applied"] == 0


class TestRestructureCommandBackup:
    """Test backup functionality for file safety"""

    def test_existing_valid_files_not_overwritten(self):
        """
        TDD: Existing valid files should NOT be overwritten (no backup needed)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create existing README.md with custom content
            readme = claude_path / "README.md"
            original_content = "# My Custom README\n\nDon't overwrite this!"
            readme.write_text(original_content)

            # Run restructure
            command = RestructureCommand(project_path)
            result = command.execute(auto_approve=True)

            # Original file should still exist with original content (not overwritten)
            assert readme.read_text() == original_content, "Original file should not be overwritten"

            # No backup should be created (file wasn't touched)
            backup_path = claude_path / "README.md.bak"
            assert not backup_path.exists(), "No backup should be created for untouched files"

    def test_no_backup_for_new_files(self):
        """
        TDD: No backup should be created for new files (nothing to backup)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Run restructure (creates .claude from scratch)
            command = RestructureCommand(project_path)
            result = command.execute(auto_approve=True)

            # Should be no backup files
            claude_path = project_path / ".claude"
            backup_files = list(claude_path.glob("*.bak"))
            assert len(backup_files) == 0, "No backups should be created for new files"

    def test_idempotent_restructure_doesnt_modify_files(self):
        """
        TDD: Running restructure multiple times should be idempotent
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # First restructure - creates everything
            command = RestructureCommand(project_path)
            command.execute(auto_approve=True)

            claude_path = project_path / ".claude"
            readme = claude_path / "README.md"

            # Get content after first run
            first_content = readme.read_text()
            first_mtime = readme.stat().st_mtime

            # Second restructure - should not modify existing files
            import time
            time.sleep(0.1)  # Ensure mtime would change if file was rewritten
            command.execute(auto_approve=True)

            second_content = readme.read_text()
            second_mtime = readme.stat().st_mtime

            # Files should be unchanged
            assert second_content == first_content
            assert second_mtime == first_mtime, "File should not be modified on second run"

            # No backups should exist
            backup_path = claude_path / "README.md.bak"
            assert not backup_path.exists(), "No backup for idempotent operations"

    def test_backup_preserves_file_permissions(self):
        """
        TDD: Backup should preserve original file permissions and metadata
        """
        import os
        import stat

        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            claude_path = project_path / ".claude"
            claude_path.mkdir()

            # Create file with specific permissions
            readme = claude_path / "README.md"
            readme.write_text("Original content")
            os.chmod(readme, stat.S_IRUSR | stat.S_IWUSR)  # 0600

            original_stat = readme.stat()

            # Run restructure
            command = RestructureCommand(project_path)
            command.execute(auto_approve=True)

            # Check backup preserves metadata
            backup_path = claude_path / "README.md.bak"
            if backup_path.exists():
                backup_stat = backup_path.stat()
                # Permissions should be preserved (shutil.copy2 does this)
                assert stat.S_IMODE(backup_stat.st_mode) == stat.S_IMODE(original_stat.st_mode)
