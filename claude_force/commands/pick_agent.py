"""
Pick Agent Command

Copies agent packs from source project to target project.
Minimal implementation following TDD.
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict

from claude_force.security import validate_project_root
from claude_force.security.sensitive_file_detector import SensitiveFileDetector


class PickAgentCommand:
    """
    /pick-agent command implementation

    Copies agent definitions and contracts from source to target project.
    """

    def __init__(self, source_project: Path, target_project: Path):
        """
        Initialize pick-agent command.

        Args:
            source_project: Path to source project (claude-force or another project)
            target_project: Path to target project to copy agents to

        Raises:
            ValueError: If paths are invalid
        """
        # Validate both paths
        self.source_project = validate_project_root(source_project)
        self.target_project = validate_project_root(target_project)

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

        # Maximum file size: 10MB
        MAX_FILE_SIZE = 10 * 1024 * 1024

        # 1. Check file size
        file_size = filepath.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size:,} bytes (max {MAX_FILE_SIZE:,} bytes)"
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

        except Exception as e:
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e)
            }

    def copy_agents(self, agent_names: List[str]) -> Dict:
        """
        Copy multiple agents to target project.

        Args:
            agent_names: List of agent names to copy

        Returns:
            Dictionary with copy results
        """
        copied = 0
        failed = 0
        errors = []

        for agent_name in agent_names:
            result = self.copy_agent(agent_name)
            if result["success"]:
                copied += 1
            else:
                failed += 1
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
        Update target project's claude.json with new agents.

        Args:
            agent_names: List of agent names to add to config

        Returns:
            Dictionary with update result
        """
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

            # Write updated config
            with open(target_config_path, 'w') as f:
                json.dump(target_config, f, indent=2)

            return {
                "success": True,
                "agents_added": added
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def execute(self, agent_names: List[str]) -> Dict:
        """
        Execute the full pick-agent workflow.

        Args:
            agent_names: List of agent names to copy

        Returns:
            Dictionary with execution results
        """
        # Copy agent files
        copy_result = self.copy_agents(agent_names)

        # Update config for successfully copied agents
        if copy_result["copied"] > 0:
            update_result = self.update_config(agent_names)
        else:
            update_result = {"success": False, "agents_added": 0}

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
