"""
.claude Folder Validator

Validates .claude folder structure and configuration for claude-force compatibility.
Part of the existing project support feature.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional
import json


@dataclass
class ValidationIssue:
    """Represents a validation issue found in .claude folder"""
    severity: str  # "error", "warning", "info"
    category: str  # "missing_file", "missing_directory", "invalid_config", etc.
    message: str
    path: Optional[Path] = None
    fix_available: bool = False
    fix_description: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of .claude folder validation"""
    is_valid: bool
    project_path: Path
    claude_path: Path
    issues: List[ValidationIssue] = field(default_factory=list)

    def errors(self) -> List[ValidationIssue]:
        """Get all error-level issues"""
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[ValidationIssue]:
        """Get all warning-level issues"""
        return [i for i in self.issues if i.severity == "warning"]

    def info(self) -> List[ValidationIssue]:
        """Get all info-level issues"""
        return [i for i in self.issues if i.severity == "info"]

    def fixable_issues(self) -> List[ValidationIssue]:
        """Get all issues that can be auto-fixed"""
        return [i for i in self.issues if i.fix_available]


class ClaudeValidator:
    """
    Validates .claude folder structure and configuration.

    Checks for:
    - Required files and directories
    - Valid claude.json configuration
    - Proper file references
    - Governance hooks setup
    """

    # Required files in .claude folder
    REQUIRED_FILES = [
        "README.md",
        "claude.json",
        "task.md",
        "scorecard.md",
    ]

    # Required directories in .claude folder
    REQUIRED_DIRECTORIES = [
        "agents",
        "contracts",
        "hooks",
        "macros",
        "tasks",
    ]

    # Optional files (warnings if missing)
    OPTIONAL_FILES = [
        "work.md",
        "commands.md",
        "workflows.md",
    ]

    # Optional directories
    OPTIONAL_DIRECTORIES = [
        "skills",
        "commands",
        "examples",
    ]

    # Required fields in claude.json
    REQUIRED_JSON_FIELDS = [
        "version",
        "name",
        "agents",
        "workflows",
        "governance",
        "paths",
        "rules",
    ]

    def __init__(self, project_path: Path):
        """
        Initialize validator for a project.

        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.claude_path = self.project_path / ".claude"

    def validate(self) -> ValidationResult:
        """
        Validate .claude folder structure.

        Returns:
            ValidationResult with all issues found
        """
        issues: List[ValidationIssue] = []

        # Check if .claude folder exists
        if not self.claude_path.exists():
            issues.append(ValidationIssue(
                severity="error",
                category="missing_directory",
                message=".claude folder does not exist",
                path=self.claude_path,
                fix_available=True,
                fix_description="Create .claude folder with default structure"
            ))
            # If .claude doesn't exist, no point checking further
            return ValidationResult(
                is_valid=False,
                project_path=self.project_path,
                claude_path=self.claude_path,
                issues=issues
            )

        # Check required files
        issues.extend(self._check_required_files())

        # Check required directories
        issues.extend(self._check_required_directories())

        # Check optional files (warnings)
        issues.extend(self._check_optional_files())

        # Validate claude.json if it exists
        claude_json_path = self.claude_path / "claude.json"
        if claude_json_path.exists():
            issues.extend(self._validate_claude_json(claude_json_path))

        # Determine if valid (no errors)
        has_errors = any(i.severity == "error" for i in issues)

        return ValidationResult(
            is_valid=not has_errors,
            project_path=self.project_path,
            claude_path=self.claude_path,
            issues=issues
        )

    def _check_required_files(self) -> List[ValidationIssue]:
        """Check for required files"""
        issues = []
        for filename in self.REQUIRED_FILES:
            filepath = self.claude_path / filename
            if not filepath.exists():
                issues.append(ValidationIssue(
                    severity="error",
                    category="missing_file",
                    message=f"Required file missing: {filename}",
                    path=filepath,
                    fix_available=True,
                    fix_description=f"Create {filename} with default template"
                ))
        return issues

    def _check_required_directories(self) -> List[ValidationIssue]:
        """Check for required directories"""
        issues = []
        for dirname in self.REQUIRED_DIRECTORIES:
            dirpath = self.claude_path / dirname
            if not dirpath.exists():
                issues.append(ValidationIssue(
                    severity="error",
                    category="missing_directory",
                    message=f"Required directory missing: {dirname}/",
                    path=dirpath,
                    fix_available=True,
                    fix_description=f"Create {dirname}/ directory"
                ))
        return issues

    def _check_optional_files(self) -> List[ValidationIssue]:
        """Check for optional files (warnings if missing)"""
        issues = []
        for filename in self.OPTIONAL_FILES:
            filepath = self.claude_path / filename
            if not filepath.exists():
                issues.append(ValidationIssue(
                    severity="warning",
                    category="missing_file",
                    message=f"Optional file missing: {filename}",
                    path=filepath,
                    fix_available=True,
                    fix_description=f"Create {filename} with default template"
                ))
        return issues

    def _validate_claude_json(self, json_path: Path) -> List[ValidationIssue]:
        """Validate claude.json structure"""
        issues = []

        try:
            with open(json_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                severity="error",
                category="invalid_config",
                message=f"claude.json is not valid JSON: {e}",
                path=json_path,
                fix_available=False
            ))
            return issues
        except Exception as e:
            issues.append(ValidationIssue(
                severity="error",
                category="invalid_config",
                message=f"Cannot read claude.json: {e}",
                path=json_path,
                fix_available=False
            ))
            return issues

        # Check required fields
        for field in self.REQUIRED_JSON_FIELDS:
            if field not in config:
                issues.append(ValidationIssue(
                    severity="error",
                    category="invalid_config",
                    message=f"claude.json missing required field: {field}",
                    path=json_path,
                    fix_available=True,
                    fix_description=f"Add '{field}' field to claude.json"
                ))

        # Validate agent file references
        if "agents" in config and isinstance(config["agents"], dict):
            for agent_name, agent_config in config["agents"].items():
                if "file" in agent_config:
                    agent_file = self.claude_path / agent_config["file"]
                    if not agent_file.exists():
                        issues.append(ValidationIssue(
                            severity="warning",
                            category="missing_file",
                            message=f"Agent file not found: {agent_config['file']} (referenced by '{agent_name}')",
                            path=agent_file,
                            fix_available=False
                        ))

                if "contract" in agent_config:
                    contract_file = self.claude_path / agent_config["contract"]
                    if not contract_file.exists():
                        issues.append(ValidationIssue(
                            severity="warning",
                            category="missing_file",
                            message=f"Contract file not found: {agent_config['contract']} (referenced by '{agent_name}')",
                            path=contract_file,
                            fix_available=False
                        ))

        return issues
