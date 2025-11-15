"""
Abstract base classes and protocols for Claude Force.

This module defines the core abstractions that enable extensibility
and plugin architecture for Claude Force.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class AgentResult:
    """
    Result from an agent execution.

    Attributes:
        success: Whether the agent execution succeeded
        output: The agent's output text
        errors: List of error messages (empty if successful)
        metadata: Additional execution metadata (tokens, model, etc.)
        agent_name: Name of the agent that was executed
    """

    success: bool
    output: str
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    agent_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "errors": self.errors,
            "metadata": self.metadata,
            "agent_name": self.agent_name,
        }


@dataclass
class WorkflowResult:
    """
    Result from a workflow execution.

    Attributes:
        success: Whether all agents in the workflow succeeded
        agent_results: List of results from each agent
        metadata: Workflow-level metadata
        workflow_name: Name of the workflow that was executed
    """

    success: bool
    agent_results: List[AgentResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    workflow_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "agent_results": [r.to_dict() for r in self.agent_results],
            "metadata": self.metadata,
            "workflow_name": self.workflow_name,
        }


class BaseOrchestrator(ABC):
    """
    Abstract base class for orchestrators.

    All orchestrator implementations must inherit from this class
    and implement the required methods. This enables users to create
    custom orchestrators with their own logic while maintaining
    compatibility with the CLI and other tools.

    Example:
        >>> class MyOrchestrator(BaseOrchestrator):
        ...     def run_agent(self, agent_name, task, **kwargs):
        ...         # Custom implementation
        ...         return AgentResult(
        ...             success=True,
        ...             output="Custom result",
        ...             errors=[],
        ...             metadata={}
        ...         )
        ...
        ...     def run_workflow(self, workflow_name, task, **kwargs):
        ...         # Custom implementation
        ...         pass
        ...
        ...     def list_agents(self):
        ...         return {}
        ...
        ...     def list_workflows(self):
        ...         return {}
    """

    @abstractmethod
    def run_agent(self, agent_name: str, task: str, **kwargs) -> AgentResult:
        """
        Execute a single agent on a task.

        This method must be implemented by all concrete orchestrator classes.

        Args:
            agent_name: Name of the agent to execute
            task: Task description or prompt
            **kwargs: Additional parameters (model, max_tokens, etc.)

        Returns:
            AgentResult with execution outcome

        Raises:
            ValueError: If agent_name is invalid or not found
            RuntimeError: If execution fails
        """
        pass

    @abstractmethod
    def run_workflow(self, workflow_name: str, task: str, **kwargs) -> List[AgentResult]:
        """
        Execute a multi-agent workflow.

        This method must be implemented by all concrete orchestrator classes.

        Args:
            workflow_name: Name of the workflow to execute
            task: Task description or prompt
            **kwargs: Additional parameters

        Returns:
            List of AgentResult objects, one per agent in the workflow

        Raises:
            ValueError: If workflow_name is invalid or not found
            RuntimeError: If workflow execution fails
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all available agents.

        Returns:
            List of agent dictionaries with name, priority, domains, etc.
        """
        pass

    @abstractmethod
    def list_workflows(self) -> Dict[str, List[str]]:
        """
        List all available workflows.

        Returns:
            Dictionary mapping workflow names to lists of agent names
        """
        pass


class CacheProtocol(Protocol):
    """
    Protocol for cache implementations.

    Any cache implementation that satisfies this protocol can be used
    with Claude Force. This enables custom caching backends (Redis,
    Memcached, etc.) without modifying the core code.

    Example:
        >>> class RedisCache:
        ...     def get(self, key: str) -> Optional[str]:
        ...         return redis_client.get(key)
        ...
        ...     def set(self, key: str, value: str, ttl: int = 86400):
        ...         redis_client.setex(key, ttl, value)
        ...
        ...     # ... implement other methods
    """

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        ...

    def set(self, key: str, value: str, ttl: int = 86400) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to store (should be string/serialized)
            ttl: Time-to-live in seconds (default: 24 hours)
        """
        ...

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted, False if not found
        """
        ...

    def clear(self) -> None:
        """Clear all cache entries."""
        ...

    def size(self) -> int:
        """
        Get number of entries in cache.

        Returns:
            Number of cached entries
        """
        ...


class TrackerProtocol(Protocol):
    """
    Protocol for performance tracker implementations.

    Any tracker implementation that satisfies this protocol can be used
    with Claude Force. This enables custom tracking backends (Prometheus,
    DataDog, etc.) without modifying the core code.

    Example:
        >>> class PrometheusTracker:
        ...     def record_execution(self, agent_name, task, success, ...):
        ...         prometheus_counter.inc()
        ...         # ... record metrics
        ...
        ...     def get_summary(self):
        ...         return prometheus_client.get_metrics()
    """

    def record_execution(
        self,
        agent_name: str,
        task: str,
        success: bool,
        duration_ms: float,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """
        Record a single agent execution.

        Args:
            agent_name: Name of the agent
            task: Task that was executed
            success: Whether execution succeeded
            duration_ms: Execution duration in milliseconds
            model: Claude model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        """
        ...

    def get_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get performance summary.

        Args:
            hours: Only include metrics from last N hours (None = all time)

        Returns:
            Dictionary with summary statistics
        """
        ...

    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get per-agent statistics.

        Returns:
            Dictionary mapping agent names to their statistics
        """
        ...

    def export_json(self, output_path: str) -> None:
        """
        Export metrics to JSON file.

        Args:
            output_path: Path to write JSON file
        """
        ...

    def export_csv(self, output_path: str) -> None:
        """
        Export metrics to CSV file.

        Args:
            output_path: Path to write CSV file
        """
        ...
