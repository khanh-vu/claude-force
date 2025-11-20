"""
Shell subpackage for interactive REPL mode.

Components:
- executor: Command execution and routing
- completer: Tab completion
- config: Shell configuration
- formatter: Output formatting
"""

from .executor import CommandExecutor, ExecutionResult

__all__ = ["CommandExecutor", "ExecutionResult"]
