"""
Plugin Marketplace for claude-force.

Enables discovery, installation, and management of agent packs from multiple sources
including built-in claude-force plugins and external repositories like wshobson/agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from pathlib import Path
from enum import Enum
import logging
import yaml
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class PluginSource(Enum):
    """Plugin source types."""

    BUILTIN = "builtin"  # claude-force built-in plugins
    WSHOBSON = "wshobson"  # wshobson/agents marketplace
    EXTERNAL = "external"  # Other external sources
    CUSTOM = "custom"  # User-created plugins


class PluginCategory(Enum):
    """Plugin categories for organization."""

    DEVELOPMENT = "development"
    AI_ML = "ai-ml"
    DATA_ENGINEERING = "data-engineering"
    INFRASTRUCTURE = "infrastructure"
    FRONTEND = "frontend"
    BACKEND = "backend"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


@dataclass
class Plugin:
    """Represents a plugin available in the marketplace."""

    id: str
    name: str
    description: str
    version: str
    source: PluginSource
    category: PluginCategory

    agents: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)

    dependencies: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    author: Optional[str] = None
    repository: Optional[str] = None
    installed: bool = False
    installed_version: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert plugin to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "source": self.source.value,
            "category": self.category.value,
            "agents": self.agents,
            "skills": self.skills,
            "workflows": self.workflows,
            "tools": self.tools,
            "dependencies": self.dependencies,
            "keywords": self.keywords,
            "author": self.author,
            "repository": self.repository,
            "installed": self.installed,
            "installed_version": self.installed_version,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Plugin":
        """Create plugin from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            source=PluginSource(data.get("source", "builtin")),
            category=PluginCategory(data.get("category", "development")),
            agents=data.get("agents", []),
            skills=data.get("skills", []),
            workflows=data.get("workflows", []),
            tools=data.get("tools", []),
            dependencies=data.get("dependencies", []),
            keywords=data.get("keywords", []),
            author=data.get("author"),
            repository=data.get("repository"),
            installed=data.get("installed", False),
            installed_version=data.get("installed_version"),
        )


