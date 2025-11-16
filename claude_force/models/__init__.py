"""
Data models for TÂCHES integration.

This module contains data models for workflow management features:
- TodoItem: Task capture and management
- Handoff: Session continuity and context preservation
- MetaPrompt: Meta-prompting requests and responses
"""

from .todo import TodoItem, Priority, Complexity, TodoStatus
from .handoff import (
    Handoff,
    SessionSummary,
    WorkflowProgress,
    WorkCompleted,
    WorkRemaining,
    ActiveContext,
    GovernanceStatus,
    PerformanceMetrics,
    ConfidenceLevel,
)
from .meta_prompt import (
    MetaPromptRequest,
    MetaPromptResponse,
    MetaPromptConstraints,
    MetaPromptContext,
    ProposedApproach,
    GovernanceCompliance,
    RefinementIteration,
)

__all__ = [
    # Todo models
    "TodoItem",
    "Priority",
    "Complexity",
    "TodoStatus",
    # Handoff models
    "Handoff",
    "SessionSummary",
    "WorkflowProgress",
    "WorkCompleted",
    "WorkRemaining",
    "ActiveContext",
    "GovernanceStatus",
    "PerformanceMetrics",
    "ConfidenceLevel",
    # Meta-prompt models
    "MetaPromptRequest",
    "MetaPromptResponse",
    "MetaPromptConstraints",
    "MetaPromptContext",
    "ProposedApproach",
    "GovernanceCompliance",
    "RefinementIteration",
]
