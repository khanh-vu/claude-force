"""
Review Command

Analyzes existing projects for claude-force integration.
Minimal implementation following TDD.
"""

from pathlib import Path


class ReviewCommand:
    """
    /review command implementation

    Analyzes a project and provides recommendations.
    """

    def __init__(self, project_path: Path):
        """
        Initialize review command.

        Args:
            project_path: Path to project to analyze
        """
        self.project_path = project_path
