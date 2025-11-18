"""
Restructure Command

Fixes and updates existing .claude folders for claude-force compatibility.
Minimal implementation following TDD.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable

from claude_force.project_analysis.claude_validator import (
    ClaudeValidator,
    ValidationResult,
    ValidationIssue,
)
from claude_force.security import validate_project_root
from claude_force.commands.templates import (
    README_TEMPLATE,
    TASK_TEMPLATE,
    SCORECARD_TEMPLATE,
    WORK_TEMPLATE,
    COMMANDS_TEMPLATE,
    WORKFLOWS_TEMPLATE,
    get_claude_json_template,
)

logger = logging.getLogger(__name__)


class RestructureCommand:
    """
    /restructure command implementation

    Validates and fixes .claude folder structure.
    """

    # Configuration constants
    MAX_RESTRUCTURE_ITERATIONS = 5  # Maximum iterative fix attempts
    DEFAULT_TIMEOUT = 300.0  # Default timeout in seconds (5 minutes)

    def __init__(self, project_path: Path):
        """
        Initialize restructure command.

        Args:
            project_path: Path to project to restructure

        Raises:
            ValueError: If project_path is invalid
        """
        # Validate project path (raises ValueError if invalid)
        self.project_path = validate_project_root(project_path)
        self.validator = ClaudeValidator(self.project_path)

        # Track changes for rollback capability
        self.changes_made = []

    def validate(self) -> ValidationResult:
        """
        Validate .claude folder structure.

        Returns:
            ValidationResult with all issues found
        """
        return self.validator.validate()

    def generate_fix_plan(self, validation: ValidationResult) -> List[Dict]:
        """
        Generate a plan to fix validation issues.

        Args:
            validation: ValidationResult from validate()

        Returns:
            List of fixes to apply
        """
        fix_plan = []

        # Get all fixable issues
        fixable = validation.fixable_issues()

        for issue in fixable:
            fix = {
                "action": self._determine_action(issue),
                "description": issue.fix_description or issue.message,
                "path": str(issue.path) if issue.path else None,
                "category": issue.category,
                "severity": issue.severity,
            }
            fix_plan.append(fix)

        return fix_plan

    def _determine_action(self, issue: ValidationIssue) -> str:
        """Determine the action needed to fix an issue"""
        if issue.category == "missing_directory":
            if ".claude folder" in issue.message:
                return "create_claude_folder"
            return "create_directory"
        elif issue.category == "missing_file":
            return "create_file"
        elif issue.category == "invalid_config":
            return "fix_config"
        else:
            return "unknown"

    def apply_fixes(
        self,
        fix_plan: List[Dict],
        auto_approve: bool = False,
        approval_callback: Optional[Callable[[Dict], bool]] = None,
    ) -> Dict:
        """
        Apply fixes from the fix plan.

        Args:
            fix_plan: List of fixes to apply
            auto_approve: If True, apply all fixes without asking
            approval_callback: Function to call for approval (returns bool)

        Returns:
            Dictionary with applied and skipped counts
        """
        applied = 0
        skipped = 0

        for fix in fix_plan:
            # Check if should apply this fix
            should_apply = auto_approve

            if not auto_approve and approval_callback:
                should_apply = approval_callback(fix)

            if should_apply:
                self._apply_fix(fix)
                applied += 1
            else:
                skipped += 1

        return {
            "applied": applied,
            "skipped": skipped,
        }

    def _apply_fix(self, fix: Dict):
        """Apply a single fix and track changes for rollback"""
        action = fix["action"]
        path = Path(fix["path"]) if fix["path"] else None

        if action == "create_claude_folder":
            claude_path = self.project_path / ".claude"
            existed_before = claude_path.exists()
            self._create_claude_folder()

            # Track for rollback
            if not existed_before:
                self.changes_made.append(
                    {"action": "created_directory", "path": claude_path, "existed_before": False}
                )

        elif action == "create_directory":
            if path:
                existed_before = path.exists()
                path.mkdir(parents=True, exist_ok=True)

                # Track for rollback
                if not existed_before:
                    self.changes_made.append(
                        {"action": "created_directory", "path": path, "existed_before": False}
                    )

        elif action == "create_file":
            if path:
                existed_before = path.exists()
                original_content = path.read_text() if existed_before else None

                self._create_file_with_template(path)

                # Track for rollback
                self.changes_made.append(
                    {
                        "action": "created_file",
                        "path": path,
                        "existed_before": existed_before,
                        "original_content": original_content,
                    }
                )

        elif action == "fix_config":
            # For now, just create minimal config if missing
            if path and path.name == "claude.json":
                existed_before = path.exists()
                original_content = path.read_text() if existed_before else None

                self._create_minimal_claude_json(path)

                # Track for rollback
                self.changes_made.append(
                    {
                        "action": "created_file",
                        "path": path,
                        "existed_before": existed_before,
                        "original_content": original_content,
                    }
                )

    def _rollback_changes(self):
        """
        Rollback all changes made during execute.

        Undoes changes in reverse order (LIFO).
        """
        import shutil

        for change in reversed(self.changes_made):
            try:
                action = change["action"]
                path = change["path"]

                if action == "created_file":
                    if change["existed_before"]:
                        # Restore original content
                        if change["original_content"] is not None:
                            path.write_text(change["original_content"])
                    else:
                        # Delete created file
                        if path.exists():
                            path.unlink()

                elif action == "created_directory":
                    if not change["existed_before"]:
                        # Remove created directory if empty
                        if path.exists() and not any(path.iterdir()):
                            path.rmdir()

            except Exception as e:
                # Log rollback errors but continue rolling back
                # (Don't want rollback itself to fail)
                pass

        # Clear changes after rollback
        self.changes_made = []

    def _create_claude_folder(self):
        """Create .claude folder with basic structure"""
        claude_path = self.project_path / ".claude"
        claude_path.mkdir(exist_ok=True)

    def _create_backup(self, filepath: Path) -> None:
        """
        Create backup of existing file before overwriting.

        Args:
            filepath: Path to file to backup
        """
        import shutil

        if filepath.exists():
            backup_path = filepath.with_suffix(filepath.suffix + ".bak")
            # Use shutil.copy2 to preserve metadata (permissions, timestamps)
            shutil.copy2(filepath, backup_path)

    def _create_file_with_template(self, filepath: Path):
        """Create a file with appropriate template"""
        filename = filepath.name

        if filename == "README.md":
            content = README_TEMPLATE
        elif filename == "claude.json":
            content = get_claude_json_template()
        elif filename == "task.md":
            content = TASK_TEMPLATE
        elif filename == "scorecard.md":
            content = SCORECARD_TEMPLATE
        elif filename == "work.md":
            content = WORK_TEMPLATE
        elif filename == "commands.md":
            content = COMMANDS_TEMPLATE
        elif filename == "workflows.md":
            content = WORKFLOWS_TEMPLATE
        else:
            content = f"# {filename}\n\nCreated by /restructure command\n"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Create backup before overwriting
        self._create_backup(filepath)

        filepath.write_text(content)

    def _create_minimal_claude_json(self, filepath: Path):
        """Create minimal valid claude.json"""
        content = get_claude_json_template()
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Create backup before overwriting
        self._create_backup(filepath)

        filepath.write_text(content)

    def execute(
        self,
        auto_approve: bool = False,
        show_progress: bool = True,
        timeout: Optional[float] = None,
    ) -> Dict:
        """
        Execute the full restructure workflow with error handling and rollback.

        Args:
            auto_approve: If True, apply all fixes without asking
            show_progress: Whether to show progress messages (default: True)
            timeout: Maximum execution time in seconds (None = no timeout)

        Returns:
            Dictionary with execution results

        Raises:
            ValueError: If operation fails with user-friendly error message
            TimeoutError: If operation exceeds timeout (best effort)

        Note:
            Timeout is "best effort" - operation may complete slightly after timeout
            for operations that cannot be safely interrupted.
        """
        total_applied = 0
        total_skipped = 0
        start_time = time.time() if timeout else None

        try:
            if show_progress:
                print(f"🔧 Restructuring project: {self.project_path}")
                print("   Validating .claude folder structure...")

            # Iteratively validate and fix until no more fixable issues
            # (needed because some fixes reveal new issues, e.g., creating .claude folder)
            for iteration in range(self.MAX_RESTRUCTURE_ITERATIONS):
                # Check timeout at start of each iteration
                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(f"Restructure exceeded timeout of {timeout}s")

                # Validate
                validation = self.validate()

                # If valid or no fixable issues, we're done
                if validation.is_valid or len(validation.fixable_issues()) == 0:
                    if show_progress and iteration > 0:
                        print(f"✓ Structure validated successfully")
                    break

                # Generate fix plan
                fix_plan = self.generate_fix_plan(validation)

                if show_progress:
                    fixable_count = len(validation.fixable_issues())
                    print(f"   Found {fixable_count} issues to fix...")

                # Apply fixes
                apply_result = self.apply_fixes(fix_plan, auto_approve=auto_approve)

                total_applied += apply_result["applied"]
                total_skipped += apply_result["skipped"]

                if show_progress and apply_result["applied"] > 0:
                    print(f"   Applied {apply_result['applied']} fixes")

                # If nothing was applied, no point continuing
                if apply_result["applied"] == 0:
                    break

            # Final validation
            final_validation = self.validate()

            if show_progress:
                if total_applied > 0:
                    print(f"✓ Restructure complete: {total_applied} fixes applied")
                else:
                    print(f"✓ Structure already valid")

            # Return comprehensive result
            return {
                "validation": {
                    "is_valid": final_validation.is_valid,
                    "errors": len(final_validation.errors()),
                    "warnings": len(final_validation.warnings()),
                },
                "fixes_applied": total_applied,
                "fixes_skipped": total_skipped,
                "success": True,
            }

        except TimeoutError:
            # Rollback on timeout
            self._rollback_changes()
            # Re-raise TimeoutError as-is
            raise

        except PermissionError as e:
            # Rollback on permission errors
            self._rollback_changes()
            raise ValueError(f"Permission denied during restructure: {e}")

        except OSError as e:
            # Rollback on OS errors (disk full, etc.)
            self._rollback_changes()
            if e.errno == 28:  # ENOSPC - No space left on device
                raise ValueError(f"Disk full: Cannot complete restructure")
            raise ValueError(f"OS error during restructure: {e}")

        except Exception as e:
            # Rollback on any unexpected error
            self._rollback_changes()
            raise ValueError(f"Restructure failed: {e}")

    def format_markdown(self, result: Dict) -> str:
        """
        Format execution result as markdown.

        Args:
            result: Result from execute()

        Returns:
            Markdown-formatted string
        """
        lines = []
        lines.append("# Project Restructure Report")
        lines.append("")
        lines.append(f"**Project**: {self.project_path}")
        lines.append("")

        # Validation section
        validation = result.get("validation", {})
        lines.append("## Validation Results")
        lines.append("")
        lines.append(
            f"- **Status**: {'✅ Valid' if validation.get('is_valid') else '⚠️ Issues Found'}"
        )
        lines.append(f"- **Errors**: {validation.get('errors', 0)}")
        lines.append(f"- **Warnings**: {validation.get('warnings', 0)}")
        lines.append("")

        # Fixes section
        lines.append("## Fixes Applied")
        lines.append("")
        lines.append(f"- **Applied**: {result.get('fixes_applied', 0)} fixes")
        lines.append(f"- **Skipped**: {result.get('fixes_skipped', 0)} fixes")
        lines.append("")

        # Success status
        if result.get("success"):
            lines.append("✅ **Restructure completed successfully**")
        else:
            lines.append("❌ **Restructure failed**")

        return "\n".join(lines)

    def format_json(self, result: Dict) -> str:
        """
        Format execution result as JSON.

        Args:
            result: Result from execute()

        Returns:
            JSON-formatted string
        """
        return json.dumps(result, indent=2)
