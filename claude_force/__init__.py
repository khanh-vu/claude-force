"""
Claude-Force: Multi-Agent Orchestration System for Claude

A production-ready framework for orchestrating multiple specialized Claude agents
with formal contracts, governance, and quality gates.
"""

__version__ = "2.1.0"
__author__ = "Claude Force Team"
__license__ = "MIT"

from .orchestrator import AgentOrchestrator
from .cli import main as cli_main

__all__ = ["AgentOrchestrator", "cli_main"]
