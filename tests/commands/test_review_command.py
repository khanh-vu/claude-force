"""
Tests for /review CLI command (TDD - Step by Step)

Following strict TDD: One test at a time.
"""

import pytest
from pathlib import Path
import tempfile

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
