"""
Pick Agent Command

Copies agent packs from built-in claude-force agents to target project.
Minimal implementation following TDD.
"""

import json
import logging
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional

from claude_force.security import validate_project_root
from claude_force.security.sensitive_file_detector import SensitiveFileDetector

logger = logging.getLogger(__name__)


def _is_builtin_agents_dir(claude_dir: Path) -> bool:
    """
    Verify that a .claude directory contains built-in claude-force agents.

    This prevents selecting a user's project .claude folder by checking
    for known built-in agents that ship with claude-force.

    Args:
        claude_dir: Path to .claude directory to check

    Returns:
        True if this contains built-in agents from claude-force
    """
    if not claude_dir.exists():
        logger.debug(f"Validation failed: {claude_dir} does not exist")
        return False

    agents_dir = claude_dir / "agents"
    if not agents_dir.exists():
        logger.debug(f"Validation failed: {agents_dir} does not exist")
        return False

    # Check for known built-in agents that ship with claude-force
    # These are unlikely to exist in user projects with the same names
    builtin_markers = [
        "code-reviewer.md",
        "python-expert.md",
        "qc-automation-expert.md",
    ]

    found_markers_list = [marker for marker in builtin_markers if (agents_dir / marker).exists()]
    found_markers = len(found_markers_list)

    logger.debug(
        f"Validation check for {claude_dir}: found {found_markers}/3 markers: {found_markers_list}"
    )

    # Require at least 2 of the 3 marker agents
    # This prevents false positives while being resilient to changes
    is_valid = found_markers >= 2
    if not is_valid:
        logger.debug(f"Validation failed: only {found_markers}/3 markers found (need at least 2)")
    return is_valid


def get_builtin_agents_path() -> Optional[Path]:
    """
    Find the built-in agents directory from claude-force installation.

    Returns:
        Path to built-in agents directory, or None if not found
    """
    import claude_force

    package_dir = Path(claude_force.__file__).parent
    logger.debug(f"Searching for built-in agents, package_dir: {package_dir}")

    # Try 0: Package templates directory (pip installed package)
    # This is where agents are stored when installed via pip
    templates_dir = package_dir / "templates"
    logger.debug(f"Try 0: Checking {templates_dir}")
    if _is_builtin_agents_dir(templates_dir):
        logger.info(f"Found built-in agents at: {templates_dir}")
        return templates_dir
    logger.debug(f"Try 0: Not found at {templates_dir}")

    # Try 1: Package directory (alternative package data location)
    claude_dir = package_dir / ".claude"
    logger.debug(f"Try 1: Checking {claude_dir}")
    if _is_builtin_agents_dir(claude_dir):
        logger.info(f"Found built-in agents at: {claude_dir}")
        return claude_dir
    logger.debug(f"Try 1: Not found at {claude_dir}")

    # Try 2: Parent directory (development mode with editable install)
    dev_claude_dir = package_dir.parent / ".claude"
    logger.debug(f"Try 2: Checking {dev_claude_dir}")
    if _is_builtin_agents_dir(dev_claude_dir):
        logger.info(f"Found built-in agents at: {dev_claude_dir}")
        return dev_claude_dir
    logger.debug(f"Try 2: Not found at {dev_claude_dir}")

    # Try 3: Site-packages parallel directory (some pip install scenarios)
    # /path/to/site-packages/claude_force -> /path/to/site-packages/.claude
    site_packages_claude = package_dir.parent / ".claude"
    if site_packages_claude != dev_claude_dir:
        logger.debug(f"Try 3: Checking {site_packages_claude}")
        if _is_builtin_agents_dir(site_packages_claude):
            logger.info(f"Found built-in agents at: {site_packages_claude}")
            return site_packages_claude
        logger.debug(f"Try 3: Not found at {site_packages_claude}")

    # Try 4: Check if package is in claude-force git repo (development)
    # Only use git if the package_dir is actually inside the repo
    try:
        import subprocess

        logger.debug("Try 4: Attempting git fallback")
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=package_dir,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            repo_root = Path(result.stdout.strip())
            logger.debug(f"Try 4: Git repo root: {repo_root}")

            # CRITICAL: Only use this if package_dir is inside the repo
            # This prevents selecting user's project .claude folder
            try:
                package_dir.relative_to(repo_root)
                # If we get here, package is inside the repo
                logger.debug(f"Try 4: Package is inside repo, checking {repo_root}/.claude")
                repo_claude_dir = repo_root / ".claude"
                if _is_builtin_agents_dir(repo_claude_dir):
                    logger.info(f"Found built-in agents at: {repo_claude_dir}")
                    return repo_claude_dir
                logger.debug(f"Try 4: Not found at {repo_claude_dir}")
            except ValueError:
                # package_dir is not inside repo_root, skip this fallback
                logger.debug(f"Try 4: Package {package_dir} not inside repo {repo_root}, skipping")
        else:
            logger.debug(f"Try 4: Git command failed with code {result.returncode}")
    except Exception as e:
        logger.debug(f"Try 4: Git fallback failed: {e}")

    logger.warning("Built-in agents not found in any known location")
    return None


