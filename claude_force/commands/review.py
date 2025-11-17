"""
Review Command

Analyzes existing projects for claude-force integration.
Minimal implementation following TDD.
"""

import json
from pathlib import Path
from typing import Dict

from claude_force.project_analysis import ProjectAnalyzer, AnalysisResult
from claude_force.security import validate_project_root


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

        Raises:
            ValueError: If project_path is invalid
        """
        # Validate project path (raises ValueError if invalid)
        self.project_path = validate_project_root(project_path)

    def execute(self) -> AnalysisResult:
        """
        Execute the review command.

        Analyzes the project and returns the result.

        Returns:
            AnalysisResult with project analysis
        """
        # Use ProjectAnalyzer to analyze the project
        analyzer = ProjectAnalyzer(self.project_path)
        result = analyzer.analyze()

        return result

    def format_markdown(self, result: AnalysisResult) -> str:
        """
        Format analysis result as markdown.

        Args:
            result: AnalysisResult to format

        Returns:
            Markdown-formatted string
        """
        return result.to_markdown()

    def format_json(self, result: AnalysisResult) -> str:
        """
        Format analysis result as JSON.

        Args:
            result: AnalysisResult to format

        Returns:
            JSON-formatted string
        """
        return json.dumps(result.to_dict(), indent=2)

    def format_dict(self, result: AnalysisResult) -> Dict:
        """
        Format analysis result as dictionary.

        Args:
            result: AnalysisResult to format

        Returns:
            Dictionary representation
        """
        return result.to_dict()
