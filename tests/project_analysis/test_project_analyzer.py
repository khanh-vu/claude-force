"""
Tests for ProjectAnalyzer (TDD)

Following Test-Driven Development:
1. Write tests first (RED)
2. Implement to pass (GREEN)
3. Refactor (REFACTOR)
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

# These imports will fail initially - that's expected in TDD!
from claude_force.project_analysis import (
    ProjectAnalyzer,
    AnalysisResult,
    ProjectStats,
    TechnologyStack,
)


class TestProjectAnalyzerInitialization:
    """Test ProjectAnalyzer initialization (TDD Step 1)"""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "src").mkdir()
            (project / "src" / "main.py").write_text("print('hello')")
            yield project

    def test_analyzer_accepts_valid_project_path(self, temp_project):
        """RED: Should initialize with valid project path"""
        analyzer = ProjectAnalyzer(temp_project)
        assert analyzer.project_root == temp_project

    def test_analyzer_rejects_nonexistent_path(self):
        """RED: Should reject nonexistent project path"""
        with pytest.raises(ValueError, match="does not exist"):
            ProjectAnalyzer("/nonexistent/path")

    def test_analyzer_rejects_file_as_project(self, temp_project):
        """RED: Should reject file instead of directory"""
        file_path = temp_project / "src" / "main.py"
        with pytest.raises(ValueError, match="not a directory"):
            ProjectAnalyzer(file_path)

    def test_analyzer_rejects_system_directory(self):
        """RED: Should reject system directories"""
        if Path("/etc").exists():
            with pytest.raises(ValueError, match="system directory"):
                ProjectAnalyzer("/etc")

    def test_analyzer_stores_configuration(self, temp_project):
        """RED: Should store analysis configuration"""
        analyzer = ProjectAnalyzer(
            temp_project,
            skip_sensitive=True,
            max_depth=3,
            max_files=5000
        )

        assert analyzer.skip_sensitive is True
        assert analyzer.max_depth == 3
        assert analyzer.max_files == 5000


class TestProjectStatsCollection:
    """Test project statistics collection (TDD Step 2)"""

    @pytest.fixture
    def python_project(self):
        """Create a Python project for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create Python files
            (project / "src").mkdir()
            (project / "src" / "__init__.py").write_text("")
            (project / "src" / "main.py").write_text("print('hello')\n" * 10)
            (project / "src" / "utils.py").write_text("def util(): pass\n" * 5)

            # Create test files
            (project / "tests").mkdir()
            (project / "tests" / "test_main.py").write_text("def test(): pass\n" * 3)

            # Create config files
            (project / "setup.py").write_text("from setuptools import setup\nsetup()")
            (project / "README.md").write_text("# Project\n")
            (project / ".gitignore").write_text("*.pyc\n")

            yield project

    def test_counts_total_files(self, python_project):
        """RED: Should count total files in project"""
        analyzer = ProjectAnalyzer(python_project)
        result = analyzer.analyze()

        assert result.stats.total_files == 7

    def test_calculates_total_size(self, python_project):
        """RED: Should calculate total project size in bytes"""
        analyzer = ProjectAnalyzer(python_project)
        result = analyzer.analyze()

        assert result.stats.total_size_bytes > 0

    def test_counts_lines_of_code(self, python_project):
        """RED: Should count total lines of code"""
        analyzer = ProjectAnalyzer(python_project)
        result = analyzer.analyze()

        # 10 + 5 + 3 + setup.py lines + README line
        assert result.stats.total_lines > 18

    def test_groups_files_by_extension(self, python_project):
        """RED: Should group files by extension"""
        analyzer = ProjectAnalyzer(python_project)
        result = analyzer.analyze()

        assert ".py" in result.stats.files_by_extension
        assert result.stats.files_by_extension[".py"] == 5  # 4 .py + setup.py
        assert ".md" in result.stats.files_by_extension
        assert result.stats.files_by_extension[".md"] == 1

    def test_detects_has_tests(self, python_project):
        """RED: Should detect if project has tests"""
        analyzer = ProjectAnalyzer(python_project)
        result = analyzer.analyze()

        assert result.stats.has_tests is True

    def test_detects_git_repository(self):
        """RED: Should detect if project is a git repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".git").mkdir()
            (project / "file.txt").write_text("test")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert result.stats.is_git_repo is True


class TestTechnologyStackDetection:
    """Test technology stack detection (TDD Step 3)"""

    def test_detects_python_project(self):
        """RED: Should detect Python as primary language"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "main.py").write_text("print('hello')")
            (project / "requirements.txt").write_text("requests\n")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert "Python" in result.tech_stack.languages
            assert result.tech_stack.primary_language == "Python"

    def test_detects_javascript_project(self):
        """RED: Should detect JavaScript project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "index.js").write_text("console.log('hello');")
            (project / "package.json").write_text('{"name": "test"}')

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert "JavaScript" in result.tech_stack.languages

    def test_detects_typescript_project(self):
        """RED: Should detect TypeScript project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "index.ts").write_text("const x: string = 'hello';")
            (project / "tsconfig.json").write_text('{"compilerOptions": {}}')

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert "TypeScript" in result.tech_stack.languages

    def test_detects_react_framework(self):
        """RED: Should detect React framework"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "package.json").write_text('{"dependencies": {"react": "18.0.0"}}')
            (project / "src").mkdir()
            (project / "src" / "App.jsx").write_text("import React from 'react';")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert "React" in result.tech_stack.frameworks

    def test_detects_fastapi_framework(self):
        """RED: Should detect FastAPI framework"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "requirements.txt").write_text("fastapi\nuvicorn\n")
            (project / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert "FastAPI" in result.tech_stack.frameworks

    def test_detects_postgresql_database(self):
        """RED: Should detect PostgreSQL usage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "requirements.txt").write_text("psycopg2\n")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert "PostgreSQL" in result.tech_stack.databases

    def test_detects_docker_infrastructure(self):
        """RED: Should detect Docker usage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "Dockerfile").write_text("FROM python:3.11\n")
            (project / "docker-compose.yml").write_text("version: '3'\n")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert "Docker" in result.tech_stack.infrastructure


