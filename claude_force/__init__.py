"""
Claude-Force: Multi-Agent Orchestration System for Claude

A production-ready framework for orchestrating multiple specialized Claude agents
with formal contracts, governance, and quality gates.

P1 Enhancements:
- Semantic agent selection with embeddings
- Performance tracking and analytics
- GitHub Actions integration
- REST API server
"""

__version__ = "1.1.0"
__author__ = "Claude Force Team"
__license__ = "MIT"

# Core imports - always needed
from .orchestrator import AgentOrchestrator, AgentResult

# All available exports
__all__ = [
    "AgentOrchestrator",
    "AgentResult",
    "cli_main",
    "SemanticAgentSelector",
    "AgentMatch",
    "MCPServer",
    "MCPCapability",
    "MCPRequest",
    "MCPResponse",
    "QuickStartOrchestrator",
    "ProjectTemplate",
    "ProjectConfig",
    "get_quick_start_orchestrator",
    "HybridOrchestrator",
    "ModelPricing",
    "CostEstimate",
    "get_hybrid_orchestrator",
    "ProgressiveSkillsManager",
    "get_skills_manager",
]

# Lazy imports for non-core functionality
_LAZY_IMPORTS = {
    "cli_main": ("cli", "main"),
    "MCPServer": ("mcp_server", "MCPServer"),
    "MCPCapability": ("mcp_server", "MCPCapability"),
    "MCPRequest": ("mcp_server", "MCPRequest"),
    "MCPResponse": ("mcp_server", "MCPResponse"),
    "QuickStartOrchestrator": ("quick_start", "QuickStartOrchestrator"),
    "ProjectTemplate": ("quick_start", "ProjectTemplate"),
    "ProjectConfig": ("quick_start", "ProjectConfig"),
    "get_quick_start_orchestrator": ("quick_start", "get_quick_start_orchestrator"),
    "HybridOrchestrator": ("hybrid_orchestrator", "HybridOrchestrator"),
    "ModelPricing": ("hybrid_orchestrator", "ModelPricing"),
    "CostEstimate": ("hybrid_orchestrator", "CostEstimate"),
    "get_hybrid_orchestrator": ("hybrid_orchestrator", "get_hybrid_orchestrator"),
    "ProgressiveSkillsManager": ("skills_manager", "ProgressiveSkillsManager"),
    "get_skills_manager": ("skills_manager", "get_skills_manager"),
    "SemanticAgentSelector": ("semantic_selector", "SemanticAgentSelector"),
    "AgentMatch": ("semantic_selector", "AgentMatch"),
}


def __getattr__(name):
    """Lazy import handler for non-core functionality."""
    if name in _LAZY_IMPORTS:
        module_name, attr_name = _LAZY_IMPORTS[name]
        try:
            from importlib import import_module

            module = import_module(f".{module_name}", package="claude_force")
            attr = getattr(module, attr_name)
            # Cache the imported attribute
            globals()[name] = attr
            return attr
        except ImportError:
            # Handle optional dependencies gracefully
            if module_name == "semantic_selector":
                raise ImportError(
                    f"'{name}' requires sentence-transformers. "
                    "Install with: pip install sentence-transformers"
                )
            raise
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
