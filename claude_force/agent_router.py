"""
Intelligent Agent Routing for claude-force.

Provides semantic agent selection with marketplace integration,
enabling intelligent recommendations across builtin and external agents.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentMatch:
    """Agent match result with confidence score."""

    agent_id: str
    agent_name: str
    confidence: float
    source: str  # "builtin" or "marketplace"
    installed: bool
    plugin_id: Optional[str] = None
    description: str = ""
    expertise: List[str] = None
    reason: str = ""

    def __post_init__(self):
        if self.expertise is None:
            self.expertise = []


class AgentRouter:
    """
    Intelligent agent routing with semantic selection.

    Features:
    - Semantic matching across builtin and marketplace agents
    - Task complexity analysis
    - Confidence scoring
    - Installation recommendations
    - Multi-source agent discovery
    """

    # Agent expertise mappings for builtin agents
    AGENT_EXPERTISE = {
        "frontend-architect": {
            "keywords": ["react", "vue", "angular", "ui", "frontend", "components", "state management"],
            "description": "Frontend architecture and UI design"
        },
        "backend-architect": {
            "keywords": ["api", "backend", "server", "microservices", "architecture", "scalability"],
            "description": "Backend architecture and API design"
        },
        "database-architect": {
            "keywords": ["database", "sql", "nosql", "schema", "migration", "postgres", "mongodb"],
            "description": "Database design and optimization"
        },
        "ai-engineer": {
            "keywords": ["ai", "ml", "machine learning", "model", "training", "tensorflow", "pytorch"],
            "description": "AI/ML model development"
        },
        "prompt-engineer": {
            "keywords": ["llm", "prompt", "chatbot", "gpt", "claude", "openai", "rag"],
            "description": "LLM prompt engineering and optimization"
        },
        "data-engineer": {
            "keywords": ["etl", "pipeline", "data", "airflow", "spark", "analytics"],
            "description": "Data engineering and ETL pipelines"
        },
        "code-reviewer": {
            "keywords": ["review", "code quality", "refactor", "best practices", "security"],
            "description": "Code review and quality assurance"
        },
        "security-specialist": {
            "keywords": ["security", "vulnerability", "owasp", "authentication", "encryption"],
            "description": "Security auditing and best practices"
        },
        "devops-architect": {
            "keywords": ["docker", "kubernetes", "ci/cd", "deployment", "infrastructure"],
            "description": "DevOps and infrastructure"
        },
        "google-cloud-expert": {
            "keywords": ["gcp", "google cloud", "cloud", "gke", "bigquery"],
            "description": "Google Cloud Platform expertise"
        },
        "bug-investigator": {
            "keywords": ["debug", "bug", "error", "troubleshoot", "fix"],
            "description": "Bug investigation and debugging"
        },
        "python-expert": {
            "keywords": ["python", "async", "packages", "pip", "pytest"],
            "description": "Python development expertise"
        }
    }

    def __init__(self, include_marketplace: bool = True):
        """
        Initialize agent router.

        Args:
            include_marketplace: Include marketplace agents in recommendations
        """
        self.include_marketplace = include_marketplace
        self._marketplace = None
        self._builtin_agents = self._load_builtin_agents()

    def _load_builtin_agents(self) -> Dict[str, Dict]:
        """Load builtin agent information."""
        return self.AGENT_EXPERTISE

    @property
    def marketplace(self):
        """Lazy load marketplace manager."""
        if self._marketplace is None and self.include_marketplace:
            try:
                from .marketplace import get_marketplace_manager
                self._marketplace = get_marketplace_manager()
            except Exception as e:
                logger.warning(f"Failed to load marketplace: {e}")
                self._marketplace = None
        return self._marketplace

    def recommend_agents(
        self,
        task: str,
        top_k: int = 5,
        include_marketplace: bool = None,
        min_confidence: float = 0.0
    ) -> List[AgentMatch]:
        """
        Recommend agents for a task using semantic matching.

        Args:
            task: Task description
            top_k: Number of recommendations to return
            include_marketplace: Override instance setting
            min_confidence: Minimum confidence threshold

        Returns:
            List of agent matches sorted by confidence
        """
        if include_marketplace is None:
            include_marketplace = self.include_marketplace

        matches = []

        # Get builtin agent matches
        builtin_matches = self._match_builtin_agents(task)
        matches.extend(builtin_matches)

        # Get marketplace agent matches
        if include_marketplace and self.marketplace:
            marketplace_matches = self._match_marketplace_agents(task)
            matches.extend(marketplace_matches)

        # Filter by confidence
        matches = [m for m in matches if m.confidence >= min_confidence]

        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)

        return matches[:top_k]

    def _match_builtin_agents(self, task: str) -> List[AgentMatch]:
        """Match task against builtin agents."""
        if not task:
            return []
        task_lower = task.lower()
        matches = []

        for agent_id, agent_info in self._builtin_agents.items():
            # Calculate confidence based on keyword matching
            confidence = self._calculate_confidence(
                task_lower,
                agent_info["keywords"]
            )

            if confidence > 0:
                # Determine reason based on matched keywords
                matched_keywords = [
                    kw for kw in agent_info["keywords"]
                    if kw in task_lower
                ]
                reason = f"Matches keywords: {', '.join(matched_keywords[:3])}"

                matches.append(AgentMatch(
                    agent_id=agent_id,
                    agent_name=agent_id,
                    confidence=confidence,
                    source="builtin",
                    installed=True,
                    description=agent_info["description"],
                    expertise=agent_info["keywords"],
                    reason=reason
                ))

        return matches

    def _match_marketplace_agents(self, task: str) -> List[AgentMatch]:
        """Match task against marketplace agents."""
        if not self.marketplace:
            return []
        if not task:
            return []

        task_lower = task.lower()
        matches = []

        # Search marketplace plugins
        for plugin in self.marketplace.available_plugins.values():
            # Match against plugin metadata
            confidence = self._calculate_plugin_confidence(task_lower, plugin)

            if confidence > 0:
                # Determine primary agent from plugin
                primary_agent = plugin.agents[0] if plugin.agents else plugin.id

                reason = f"From {plugin.source.value} marketplace"
                if plugin.installed:
                    reason += " (already installed)"

                matches.append(AgentMatch(
                    agent_id=primary_agent,
                    agent_name=plugin.name,
                    confidence=confidence,
                    source="marketplace",
                    installed=plugin.installed,
                    plugin_id=plugin.id,
                    description=plugin.description,
                    expertise=plugin.keywords,
                    reason=reason
                ))

        return matches

    def _calculate_confidence(
        self,
        task: str,
        keywords: List[str]
    ) -> float:
        """
        Calculate confidence score based on keyword matching.

        Returns score between 0.0 and 1.0
        """
        if not keywords:
            return 0.0

        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in task)

        if matches == 0:
            return 0.0

        # Base confidence on match ratio
        base_confidence = matches / len(keywords)

        # Boost for multiple matches
        if matches >= 3:
            base_confidence = min(base_confidence + 0.2, 1.0)
        elif matches >= 2:
            base_confidence = min(base_confidence + 0.1, 1.0)

        # Ensure minimum confidence for any match
        return max(base_confidence, 0.3)

    def _calculate_plugin_confidence(self, task: str, plugin) -> float:
        """Calculate confidence score for marketplace plugin."""
        # Search in keywords, description, agents
        searchable = [
            *[k.lower() for k in plugin.keywords],
            plugin.description.lower(),
            *[a.lower() for a in plugin.agents]
        ]

        matches = sum(1 for text in searchable if any(word in text for word in task.split()))

        if matches == 0:
            return 0.0

        # Base confidence
        base_confidence = min(matches * 0.2, 0.9)

        # Boost for installed plugins
        if plugin.installed:
            base_confidence = min(base_confidence + 0.1, 1.0)

        return base_confidence

    def analyze_task_complexity(self, task: str) -> Dict[str, any]:
        """
        Analyze task to determine complexity and requirements.

        Returns dict with:
        - complexity: simple | medium | complex
        - estimated_agents: number of agents likely needed
        - categories: list of relevant categories
        - recommendations: list of agent recommendations
        """
        task_lower = task.lower()

        # Complexity indicators
        simple_keywords = ["fix", "update", "add", "remove", "change"]
        complex_keywords = ["implement", "design", "architect", "build", "create system"]
        critical_keywords = ["production", "migrate", "refactor entire", "rebuild"]

        # Count indicators
        simple_count = sum(1 for kw in simple_keywords if kw in task_lower)
        complex_count = sum(1 for kw in complex_keywords if kw in task_lower)
        critical_count = sum(1 for kw in critical_keywords if kw in task_lower)

        # Determine complexity
        if critical_count > 0 or len(task.split()) > 30:
            complexity = "complex"
            estimated_agents = 3
        elif complex_count > 0 or len(task.split()) > 15:
            complexity = "medium"
            estimated_agents = 2
        else:
            complexity = "simple"
            estimated_agents = 1

        # Identify categories
        categories = []
        if any(kw in task_lower for kw in ["frontend", "ui", "react", "vue"]):
            categories.append("frontend")
        if any(kw in task_lower for kw in ["backend", "api", "server"]):
            categories.append("backend")
        if any(kw in task_lower for kw in ["database", "sql", "schema"]):
            categories.append("database")
        if any(kw in task_lower for kw in ["ai", "ml", "model", "llm"]):
            categories.append("ai")
        if any(kw in task_lower for kw in ["devops", "docker", "kubernetes"]):
            categories.append("devops")

        # Get recommendations
        recommendations = self.recommend_agents(task, top_k=estimated_agents)

        return {
            "complexity": complexity,
            "estimated_agents": estimated_agents,
            "categories": categories,
            "recommendations": recommendations,
            "task_length": len(task.split()),
            "requires_multiple_agents": estimated_agents > 1
        }

    def get_installation_plan(
        self,
        agent_matches: List[AgentMatch]
    ) -> Dict[str, any]:
        """
        Create installation plan for marketplace agents.

        Args:
            agent_matches: List of agent matches

        Returns:
            Dict with installation plan
        """
        to_install = []
        already_installed = []
        builtin = []

        for match in agent_matches:
            if match.source == "builtin":
                builtin.append(match)
            elif match.installed:
                already_installed.append(match)
            else:
                to_install.append(match)

        return {
            "to_install": to_install,
            "already_installed": already_installed,
            "builtin": builtin,
            "total_agents": len(agent_matches),
            "requires_installation": len(to_install) > 0,
            "ready_to_use": len(builtin) + len(already_installed)
        }


def get_agent_router(include_marketplace: bool = True) -> AgentRouter:
    """
    Get agent router instance.

    Args:
        include_marketplace: Include marketplace in recommendations

    Returns:
        AgentRouter instance
    """
    return AgentRouter(include_marketplace=include_marketplace)
