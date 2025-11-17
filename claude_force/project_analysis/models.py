"""
Data models for project analysis

Following TDD: Implementing minimal data structures to pass tests.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


@dataclass
class ProjectStats:
    """Statistics about the analyzed project"""

    total_files: int = 0
    total_size_bytes: int = 0
    total_lines: int = 0
    files_by_extension: Dict[str, int] = field(default_factory=dict)
    has_tests: bool = False
    is_git_repo: bool = False
    files_analyzed: int = 0  # For max_files limit tracking

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TechnologyStack:
    """Detected technology stack"""

    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    infrastructure: List[str] = field(default_factory=list)
    primary_language: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AgentRecommendation:
    """Recommended agent with confidence score"""

    agent: str
    confidence: float  # 0.0 to 1.0
    reason: str
    skills_required: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AnalysisResult:
    """Complete analysis result"""

    timestamp: datetime
    project_path: str
    stats: ProjectStats
    tech_stack: TechnologyStack
    recommended_agents: List[Dict] = field(default_factory=list)
    sensitive_files_skipped: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "project_path": str(self.project_path),
            "stats": self.stats.to_dict(),
            "tech_stack": self.tech_stack.to_dict(),
            "recommended_agents": self.recommended_agents,
            "sensitive_files_skipped": self.sensitive_files_skipped,
            "warnings": self.warnings,
        }

    def to_markdown(self) -> str:
        """Convert to markdown report"""
        lines = [
            "# Project Analysis Report",
            "",
            f"**Generated**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project**: {self.project_path}",
            "",
            "## Project Statistics",
            "",
            f"- **Total Files**: {self.stats.total_files}",
            f"- **Total Size**: {self.stats.total_size_bytes:,} bytes",
            f"- **Total Lines**: {self.stats.total_lines:,}",
            f"- **Has Tests**: {'Yes' if self.stats.has_tests else 'No'}",
            f"- **Git Repository**: {'Yes' if self.stats.is_git_repo else 'No'}",
            "",
            "### Files by Extension",
            "",
        ]

        for ext, count in sorted(self.stats.files_by_extension.items()):
            lines.append(f"- `{ext}`: {count} files")

        lines.extend([
            "",
            "## Technology Stack",
            "",
        ])

        if self.tech_stack.primary_language:
            lines.append(f"**Primary Language**: {self.tech_stack.primary_language}")
            lines.append("")

        if self.tech_stack.languages:
            lines.append("**Languages**: " + ", ".join(self.tech_stack.languages))
        if self.tech_stack.frameworks:
            lines.append("**Frameworks**: " + ", ".join(self.tech_stack.frameworks))
        if self.tech_stack.databases:
            lines.append("**Databases**: " + ", ".join(self.tech_stack.databases))
        if self.tech_stack.infrastructure:
            lines.append("**Infrastructure**: " + ", ".join(self.tech_stack.infrastructure))

        lines.extend([
            "",
            "## Recommended Agents",
            "",
        ])

        for i, rec in enumerate(self.recommended_agents, 1):
            confidence_pct = rec['confidence'] * 100
            lines.append(f"{i}. **{rec['agent']}** ({confidence_pct:.0f}% confidence)")
            lines.append(f"   - {rec['reason']}")
            lines.append("")

        if self.sensitive_files_skipped:
            lines.extend([
                "## Sensitive Files Skipped",
                "",
                f"For privacy and security, {len(self.sensitive_files_skipped)} sensitive files were not analyzed:",
                "",
            ])
            for file in self.sensitive_files_skipped[:10]:  # Show first 10
                lines.append(f"- {file}")
            if len(self.sensitive_files_skipped) > 10:
                lines.append(f"- ... and {len(self.sensitive_files_skipped) - 10} more")

        return "\n".join(lines)
