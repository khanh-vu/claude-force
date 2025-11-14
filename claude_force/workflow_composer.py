"""
Smart Workflow Composer for claude-force.

Intelligently composes workflows from high-level goals by selecting optimal
agents from both builtin and marketplace sources with cost/duration estimation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
import logging

from claude_force.agent_router import get_agent_router, AgentMatch

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single step in a workflow."""

    step_number: int
    step_type: str  # e.g., "design", "implementation", "testing", "deployment"
    agent: AgentMatch
    description: str
    estimated_duration_min: int = 15
    estimated_cost: float = 0.50


@dataclass
class ComposedWorkflow:
    """Complete workflow composition."""

    name: str
    description: str
    goal: str
    steps: List[WorkflowStep]
    total_estimated_duration_min: int
    total_estimated_cost: float
    agents_count: int
    builtin_count: int
    marketplace_count: int
    requires_installation: bool
    installation_needed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "goal": self.goal,
            "steps": [
                {
                    "step_number": step.step_number,
                    "step_type": step.step_type,
                    "agent_id": step.agent.agent_id,
                    "agent_name": step.agent.agent_name,
                    "description": step.description,
                    "estimated_duration_min": step.estimated_duration_min,
                    "estimated_cost": step.estimated_cost
                }
                for step in self.steps
            ],
            "total_estimated_duration_min": self.total_estimated_duration_min,
            "total_estimated_cost": self.total_estimated_cost,
            "agents_count": self.agents_count,
            "builtin_count": self.builtin_count,
            "marketplace_count": self.marketplace_count,
            "requires_installation": self.requires_installation,
            "installation_needed": self.installation_needed
        }


