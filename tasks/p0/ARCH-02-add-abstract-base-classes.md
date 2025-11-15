# ARCH-02: Add Abstract Base Classes

**Priority**: P0 - Critical
**Estimated Effort**: 4-6 hours
**Impact**: HIGH - Enables extensibility and plugin architecture
**Category**: Architecture

---

## Problem Statement

Current implementation lacks abstract base classes, making it:
- Hard to create custom orchestrator implementations
- Difficult to extend with plugins
- No clear protocol definitions for cache/tracker interfaces
- Tight coupling to concrete implementations

**Files Affected**:
- `claude_force/orchestrator.py`
- `claude_force/response_cache.py`
- `claude_force/performance_tracker.py`

---

## Solution

Create abstract base classes and protocols to enable extensibility.

---

## Implementation Steps

### Step 1: Create Base Module (1 hour)

```python
# claude_force/base.py
"""Abstract base classes and protocols for Claude Force."""

from abc import ABC, abstractmethod
from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class AgentResult:
    """Result from an agent execution."""
    success: bool
    output: str
    errors: List[str]
    metadata: Dict[str, Any]


@dataclass
class WorkflowResult:
    """Result from a workflow execution."""
    success: bool
    agent_results: List[AgentResult]
    metadata: Dict[str, Any]


class BaseOrchestrator(ABC):
    """
    Abstract base class for orchestrators.

    All orchestrator implementations must inherit from this class
    and implement the required methods.

    Example:
        >>> class MyOrchestrator(BaseOrchestrator):
        ...     def run_agent(self, agent_name, task):
        ...         # Custom implementation
        ...         pass
    """

    @abstractmethod
    def run_agent(
        self,
        agent_name: str,
        task: str,
        **kwargs
    ) -> AgentResult:
        """
        Execute a single agent on a task.

        Args:
            agent_name: Name of the agent to execute
            task: Task description
            **kwargs: Additional parameters

        Returns:
            AgentResult with execution outcome

        Raises:
            ValueError: If agent_name is invalid
            RuntimeError: If execution fails
        """
        pass

    @abstractmethod
    def run_workflow(
        self,
        workflow_name: str,
        task: str,
        **kwargs
    ) -> WorkflowResult:
        """
        Execute a multi-agent workflow.

        Args:
            workflow_name: Name of the workflow
            task: Task description
            **kwargs: Additional parameters

        Returns:
            WorkflowResult with all agent results

        Raises:
            ValueError: If workflow_name is invalid
            RuntimeError: If workflow fails
        """
        pass

    @abstractmethod
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all available agents."""
        pass

    @abstractmethod
    def list_workflows(self) -> Dict[str, List[str]]:
        """List all available workflows."""
        pass


class CacheProtocol(Protocol):
    """
    Protocol for cache implementations.

    Any cache implementation must provide these methods.
    """

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    def set(
        self,
        key: str,
        value: str,
        ttl: int = 86400
    ) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds
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
        """Get number of entries in cache."""
        ...


class TrackerProtocol(Protocol):
    """Protocol for performance tracker implementations."""

    def record_metric(
        self,
        agent_name: str,
        duration_ms: float,
        tokens_used: int,
        cost: float,
        success: bool
    ) -> None:
        """Record a performance metric."""
        ...

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        ...

    def export(self, filepath: str, format: str = "json") -> None:
        """Export metrics to file."""
        ...
```

### Step 2: Update AgentOrchestrator to Inherit (1 hour)

```python
# claude_force/orchestrator.py
from claude_force.base import BaseOrchestrator, AgentResult, WorkflowResult


class AgentOrchestrator(BaseOrchestrator):
    """
    Standard orchestrator implementation.

    Inherits from BaseOrchestrator and provides concrete
    implementation for all abstract methods.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        enable_cache: bool = True,
        enable_tracking: bool = True
    ):
        """Initialize orchestrator."""
        self._config_path = config_path
        self._enable_cache = enable_cache
        self._enable_tracking = enable_tracking
        # ... existing initialization

    def run_agent(
        self,
        agent_name: str,
        task: str,
        **kwargs
    ) -> AgentResult:
        """Execute a single agent (concrete implementation)."""
        # Existing implementation
        pass

    def run_workflow(
        self,
        workflow_name: str,
        task: str,
        **kwargs
    ) -> WorkflowResult:
        """Execute a workflow (concrete implementation)."""
        # Existing implementation
        pass

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all available agents."""
        return self.config.get('agents', {})

    def list_workflows(self) -> Dict[str, List[str]]:
        """List all available workflows."""
        return self.config.get('workflows', {})
```

### Step 3: Update Other Orchestrators (1 hour)

```python
# claude_force/hybrid_orchestrator.py
from claude_force.base import BaseOrchestrator


class HybridOrchestrator(BaseOrchestrator):
    """Cost-optimized orchestrator with auto model selection."""

    # Inherits abstract methods and must implement them
    pass


# claude_force/async_orchestrator.py
from claude_force.base import BaseOrchestrator


class AsyncOrchestrator(BaseOrchestrator):
    """Async orchestrator for concurrent execution."""

    # Inherits abstract methods and must implement them
    pass
```

### Step 4: Update Cache to Match Protocol (0.5 hours)

