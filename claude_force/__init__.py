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

__version__ = "2.1.0-p1"
__author__ = "Claude Force Team"
__license__ = "MIT"

from .orchestrator import AgentOrchestrator, AgentResult
from .cli import main as cli_main
from .mcp_server import MCPServer, MCPCapability, MCPRequest, MCPResponse
from .quick_start import (
    QuickStartOrchestrator,
    ProjectTemplate,
    ProjectConfig,
    get_quick_start_orchestrator
)
from .hybrid_orchestrator import (
    HybridOrchestrator,
    ModelPricing,
    CostEstimate,
    get_hybrid_orchestrator
)
from .skills_manager import (
    ProgressiveSkillsManager,
    get_skills_manager
)

# Optional: Semantic agent selection (requires sentence-transformers)
try:
    from .semantic_selector import SemanticAgentSelector, AgentMatch
    __all__ = [
        "AgentOrchestrator", "AgentResult", "cli_main",
        "SemanticAgentSelector", "AgentMatch",
        "MCPServer", "MCPCapability", "MCPRequest", "MCPResponse",
        "QuickStartOrchestrator", "ProjectTemplate", "ProjectConfig",
        "get_quick_start_orchestrator",
        "HybridOrchestrator", "ModelPricing", "CostEstimate",
        "get_hybrid_orchestrator",
        "ProgressiveSkillsManager", "get_skills_manager"
    ]
except ImportError:
    # sentence-transformers not installed
    __all__ = [
        "AgentOrchestrator", "AgentResult", "cli_main",
        "MCPServer", "MCPCapability", "MCPRequest", "MCPResponse",
        "QuickStartOrchestrator", "ProjectTemplate", "ProjectConfig",
        "get_quick_start_orchestrator",
        "HybridOrchestrator", "ModelPricing", "CostEstimate",
        "get_hybrid_orchestrator",
        "ProgressiveSkillsManager", "get_skills_manager"
    ]
