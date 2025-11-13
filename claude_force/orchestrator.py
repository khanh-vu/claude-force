"""
Agent Orchestrator - Core orchestration engine for Claude multi-agent system
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class AgentResult:
    """Result from an agent execution"""
    agent_name: str
    success: bool
    output: str
    metadata: Dict[str, Any]
    errors: List[str] = None

    def to_dict(self):
        return asdict(self)


class AgentOrchestrator:
    """
    Orchestrates multiple Claude agents with governance and quality gates.

    Usage:
        orchestrator = AgentOrchestrator(config_path=".claude/claude.json")
        result = orchestrator.run_agent("code-reviewer", task="Review this code")
        results = orchestrator.run_workflow("full-stack-feature", task="Build auth")
    """

    def __init__(self, config_path: str = ".claude/claude.json", anthropic_api_key: Optional[str] = None):
        """
        Initialize orchestrator with configuration.

        Args:
            config_path: Path to claude.json configuration file
            anthropic_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Lazy import anthropic to allow installation without API key
        try:
            import anthropic
            self.client = anthropic.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

    def _load_config(self) -> Dict:
        """Load claude.json configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Make sure you're in a claude-force repository with .claude/claude.json"
            )

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.config_path}: {e}")

    def _load_agent_definition(self, agent_name: str) -> str:
        """Load agent definition from markdown file"""
        agent_config = self.config['agents'].get(agent_name)
        if not agent_config:
            raise ValueError(
                f"Agent '{agent_name}' not found in configuration. "
                f"Available agents: {', '.join(self.config['agents'].keys())}"
            )

        agent_file = self.config_path.parent / agent_config['file']
        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

        with open(agent_file, 'r') as f:
            return f.read()

    def _load_agent_contract(self, agent_name: str) -> str:
        """Load agent contract"""
        agent_config = self.config['agents'].get(agent_name)
        if not agent_config or 'contract' not in agent_config:
            return ""

        contract_file = self.config_path.parent / agent_config['contract']
        if not contract_file.exists():
            return ""

        with open(contract_file, 'r') as f:
            return f.read()

    def _build_prompt(self, agent_definition: str, agent_contract: str, task: str) -> str:
        """Build complete prompt for agent"""
        prompt_parts = [
            "# Agent Definition",
            agent_definition,
            "",
        ]

        if agent_contract:
            prompt_parts.extend([
                "# Agent Contract",
                agent_contract,
                "",
            ])

        prompt_parts.extend([
            "# Task",
            task,
            "",
            "Please execute this task following your agent definition and contract.",
        ])

        return "\n".join(prompt_parts)

    def run_agent(
        self,
        agent_name: str,
        task: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> AgentResult:
        """
        Run a single agent on a task.

        Args:
            agent_name: Name of agent to run (e.g., "code-reviewer")
            task: Task description or content to process
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation (0.0-1.0)

        Returns:
            AgentResult with output and metadata

        Example:
            result = orchestrator.run_agent(
                "code-reviewer",
                task="Review this code: def foo(): pass"
            )
            print(result.output)
        """
        try:
            # Load agent definition and contract
            agent_definition = self._load_agent_definition(agent_name)
            agent_contract = self._load_agent_contract(agent_name)

            # Build prompt
            prompt = self._build_prompt(agent_definition, agent_contract, task)

            # Call Claude API
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract text from response
            output = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    output += block.text

            return AgentResult(
                agent_name=agent_name,
                success=True,
                output=output,
                metadata={
                    "model": model,
                    "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            )

        except Exception as e:
            return AgentResult(
                agent_name=agent_name,
                success=False,
                output="",
                metadata={},
                errors=[str(e)]
            )

    def run_workflow(
        self,
        workflow_name: str,
        task: str,
        pass_output_to_next: bool = True
    ) -> List[AgentResult]:
        """
        Run a multi-agent workflow.

        Args:
            workflow_name: Name of workflow (e.g., "full-stack-feature")
            task: Initial task description
            pass_output_to_next: Whether to pass each agent's output to the next

        Returns:
            List of AgentResult objects, one per agent

        Example:
            results = orchestrator.run_workflow(
                "bug-fix",
                task="Investigate 500 error in /api/users endpoint"
            )
            for result in results:
                print(f"{result.agent_name}: {result.success}")
        """
        workflow = self.config['workflows'].get(workflow_name)
        if not workflow:
            raise ValueError(
                f"Workflow '{workflow_name}' not found. "
                f"Available workflows: {', '.join(self.config['workflows'].keys())}"
            )

        results = []
        current_task = task

        for i, agent_name in enumerate(workflow):
            print(f"Running agent {i+1}/{len(workflow)}: {agent_name}...")

            result = self.run_agent(agent_name, current_task)
            results.append(result)

            if not result.success:
                print(f"❌ Agent {agent_name} failed: {result.errors}")
                break

            print(f"✓ Agent {agent_name} completed")

            # Pass output to next agent
            if pass_output_to_next and result.success:
                current_task = f"""
# Previous Agent Output

Agent: {agent_name}

Output:
{result.output}

# Your Task

Continue from the previous agent's output. Original task: {task}
"""

        return results

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        agents = []
        for name, config in self.config['agents'].items():
            agents.append({
                "name": name,
                "file": config.get("file", ""),
                "domains": config.get("domains", []),
                "priority": config.get("priority", 3)
            })
        return sorted(agents, key=lambda x: x['priority'])

    def list_workflows(self) -> Dict[str, List[str]]:
        """List all available workflows"""
        return self.config.get('workflows', {})

    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed information about an agent"""
        if agent_name not in self.config['agents']:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent_config = self.config['agents'][agent_name]

        # Try to load agent definition to extract role
        try:
            definition = self._load_agent_definition(agent_name)
            # Extract first few lines as description
            lines = definition.split('\n')[:10]
            description = '\n'.join(lines)
        except:
            description = "No description available"

        return {
            "name": agent_name,
            "file": agent_config.get("file", ""),
            "contract": agent_config.get("contract", ""),
            "domains": agent_config.get("domains", []),
            "priority": agent_config.get("priority", 3),
            "description": description
        }
