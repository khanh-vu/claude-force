"""
Community Contribution System for claude-force.

Enables users to contribute agents and skills back to wshobson/agents
or other repositories with validation, formatting, and PR templates.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import logging

from claude_force.import_export import get_porting_tool, AgentPortingTool

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of contribution validation."""

    valid: bool
    errors: List[str]
    warnings: List[str]
    passed_checks: List[str]


@dataclass
class ContributionPackage:
    """Package ready for contribution."""

    agent_name: str
    export_path: Path
    validation: ValidationResult
    pr_template_path: Optional[Path] = None
    plugin_structure: Optional[Dict] = None


class ContributionManager:
    """
    Manage community contributions of agents and skills.

    Features:
    - Validate agent definitions
    - Convert to target repository format
    - Generate plugin structures
    - Create PR templates
    - Package for submission
    """

    def __init__(
        self,
        agents_dir: Optional[Path] = None,
        export_dir: Optional[Path] = None
    ):
        """
        Initialize contribution manager.

        Args:
            agents_dir: Path to .claude/agents directory
            export_dir: Path for exported contributions
        """
        self.agents_dir = agents_dir or Path(".claude/agents")
        self.export_dir = export_dir or Path("./exported")
        self.contracts_dir = Path(".claude/contracts")

        # Reuse porting tool for format conversion
        self.porting_tool = get_porting_tool(agents_dir=self.agents_dir)

    def validate_agent_for_contribution(
        self,
        agent_name: str,
        target_repo: str = "wshobson"
    ) -> ValidationResult:
        """
        Validate agent is ready for contribution.

        Args:
            agent_name: Name of agent to validate
            target_repo: Target repository (wshobson, claude-force)

        Returns:
            ValidationResult with errors, warnings, and passed checks
        """
        errors = []
        warnings = []
        passed = []

        agent_dir = self.agents_dir / agent_name

        # Check 1: Agent exists
        if not agent_dir.exists():
            errors.append(f"Agent directory not found: {agent_dir}")
            return ValidationResult(
                valid=False,
                errors=errors,
                warnings=warnings,
                passed_checks=passed
            )
        passed.append("Agent directory exists")

        # Check 2: AGENT.md exists
        agent_md = agent_dir / "AGENT.md"
        if not agent_md.exists():
            errors.append("AGENT.md not found")
        else:
            passed.append("AGENT.md exists")

            # Check content quality
            content = agent_md.read_text()

            if len(content) < 100:
                errors.append("AGENT.md content too short (< 100 chars)")
            else:
                passed.append("AGENT.md has sufficient content")

            # Check for title
            if not content.strip().startswith("#"):
                warnings.append("AGENT.md should start with a title (# heading)")
            else:
                passed.append("AGENT.md has title")

            # Check for description
            if "description" not in content.lower() and len(content.split("\n\n")) < 2:
                warnings.append("AGENT.md should include description section")
            else:
                passed.append("AGENT.md includes description")

        # Check 3: Contract exists (for claude-force)
        contract_dir = self.contracts_dir / agent_name
        if contract_dir.exists() and (contract_dir / "CONTRACT.md").exists():
            passed.append("Contract exists")
        else:
            if target_repo == "claude-force":
                warnings.append("No contract found (recommended for claude-force)")

        # Check 4: Examples included
        if agent_md.exists():
            content = agent_md.read_text()
            if "example" in content.lower():
                passed.append("Includes examples")
            else:
                warnings.append("No examples found (recommended for contributions)")

        # Check 5: Agent is not a duplicate of builtin
        builtin_agents = [
            "frontend-architect", "backend-architect", "database-architect",
            "ai-engineer", "prompt-engineer", "data-engineer",
            "security-specialist", "devops-engineer", "api-designer",
            "code-reviewer", "python-expert", "documentation-expert"
        ]

        if agent_name in builtin_agents:
            warnings.append(
                f"Agent name '{agent_name}' matches builtin agent. "
                "Consider using a different name to avoid confusion."
            )

        # Determine validity
        valid = len(errors) == 0

        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            passed_checks=passed
        )

    def prepare_contribution(
        self,
        agent_name: str,
        target_repo: str = "wshobson",
        include_metadata: bool = True,
        validate: bool = True
    ) -> ContributionPackage:
        """
        Prepare agent for contribution.

        Args:
            agent_name: Name of agent to contribute
            target_repo: Target repository
            include_metadata: Include metadata in export
            validate: Run validation before export

        Returns:
            ContributionPackage ready for submission

        Raises:
            ValueError: If validation fails and validate=True
        """
        # Validate first
        validation = None
        if validate:
            validation = self.validate_agent_for_contribution(agent_name, target_repo)
            if not validation.valid:
                raise ValueError(
                    f"Agent validation failed:\n" +
                    "\n".join(f"  - {err}" for err in validation.errors)
                )

        # Create export directory
        export_path = self.export_dir / f"{agent_name}-plugin"
        export_path.mkdir(parents=True, exist_ok=True)

        # Export agent to target format
        if target_repo == "wshobson":
            agent_file = self.porting_tool.export_to_wshobson(
                agent_name=agent_name,
                output_dir=export_path,
                include_metadata=include_metadata
            )
        else:
            # For claude-force format, just copy
            agent_file = self._export_claude_force_format(agent_name, export_path)

        # Generate plugin structure
        plugin_structure = self._generate_plugin_structure(
            agent_name,
            target_repo,
            export_path
        )

        # Generate PR template
        pr_template_path = self._generate_pr_template(
            agent_name,
            target_repo,
            export_path,
            validation
        )

        logger.info(f"Prepared contribution for '{agent_name}' at {export_path}")

        return ContributionPackage(
            agent_name=agent_name,
            export_path=export_path,
            validation=validation,
            pr_template_path=pr_template_path,
            plugin_structure=plugin_structure
        )

    def _export_claude_force_format(
        self,
        agent_name: str,
        output_dir: Path
    ) -> Path:
        """Export agent in claude-force format."""
        agent_dir = self.agents_dir / agent_name
        agent_md = agent_dir / "AGENT.md"

        if not agent_md.exists():
            raise FileNotFoundError(f"AGENT.md not found for '{agent_name}'")

        # Copy AGENT.md
        output_file = output_dir / f"{agent_name}.md"
        output_file.write_text(agent_md.read_text())

        # Copy contract if exists
        contract_dir = self.contracts_dir / agent_name
        if contract_dir.exists() and (contract_dir / "CONTRACT.md").exists():
            contract_out = output_dir / "CONTRACT.md"
            contract_out.write_text((contract_dir / "CONTRACT.md").read_text())

        return output_file

    def _generate_plugin_structure(
        self,
        agent_name: str,
        target_repo: str,
        export_path: Path
    ) -> Dict:
        """Generate plugin structure for marketplace."""
        if target_repo == "wshobson":
            structure = {
                "plugin_id": f"{agent_name}-plugin",
                "name": agent_name.replace("-", " ").title(),
                "version": "1.0.0",
                "description": f"Contribution: {agent_name} agent",
                "source": "community",
                "agents": [agent_name],
                "skills": [],
                "workflows": []
            }
        else:
            structure = {
                "plugin_id": f"{agent_name}-plugin",
                "name": agent_name.replace("-", " ").title(),
                "version": "1.0.0",
                "description": f"Community contribution: {agent_name}",
                "agents": [
                    {
                        "id": agent_name,
                        "name": agent_name.replace("-", " ").title(),
                        "file": f"{agent_name}.md"
                    }
                ]
            }

        # Write plugin.json
        plugin_file = export_path / "plugin.json"
        with open(plugin_file, 'w') as f:
            json.dump(structure, f, indent=2)

        return structure

    def _generate_pr_template(
        self,
        agent_name: str,
        target_repo: str,
        export_path: Path,
        validation: Optional[ValidationResult] = None
    ) -> Path:
        """Generate PR template for contribution."""
        template = f"""# Contribution: {agent_name}

## Overview

Contributing the **{agent_name}** agent to {target_repo}/agents.

## Agent Description

[Brief description of what this agent does and its primary use cases]

## Validation Results

"""

        if validation:
            template += f"**Status:** {'✅ Passed' if validation.valid else '❌ Failed'}\n\n"

            if validation.passed_checks:
                template += "### Passed Checks\n\n"
                for check in validation.passed_checks:
                    template += f"- ✅ {check}\n"
                template += "\n"

            if validation.warnings:
                template += "### Warnings\n\n"
                for warning in validation.warnings:
                    template += f"- ⚠️ {warning}\n"
                template += "\n"

            if validation.errors:
                template += "### Errors\n\n"
                for error in validation.errors:
                    template += f"- ❌ {error}\n"
                template += "\n"

        template += """## Testing

I have tested this agent with the following tasks:

1. [Example task 1]
2. [Example task 2]
3. [Example task 3]

## Examples

### Example 1: [Task description]

**Input:**
```
[Task input]
```

**Output:**
```
[Agent output]
```

## Checklist

- [ ] Agent definition is complete and well-documented
- [ ] Agent has been tested with multiple tasks
- [ ] Examples are included
- [ ] No sensitive information in agent definition
- [ ] Agent name doesn't conflict with existing agents
- [ ] Agent follows repository conventions

## Additional Notes

[Any additional context or notes about this contribution]

---

*Generated by claude-force contribution system*
"""

        pr_template_path = export_path / "PR_TEMPLATE.md"
        pr_template_path.write_text(template)

        return pr_template_path

    def get_contribution_instructions(
        self,
        agent_name: str,
        target_repo: str,
        package: ContributionPackage
    ) -> str:
        """
        Get step-by-step contribution instructions.

        Args:
            agent_name: Agent name
            target_repo: Target repository
            package: Contribution package

        Returns:
            Formatted instructions
        """
        if target_repo == "wshobson":
            repo_url = "https://github.com/wshobson/agents"
        else:
            repo_url = "https://github.com/your-org/claude-force"

        instructions = f"""
🎁 Contribution Package Ready: {agent_name}
{'=' * 60}

📦 Package Location: {package.export_path}

📋 Next Steps:

1. Review the exported plugin:
   $ cd {package.export_path}
   $ ls -la

2. Test the agent one more time:
   $ claude-force run agent {agent_name} --task "Your test task"

3. Fork the target repository:
   $ gh repo fork {repo_url}

4. Clone your fork (replace YOUR_USERNAME with your GitHub username):
   $ git clone https://github.com/YOUR_USERNAME/agents
   $ cd agents

5. Add the plugin to marketplace.json:
   - Open marketplace.json
   - Add entry for {agent_name}-plugin
   - Include plugin metadata from {package.export_path}/plugin.json

6. Copy the agent file:
   $ cp {package.export_path}/{agent_name}.md agents/

7. Create a pull request:
   - Use the PR template at {package.pr_template_path}
   - Fill in examples and testing details
   - Submit PR to {repo_url}

📄 PR Template: {package.pr_template_path}

💡 Tips:
- Make sure to test your agent thoroughly before contributing
- Include clear examples in your PR
- Respond to review feedback promptly
- Follow the repository's contribution guidelines

✅ Validation Status: {'PASSED' if package.validation and package.validation.valid else 'REVIEW NEEDED'}
"""

        if package.validation and package.validation.warnings:
            instructions += "\n⚠️  Warnings:\n"
            for warning in package.validation.warnings:
                instructions += f"   - {warning}\n"

        return instructions


def get_contribution_manager(
    agents_dir: Optional[Path] = None,
    export_dir: Optional[Path] = None
) -> ContributionManager:
    """
    Get singleton contribution manager instance.

    Args:
        agents_dir: Path to agents directory
        export_dir: Path for exports

    Returns:
        ContributionManager instance
    """
    return ContributionManager(agents_dir=agents_dir, export_dir=export_dir)
