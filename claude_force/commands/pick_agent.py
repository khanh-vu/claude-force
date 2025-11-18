"""
Pick Agent Command

Copies agent packs from source project to target project.
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

        self.source_claude = self.source_project / ".claude"
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
            backup_path = filepath.with_suffix(filepath.suffix + '.bak')
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
            content = filepath.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            raise ValueError("File contains invalid UTF-8 characters")

        # 3. Scan for sensitive data patterns in content
        sensitive_patterns = [
            (r'sk-[a-zA-Z0-9]{32,}', 'API key (sk-...)'),
            (r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']', 'API key assignment'),
            (r'password\s*[:=]\s*["\'][^"\']+["\']', 'Password assignment'),
            (r'secret[_-]?key\s*[:=]\s*["\'][^"\']+["\']', 'Secret key assignment'),
            (r'aws[_-]?access[_-]?key[_-]?id\s*[:=]', 'AWS credentials'),
            (r'private[_-]?key\s*[:=]', 'Private key'),
            (r'bearer\s+[a-zA-Z0-9\-._~+/]+=*', 'Bearer token'),
            (r'token\s*[:=]\s*["\'][^"\']{20,}["\']', 'Access token'),
        ]

        for pattern, reason in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValueError(
                    f"File contains sensitive data ({reason})"
                )

        # 4. Check filename for sensitive patterns
        detector = SensitiveFileDetector()
        should_skip, reason = detector.should_skip_content(filepath)
        if should_skip:
            raise ValueError(
                f"File is sensitive ({reason})"
            )

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

            return {
                "success": True,
                "agent": agent_name,
                "files_copied": 2
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Agent files not found: {e}"
            }

        except PermissionError as e:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Permission denied: {e}"
            }

        except ValueError as e:
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e)
            }

        except OSError as e:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"File system error: {e}"
            }

    def copy_agents(
        self,
        agent_names: List[str],
        show_progress: bool = True,
        timeout: Optional[float] = None,
        start_time: Optional[float] = None
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
                errors.append({
                    "agent": agent_name,
                    "error": result.get("error", "Unknown error")
                })

        return {
            "copied": copied,
            "failed": failed,
            "errors": errors
        }

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
            source_config_path = self.source_claude / "claude.json"
            if not source_config_path.exists():
                return {
                    "success": False,
                    "error": "Source claude.json not found"
                }

            with open(source_config_path, 'r') as f:
                source_config = json.load(f)

            # Load target config
            target_config_path = self.target_claude / "claude.json"
            if not target_config_path.exists():
                return {
                    "success": False,
                    "error": "Target claude.json not found"
                }

            # Step 1: Create backup of original config
            backup_path = target_config_path.with_suffix('.json.bak')
            shutil.copy2(target_config_path, backup_path)

            # Step 2: Load and modify config
            with open(target_config_path, 'r') as f:
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
                dir=target_config_path.parent,
                prefix='.claude.json.',
                suffix='.tmp'
            )

            try:
                with os.fdopen(temp_fd, 'w') as f:
                    json.dump(target_config, f, indent=2)
            except Exception:
                # If write fails, close and remove temp file
                os.close(temp_fd)
                raise

            # Step 4: Atomic rename (replaces target file)
            # On Unix this is atomic; on Windows it's not but close enough
            os.replace(temp_path, target_config_path)
            temp_path = None  # Renamed, don't delete

            return {
                "success": True,
                "agents_added": added
            }

        except Exception as e:
            # On failure, backup is preserved for manual recovery
            return {
                "success": False,
                "error": str(e)
            }

        finally:
            # Cleanup: Remove temp file if it still exists
            if temp_path and Path(temp_path).exists():
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass  # Best effort cleanup

    def execute(
        self,
        agent_names: List[str],
        show_progress: bool = True,
        timeout: Optional[float] = None
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
            agent_names,
            show_progress=show_progress,
            timeout=timeout,
            start_time=start_time
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

        if show_progress:
            if copy_result["copied"] > 0:
                print(f"✓ Pick complete: {copy_result['copied']} agent(s) copied")
            else:
                print(f"✗ No agents were copied")

        # Return comprehensive result
        return {
            "success": copy_result["copied"] > 0,
            "agents_copied": copy_result["copied"],
            "agents_failed": copy_result["failed"],
            "config_updated": update_result.get("success", False),
            "agents_added_to_config": update_result.get("agents_added", 0),
            "errors": copy_result.get("errors", [])
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
        lines.append(f"- **Config Updated**: {'✅ Yes' if result.get('config_updated') else '❌ No'}")
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