class TestSensitiveFileHandling:
    """Test sensitive file handling integration (TDD Step 4)"""

    def test_skips_sensitive_files_by_default(self):
        """RED: Should skip sensitive files during analysis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "main.py").write_text("print('hello')")
            (project / ".env").write_text("API_KEY=secret123")
            (project / "credentials.json").write_text('{"key": "secret"}')

            analyzer = ProjectAnalyzer(project, skip_sensitive=True)
            result = analyzer.analyze()

            # Should count total files including sensitive
            assert result.stats.total_files == 3

            # But sensitive files should be tracked separately
            assert len(result.sensitive_files_skipped) == 2
            assert any(".env" in f for f in result.sensitive_files_skipped)

    def test_includes_sensitive_files_when_configured(self):
        """RED: Should include sensitive files if skip_sensitive=False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".env").write_text("API_KEY=secret123")

            analyzer = ProjectAnalyzer(project, skip_sensitive=False)
            result = analyzer.analyze()

            assert len(result.sensitive_files_skipped) == 0


class TestAgentRecommendations:
    """Test agent recommendation engine (TDD Step 5)"""

    def test_recommends_python_expert_for_python_project(self):
        """RED: Should recommend python-expert for Python projects"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "main.py").write_text("print('hello')\n" * 100)

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            agent_names = [rec["agent"] for rec in result.recommended_agents]
            assert "python-expert" in agent_names

    def test_recommends_frontend_developer_for_react_project(self):
        """RED: Should recommend frontend-developer for React projects"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "package.json").write_text('{"dependencies": {"react": "18.0.0"}}')
            (project / "src").mkdir()
            (project / "src" / "App.tsx").write_text("export const App = () => <div />;")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            agent_names = [rec["agent"] for rec in result.recommended_agents]
            assert "frontend-developer" in agent_names

    def test_recommends_database_architect_for_db_project(self):
        """RED: Should recommend database-architect when DB detected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "requirements.txt").write_text("psycopg2\nsqlalchemy\n")
            (project / "models.py").write_text("from sqlalchemy import Column\n")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            agent_names = [rec["agent"] for rec in result.recommended_agents]
            assert "database-architect" in agent_names

    def test_includes_confidence_scores_in_recommendations(self):
        """RED: Should include confidence scores for each recommendation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "main.py").write_text("print('hello')\n" * 100)

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert len(result.recommended_agents) > 0
            for rec in result.recommended_agents:
                assert "agent" in rec
                assert "confidence" in rec
                assert 0.0 <= rec["confidence"] <= 1.0
                assert "reason" in rec

    def test_always_recommends_code_reviewer(self):
        """RED: Should always recommend code-reviewer (universal agent)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "file.txt").write_text("random content")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            agent_names = [rec["agent"] for rec in result.recommended_agents]
            assert "code-reviewer" in agent_names

    def test_limits_recommendations_to_top_n(self):
        """RED: Should limit recommendations to top N agents"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            # Create a complex project that would match many agents
            (project / "main.py").write_text("print('hello')")
            (project / "index.ts").write_text("const x: string = 'hello';")
            (project / "Dockerfile").write_text("FROM python:3.11")

            analyzer = ProjectAnalyzer(project, max_recommendations=3)
            result = analyzer.analyze()

            assert len(result.recommended_agents) <= 3


