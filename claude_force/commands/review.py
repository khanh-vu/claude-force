"""
Review Command

Analyzes existing projects for claude-force integration.
Minimal implementation following TDD.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional

from claude_force.project_analysis import ProjectAnalyzer, AnalysisResult
from claude_force.security import validate_project_root

logger = logging.getLogger(__name__)


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

    def execute(
        self,
        show_progress: bool = True,
        timeout: Optional[float] = None
    ) -> AnalysisResult:
        """
        Execute the review command with error handling.

        Analyzes the project and returns the result.

        Args:
            show_progress: Whether to show progress messages (default: True)
            timeout: Maximum execution time in seconds (None = no timeout)

        Returns:
            AnalysisResult with project analysis

        Raises:
            ValueError: If analysis fails with user-friendly error message
            TimeoutError: If operation exceeds timeout (best effort)

        Note:
            Timeout is "best effort" - operation may complete slightly after timeout
            for operations that cannot be safely interrupted.
        """
        start_time = time.time() if timeout else None

        logger.info(f"Starting project review: {self.project_path}")
        logger.debug(f"Review settings - show_progress: {show_progress}, timeout: {timeout}")

        try:
            if show_progress:
                print(f"🔍 Analyzing project: {self.project_path}")
                print("   Scanning files...")

            # Use ProjectAnalyzer to analyze the project
            analyzer = ProjectAnalyzer(self.project_path)
            result = analyzer.analyze()

            # Check timeout after analysis
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Analysis exceeded timeout of {timeout}s")
                raise TimeoutError(f"Analysis exceeded timeout of {timeout}s")

            logger.info(f"Analysis complete: {result.stats.total_files} files, {result.stats.total_lines} lines")
            logger.debug(f"Languages detected: {result.tech_stack.languages}")
            logger.debug(f"Recommended agents: {len(result.recommended_agents)}")

            if show_progress:
                print(f"✓ Analysis complete: {result.stats.total_files} files analyzed")
                if result.stats.files_analyzed > 0:
                    print(f"   {result.stats.total_lines:,} lines of code")
                if len(result.tech_stack.languages) > 0:
                    print(f"   Languages: {', '.join(result.tech_stack.languages)}")

            return result

        except PermissionError as e:
            logger.error(f"Permission denied during analysis: {e}")
            raise ValueError(f"Permission denied analyzing project: {e}")

        except OSError as e:
            logger.error(f"OS error during analysis: {e}")
            raise ValueError(f"Error accessing project: {e}")

        except TimeoutError:
            # Re-raise TimeoutError as-is
            raise

        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            raise ValueError(f"Analysis failed: {e}")

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

        Raises:
            ValueError: If result cannot be serialized to JSON
        """
        try:
            return json.dumps(result.to_dict(), indent=2)
        except TypeError as e:
            raise ValueError(f"Cannot serialize result to JSON: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid data for JSON serialization: {e}")

    def format_dict(self, result: AnalysisResult) -> Dict:
        """
        Format analysis result as dictionary.

        Args:
            result: AnalysisResult to format

        Returns:
            Dictionary representation
        """
        return result.to_dict()
