"""
Service layer for TÂCHES integration.

This module provides business logic services for workflow management:
- TodoManager: Todo CRUD operations with AI recommendations
- HandoffGenerator: Session handoff generation
- MetaPrompter: Meta-prompting with governance validation
"""

from .todo_manager import TodoManager
from .handoff_generator import HandoffGenerator
from .meta_prompter import MetaPrompter

__all__ = [
    "TodoManager",
    "HandoffGenerator",
    "MetaPrompter",
]
