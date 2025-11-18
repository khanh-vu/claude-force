"""
Technology Stack Detectors

Following TDD: Minimal implementation to pass technology detection tests.
"""

from pathlib import Path
from typing import List, Dict, Set
import logging


logger = logging.getLogger(__name__)


class TechnologyDetector:
    """Detects technologies used in a project"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.files_by_extension: Dict[str, int] = {}
        self.file_contents_cache: Dict[str, str] = {}

    def detect_languages(self, files_by_ext: Dict[str, int]) -> List[str]:
        """
        Detect programming languages based on file extensions.

        Args:
            files_by_ext: Dictionary mapping extensions to file counts

        Returns:
            List of detected language names
        """
        languages = []

        # Language detection rules
        language_extensions = {
            "Python": {".py"},
            "JavaScript": {".js", ".jsx", ".mjs"},
            "TypeScript": {".ts", ".tsx"},
            "Java": {".java"},
            "Go": {".go"},
            "Rust": {".rs"},
            "C++": {".cpp", ".cc", ".cxx", ".hpp", ".h"},
            "C": {".c", ".h"},
            "Ruby": {".rb"},
            "PHP": {".php"},
            "Swift": {".swift"},
            "Kotlin": {".kt", ".kts"},
        }

        for lang, extensions in language_extensions.items():
            if any(ext in files_by_ext for ext in extensions):
                languages.append(lang)

        return languages

    def detect_primary_language(self, files_by_ext: Dict[str, int], languages: List[str]) -> str:
        """
        Determine the primary language based on file counts.

        Args:
            files_by_ext: Dictionary mapping extensions to file counts
            languages: List of detected languages

        Returns:
            Primary language name or None
        """
        if not languages:
            return None

        # Extension to language mapping
        ext_to_lang = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
        }

        # Count files per language
        lang_counts = {}
        for ext, count in files_by_ext.items():
            if ext in ext_to_lang:
                lang = ext_to_lang[ext]
                lang_counts[lang] = lang_counts.get(lang, 0) + count

        # Return language with most files
        if lang_counts:
            return max(lang_counts.items(), key=lambda x: x[1])[0]

        return languages[0] if languages else None

    def detect_frameworks(self, project_root: Path, languages: List[str]) -> List[str]:
        """
        Detect frameworks based on project files and dependencies.

        Args:
            project_root: Project root directory
            languages: Detected languages

        Returns:
            List of detected framework names
        """
        frameworks = []

        # Check package.json for JavaScript/TypeScript frameworks
        if "JavaScript" in languages or "TypeScript" in languages:
            package_json = project_root / "package.json"
            if package_json.exists():
                try:
                    import json

                    content = package_json.read_text()
                    data = json.loads(content)

                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    if "react" in deps:
                        frameworks.append("React")
                    if "vue" in deps:
                        frameworks.append("Vue.js")
                    if "@angular/core" in deps:
                        frameworks.append("Angular")
                    if "next" in deps:
                        frameworks.append("Next.js")
                    if "express" in deps:
                        frameworks.append("Express")
                    if "nestjs" in deps or "@nestjs/core" in deps:
                        frameworks.append("NestJS")

                except (json.JSONDecodeError, OSError) as e:
                    logger.debug(f"Error reading package.json: {e}")

        # Check requirements.txt for Python frameworks
        if "Python" in languages:
            requirements_files = [
                project_root / "requirements.txt",
                project_root / "requirements" / "base.txt",
                project_root / "setup.py",
            ]

            for req_file in requirements_files:
                if req_file.exists():
                    try:
                        content = req_file.read_text().lower()

                        if "fastapi" in content:
                            frameworks.append("FastAPI")
                        if "django" in content:
                            frameworks.append("Django")
                        if "flask" in content:
                            frameworks.append("Flask")
                        if "tornado" in content:
                            frameworks.append("Tornado")
                        if "aiohttp" in content:
                            frameworks.append("aiohttp")

                    except OSError as e:
                        logger.debug(f"Error reading {req_file}: {e}")

        return list(set(frameworks))  # Remove duplicates

    def detect_databases(self, project_root: Path, languages: List[str]) -> List[str]:
        """
        Detect databases based on dependencies.

        Args:
            project_root: Project root directory
            languages: Detected languages

        Returns:
            List of detected database names
        """
        databases = []

        # Check Python requirements
        # Also check if requirements.txt exists (indicates Python project)
        requirements_files = [
            project_root / "requirements.txt",
            project_root / "setup.py",
        ]
        has_python_deps = any(f.exists() for f in requirements_files)

        if "Python" in languages or has_python_deps:
            for req_file in requirements_files:
                if req_file.exists():
                    try:
                        content = req_file.read_text().lower()

                        if "psycopg2" in content or "asyncpg" in content:
                            databases.append("PostgreSQL")
                        if "pymysql" in content or "mysqlclient" in content:
                            databases.append("MySQL")
                        if "pymongo" in content:
                            databases.append("MongoDB")
                        if "redis" in content:
                            databases.append("Redis")
                        if "sqlite" in content:
                            databases.append("SQLite")

                    except OSError:
                        pass

        # Check JavaScript/TypeScript packages
        if "JavaScript" in languages or "TypeScript" in languages:
            package_json = project_root / "package.json"
            if package_json.exists():
                try:
                    import json

                    content = package_json.read_text()
                    data = json.loads(content)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    if "pg" in deps or "postgres" in deps:
                        databases.append("PostgreSQL")
                    if "mysql" in deps or "mysql2" in deps:
                        databases.append("MySQL")
                    if "mongodb" in deps or "mongoose" in deps:
                        databases.append("MongoDB")
                    if "redis" in deps or "ioredis" in deps:
                        databases.append("Redis")

                except (json.JSONDecodeError, OSError):
                    pass

        return list(set(databases))

    def detect_infrastructure(self, project_root: Path) -> List[str]:
        """
        Detect infrastructure tools.

        Args:
            project_root: Project root directory

        Returns:
            List of detected infrastructure tool names
        """
        infrastructure = []

        # Check for Docker
        if (project_root / "Dockerfile").exists():
            infrastructure.append("Docker")
        if (project_root / "docker-compose.yml").exists():
            infrastructure.append("Docker Compose")

        # Check for Kubernetes
        k8s_dir = project_root / "k8s"
        if k8s_dir.exists() and k8s_dir.is_dir():
            infrastructure.append("Kubernetes")

        # Check for Terraform
        if any(project_root.glob("*.tf")):
            infrastructure.append("Terraform")

        # Check for AWS
        if (project_root / "serverless.yml").exists():
            infrastructure.append("AWS (Serverless)")

        # Check for CI/CD
        if (project_root / ".github" / "workflows").exists():
            infrastructure.append("GitHub Actions")
        if (project_root / ".gitlab-ci.yml").exists():
            infrastructure.append("GitLab CI")
        if (project_root / "Jenkinsfile").exists():
            infrastructure.append("Jenkins")

        return infrastructure