class WorkflowComposer:
    """
    Intelligent workflow creation using agents from multiple sources.

    Features:
    - Goal analysis and decomposition
    - Agent selection from builtin + marketplace
    - Cost and duration estimation
    - Installation guidance for marketplace agents
    - Workflow sequence validation
    """

    # Step types and their characteristics
    STEP_TYPES = {
        "architecture": {
            "keywords": ["design", "architecture", "structure", "plan"],
            "duration_min": 20,
            "cost": 0.75
        },
        "implementation": {
            "keywords": ["implement", "build", "create", "develop", "code"],
            "duration_min": 30,
            "cost": 1.00
        },
        "database": {
            "keywords": ["database", "schema", "sql", "data model"],
            "duration_min": 25,
            "cost": 0.80
        },
        "testing": {
            "keywords": ["test", "qa", "quality", "validation"],
            "duration_min": 20,
            "cost": 0.60
        },
        "security": {
            "keywords": ["security", "auth", "vulnerability", "encryption"],
            "duration_min": 25,
            "cost": 0.85
        },
        "deployment": {
            "keywords": ["deploy", "production", "release", "ci/cd", "docker", "kubernetes"],
            "duration_min": 20,
            "cost": 0.70
        },
        "documentation": {
            "keywords": ["document", "docs", "readme", "api docs"],
            "duration_min": 15,
            "cost": 0.40
        },
        "monitoring": {
            "keywords": ["monitor", "observability", "logging", "metrics"],
            "duration_min": 20,
            "cost": 0.65
        }
    }

    def __init__(self, include_marketplace: bool = True):
        """
        Initialize workflow composer.

        Args:
            include_marketplace: Include marketplace agents in composition
        """
        self.include_marketplace = include_marketplace
        self.router = get_agent_router(include_marketplace=include_marketplace)

    def compose_workflow(
        self,
        goal: str,
        max_agents: int = 10,
        prefer_builtin: bool = False
    ) -> ComposedWorkflow:
        """
        Compose optimal workflow for a goal.

        Args:
            goal: High-level goal description
            max_agents: Maximum number of agents in workflow
            prefer_builtin: Prefer builtin agents over marketplace

        Returns:
            ComposedWorkflow with selected agents and steps
        """
        logger.info(f"Composing workflow for goal: {goal}")

        # Step 1: Analyze goal to identify required steps
        required_steps = self._analyze_goal(goal)

        # Step 2: Select best agent for each step
        workflow_steps = []
        for i, (step_type, step_description) in enumerate(required_steps, 1):
            agent = self._select_agent_for_step(
                step_type,
                step_description,
                goal,
                prefer_builtin
            )

            if agent:
                # Get step characteristics
                step_info = self.STEP_TYPES.get(step_type, {
                    "duration_min": 20,
                    "cost": 0.60
                })

                workflow_steps.append(WorkflowStep(
                    step_number=i,
                    step_type=step_type,
                    agent=agent,
                    description=step_description,
                    estimated_duration_min=step_info["duration_min"],
                    estimated_cost=step_info["cost"]
                ))

            if len(workflow_steps) >= max_agents:
                break

        # Step 3: Calculate totals and metadata
        total_duration = sum(step.estimated_duration_min for step in workflow_steps)
        total_cost = sum(step.estimated_cost for step in workflow_steps)

        builtin_count = sum(1 for step in workflow_steps if step.agent.source == "builtin")
        marketplace_count = sum(1 for step in workflow_steps if step.agent.source == "marketplace")

        installation_needed = [
            step.agent.plugin_id
            for step in workflow_steps
            if step.agent.source == "marketplace" and not step.agent.installed
        ]

        # Generate workflow name
        workflow_name = self._generate_workflow_name(goal)

        # Create composed workflow
        workflow = ComposedWorkflow(
            name=workflow_name,
            description=f"Custom workflow for: {goal}",
            goal=goal,
            steps=workflow_steps,
            total_estimated_duration_min=total_duration,
            total_estimated_cost=total_cost,
            agents_count=len(workflow_steps),
            builtin_count=builtin_count,
            marketplace_count=marketplace_count,
            requires_installation=len(installation_needed) > 0,
            installation_needed=installation_needed
        )

        logger.info(f"Composed workflow '{workflow_name}' with {len(workflow_steps)} steps")

        return workflow

    def _analyze_goal(self, goal: str) -> List[Tuple[str, str]]:
        """
        Analyze goal to identify required workflow steps.

        Args:
            goal: Goal description

        Returns:
            List of (step_type, step_description) tuples
        """
        goal_lower = goal.lower()
        required_steps = []

        # Check for each step type
        for step_type, info in self.STEP_TYPES.items():
            keywords = info["keywords"]
            if any(keyword in goal_lower for keyword in keywords):
                # Generate step description
                description = self._generate_step_description(step_type, goal)
                required_steps.append((step_type, description))

        # If no specific steps identified, use general implementation flow
        if not required_steps:
            required_steps = [
                ("architecture", "Design system architecture"),
                ("implementation", "Implement core functionality"),
                ("testing", "Test implementation")
            ]

        # Sort by typical workflow order
        step_order = {
            "architecture": 1,
            "database": 2,
            "implementation": 3,
            "testing": 4,
            "security": 5,
            "deployment": 6,
            "monitoring": 7,
            "documentation": 8
        }

        required_steps.sort(key=lambda x: step_order.get(x[0], 99))

        return required_steps

    def _generate_step_description(self, step_type: str, goal: str) -> str:
        """Generate description for a workflow step."""
        descriptions = {
            "architecture": "Design system architecture and components",
            "implementation": "Implement core functionality and features",
            "database": "Design database schema and data models",
            "testing": "Write and run comprehensive tests",
            "security": "Security review and hardening",
            "deployment": "Deploy to production environment",
            "documentation": "Create technical documentation",
            "monitoring": "Set up monitoring and observability"
        }

        base_description = descriptions.get(step_type, f"{step_type.title()} phase")

        # Extract key terms from goal
        goal_terms = self._extract_key_terms(goal)
        if goal_terms:
            base_description += f" for {goal_terms[0]}"

        return base_description

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key technical terms from text."""
        # Common technical terms to look for
        technical_terms = [
            "ml model", "machine learning", "api", "microservices", "frontend",
            "backend", "database", "kubernetes", "docker", "react", "python",
            "authentication", "chatbot", "rag", "deployment", "monitoring"
        ]

        found_terms = []
        text_lower = text.lower()

        for term in technical_terms:
            if term in text_lower:
                found_terms.append(term)

        return found_terms

    def _select_agent_for_step(
        self,
        step_type: str,
        step_description: str,
        goal: str,
        prefer_builtin: bool
    ) -> Optional[AgentMatch]:
        """
        Select best agent for a workflow step.

        Args:
            step_type: Type of step
            step_description: Step description
            goal: Overall goal
            prefer_builtin: Prefer builtin agents

        Returns:
            AgentMatch or None
        """
        # Build search query combining step type and description
        search_query = f"{step_type} {step_description} {goal}"

        # Get agent recommendations
        matches = self.router.recommend_agents(
            task=search_query,
            top_k=5,
            min_confidence=0.3
        )

        if not matches:
            return None

        # If prefer_builtin, filter builtin first
        if prefer_builtin:
            builtin_matches = [m for m in matches if m.source == "builtin"]
            if builtin_matches:
                return builtin_matches[0]

        # Return top match (highest confidence)
        return matches[0]

    def _generate_workflow_name(self, goal: str) -> str:
        """Generate workflow name from goal."""
        # Slugify goal
        name = goal.lower()
        # Remove special characters
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces with hyphens
        name = re.sub(r'[\s_]+', '-', name)
        # Limit length
        name = name[:50]
        # Remove trailing hyphens
        name = name.strip('-')

        return f"custom-{name}"

    def save_workflow(
        self,
        workflow: ComposedWorkflow,
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Save workflow to file.

        Args:
            workflow: Workflow to save
            output_dir: Output directory (default: .claude/workflows)

        Returns:
            Path to saved workflow file
        """
        import json

        if output_dir is None:
            output_dir = Path(".claude/workflows")

        output_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = output_dir / f"{workflow.name}.json"

        with open(workflow_file, 'w') as f:
            json.dump(workflow.to_dict(), f, indent=2)

        logger.info(f"Saved workflow to {workflow_file}")

        return workflow_file

    def estimate_workflow_cost(
        self,
        workflow: ComposedWorkflow,
        runs_per_month: int = 1
    ) -> Dict[str, float]:
        """
        Estimate monthly cost for workflow.

        Args:
            workflow: Workflow to estimate
            runs_per_month: Expected runs per month

        Returns:
            Cost breakdown dictionary
        """
        cost_per_run = workflow.total_estimated_cost
        monthly_cost = cost_per_run * runs_per_month

        return {
            "cost_per_run": cost_per_run,
            "runs_per_month": runs_per_month,
            "monthly_cost": monthly_cost,
            "annual_cost": monthly_cost * 12
        }


def get_workflow_composer(include_marketplace: bool = True) -> WorkflowComposer:
    """
    Get singleton workflow composer instance.

    Args:
        include_marketplace: Include marketplace agents

    Returns:
        WorkflowComposer instance
    """
    return WorkflowComposer(include_marketplace=include_marketplace)
