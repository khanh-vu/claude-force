"""
Agent Import/Export Tool for claude-force.

Enables importing agents from wshobson/agents format and exporting
claude-force agents to external formats for cross-repository compatibility.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import re
import json
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """Metadata extracted from agent definition."""

    name: str
    description: str
    content: str
    expertise: List[str] = None
    tools: List[str] = None
    model: str = "claude-3-5-sonnet-20241022"
    source: str = "imported"

    def __post_init__(self):
        if self.expertise is None:
            self.expertise = []
        if self.tools is None:
            self.tools = []


@dataclass
class ContractMetadata:
    """Contract metadata for agent."""

    inputs: List[str]
    outputs: List[str]
    constraints: List[str]
    quality_metrics: List[str]


class AgentPortingTool:
    """
    Import/export agents between claude-force and wshobson/agents formats.

    Supports:
    - Importing from wshobson/agents (markdown) to claude-force
    - Exporting claude-force agents to wshobson format
    - Automatic contract generation for imported agents
    - Format conversion and validation
    """

    def __init__(self, agents_dir: Optional[Path] = None):
        """
        Initialize porting tool.

        Args:
            agents_dir: Path to .claude/agents directory
        """
        self.agents_dir = agents_dir or Path(".claude/agents")
        self.contracts_dir = Path(".claude/contracts")

    def import_from_wshobson(
        self,
        agent_file: Path,
        generate_contract: bool = True,
        target_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Import agent from wshobson/agents markdown format.

        Args:
            agent_file: Path to agent markdown file
            generate_contract: Auto-generate claude-force contract
            target_name: Override agent name

        Returns:
            Dict with agent info and paths
        """
        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

        # Parse wshobson format
        metadata = self._parse_wshobson_format(agent_file)

        # Override name if provided
        if target_name:
            metadata.name = target_name

        # Create agent directory
        agent_dir = self.agents_dir / metadata.name
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Write AGENT.md
        agent_md = agent_dir / "AGENT.md"
        agent_md.write_text(metadata.content)

        # Generate contract if requested
        contract_path = None
        if generate_contract:
            contract_path = self._generate_contract(metadata)

        logger.info(f"Successfully imported agent '{metadata.name}' from {agent_file}")

        return {
            "name": metadata.name,
            "agent_path": str(agent_md),
            "contract_path": str(contract_path) if contract_path else None,
            "metadata": metadata
        }

    def export_to_wshobson(
        self,
        agent_name: str,
        output_dir: Path,
        include_metadata: bool = True
    ) -> Path:
        """
        Export claude-force agent to wshobson markdown format.

        Args:
            agent_name: Name of agent to export
            output_dir: Output directory for exported agent
            include_metadata: Include metadata header

        Returns:
            Path to exported agent file
        """
        agent_dir = self.agents_dir / agent_name
        if not agent_dir.exists():
            raise FileNotFoundError(f"Agent '{agent_name}' not found in {self.agents_dir}")

        # Read AGENT.md
        agent_md = agent_dir / "AGENT.md"
        if not agent_md.exists():
            raise FileNotFoundError(f"AGENT.md not found for '{agent_name}'")

        content = agent_md.read_text()

        # Simplify format (remove claude-force specific sections)
        simplified = self._simplify_to_wshobson(content, agent_name)

        # Add metadata if requested
        if include_metadata:
            simplified = self._add_wshobson_metadata(simplified, agent_name)

        # Write to output
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{agent_name}.md"
        output_file.write_text(simplified)

        logger.info(f"Successfully exported agent '{agent_name}' to {output_file}")

        return output_file

    def _parse_wshobson_format(self, agent_file: Path) -> AgentMetadata:
        """
        Parse wshobson/agents markdown format.

        Wshobson format is typically simpler:
        - Title line with agent name
        - Description section
        - Expertise/capabilities sections
        - No formal contracts
        """
        content = agent_file.read_text()

        # Extract agent name from filename or title
        agent_name = agent_file.stem

        # Try to extract from markdown title
        title_match = re.search(r'^#\s+(.+?)(?:\n|$)', content, re.MULTILINE)
        if title_match:
            agent_name = self._slugify(title_match.group(1))

        # Extract description (first paragraph after title)
        description = "Imported agent from wshobson/agents"
        desc_match = re.search(r'^#\s+.+?\n\n(.+?)(?:\n\n|$)', content, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            # Limit to first sentence or 200 chars
            description = description.split('.')[0][:200]

        # Extract expertise areas
        expertise = []
        expertise_section = re.search(
            r'(?:##\s+Expertise|##\s+Capabilities|##\s+Skills)(.+?)(?:##|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if expertise_section:
            # Extract bullet points
            bullets = re.findall(r'[-*]\s+(.+)', expertise_section.group(1))
            expertise = [b.strip() for b in bullets]

        return AgentMetadata(
            name=agent_name,
            description=description,
            content=content,
            expertise=expertise,
            source="wshobson"
        )

    def _generate_contract(self, metadata: AgentMetadata) -> Path:
        """
        Generate claude-force contract for imported agent.

        Contracts specify:
        - Expected inputs
        - Output format
        - Quality constraints
        - Success metrics
        """
        contract_dir = self.contracts_dir / metadata.name
        contract_dir.mkdir(parents=True, exist_ok=True)

        # Infer contract from metadata
        contract_data = self._infer_contract_from_metadata(metadata)

        # Write CONTRACT.md
        contract_md = contract_dir / "CONTRACT.md"
        contract_content = self._format_contract(metadata.name, contract_data)
        contract_md.write_text(contract_content)

        logger.info(f"Generated contract for '{metadata.name}' at {contract_md}")

        return contract_md

    def _infer_contract_from_metadata(self, metadata: AgentMetadata) -> ContractMetadata:
        """Infer contract details from agent metadata."""

        # Default inputs for imported agents
        inputs = [
            "task: Clear description of the task to be performed",
            "context: Optional context or background information"
        ]

        # Default outputs
        outputs = [
            "analysis: Detailed analysis of the task",
            "recommendations: Actionable recommendations",
            "implementation: Code or configuration if applicable"
        ]

        # Infer constraints from expertise
        constraints = [
            "Follow industry best practices",
            "Provide clear explanations",
            "Include examples where helpful"
        ]

        if "security" in metadata.description.lower() or "security" in str(metadata.expertise).lower():
            constraints.append("Address security considerations")

        if "performance" in metadata.description.lower():
            constraints.append("Consider performance implications")

        # Quality metrics
        quality_metrics = [
            "Completeness: All aspects of task addressed",
            "Clarity: Clear and understandable output",
            "Actionability: Recommendations are specific and actionable"
        ]

        return ContractMetadata(
            inputs=inputs,
            outputs=outputs,
            constraints=constraints,
            quality_metrics=quality_metrics
        )

    def _format_contract(self, agent_name: str, contract: ContractMetadata) -> str:
        """Format contract as markdown."""

        content = f"""# Agent Contract: {agent_name}

## Overview

This contract defines the expected behavior and output format for the {agent_name} agent.

## Inputs

"""

        for inp in contract.inputs:
            content += f"- {inp}\n"

        content += "\n## Expected Outputs\n\n"

        for out in contract.outputs:
            content += f"- {out}\n"

        content += "\n## Constraints\n\n"

        for constraint in contract.constraints:
            content += f"- {constraint}\n"

        content += "\n## Quality Metrics\n\n"

        for metric in contract.quality_metrics:
            content += f"- {metric}\n"

        content += """
## Validation

Outputs from this agent should be validated against:
1. All required outputs are present
2. Outputs meet quality metrics
3. Constraints are satisfied

---

*Auto-generated contract - can be customized as needed*
"""

        return content

    def _simplify_to_wshobson(self, content: str, agent_name: str) -> str:
        """
        Simplify claude-force format to wshobson format.

        Removes:
        - Contract references
        - Claude-force specific sections
        - Governance details
        """
        # Remove contract sections
        content = re.sub(
            r'##\s+Contract.+?(?=##|$)',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Remove governance sections
        content = re.sub(
            r'##\s+Governance.+?(?=##|$)',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Remove MCP references
        content = re.sub(
            r'##\s+MCP.+?(?=##|$)',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Clean up extra whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)

        return content.strip()

    def _add_wshobson_metadata(self, content: str, agent_name: str) -> str:
        """Add wshobson-style metadata header."""

        header = f"""# {agent_name}

*Exported from claude-force*

---

"""
        return header + content

    def _slugify(self, text: str) -> str:
        """Convert text to slug format."""
        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', text.lower())
        # Replace spaces with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        # Remove leading/trailing hyphens
        return text.strip('-')

    def bulk_import(
        self,
        source_dir: Path,
        pattern: str = "*.md",
        generate_contracts: bool = True
    ) -> Dict[str, any]:
        """
        Import multiple agents from a directory.

        Args:
            source_dir: Directory containing agent markdown files
            pattern: File pattern to match
            generate_contracts: Generate contracts for all imported agents

        Returns:
            Dict with import results
        """
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        results = {
            "imported": [],
            "failed": [],
            "total": 0
        }

        for agent_file in source_dir.glob(pattern):
            results["total"] += 1

            try:
                result = self.import_from_wshobson(
                    agent_file=agent_file,
                    generate_contract=generate_contracts
                )
                results["imported"].append(result)

            except Exception as e:
                logger.error(f"Failed to import {agent_file}: {e}")
                results["failed"].append({
                    "file": str(agent_file),
                    "error": str(e)
                })

        logger.info(
            f"Bulk import complete: {len(results['imported'])}/{results['total']} successful"
        )

        return results

    def bulk_export(
        self,
        agent_names: List[str],
        output_dir: Path,
        include_metadata: bool = True
    ) -> Dict[str, any]:
        """
        Export multiple agents to wshobson format.

        Args:
            agent_names: List of agent names to export
            output_dir: Output directory
            include_metadata: Include metadata headers

        Returns:
            Dict with export results
        """
        results = {
            "exported": [],
            "failed": [],
            "total": len(agent_names)
        }

        for agent_name in agent_names:
            try:
                output_file = self.export_to_wshobson(
                    agent_name=agent_name,
                    output_dir=output_dir,
                    include_metadata=include_metadata
                )
                results["exported"].append({
                    "name": agent_name,
                    "path": str(output_file)
                })

            except Exception as e:
                logger.error(f"Failed to export {agent_name}: {e}")
                results["failed"].append({
                    "name": agent_name,
                    "error": str(e)
                })

        logger.info(
            f"Bulk export complete: {len(results['exported'])}/{results['total']} successful"
        )

        return results


def get_porting_tool(agents_dir: Optional[Path] = None) -> AgentPortingTool:
    """
    Get singleton porting tool instance.

    Args:
        agents_dir: Path to agents directory

    Returns:
        AgentPortingTool instance
    """
    return AgentPortingTool(agents_dir=agents_dir)
