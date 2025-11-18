"""
Project Analyzer

Following TDD: Minimal implementation to pass all tests.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import logging

from claude_force.security import (
    ProjectPathValidator,
    SensitiveFileDetector,
    validate_project_root,
    SecurityError,
)
from claude_force.project_analysis.models import (
    AnalysisResult,
    ProjectStats,
    TechnologyStack,
    AgentRecommendation,
)
from claude_force.project_analysis.detectors import TechnologyDetector


logger = logging.getLogger(__name__)


class ProjectAnalyzer:
    """
    Analyzes existing projects for claude-force integration.

    Following TDD: Implementation guided by test requirements.
    """

    def __init__(
        self,
        project_root: Path,
        skip_sensitive: bool = True,
        max_depth: Optional[int] = None,
        max_files: Optional[int] = None,
        max_recommendations: int = 10,
    ):
        """
        Initialize project analyzer.

        Args:
            project_root: Path to project directory
            skip_sensitive: Skip sensitive files during analysis
            max_depth: Maximum directory depth to traverse
            max_files: Maximum number of files to analyze
            max_recommendations: Maximum agent recommendations

        Raises:
            ValueError: If project_root is invalid
        """
        # Validate project root (TDD requirement)
        self.project_root = validate_project_root(project_root)

        # Store configuration
        self.skip_sensitive = skip_sensitive
        self.max_depth = max_depth
        self.max_files = max_files
        self.max_recommendations = max_recommendations

        # Initialize security components
        self.path_validator = ProjectPathValidator(self.project_root)
        self.sensitive_detector = SensitiveFileDetector()

        # Initialize tech detector
        self.tech_detector = TechnologyDetector(self.project_root)

        logger.info(f"ProjectAnalyzer initialized for: {self.project_root}")

    def analyze(self) -> AnalysisResult:
        """
        Analyze the project and generate recommendations.

        Returns:
            AnalysisResult with complete analysis

        Raises:
            SecurityError: If path validation fails
        """
        logger.info("Starting project analysis...")

        # Collect statistics
        stats = self._collect_statistics()

        # Detect technology stack
        tech_stack = self._detect_technology_stack(stats)

        # Generate agent recommendations
        recommended_agents = self._recommend_agents(stats, tech_stack)

        # Build result
        result = AnalysisResult(
            timestamp=datetime.now(),
            project_path=str(self.project_root),
            stats=stats,
            tech_stack=tech_stack,
            recommended_agents=recommended_agents,
            sensitive_files_skipped=self._sensitive_files,
            warnings=self._warnings,
        )

        logger.info(f"Analysis complete: {stats.total_files} files analyzed")
        return result

    def _collect_statistics(self) -> ProjectStats:
        """Collect project statistics"""
        stats = ProjectStats()

        self._sensitive_files = []
        self._warnings = []

        files_analyzed = 0

        try:
            # Walk project directory with safety checks
            for dirpath, dirnames, filenames in self.path_validator.safe_walk(
                self.project_root, max_depth=self.max_depth
            ):
                for filename in filenames:
                    file_path = dirpath / filename

                    # Check file limit
                    if self.max_files and files_analyzed >= self.max_files:
                        logger.info(f"Reached max_files limit: {self.max_files}")
                        stats.files_analyzed = files_analyzed
                        return stats

                    # Check if sensitive
                    if self.skip_sensitive and self.sensitive_detector.is_sensitive(file_path):
                        self._sensitive_files.append(str(file_path.relative_to(self.project_root)))
                        stats.total_files += 1
                        continue

                    # Count file
                    stats.total_files += 1
                    files_analyzed += 1

                    # Get file info
                    try:
                        stat = file_path.stat()
                        stats.total_size_bytes += stat.st_size

                        # Count by extension
                        ext = file_path.suffix.lower() or ".no_extension"
                        stats.files_by_extension[ext] = stats.files_by_extension.get(ext, 0) + 1

                        # Count lines (for text files)
                        if ext in {
                            ".py",
                            ".js",
                            ".ts",
                            ".jsx",
                            ".tsx",
                            ".java",
                            ".go",
                            ".rs",
                            ".rb",
                            ".php",
                            ".c",
                            ".cpp",
                            ".h",
                            ".md",
                            ".txt",
                            ".yml",
                            ".yaml",
                            ".json",
                            ".xml",
                        }:
                            try:
                                content = file_path.read_text(errors="ignore")
                                stats.total_lines += len(content.splitlines())
                            except (OSError, UnicodeDecodeError):
                                pass

                    except (OSError, PermissionError) as e:
                        logger.debug(f"Error reading {file_path}: {e}")
                        self._warnings.append(f"Could not read: {file_path.name}")

        except SecurityError as e:
            logger.error(f"Security error during analysis: {e}")
            raise

        # Detect tests
        stats.has_tests = self._has_tests(stats)

        # Detect git repo
        stats.is_git_repo = (self.project_root / ".git").exists()

        stats.files_analyzed = files_analyzed

        return stats

    def _has_tests(self, stats: ProjectStats) -> bool:
        """Check if project has tests"""
        # Check for test directories or files
        test_indicators = [
            self.project_root / "tests",
            self.project_root / "test",
            self.project_root / "__tests__",
        ]

        for indicator in test_indicators:
            if indicator.exists():
                return True

        # Check for test files in stats
        for ext, count in stats.files_by_extension.items():
            if "test" in ext.lower():
                return True

        return False

    def _detect_technology_stack(self, stats: ProjectStats) -> TechnologyStack:
        """Detect technology stack from project"""
        # Detect languages
        languages = self.tech_detector.detect_languages(stats.files_by_extension)

        # Detect primary language
        primary = self.tech_detector.detect_primary_language(stats.files_by_extension, languages)

        # Detect frameworks
        frameworks = self.tech_detector.detect_frameworks(self.project_root, languages)

        # Detect databases
        databases = self.tech_detector.detect_databases(self.project_root, languages)

        # Detect infrastructure
        infrastructure = self.tech_detector.detect_infrastructure(self.project_root)

        return TechnologyStack(
            languages=languages,
            primary_language=primary,
            frameworks=frameworks,
            databases=databases,
            infrastructure=infrastructure,
        )

    def _recommend_agents(self, stats: ProjectStats, tech_stack: TechnologyStack) -> List[Dict]:
        """Generate agent recommendations"""
        recommendations = []

        # Always recommend code-reviewer (universal agent)
        recommendations.append(
            {
                "agent": "code-reviewer",
                "confidence": 0.99,
                "reason": "Essential for all projects - reviews code quality, security, and best practices",
                "skills_required": ["code-review"],
            }
        )

        # Language-based recommendations
        if "Python" in tech_stack.languages:
            # Calculate confidence based on Python file count
            py_files = stats.files_by_extension.get(".py", 0)
            confidence = min(0.9, 0.5 + (py_files / max(stats.total_files, 1)) * 0.5)

            recommendations.append(
                {
                    "agent": "python-expert",
                    "confidence": confidence,
                    "reason": f"Python project detected ({py_files} .py files)",
                    "skills_required": ["python", "testing"],
                }
            )

        if "JavaScript" in tech_stack.languages or "TypeScript" in tech_stack.languages:
            js_files = stats.files_by_extension.get(".js", 0) + stats.files_by_extension.get(
                ".jsx", 0
            )
            ts_files = stats.files_by_extension.get(".ts", 0) + stats.files_by_extension.get(
                ".tsx", 0
            )
            total_js = js_files + ts_files

            confidence = min(0.9, 0.5 + (total_js / max(stats.total_files, 1)) * 0.5)

            recommendations.append(
                {
                    "agent": "frontend-developer",
                    "confidence": confidence,
                    "reason": f"JavaScript/TypeScript project detected ({total_js} files)",
                    "skills_required": ["javascript", "react"],
                }
            )

        # Framework-based recommendations
        if "React" in tech_stack.frameworks:
            recommendations.append(
                {
                    "agent": "ui-components-expert",
                    "confidence": 0.85,
                    "reason": "React framework detected - component design expertise needed",
                    "skills_required": ["react", "component-design"],
                }
            )

        if "FastAPI" in tech_stack.frameworks or "Django" in tech_stack.frameworks:
            recommendations.append(
                {
                    "agent": "backend-architect",
                    "confidence": 0.85,
                    "reason": f"Backend framework detected: {', '.join(tech_stack.frameworks)}",
                    "skills_required": ["api-design", "backend"],
                }
            )

        # Database recommendations
        if tech_stack.databases:
            recommendations.append(
                {
                    "agent": "database-architect",
                    "confidence": 0.80,
                    "reason": f"Databases detected: {', '.join(tech_stack.databases)}",
                    "skills_required": ["database", "sql"],
                }
            )

        # Infrastructure recommendations
        if "Docker" in tech_stack.infrastructure:
            recommendations.append(
                {
                    "agent": "devops-architect",
                    "confidence": 0.75,
                    "reason": "Docker infrastructure detected",
                    "skills_required": ["docker", "devops"],
                }
            )

        # Testing recommendation
        if stats.has_tests:
            recommendations.append(
                {
                    "agent": "qc-automation-expert",
                    "confidence": 0.70,
                    "reason": "Test infrastructure detected",
                    "skills_required": ["testing", "qa"],
                }
            )

        # Sort by confidence (descending)
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        # Limit to max_recommendations
        return recommendations[: self.max_recommendations]