```python
# claude_force/response_cache.py

class ResponseCache:
    """
    SQLite-based response cache.

    Implements CacheProtocol for compatibility.
    """

    def get(self, key: str) -> Optional[str]:
        """Retrieve from cache (protocol implementation)."""
        # Existing implementation
        pass

    def set(self, key: str, value: str, ttl: int = 86400) -> None:
        """Store in cache (protocol implementation)."""
        # Existing implementation
        pass

    def delete(self, key: str) -> bool:
        """Delete from cache (protocol implementation)."""
        # New method
        pass

    def clear(self) -> None:
        """Clear all cache entries (protocol implementation)."""
        # New method
        pass

    def size(self) -> int:
        """Get number of entries (protocol implementation)."""
        # New method
        pass
```

### Step 5: Add Type Checking Validation (0.5 hours)

```python
# Type check that implementations satisfy protocols
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from claude_force.base import CacheProtocol, TrackerProtocol

    # These will cause mypy errors if protocols aren't satisfied
    _cache: CacheProtocol = ResponseCache()
    _tracker: TrackerProtocol = PerformanceTracker()
```

### Step 6: Create Example Custom Orchestrator (1 hour)

```python
# examples/python/custom_orchestrator.py
"""Example of creating a custom orchestrator."""

from claude_force.base import BaseOrchestrator, AgentResult, WorkflowResult


class CustomOrchestrator(BaseOrchestrator):
    """
    Custom orchestrator example.

    Demonstrates how to extend BaseOrchestrator with
    custom behavior.
    """

    def __init__(self, custom_config: dict):
        self.custom_config = custom_config

    def run_agent(
        self,
        agent_name: str,
        task: str,
        **kwargs
    ) -> AgentResult:
        """Custom agent execution logic."""
        print(f"Custom orchestrator running: {agent_name}")

        # Your custom logic here
        result = self._execute_custom_agent(agent_name, task)

        return AgentResult(
            success=True,
            output=result,
            errors=[],
            metadata={'custom': True}
        )

    def run_workflow(
        self,
        workflow_name: str,
        task: str,
        **kwargs
    ) -> WorkflowResult:
        """Custom workflow execution logic."""
        # Your custom logic here
        pass

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List custom agents."""
        return self.custom_config.get('agents', {})

    def list_workflows(self) -> Dict[str, List[str]]:
        """List custom workflows."""
        return self.custom_config.get('workflows', {})


# Usage
if __name__ == '__main__':
    orchestrator = CustomOrchestrator(custom_config={'agents': {}})
    result = orchestrator.run_agent('my-agent', 'my task')
    print(result)
```

### Step 7: Add Tests (1-2 hours)

```python
# tests/test_base.py
"""Tests for abstract base classes."""

import pytest
from claude_force.base import BaseOrchestrator, CacheProtocol
from claude_force import AgentOrchestrator, ResponseCache


class TestBaseOrchestrator:
    """Test that BaseOrchestrator works correctly."""

    def test_cannot_instantiate_abstract_class(self):
        """Abstract class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseOrchestrator()

    def test_concrete_class_inherits(self):
        """Concrete orchestrators inherit from base."""
        orchestrator = AgentOrchestrator()
        assert isinstance(orchestrator, BaseOrchestrator)

    def test_has_required_methods(self):
        """Base class defines required methods."""
        required_methods = [
            'run_agent',
            'run_workflow',
            'list_agents',
            'list_workflows'
        ]
        for method in required_methods:
            assert hasattr(BaseOrchestrator, method)


class TestCacheProtocol:
    """Test that cache implementations match protocol."""

    def test_response_cache_satisfies_protocol(self):
        """ResponseCache satisfies CacheProtocol."""
        cache = ResponseCache()

        # Check protocol methods exist
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'delete')
        assert hasattr(cache, 'clear')
        assert hasattr(cache, 'size')
```

### Step 8: Update Documentation (0.5 hours)

Update README.md and docs to show extensibility:

```markdown
## Extending Claude Force

### Custom Orchestrator

Create your own orchestrator by inheriting from `BaseOrchestrator`:

\`\`\`python
from claude_force.base import BaseOrchestrator, AgentResult

class MyOrchestrator(BaseOrchestrator):
    def run_agent(self, agent_name, task, **kwargs):
        # Your custom implementation
        return AgentResult(success=True, output="...", errors=[], metadata={})
\`\`\`

### Custom Cache

Implement the `CacheProtocol` for custom caching:

\`\`\`python
class MyCache:
    def get(self, key: str) -> Optional[str]:
        # Your implementation
        pass

    def set(self, key: str, value: str, ttl: int = 86400):
        # Your implementation
        pass
\`\`\`
```

---

## Acceptance Criteria

- [ ] `BaseOrchestrator` abstract class created
- [ ] `CacheProtocol` protocol defined
- [ ] `TrackerProtocol` protocol defined
- [ ] All existing orchestrators inherit from `BaseOrchestrator`
- [ ] All existing implementations satisfy protocols
- [ ] Example custom orchestrator works
- [ ] Tests cover abstract classes and protocols
- [ ] Documentation updated with extensibility examples
- [ ] No breaking changes to existing API

---

## Testing

```bash
# Run tests
pytest tests/test_base.py -v

# Type check
mypy claude_force/base.py --strict

# Verify example works
python examples/python/custom_orchestrator.py
```

---

## Dependencies

None

---

## Related Tasks

- ARCH-01: Refactor CLI (can use similar patterns)
- MARKET-01: Plugin Installation (depends on these abstractions)

---

**Status**: Not Started
**Assignee**: TBD
**Due Date**: End of Week 1
