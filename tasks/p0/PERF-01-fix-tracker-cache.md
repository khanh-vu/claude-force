# PERF-01: Fix Unbounded Performance Tracker Cache

**Priority**: P0 - Critical
**Estimated Effort**: 2-3 hours
**Impact**: CRITICAL - Prevents OOM in production
**Category**: Performance

---

## Problem Statement

`PerformanceTracker` has unbounded in-memory cache for metrics:
- No limit on number of metrics stored
- Could cause OOM with 10K+ executions
- Memory leak risk in long-running processes
- Production risk for high-volume deployments

**File**: `claude_force/performance_tracker.py`

---

## Solution

Implement ring buffer with configurable size limit using `collections.deque`.

---

## Implementation

### Step 1: Add Ring Buffer (1 hour)

```python
# claude_force/performance_tracker.py
from collections import deque
from typing import Optional, List, Dict, Any
import time


class PerformanceTracker:
    """
    Track agent execution performance with bounded memory.

    Uses ring buffer to limit memory usage in long-running processes.
    Oldest metrics are automatically evicted when limit is reached.
    """

    def __init__(
        self,
        max_entries: int = 10000,
        enable_persistence: bool = True
    ):
        """
        Initialize tracker.

        Args:
            max_entries: Maximum metrics to keep in memory (ring buffer)
            enable_persistence: Whether to persist to disk (JSONL)
        """
        self._metrics = deque(maxlen=max_entries)  # Ring buffer
        self._summary_cache = None
        self._cache_dirty = True
        self.max_entries = max_entries
        self.enable_persistence = enable_persistence

    def record_metric(
        self,
        agent_name: str,
        duration_ms: float,
        tokens_used: int,
        cost: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a performance metric.

        Automatically evicts oldest entry when max_entries is reached.
        """
        metric = {
            'timestamp': time.time(),
            'agent_name': agent_name,
            'duration_ms': duration_ms,
            'tokens_used': tokens_used,
            'cost': cost,
            'success': success,
            'metadata': metadata or {}
        }

        # Add to ring buffer (auto-evicts oldest if at capacity)
        self._metrics.append(metric)
        self._cache_dirty = True

        # Persist to disk if enabled
        if self.enable_persistence:
            self._persist_metric(metric)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary with caching.

        Caches computed summary and only recomputes when metrics change.
        """
        if not self._cache_dirty and self._summary_cache:
            return self._summary_cache

        # Compute summary
        if not self._metrics:
            return {
                'total_executions': 0,
                'total_cost': 0.0,
                'avg_duration_ms': 0.0,
                'success_rate': 0.0
            }

        total_executions = len(self._metrics)
        total_cost = sum(m['cost'] for m in self._metrics)
        avg_duration = sum(m['duration_ms'] for m in self._metrics) / total_executions
        success_count = sum(1 for m in self._metrics if m['success'])

        summary = {
            'total_executions': total_executions,
            'total_cost': total_cost,
            'avg_duration_ms': avg_duration,
            'success_rate': success_count / total_executions if total_executions > 0 else 0.0,
            'in_memory_count': total_executions,
            'max_entries': self.max_entries,
            'memory_usage_mb': self._estimate_memory_usage()
        }

        # Cache the summary
        self._summary_cache = summary
        self._cache_dirty = False

        return summary

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        # Rough estimate: ~1KB per metric entry
        return (len(self._metrics) * 1024) / (1024 * 1024)

    def clear(self):
        """Clear all in-memory metrics."""
        self._metrics.clear()
        self._summary_cache = None
        self._cache_dirty = True
```

### Step 2: Add Configuration Options (0.5 hours)

```python
# claude_force/constants.py (if ARCH-05 done first)
# Or add to config

# Performance Tracking
DEFAULT_MAX_METRICS_IN_MEMORY = 10_000
MAX_METRICS_IN_MEMORY_LIMIT = 100_000  # Hard limit
```

### Step 3: Update Orchestrator Integration (0.5 hours)

```python
# claude_force/orchestrator.py

class AgentOrchestrator:
    def __init__(
        self,
        enable_tracking: bool = True,
        max_metrics: int = 10000
    ):
        if enable_tracking:
            self._tracker = PerformanceTracker(max_entries=max_metrics)
```

