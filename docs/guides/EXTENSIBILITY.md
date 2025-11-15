# Extensibility Guide

Claude Force is designed to be highly extensible. You can customize and extend the framework by:

1. **Creating Custom Orchestrators** - Implement specialized routing and execution logic
2. **Implementing Custom Caches** - Use Redis, Memcached, or other backends
3. **Building Custom Trackers** - Integrate with Prometheus, DataDog, etc.
4. **Extending Data Structures** - Use AgentResult and WorkflowResult in your code

This guide shows you how to extend claude-force without modifying the core code.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Custom Orchestrators](#custom-orchestrators)
- [Custom Cache Implementations](#custom-cache-implementations)
- [Custom Performance Trackers](#custom-performance-trackers)
- [Using Dataclasses](#using-dataclasses)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## Architecture Overview

Claude Force uses **abstract base classes** and **protocols** to define clear interfaces:

```python
from claude_force.base import (
    BaseOrchestrator,      # Abstract base class for orchestrators
    CacheProtocol,         # Protocol for cache implementations
    TrackerProtocol,       # Protocol for performance trackers
    AgentResult,           # Dataclass for agent results
    WorkflowResult,        # Dataclass for workflow results
)
```

**Key Concepts:**

- **Abstract Base Classes (ABC)**: Enforce interface compliance through inheritance
- **Protocols**: Enable duck-typed interfaces without inheritance
- **Dataclasses**: Standardized data structures for results and metadata

---

## Custom Orchestrators

### Why Create a Custom Orchestrator?

- Implement specialized routing strategies
- Add retry logic, circuit breakers, or rate limiting
- Integrate with external systems (logging, monitoring)
- Create domain-specific orchestration patterns

### BaseOrchestrator Interface

All orchestrators must implement these 4 methods:

```python
from claude_force.base import BaseOrchestrator, AgentResult
from typing import Dict, List, Any

class MyOrchestrator(BaseOrchestrator):
    def run_agent(self, agent_name: str, task: str, **kwargs) -> AgentResult:
        """Execute a single agent."""
        pass  # Your implementation

    def run_workflow(self, workflow_name: str, task: str, **kwargs) -> List[AgentResult]:
        """Execute a multi-agent workflow."""
        pass  # Your implementation

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        pass  # Your implementation

    def list_workflows(self) -> Dict[str, List[str]]:
        """List all available workflows."""
        pass  # Your implementation
```

### Example: Logging Orchestrator

```python
from claude_force.base import BaseOrchestrator, AgentResult
import anthropic

class LoggingOrchestrator(BaseOrchestrator):
    """Logs all agent executions to a file."""

    def __init__(self, api_key: str, log_file: str = "executions.log"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.log_file = log_file

    def _log(self, message: str):
        """Write to log file."""
        with open(self.log_file, "a") as f:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] {message}\n")

    def run_agent(self, agent_name: str, task: str, **kwargs) -> AgentResult:
        """Execute agent with logging."""
        self._log(f"Starting: {agent_name}")

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=kwargs.get("model", "claude-3-haiku-20240307"),
                max_tokens=kwargs.get("max_tokens", 4096),
                messages=[{"role": "user", "content": task}],
            )

            output = "".join(block.text for block in response.content if hasattr(block, "text"))
            self._log(f"Success: {agent_name}")

            return AgentResult(
                success=True,
                output=output,
                errors=[],
                metadata={"tokens": response.usage.input_tokens + response.usage.output_tokens},
                agent_name=agent_name,
            )

        except Exception as e:
            self._log(f"Error: {agent_name} - {str(e)}")
            return AgentResult(
                success=False,
                output="",
                errors=[str(e)],
                metadata={},
                agent_name=agent_name,
            )

    def list_agents(self) -> List[Dict[str, Any]]:
        return [{"name": "default-agent", "priority": 1}]

    def list_workflows(self) -> Dict[str, List[str]]:
        return {}

    def run_workflow(self, workflow_name: str, task: str, **kwargs) -> List[AgentResult]:
        return []
```

**Usage:**

```python
orch = LoggingOrchestrator(api_key="your-api-key")
result = orch.run_agent("test-agent", "Write a Python function")
print(result.output)
# Check executions.log for logs
```

### Example: Retry Orchestrator (Wrapper Pattern)

```python
class RetryOrchestrator(BaseOrchestrator):
    """Wraps another orchestrator with retry logic."""

    def __init__(self, base: BaseOrchestrator, max_retries: int = 3):
        self.base = base
        self.max_retries = max_retries

    def run_agent(self, agent_name: str, task: str, **kwargs) -> AgentResult:
        """Execute agent with retries."""
        for attempt in range(self.max_retries):
            result = self.base.run_agent(agent_name, task, **kwargs)

            if result.success:
                if attempt > 0:
                    result.metadata["retry_count"] = attempt
                return result

            print(f"Attempt {attempt + 1} failed, retrying...")

        # All retries exhausted
        result.errors.append(f"Failed after {self.max_retries} attempts")
        return result

    # Delegate other methods to base
    def run_workflow(self, workflow_name: str, task: str, **kwargs):
        return self.base.run_workflow(workflow_name, task, **kwargs)

    def list_agents(self):
        return self.base.list_agents()

    def list_workflows(self):
        return self.base.list_workflows()
```

**Usage:**

```python
from claude_force.orchestrator import AgentOrchestrator

# Wrap standard orchestrator with retry logic
base_orch = AgentOrchestrator()
retry_orch = RetryOrchestrator(base_orch, max_retries=3)

# Now has automatic retry
result = retry_orch.run_agent("code-reviewer", "Review this code")
```

---

## Custom Cache Implementations

### Why Create a Custom Cache?

- Use Redis for distributed caching
- Integrate with Memcached
- Implement custom eviction strategies
- Add cache warming or preloading

### CacheProtocol Interface

```python
from typing import Protocol, Optional

class CacheProtocol(Protocol):
    """Protocol that all caches must satisfy."""

    def get(self, key: str) -> Optional[str]:
        """Retrieve value from cache."""
        ...

    def set(self, key: str, value: str, ttl: int = 86400) -> None:
        """Store value in cache."""
        ...

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...

    def clear(self) -> None:
        """Clear all cache entries."""
        ...

    def size(self) -> int:
        """Get number of entries."""
        ...
```

### Example: Redis Cache

```python
import redis
import json
from typing import Optional

class RedisCache:
    """Redis-backed cache implementation."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def get(self, key: str) -> Optional[str]:
        """Retrieve from Redis."""
        return self.client.get(key)

    def set(self, key: str, value: str, ttl: int = 86400) -> None:
        """Store in Redis with TTL."""
        self.client.setex(key, ttl, value)

    def delete(self, key: str) -> bool:
        """Delete from Redis."""
        return bool(self.client.delete(key))

    def clear(self) -> None:
        """Clear all keys."""
        self.client.flushdb()

    def size(self) -> int:
        """Get key count."""
        return self.client.dbsize()
```

**Usage with Orchestrator:**

Since Python protocols are duck-typed, any class with matching methods can be used:

```python
from claude_force.orchestrator import AgentOrchestrator

# Use custom Redis cache
cache = RedisCache(host="localhost")

# Note: AgentOrchestrator would need to accept cache parameter
# This is an example of how it could work
orch = AgentOrchestrator(cache=cache)
```

---

## Custom Performance Trackers

### Why Create a Custom Tracker?

- Send metrics to Prometheus
- Integrate with DataDog or New Relic
- Store in time-series databases
- Custom analytics pipelines

### TrackerProtocol Interface

```python
from typing import Protocol, Optional, Dict, Any

class TrackerProtocol(Protocol):
    """Protocol that all trackers must satisfy."""

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
        """Record a single execution."""
        ...

    def get_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Get summary statistics."""
        ...

    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get per-agent statistics."""
        ...

    def export_json(self, output_path: str) -> None:
        """Export to JSON file."""
        ...

    def export_csv(self, output_path: str) -> None:
        """Export to CSV file."""
        ...
```

### Example: Prometheus Tracker

```python
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any, Optional

class PrometheusTracker:
    """Send metrics to Prometheus."""

    def __init__(self):
        # Define metrics
        self.executions_total = Counter(
            'claude_force_executions_total',
            'Total agent executions',
            ['agent_name', 'success']
        )

        self.execution_duration = Histogram(
            'claude_force_execution_duration_ms',
            'Execution duration in milliseconds',
            ['agent_name']
        )

        self.tokens_total = Counter(
            'claude_force_tokens_total',
            'Total tokens used',
            ['agent_name', 'type']  # type: input or output
        )

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
        """Record metrics in Prometheus."""
        # Increment execution counter
        self.executions_total.labels(
            agent_name=agent_name,
            success=str(success)
        ).inc()

        # Record duration
        self.execution_duration.labels(agent_name=agent_name).observe(duration_ms)

        # Record tokens
        self.tokens_total.labels(agent_name=agent_name, type='input').inc(input_tokens)
        self.tokens_total.labels(agent_name=agent_name, type='output').inc(output_tokens)

    def get_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Get summary from Prometheus."""
        # Query Prometheus for metrics
        # This is simplified - real implementation would query Prometheus HTTP API
        return {"note": "Query Prometheus /metrics endpoint"}

    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get per-agent stats."""
        return {}

    def export_json(self, output_path: str) -> None:
        """Not applicable for Prometheus."""
        pass

    def export_csv(self, output_path: str) -> None:
        """Not applicable for Prometheus."""
        pass
```

**Usage:**

```python
from claude_force.orchestrator import AgentOrchestrator

tracker = PrometheusTracker()

# Use with orchestrator (if it accepts tracker parameter)
orch = AgentOrchestrator(tracker=tracker)

# Metrics are automatically sent to Prometheus
result = orch.run_agent("code-reviewer", "Review code")
```

---

## Using Dataclasses

### AgentResult

Standard result format from agent executions:

```python
from claude_force.base import AgentResult

result = AgentResult(
    success=True,
    output="Agent response text",
    errors=[],  # Empty if successful
    metadata={
        "model": "claude-3-haiku-20240307",
        "tokens_used": 500,
        "execution_time_ms": 1234,
    },
    agent_name="code-reviewer",
)

# Convert to dict for JSON serialization
result_dict = result.to_dict()

# Check success
if result.success:
    print(result.output)
else:
    print("Errors:", result.errors)
```

### WorkflowResult

Standard result format from workflow executions:

```python
from claude_force.base import WorkflowResult, AgentResult

workflow_result = WorkflowResult(
    success=True,
    agent_results=[
        AgentResult(...),  # Result from agent 1
        AgentResult(...),  # Result from agent 2
    ],
    metadata={
        "total_tokens": 1000,
        "total_cost": 0.05,
    },
    workflow_name="code-review-workflow",
)

# Check if all agents succeeded
all_succeeded = workflow_result.success and all(
    r.success for r in workflow_result.agent_results
)
```

---

## Best Practices

### 1. Follow Interface Contracts

When extending base classes, implement all required methods:

```python
# ✅ Good: Implements all 4 methods
class GoodOrchestrator(BaseOrchestrator):
    def run_agent(self, ...): pass
    def run_workflow(self, ...): pass
    def list_agents(self): pass
    def list_workflows(self): pass

# ❌ Bad: Missing methods will raise TypeError
class BadOrchestrator(BaseOrchestrator):
    def run_agent(self, ...): pass
    # Missing other methods!
```

### 2. Use Wrapper Pattern for Composition

Instead of modifying existing orchestrators, wrap them:

```python
# ✅ Good: Wrapper pattern
class LoggingWrapper(BaseOrchestrator):
    def __init__(self, base: BaseOrchestrator):
        self.base = base

    def run_agent(self, ...):
        log("Starting...")
        result = self.base.run_agent(...)
        log("Done")
        return result

# ❌ Bad: Modifying core code
# Don't modify AgentOrchestrator source
```

### 3. Return Standardized Results

Always return `AgentResult` or `WorkflowResult`:

```python
# ✅ Good: Returns AgentResult
def run_agent(self, ...) -> AgentResult:
    return AgentResult(
        success=True,
        output="...",
        errors=[],
        metadata={},
    )

# ❌ Bad: Returns custom structure
def run_agent(self, ...):
    return {"ok": True, "data": "..."}  # Don't do this!
```

### 4. Preserve Metadata

Include useful metadata in results:

```python
# ✅ Good: Rich metadata
metadata = {
    "model": "claude-3-haiku-20240307",
    "tokens_used": 500,
    "execution_time_ms": 1234,
    "retry_count": 2,
    "cached": False,
}

# ❌ Bad: Empty metadata
metadata = {}
```

---

## Examples

### Complete Working Example

See [`examples/python/custom_orchestrator.py`](../examples/python/custom_orchestrator.py) for:

- `LoggingOrchestrator` - Logs all executions to a file
- `RetryOrchestrator` - Adds automatic retry logic
- Full usage examples and patterns

**Run it:**

```bash
cd examples/python
python custom_orchestrator.py
```

### Testing Custom Implementations

See [`tests/test_base.py`](../tests/test_base.py) for:

- Testing custom orchestrators
- Verifying protocol compliance
- Testing dataclass conversions

**Run tests:**

```bash
python -m unittest tests.test_base -v
```

---

## Summary

**Key Points:**

✅ Extend `BaseOrchestrator` for custom orchestrators
✅ Implement `CacheProtocol` for custom caches
✅ Implement `TrackerProtocol` for custom trackers
✅ Use `AgentResult` and `WorkflowResult` for consistent interfaces
✅ Follow the wrapper pattern for composition

**Resources:**

- [Custom Orchestrator Example](../examples/python/custom_orchestrator.py)
- [Base Classes Source](../claude_force/base.py)
- [Tests](../tests/test_base.py)

---

**Need help?** Open an issue on GitHub or check the FAQ.