def list_builtin_agents() -> List[str]:
    """
    List all built-in agents from claude-force.

    Returns:
        List of agent names (without .md extension)
    """
    claude_dir = get_builtin_agents_path()
    if not claude_dir:
        return []

    agents = []
    agents_dir = claude_dir / "agents"
    contracts_dir = claude_dir / "contracts"

    # Find all agent files that have matching contracts
    for agent_file in agents_dir.glob("*.md"):
        agent_name = agent_file.stem

        # Check if contract also exists (either .md or .contract extension)
        contract_md = contracts_dir / f"{agent_name}.md"
        contract_file = contracts_dir / f"{agent_name}.contract"

        if contract_md.exists() or contract_file.exists():
            agents.append(agent_name)

    return sorted(agents)


class PickAgentCommand:
    """
    /pick-agent command implementation

    Copies agent definitions and contracts from source to target project.
    """

    # Configuration constants
    MAX_FILE_SIZE = 10 * 1024 * 1024  # Maximum agent file size (10MB)
    DEFAULT_TIMEOUT = 300.0  # Default timeout in seconds (5 minutes)

    def __init__(self, source_project: Path, target_project: Path):
        """
        Initialize pick-agent command.

        Args:
            source_project: Path to source project (claude-force or another project)
            target_project: Path to target project to copy agents to

        Raises:
            ValueError: If paths are invalid or source equals target
        """
        # Validate both paths
        self.source_project = validate_project_root(source_project)
        self.target_project = validate_project_root(target_project)

        # Validate source != target
        if self.source_project.resolve() == self.target_project.resolve():
            raise ValueError("Source and target must be different directories")

        # Detect source structure:
        # - If source has agents/ and contracts/ directly (templates structure), use it as-is
        # - Otherwise, assume standard project structure with .claude/ subdirectory
        source_has_agents = (self.source_project / "agents").exists()
        source_has_contracts = (self.source_project / "contracts").exists()

        if source_has_agents and source_has_contracts:
            # Templates structure: agents/ and contracts/ are directly under source
            self.source_claude = self.source_project
            # For templates, check if there's a .claude directory with claude.json
            # Try parent's sibling first: /path/to/templates -> /path/to/.claude/claude.json
            # Then try grandparent's child: /path/to/package/templates -> /path/to/.claude/claude.json
            sibling_claude = self.source_project.parent / ".claude"
            grandparent_claude = self.source_project.parent.parent / ".claude"

            if (sibling_claude / "claude.json").exists():
                self.source_config_dir = sibling_claude
            elif (grandparent_claude / "claude.json").exists():
                self.source_config_dir = grandparent_claude
            else:
                self.source_config_dir = None
        else:
            # Standard project structure: agents/ and contracts/ are under .claude/
            self.source_claude = self.source_project / ".claude"
            self.source_config_dir = self.source_claude

        self.target_claude = self.target_project / ".claude"

    def list_available_agents(self) -> List[str]:
        """
        List all available agents from source project.

        Returns:
            List of agent names (without .md extension)
        """
        agents = []

        agents_dir = self.source_claude / "agents"
        contracts_dir = self.source_claude / "contracts"

        if not agents_dir.exists():
            return []

        # Find all agent files
        for agent_file in agents_dir.glob("*.md"):
            agent_name = agent_file.stem  # Filename without extension

            # Check if contract also exists
            contract_file = contracts_dir / f"{agent_name}.contract"
            if contract_file.exists():
                agents.append(agent_name)

        return sorted(agents)

    def _create_backup(self, filepath: Path) -> None:
        """
        Create backup of existing file before overwriting.

        Args:
            filepath: Path to file to backup
        """
        if filepath.exists():
            backup_path = filepath.with_suffix(filepath.suffix + ".bak")
            # Use shutil.copy2 to preserve metadata (permissions, timestamps)
            shutil.copy2(filepath, backup_path)

    def _validate_file_content(self, filepath: Path) -> None:
        """
        Validate file content before copying.

        Args:
            filepath: Path to file to validate

        Raises:
            ValueError: If file contains sensitive data or is too large
        """
        import re

        # 1. Check file size
        file_size = filepath.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size:,} bytes (max {self.MAX_FILE_SIZE:,} bytes)"
            )

        # 2. Read and validate content
        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError("File contains invalid UTF-8 characters")

        # 3. Scan for sensitive data patterns in content
        sensitive_patterns = [
            (r"sk-[a-zA-Z0-9]{32,}", "API key (sk-...)"),
            (r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']', "API key assignment"),
            (r'password\s*[:=]\s*["\'][^"\']+["\']', "Password assignment"),
            (r'secret[_-]?key\s*[:=]\s*["\'][^"\']+["\']', "Secret key assignment"),
            (r"aws[_-]?access[_-]?key[_-]?id\s*[:=]", "AWS credentials"),
            (r"private[_-]?key\s*[:=]", "Private key"),
            (r"bearer\s+[a-zA-Z0-9\-._~+/]+=*", "Bearer token"),
            (r'token\s*[:=]\s*["\'][^"\']{20,}["\']', "Access token"),
        ]

        for pattern, reason in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValueError(f"File contains sensitive data ({reason})")

        # 4. Check filename for sensitive patterns
        detector = SensitiveFileDetector()
        should_skip, reason = detector.should_skip_content(filepath)
        if should_skip:
            raise ValueError(f"File is sensitive ({reason})")

    def copy_agent(self, agent_name: str) -> Dict:
        """
        Copy a single agent to target project.

        Args:
            agent_name: Name of agent to copy

        Returns:
            Dictionary with copy result
        """
        try:
            # Source files
            source_agent = self.source_claude / "agents" / f"{agent_name}.md"
            source_contract = self.source_claude / "contracts" / f"{agent_name}.contract"

            # Target files
            target_agent = self.target_claude / "agents" / f"{agent_name}.md"
            target_contract = self.target_claude / "contracts" / f"{agent_name}.contract"

            # Validate content before copying (security check)
            self._validate_file_content(source_agent)
            self._validate_file_content(source_contract)

            # Ensure target directories exist
            target_agent.parent.mkdir(parents=True, exist_ok=True)
            target_contract.parent.mkdir(parents=True, exist_ok=True)

            # Create backups before overwriting
            self._create_backup(target_agent)
            self._create_backup(target_contract)

            # Copy files
            shutil.copy2(source_agent, target_agent)
            shutil.copy2(source_contract, target_contract)

            return {"success": True, "agent": agent_name, "files_copied": 2}

        except FileNotFoundError as e:
            return {"success": False, "agent": agent_name, "error": f"Agent files not found: {e}"}

        except PermissionError as e:
            return {"success": False, "agent": agent_name, "error": f"Permission denied: {e}"}

        except ValueError as e:
            return {"success": False, "agent": agent_name, "error": str(e)}

        except OSError as e:
            return {"success": False, "agent": agent_name, "error": f"File system error: {e}"}

    def copy_agents(
        self,
        agent_names: List[str],
        show_progress: bool = True,
        timeout: Optional[float] = None,
        start_time: Optional[float] = None,
    ) -> Dict:
        """
        Copy multiple agents to target project.

        Args:
            agent_names: List of agent names to copy
            show_progress: Whether to show progress messages (default: True)
            timeout: Maximum execution time in seconds (None = no timeout)
            start_time: Start time for timeout calculation (internal use)

        Returns:
            Dictionary with copy results

        Raises:
            TimeoutError: If operation exceeds timeout
        """
        copied = 0
        failed = 0
        errors = []

        if show_progress and len(agent_names) > 0:
            print(f"📦 Copying {len(agent_names)} agent(s)...")

        for idx, agent_name in enumerate(agent_names, 1):
            # Check timeout before each copy
            if timeout and start_time and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Copy operation exceeded timeout of {timeout}s")

            if show_progress:
                print(f"   [{idx}/{len(agent_names)}] {agent_name}...", end=" ")

            result = self.copy_agent(agent_name)
            if result["success"]:
                copied += 1
                if show_progress:
                    print("✓")
            else:
                failed += 1
                if show_progress:
                    print(f"✗ ({result.get('error', 'Unknown error')})")
                errors.append({"agent": agent_name, "error": result.get("error", "Unknown error")})

        return {"copied": copied, "failed": failed, "errors": errors}

    def update_config(self, agent_names: List[str]) -> Dict:
        """
        Update target project's claude.json with new agents atomically.

        Uses atomic write pattern: backup → write to temp → rename.
        If any step fails, backup is preserved.

        Args:
            agent_names: List of agent names to add to config

        Returns:
            Dictionary with update result
        """
        import os
        import tempfile

        backup_path = None
        temp_path = None

        try:
            # Load source config to get agent definitions
            # Use source_config_dir if available (for templates), otherwise use source_claude
            if self.source_config_dir:
                source_config_path = self.source_config_dir / "claude.json"
            else:
                source_config_path = self.source_claude / "claude.json"

            if not source_config_path.exists():
                # If no source config found, we can still succeed but won't add metadata
                # This allows copying agents without configuration metadata
                logger.warning(
                    f"Source claude.json not found at {source_config_path}, skipping config metadata"
                )
                return {"success": True, "agents_added": 0}

            with open(source_config_path, "r") as f:
                source_config = json.load(f)

            # Load target config
            target_config_path = self.target_claude / "claude.json"
            if not target_config_path.exists():
                return {"success": False, "error": "Target claude.json not found"}

            # Step 1: Create backup of original config
            backup_path = target_config_path.with_suffix(".json.bak")
            shutil.copy2(target_config_path, backup_path)

            # Step 2: Load and modify config
            with open(target_config_path, "r") as f:
                target_config = json.load(f)

            # Ensure agents section exists
            if "agents" not in target_config:
                target_config["agents"] = {}

            # Copy agent configurations from source to target
            added = 0
            for agent_name in agent_names:
                if agent_name in source_config.get("agents", {}):
                    # Copy the entire agent configuration
                    target_config["agents"][agent_name] = source_config["agents"][agent_name]
                    added += 1

            # Step 3: Write to temporary file in same directory
            # (atomic rename only works within same filesystem)
            temp_fd, temp_path = tempfile.mkstemp(
                dir=target_config_path.parent, prefix=".claude.json.", suffix=".tmp"
            )

            try:
                with os.fdopen(temp_fd, "w") as f:
                    json.dump(target_config, f, indent=2)
            except Exception:
                # If write fails, close and remove temp file
                os.close(temp_fd)
                raise

            # Step 4: Atomic rename (replaces target file)
            # On Unix this is atomic; on Windows it's not but close enough
            os.replace(temp_path, target_config_path)
            temp_path = None  # Renamed, don't delete

            return {"success": True, "agents_added": added}

        except Exception as e:
            # On failure, backup is preserved for manual recovery
            return {"success": False, "error": str(e)}

        finally:
            # Cleanup: Remove temp file if it still exists
            if temp_path and Path(temp_path).exists():
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass  # Best effort cleanup

    def execute(
        self, agent_names: List[str], show_progress: bool = True, timeout: Optional[float] = None
    ) -> Dict:
        """
        Execute the full pick-agent workflow.

        Args:
            agent_names: List of agent names to copy
            show_progress: Whether to show progress messages (default: True)
            timeout: Maximum execution time in seconds (None = no timeout)

        Returns:
            Dictionary with execution results

        Raises:
            TimeoutError: If operation exceeds timeout (best effort)

        Note:
            Timeout is "best effort" - operation may complete slightly after timeout
            for operations that cannot be safely interrupted.
        """
        start_time = time.time() if timeout else None

        if show_progress:
            print(f"🎯 Pick Agent: {self.source_project} → {self.target_project}")

        # Copy agent files
        copy_result = self.copy_agents(
            agent_names, show_progress=show_progress, timeout=timeout, start_time=start_time
        )

        # Update config for successfully copied agents
        if copy_result["copied"] > 0:
            if show_progress:
                print(f"   Updating configuration...")
            update_result = self.update_config(agent_names)
            if show_progress and update_result.get("success"):
                print(f"✓ Configuration updated")
        else:
            update_result = {"success": False, "agents_added": 0}

        # Determine overall success: files must be copied AND config must be updated
        overall_success = copy_result["copied"] > 0 and update_result.get("success", False)

        if show_progress:
            if overall_success:
                print(f"✓ Pick complete: {copy_result['copied']} agent(s) copied and configured")
            elif copy_result["copied"] > 0:
                print(f"⚠ Agents copied but config update failed")
            else:
                print(f"✗ No agents were copied")

        # Return comprehensive result
        return {
            "success": overall_success,
            "agents_copied": copy_result["copied"],
            "agents_failed": copy_result["failed"],
            "config_updated": update_result.get("success", False),
            "agents_added_to_config": update_result.get("agents_added", 0),
            "errors": copy_result.get("errors", []),
        }

    def format_markdown(self, result: Dict) -> str:
        """
        Format execution result as markdown.

        Args:
            result: Result from execute()

        Returns:
            Markdown-formatted string
        """
        lines = []
        lines.append("# Pick Agent Report")
        lines.append("")
        lines.append(f"**Source**: {self.source_project}")
        lines.append(f"**Target**: {self.target_project}")
        lines.append("")

        # Summary section
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Agents Copied**: {result.get('agents_copied', 0)}")
        lines.append(f"- **Agents Failed**: {result.get('agents_failed', 0)}")
        lines.append(
            f"- **Config Updated**: {'✅ Yes' if result.get('config_updated') else '❌ No'}"
        )
        lines.append("")

        # Status
        if result.get("success"):
            lines.append("✅ **Pick agent completed successfully**")
        else:
            lines.append("❌ **Pick agent failed**")

        # Errors if any
        if result.get("errors"):
            lines.append("")
            lines.append("## Errors")
            lines.append("")
            for error in result["errors"]:
                lines.append(f"- **{error['agent']}**: {error['error']}")

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
