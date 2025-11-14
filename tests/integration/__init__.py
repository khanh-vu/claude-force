"""
Integration Tests for Claude-Force

This package contains comprehensive integration tests for the claude-force
multi-agent orchestration system.

Test Categories:
- test_orchestrator_end_to_end.py: Complete orchestrator workflows with mocked Claude API
- test_cli_commands.py: CLI command testing via subprocess
- test_workflow_marketplace.py: Workflow composition and marketplace operations

Coverage Target: 80% of critical integration paths

Run tests with:
    pytest tests/integration/ -v
    pytest tests/integration/ --cov=claude_force --cov-report=html
"""

__all__ = [
    "test_orchestrator_end_to_end",
    "test_cli_commands",
    "test_workflow_marketplace",
]