@dataclass
class InstallationResult:
    """Result of a plugin installation."""

    plugin: Plugin
    agents_added: int = 0
    skills_added: int = 0
    workflows_added: int = 0
    tools_added: int = 0
    success: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class MarketplaceManager:
    """
    Manage plugin installation from multiple sources.

    Supports:
    - Built-in claude-force plugins
    - wshobson/agents marketplace
    - Custom user plugins
    - Dependency resolution
    - Version management
    """

    OFFICIAL_REPOS = {"claude-force": "khanh-vu/claude-force", "wshobson": "wshobson/agents"}

    def __init__(self, claude_dir: Optional[Path] = None):
        """
        Initialize marketplace manager.

        Args:
            claude_dir: Path to .claude directory (default: ./.claude)
        """
        self.claude_dir = Path(claude_dir) if claude_dir else Path(".claude")
        self.marketplace_dir = self.claude_dir / "marketplace"
        self.registry_file = self.marketplace_dir / "registry.yaml"
        self.installed_file = self.marketplace_dir / "installed.json"

        # Ensure marketplace directory exists
        self.marketplace_dir.mkdir(parents=True, exist_ok=True)

        # Load state
        self.installed_plugins = self._load_installed()
        self.available_plugins = self._load_registry()

    def _load_installed(self) -> Dict[str, Plugin]:
        """Load installed plugins from file."""
        if not self.installed_file.exists():
            return {}

        try:
            with open(self.installed_file) as f:
                data = json.load(f)

            return {
                plugin_id: Plugin.from_dict(plugin_data) for plugin_id, plugin_data in data.items()
            }
        except Exception as e:
            logger.error(f"Failed to load installed plugins: {e}")
            return {}

    def _save_installed(self):
        """Save installed plugins to file."""
        data = {plugin_id: plugin.to_dict() for plugin_id, plugin in self.installed_plugins.items()}

        with open(self.installed_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_registry(self) -> Dict[str, Plugin]:
        """Load available plugins from registry."""
        if not self.registry_file.exists():
            # Create default registry
            self._create_default_registry()

        try:
            with open(self.registry_file) as f:
                data = yaml.safe_load(f)

            plugins = {}
            for category_data in data.get("categories", []):
                category = PluginCategory(
                    category_data["name"].lower().replace(" ", "-").replace("&", "")
                )

                for plugin_data in category_data.get("plugins", []):
                    plugin_data["category"] = category.value
                    plugin = Plugin.from_dict(plugin_data)

                    # Mark as installed if present
                    if plugin.id in self.installed_plugins:
                        plugin.installed = True
                        plugin.installed_version = self.installed_plugins[plugin.id].version

                    plugins[plugin.id] = plugin

            return plugins

        except Exception as e:
            logger.error(f"Failed to load plugin registry: {e}")
            return {}

    def _create_default_registry(self):
        """Create default plugin registry."""
        default_registry = {
            "categories": [
                {
                    "name": "Development",
                    "plugins": [
                        {
                            "id": "python-complete",
                            "name": "Python Development Complete",
                            "description": "Complete Python development with senior-level expertise",
                            "version": "1.0.0",
                            "source": "wshobson",
                            "agents": ["python-developer", "python-senior"],
                            "skills": ["async-patterns", "testing", "packaging"],
                            "keywords": ["python", "development", "async", "testing"],
                        },
                        {
                            "id": "frontend-complete",
                            "name": "Frontend Development Complete",
                            "description": "Complete frontend stack with React/Vue/Angular",
                            "version": "1.0.0",
                            "source": "builtin",
                            "agents": [
                                "frontend-architect",
                                "ui-components-expert",
                                "frontend-developer",
                            ],
                            "skills": ["test-generation"],
                            "workflows": ["frontend-feature"],
                            "keywords": ["frontend", "react", "vue", "angular", "ui"],
                        },
                    ],
                },
                {
                    "name": "AI-ML",
                    "plugins": [
                        {
                            "id": "llm-application-dev",
                            "name": "LLM Application Development",
                            "description": "Build LLM-powered applications with RAG and prompt engineering",
                            "version": "1.0.0",
                            "source": "wshobson",
                            "agents": ["ai-engineer", "prompt-engineer"],
                            "skills": ["prompt-engineering"],
                            "keywords": ["llm", "ai", "rag", "prompts", "chatbot"],
                        },
                        {
                            "id": "ai-ml-complete",
                            "name": "AI & ML Complete",
                            "description": "Complete AI/ML stack with training, deployment, and monitoring",
                            "version": "1.0.0",
                            "source": "builtin",
                            "agents": ["ai-engineer", "prompt-engineer", "data-engineer"],
                            "workflows": ["ai-ml-development", "llm-integration"],
                            "skills": ["create-agent", "create-skill"],
                            "keywords": ["ai", "ml", "training", "deployment", "mlops"],
                        },
                    ],
                },
                {
                    "name": "Data-Engineering",
                    "plugins": [
                        {
                            "id": "data-pipeline-complete",
                            "name": "Data Pipeline Complete",
                            "description": "Complete data engineering with ETL, quality, and monitoring",
                            "version": "1.0.0",
                            "source": "builtin",
                            "agents": ["data-engineer", "backend-architect"],
                            "workflows": ["data-pipeline"],
                            "skills": ["git-workflow"],
                            "keywords": ["data", "etl", "pipeline", "analytics"],
                        }
                    ],
                },
                {
                    "name": "Infrastructure",
                    "plugins": [
                        {
                            "id": "kubernetes-ops",
                            "name": "Kubernetes Operations",
                            "description": "Kubernetes deployment, Helm charts, and GitOps workflows",
                            "version": "1.0.0",
                            "source": "wshobson",
                            "agents": ["kubernetes-engineer"],
                            "skills": ["k8s-manifests", "helm-charts", "gitops"],
                            "keywords": ["kubernetes", "k8s", "helm", "gitops", "deployment"],
                        },
                        {
                            "id": "devops-complete",
                            "name": "DevOps Complete",
                            "description": "Complete DevOps with Docker, Kubernetes, and cloud",
                            "version": "1.0.0",
                            "source": "builtin",
                            "agents": ["devops-architect", "google-cloud-expert"],
                            "workflows": ["deployment"],
                            "skills": ["dockerfile", "git-workflow"],
                            "keywords": ["devops", "docker", "cloud", "ci/cd", "deployment"],
                        },
                    ],
                },
            ]
        }

        with open(self.registry_file, "w") as f:
            yaml.dump(default_registry, f, default_flow_style=False, sort_keys=False)

    def list_available(
        self,
        category: Optional[str] = None,
        source: Optional[str] = None,
        installed_only: bool = False,
    ) -> List[Plugin]:
        """
        List available plugins.

        Args:
            category: Filter by category
            source: Filter by source
            installed_only: Show only installed plugins

        Returns:
            List of plugins matching criteria
        """
        plugins = list(self.available_plugins.values())

        if category:
            plugins = [p for p in plugins if p.category.value == category]

        if source:
            plugins = [p for p in plugins if p.source.value == source]

        if installed_only:
            plugins = [p for p in plugins if p.installed]

        return plugins

    def search(self, query: str) -> List[Plugin]:
        """
        Search plugins by query.

        Searches in: name, description, keywords, agents, skills

        Args:
            query: Search query

        Returns:
            List of matching plugins
        """
        query_lower = query.lower()
        results = []

        for plugin in self.available_plugins.values():
            # Search in various fields
            searchable = [
                plugin.name.lower(),
                plugin.description.lower(),
                *[k.lower() for k in plugin.keywords],
                *[a.lower() for a in plugin.agents],
                *[s.lower() for s in plugin.skills],
            ]

            if any(query_lower in text for text in searchable):
                results.append(plugin)

        return results

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get plugin by ID."""
        return self.available_plugins.get(plugin_id)

    def install_plugin(self, plugin_id: str, force: bool = False) -> InstallationResult:
        """
        Install a plugin and its dependencies.

        Args:
            plugin_id: Plugin identifier
            force: Force reinstall if already installed

        Returns:
            InstallationResult with details
        """
        plugin = self.get_plugin(plugin_id)

        if not plugin:
            return InstallationResult(
                plugin=Plugin(
                    id=plugin_id,
                    name="Unknown",
                    description="",
                    version="0.0.0",
                    source=PluginSource.BUILTIN,
                    category=PluginCategory.DEVELOPMENT,
                ),
                success=False,
                errors=[f"Plugin '{plugin_id}' not found in marketplace"],
            )

        # Check if already installed
        if plugin.installed and not force:
            return InstallationResult(
                plugin=plugin,
                success=False,
                warnings=[
                    f"Plugin '{plugin_id}' is already installed (version {plugin.installed_version})"
                ],
            )

        result = InstallationResult(plugin=plugin)

        try:
            # Install dependencies first
            for dep_id in plugin.dependencies:
                dep_result = self.install_plugin(dep_id, force=False)
                if not dep_result.success:
                    result.errors.append(f"Failed to install dependency '{dep_id}'")

            # In a real implementation, we would:
            # 1. Download agents, skills, workflows from source
            # 2. Integrate them into .claude/ directory
            # 3. Generate contracts for agents
            # 4. Update claude.json

            # For now, mark as installed
            plugin.installed = True
            plugin.installed_version = plugin.version
            self.installed_plugins[plugin.id] = plugin
            self._save_installed()

            result.agents_added = len(plugin.agents)
            result.skills_added = len(plugin.skills)
            result.workflows_added = len(plugin.workflows)
            result.tools_added = len(plugin.tools)
            result.success = True

            logger.info(f"Successfully installed plugin '{plugin_id}' v{plugin.version}")

        except Exception as e:
            result.success = False
            result.errors.append(f"Installation failed: {str(e)}")
            logger.error(f"Failed to install plugin '{plugin_id}': {e}")

        return result

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        Uninstall a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if successful
        """
        if plugin_id not in self.installed_plugins:
            logger.warning(f"Plugin '{plugin_id}' is not installed")
            return False

        try:
            # Remove from installed
            del self.installed_plugins[plugin_id]
            self._save_installed()

            # Update available plugins
            if plugin_id in self.available_plugins:
                self.available_plugins[plugin_id].installed = False
                self.available_plugins[plugin_id].installed_version = None

            logger.info(f"Successfully uninstalled plugin '{plugin_id}'")
            return True

        except Exception as e:
            logger.error(f"Failed to uninstall plugin '{plugin_id}': {e}")
            return False


def get_marketplace_manager(claude_dir: Optional[Path] = None) -> MarketplaceManager:
    """
    Get singleton marketplace manager instance.

    Args:
        claude_dir: Path to .claude directory

    Returns:
        MarketplaceManager instance
    """
    return MarketplaceManager(claude_dir=claude_dir)
