"""
Project Analysis Module

Analyzes existing projects for claude-force integration.
Detects technology stack and recommends agents.
"""

from claude_force.project_analysis.analyzer import ProjectAnalyzer
from claude_force.project_analysis.models import (
    AnalysisResult,
    ProjectStats,
    TechnologyStack,
    AgentRecommendation,
)
from claude_force.project_analysis.detectors import TechnologyDetector


__all__ = [
    "ProjectAnalyzer",
    "AnalysisResult",
    "ProjectStats",
    "TechnologyStack",
    "AgentRecommendation",
    "TechnologyDetector",
]
