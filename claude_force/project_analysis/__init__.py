"""
Project Analysis Module

Analyzes existing projects for claude-force integration.
Detects technology stack and recommends agents.
Validates .claude folder structure.
"""

from claude_force.project_analysis.analyzer import ProjectAnalyzer
from claude_force.project_analysis.models import (
    AnalysisResult,
    ProjectStats,
    TechnologyStack,
    AgentRecommendation,
)
from claude_force.project_analysis.detectors import TechnologyDetector
from claude_force.project_analysis.claude_validator import (
    ClaudeValidator,
    ValidationResult,
    ValidationIssue,
)


__all__ = [
    "ProjectAnalyzer",
    "AnalysisResult",
    "ProjectStats",
    "TechnologyStack",
    "AgentRecommendation",
    "TechnologyDetector",
    "ClaudeValidator",
    "ValidationResult",
    "ValidationIssue",
]