### Step 4: Add Tests (1 hour)

```python
# tests/test_performance_tracker.py

class TestPerformanceTrackerBounds:
    """Test ring buffer behavior."""

    def test_respects_max_entries(self):
        """Tracker respects max_entries limit."""
        tracker = PerformanceTracker(max_entries=100)

        # Add 200 metrics
        for i in range(200):
            tracker.record_metric(
                agent_name='test-agent',
                duration_ms=100.0,
                tokens_used=1000,
                cost=0.01,
                success=True
            )

        # Should only have 100 (most recent)
        summary = tracker.get_summary()
        assert summary['in_memory_count'] == 100
        assert summary['total_executions'] == 100

    def test_ring_buffer_evicts_oldest(self):
        """Oldest metrics are evicted first."""
        tracker = PerformanceTracker(max_entries=3)

        # Add metrics with different metadata
        tracker.record_metric('agent', 100, 1000, 0.01, True, {'id': 1})
        tracker.record_metric('agent', 100, 1000, 0.01, True, {'id': 2})
        tracker.record_metric('agent', 100, 1000, 0.01, True, {'id': 3})
        tracker.record_metric('agent', 100, 1000, 0.01, True, {'id': 4})  # Evicts id:1

        # Get all metrics
        metrics = list(tracker._metrics)
        ids = [m['metadata']['id'] for m in metrics]

        assert ids == [2, 3, 4]  # id:1 was evicted

    def test_memory_usage_estimate(self):
        """Memory usage estimation is reasonable."""
        tracker = PerformanceTracker(max_entries=10000)

        # Add 1000 metrics
        for i in range(1000):
            tracker.record_metric('agent', 100, 1000, 0.01, True)

        summary = tracker.get_summary()

        # ~1KB per entry = ~1MB for 1000 entries
        assert summary['memory_usage_mb'] < 2.0  # Reasonable estimate

    def test_summary_caching(self):
        """Summary is cached when metrics don't change."""
        tracker = PerformanceTracker(max_entries=100)
        tracker.record_metric('agent', 100, 1000, 0.01, True)

        # First call
        summary1 = tracker.get_summary()

        # Second call (should use cache)
        summary2 = tracker.get_summary()

        assert summary1 is summary2  # Same object (cached)

        # Add new metric
        tracker.record_metric('agent', 100, 1000, 0.01, True)

        # Third call (should recompute)
        summary3 = tracker.get_summary()

        assert summary3 is not summary2  # Different object (recomputed)

    def test_long_running_process_simulation(self):
        """Simulate long-running process with many executions."""
        tracker = PerformanceTracker(max_entries=1000)

        # Simulate 100K executions
        for i in range(100_000):
            tracker.record_metric('agent', 100, 1000, 0.01, True)

            # Check memory doesn't grow unbounded
            if i % 10000 == 0:
                summary = tracker.get_summary()
                assert summary['in_memory_count'] <= 1000
                assert summary['memory_usage_mb'] < 2.0
```

---

## Acceptance Criteria

- [ ] Ring buffer implemented with `deque(maxlen=N)`
- [ ] Default max_entries = 10,000
- [ ] Configurable via constructor
- [ ] Memory usage stays bounded even with millions of executions
- [ ] Summary caching works correctly
- [ ] Tests verify ring buffer behavior
- [ ] Documentation updated
- [ ] No breaking changes

---

## Testing

```bash
# Run tests
pytest tests/test_performance_tracker.py -v

# Memory stress test
python -c "
from claude_force import PerformanceTracker
tracker = PerformanceTracker(max_entries=10000)
for i in range(1_000_000):
    tracker.record_metric('agent', 100, 1000, 0.01, True)
    if i % 100000 == 0:
        summary = tracker.get_summary()
        print(f'{i}: {summary[\"memory_usage_mb\"]:.2f}MB')
"
```

---

## Dependencies

None

---

## Related Tasks

- ARCH-05: Create Constants Module (for configuration)
- PERF-03: Optional HMAC Verification (similar performance pattern)

---

**Status**: Not Started
**Assignee**: TBD
**Due Date**: Week 1
