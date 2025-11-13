"""
Claude-Force: Multi-Agent Orchestration System for Claude

A production-ready framework for orchestrating multiple specialized Claude agents
with formal contracts, governance, and quality gates.
"""

__version__ = "2.1.0"
__author__ = "Claude Force Team"
__license__ = "MIT"

from .orchestrator import AgentOrchestrator, AgentResult
from .cli import main as cli_main

# Optional: Semantic agent selection (requires sentence-transformers)
try:
    from .semantic_selector import SemanticAgentSelector, AgentMatch
    __all__ = ["AgentOrchestrator", "AgentResult", "cli_main", "SemanticAgentSelector", "AgentMatch"]
except ImportError:
    # sentence-transformers not installed
    __all__ = ["AgentOrchestrator", "AgentResult", "cli_main"]
