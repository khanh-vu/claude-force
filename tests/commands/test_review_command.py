"""
Tests for /review CLI command (TDD - Step by Step)

Following strict TDD: One test at a time.
"""

import pytest
from pathlib import Path
import tempfile
import json

# This will fail initially - that's expected!
from claude_force.commands.review import ReviewCommand


class TestReviewCommandBasics:
    """Step 1: Test command basics"""

    def test_command_can_be_imported(self):
        """
        RED: Step 1 - Can we import ReviewCommand?

        This is the simplest possible test.
        Just checking if the class exists.
        """
        assert ReviewCommand is not None

    def test_command_can_be_initialized_with_project_path(self):
        """
        RED: Step 2 - Can we create a ReviewCommand instance?

        Test that we can instantiate the command with a project path.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # This should work
            command = ReviewCommand(project_path)

            # Command should store the project path
            assert command.project_path == project_path


class TestReviewCommandExecution:
    """Step 3: Test command execution"""

    def test_command_executes_and_returns_result(self):
        """
        RED: Step 3 - Can execute() run analysis?

        Test that execute() method:
        1. Runs the ProjectAnalyzer
        2. Returns an AnalysisResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create a simple Python file
            (project_path / "main.py").write_text("print('hello')")

            # Execute the command
            command = ReviewCommand(project_path)
            result = command.execute()

            # Should return an AnalysisResult
            from claude_force.project_analysis import AnalysisResult
            assert isinstance(result, AnalysisResult)

            # Result should contain project info
            assert result.project_path == str(project_path)
            assert result.stats.total_files >= 1


class TestReviewCommandValidation:
    """Step 4: Test input validation"""

    def test_command_rejects_nonexistent_path(self):
        """
        RED: Step 4 - Does it validate paths?

        Test that ReviewCommand raises an error for nonexistent paths.
        """
        nonexistent = Path("/nonexistent/path/to/project")

        with pytest.raises(ValueError, match="does not exist"):
            ReviewCommand(nonexistent)

    def test_command_rejects_file_instead_of_directory(self):
        """
        RED: Step 5 - Does it reject files?

        Test that ReviewCommand raises an error when given a file instead of directory.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            file_path = project_path / "file.txt"
            file_path.write_text("not a directory")

            with pytest.raises(ValueError, match="not a directory"):
                ReviewCommand(file_path)

    def test_command_rejects_system_directory(self):
        """
        RED: Step 6 - Does it reject system dirs?

        Test that ReviewCommand raises an error for system directories.
        """
        if Path("/etc").exists():
            with pytest.raises(ValueError, match="system directory"):
                ReviewCommand(Path("/etc"))


class TestReviewCommandOutput:
    """Step 7-9: Test output formatting"""

    def test_command_formats_result_as_markdown(self):
        """
        RED: Step 7 - Can format as markdown?

        Test that ReviewCommand can format the analysis result as markdown.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create a simple Python file
            (project_path / "main.py").write_text("print('hello')")

            # Execute the command
            command = ReviewCommand(project_path)
            result = command.execute()

            # Should be able to format as markdown
            markdown_output = command.format_markdown(result)

            # Verify it's a string
            assert isinstance(markdown_output, str)

            # Verify it contains expected sections
            assert "# Project Analysis Report" in markdown_output
            assert "## Project Statistics" in markdown_output
            assert "## Technology Stack" in markdown_output
            assert str(project_path) in markdown_output

    def test_command_formats_result_as_json(self):
        """
        RED: Step 8 - Can format as JSON?

        Test that ReviewCommand can format the analysis result as JSON.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create a simple Python file
            (project_path / "main.py").write_text("print('hello')")

            # Execute the command
            command = ReviewCommand(project_path)
            result = command.execute()

            # Should be able to format as JSON
            json_output = command.format_json(result)

            # Verify it's a valid JSON string
            assert isinstance(json_output, str)
            parsed = json.loads(json_output)

            # Verify it contains expected keys
            assert "timestamp" in parsed
            assert "project_path" in parsed
            assert "stats" in parsed
            assert "tech_stack" in parsed
            assert parsed["project_path"] == str(project_path)

    def test_command_formats_result_as_dict(self):
        """
        RED: Step 9 - Can format as dictionary?

        Test that ReviewCommand can format the analysis result as a dictionary.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create a simple Python file
            (project_path / "main.py").write_text("print('hello')")

            # Execute the command
            command = ReviewCommand(project_path)
            result = command.execute()

            # Should be able to format as dict
            dict_output = command.format_dict(result)

            # Verify it's a dictionary
            assert isinstance(dict_output, dict)

            # Verify it contains expected keys
            assert "timestamp" in dict_output
            assert "project_path" in dict_output
            assert "stats" in dict_output
            assert "tech_stack" in dict_output
            assert dict_output["project_path"] == str(project_path)