class TestAnalysisResult:
    """Test AnalysisResult data structure (TDD Step 6)"""

    def test_result_contains_required_fields(self):
        """RED: Should contain all required fields"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "file.txt").write_text("test")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            assert hasattr(result, "timestamp")
            assert hasattr(result, "project_path")
            assert hasattr(result, "stats")
            assert hasattr(result, "tech_stack")
            assert hasattr(result, "recommended_agents")
            assert hasattr(result, "sensitive_files_skipped")

    def test_result_timestamp_is_recent(self):
        """RED: Should have recent timestamp"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "file.txt").write_text("test")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            time_diff = datetime.now() - result.timestamp
            assert time_diff.total_seconds() < 5  # Within 5 seconds

    def test_result_converts_to_dict(self):
        """RED: Should convert to dictionary for JSON export"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "main.py").write_text("print('hello')")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            result_dict = result.to_dict()

            assert isinstance(result_dict, dict)
            assert "timestamp" in result_dict
            assert "project_path" in result_dict
            assert "stats" in result_dict
            assert "tech_stack" in result_dict
            assert "recommended_agents" in result_dict

    def test_result_converts_to_markdown(self):
        """RED: Should convert to markdown report"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "main.py").write_text("print('hello')")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            markdown = result.to_markdown()

            assert isinstance(markdown, str)
            assert "# Project Analysis Report" in markdown
            assert "Python" in markdown


class TestPerformance:
    """Test performance characteristics (TDD Step 7)"""

    def test_respects_max_files_limit(self):
        """RED: Should stop after max_files limit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create 100 files
            for i in range(100):
                (project / f"file_{i}.py").write_text(f"# File {i}")

            analyzer = ProjectAnalyzer(project, max_files=50)
            result = analyzer.analyze()

            # Should not analyze more than max_files
            assert result.stats.files_analyzed <= 50

    def test_respects_max_depth_limit(self):
        """RED: Should respect max directory depth"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create deep nested structure
            deep = project
            for i in range(10):
                deep = deep / f"level_{i}"
                deep.mkdir(parents=True, exist_ok=True)
                (deep / "file.py").write_text("test")

            analyzer = ProjectAnalyzer(project, max_depth=3)
            result = analyzer.analyze()

            # Should not go deeper than max_depth
            # Exact file count depends on depth limit
            assert result.stats.total_files < 10


class TestErrorHandling:
    """Test error handling (TDD Step 8)"""

    def test_handles_permission_denied_gracefully(self):
        """RED: Should handle permission denied errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "file.txt").write_text("test")

            restricted = project / "restricted"
            restricted.mkdir()
            (restricted / "secret.txt").write_text("secret")

            # Remove permissions
            original_mode = restricted.stat().st_mode
            try:
                restricted.chmod(0o000)

                analyzer = ProjectAnalyzer(project)
                result = analyzer.analyze()

                # Should complete without raising exception
                assert result is not None

            finally:
                restricted.chmod(original_mode)

    def test_handles_broken_symlinks_gracefully(self):
        """RED: Should handle broken symlinks"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "file.txt").write_text("test")

            try:
                # Create broken symlink
                broken = project / "broken_link"
                broken.symlink_to("/nonexistent/target")

                analyzer = ProjectAnalyzer(project)
                result = analyzer.analyze()

                # Should complete without crashing
                assert result is not None

            except OSError:
                # Skip if symlinks not supported
                pytest.skip("Symlinks not supported")

    def test_handles_unicode_errors_gracefully(self):
        """RED: Should handle unicode encoding errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create file with problematic name
            (project / "file_测试.py").write_text("print('hello')")

            analyzer = ProjectAnalyzer(project)
            result = analyzer.analyze()

            # Should complete successfully
            assert result.stats.total_files >= 1
