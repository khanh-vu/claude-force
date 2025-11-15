"""
Performance Tracking and Analytics

Track agent execution metrics, token usage, costs, and performance trends.
"""

import json
import csv
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, deque


# Claude API pricing (as of 2024-01)
# https://www.anthropic.com/pricing
PRICING = {
    "claude-3-5-sonnet-20241022": {
        "input": 0.003,  # $3 per million tokens
        "output": 0.015,  # $15 per million tokens
    },
    "claude-3-opus-20240229": {
        "input": 0.015,  # $15 per million tokens
        "output": 0.075,  # $75 per million tokens
    },
    "claude-3-sonnet-20240229": {
        "input": 0.003,  # $3 per million tokens
        "output": 0.015,  # $15 per million tokens
    },
    "claude-3-haiku-20240307": {
        "input": 0.00025,  # $0.25 per million tokens
        "output": 0.00125,  # $1.25 per million tokens
    },
}


@dataclass
class ExecutionMetrics:
    """Metrics for a single execution"""

    timestamp: str
    agent_name: str
    task_hash: str  # Hash of task for grouping
    success: bool
    execution_time_ms: float
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    error_type: Optional[str] = None
    workflow_name: Optional[str] = None
    workflow_position: Optional[int] = None


class PerformanceTracker:
    """
    Track and analyze agent execution performance.

    Collects metrics on execution time, token usage, costs, and success rates.
    Provides analytics, trends, and export functionality.
    """

    def __init__(
        self,
        metrics_dir: str = ".claude/metrics",
        max_entries: int = 10000,
        enable_persistence: bool = True
    ):
        """
        Initialize performance tracker with bounded memory.

        Args:
            metrics_dir: Directory to store metrics data
            max_entries: Maximum metrics to keep in memory (ring buffer)
            enable_persistence: Whether to persist to disk (JSONL)
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.metrics_dir / "executions.jsonl"
        self.summary_file = self.metrics_dir / "summary.json"

        # Ring buffer for bounded memory usage
        self.max_entries = max_entries
        self.enable_persistence = enable_persistence
        self._cache = deque(maxlen=max_entries)

        # Summary caching
        self._summary_cache: Optional[Dict[str, Any]] = None
        self._cache_dirty = True

        self._load_cache()

    def _load_cache(self):
        """Load metrics from disk into cache"""
        if not self.metrics_file.exists():
            return

        try:
            with open(self.metrics_file, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self._cache.append(ExecutionMetrics(**data))
        except Exception as e:
            print(f"Warning: Could not load metrics cache: {e}")

    def _task_hash(self, task: str) -> str:
        """Generate hash for task (for grouping similar tasks)"""
        import hashlib

        return hashlib.md5(task.encode()).hexdigest()[:8]

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost based on token usage

        Args:
            model: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Find matching pricing
        pricing = None
        for model_key, prices in PRICING.items():
            if model_key in model:
                pricing = prices
                break

        if not pricing:
            # Default to Sonnet pricing
            pricing = PRICING["claude-3-5-sonnet-20241022"]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def record_execution(
        self,
        agent_name: str,
        task: str,
        success: bool,
        execution_time_ms: float,
        model: str,
        input_tokens: int,
        output_tokens: int,
        error_type: Optional[str] = None,
        workflow_name: Optional[str] = None,
        workflow_position: Optional[int] = None,
    ) -> ExecutionMetrics:
        """
        Record a single agent execution

        Args:
            agent_name: Name of agent
            task: Task description
            success: Whether execution succeeded
            execution_time_ms: Execution time in milliseconds
            model: Model ID used
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            error_type: Type of error if failed
            workflow_name: Name of workflow (if part of workflow)
            workflow_position: Position in workflow (if part of workflow)

        Returns:
            ExecutionMetrics object
        """
        metrics = ExecutionMetrics(
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            task_hash=self._task_hash(task),
            success=success,
            execution_time_ms=execution_time_ms,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost=self._estimate_cost(model, input_tokens, output_tokens),
            error_type=error_type,
            workflow_name=workflow_name,
            workflow_position=workflow_position,
        )

        # Add to ring buffer (auto-evicts oldest if at capacity)
        self._cache.append(metrics)
        self._cache_dirty = True

        # Persist to disk if enabled
        if self.enable_persistence:
            try:
                with open(self.metrics_file, "a") as f:
                    f.write(json.dumps(asdict(metrics)) + "\n")
            except Exception as e:
                print(f"Warning: Could not save metrics: {e}")

        return metrics

    def get_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get summary statistics with caching.

        Caches computed summary and only recomputes when metrics change.

        Args:
            hours: Only include last N hours (None for all time)

        Returns:
            Dictionary with summary statistics
        """
        # If time filter is specified, can't use cache
        if hours:
            return self._compute_summary(hours)

        # Use cached summary if available and clean
        if not self._cache_dirty and self._summary_cache:
            return self._summary_cache

        # Compute and cache summary
        summary = self._compute_summary(hours)
        self._summary_cache = summary
        self._cache_dirty = False

        return summary

    def _compute_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Compute summary statistics (internal helper)"""
        metrics = list(self._cache)

        # Filter by time if specified
        if hours:
            cutoff = datetime.now().timestamp() - (hours * 3600)
            metrics = [
                m for m in metrics if datetime.fromisoformat(m.timestamp).timestamp() > cutoff
            ]

        if not metrics:
            return {
                "total_executions": 0,
                "success_rate": 0,
                "total_cost": 0,
                "total_tokens": 0,
                "in_memory_count": len(self._cache),
                "max_entries": self.max_entries,
                "memory_usage_mb": self._estimate_memory_usage()
            }

        total = len(metrics)
        successful = sum(1 for m in metrics if m.success)

        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "total_tokens": sum(m.total_tokens for m in metrics),
            "total_input_tokens": sum(m.input_tokens for m in metrics),
            "total_output_tokens": sum(m.output_tokens for m in metrics),
            "total_cost": sum(m.estimated_cost for m in metrics),
            "avg_execution_time_ms": sum(m.execution_time_ms for m in metrics) / total,
            "avg_cost_per_execution": sum(m.estimated_cost for m in metrics) / total,
            "time_period": f"last {hours} hours" if hours else "all time",
            "in_memory_count": len(self._cache),
            "max_entries": self.max_entries,
            "memory_usage_mb": self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> float:
        """
        Estimate memory usage in MB.

        Returns:
            Estimated memory usage in megabytes
        """
        # Rough estimate: ~1KB per metric entry
        bytes_per_entry = 1024
        total_bytes = len(self._cache) * bytes_per_entry
        return total_bytes / (1024 * 1024)

    def get_agent_stats(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics by agent

        Args:
            agent_name: Specific agent (None for all agents)

        Returns:
            Dictionary with per-agent statistics
        """
        metrics = self._cache
        if agent_name:
            metrics = [m for m in metrics if m.agent_name == agent_name]

        if not metrics:
            return {}

        # Group by agent
        by_agent = defaultdict(list)
        for m in metrics:
            by_agent[m.agent_name].append(m)

        stats = {}
        for agent, agent_metrics in by_agent.items():
            total = len(agent_metrics)
            successful = sum(1 for m in agent_metrics if m.success)

            stats[agent] = {
                "executions": total,
                "success_rate": successful / total if total > 0 else 0,
                "total_cost": sum(m.estimated_cost for m in agent_metrics),
                "avg_execution_time_ms": sum(m.execution_time_ms for m in agent_metrics) / total,
                "total_tokens": sum(m.total_tokens for m in agent_metrics),
            }

        return stats

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get cost breakdown by agent and model"""
        by_agent = defaultdict(float)
        by_model = defaultdict(float)

        for m in self._cache:
            by_agent[m.agent_name] += m.estimated_cost
            by_model[m.model] += m.estimated_cost

        return {
            "by_agent": dict(sorted(by_agent.items(), key=lambda x: x[1], reverse=True)),
            "by_model": dict(sorted(by_model.items(), key=lambda x: x[1], reverse=True)),
            "total": sum(by_agent.values()),
        }

    def get_trends(self, interval_hours: int = 24) -> Dict[str, List]:
        """
        Get performance trends over time

        Args:
            interval_hours: Group metrics by this interval

        Returns:
            Dictionary with trend data
        """
        if not self._cache:
            return {"timestamps": [], "executions": [], "costs": [], "success_rates": []}

        # Group by time interval
        intervals = defaultdict(list)

        for m in self._cache:
            ts = datetime.fromisoformat(m.timestamp)
            # Round down to interval
            interval_ts = ts.replace(minute=0, second=0, microsecond=0)
            intervals[interval_ts.isoformat()].append(m)

        # Calculate stats for each interval
        timestamps = []
        executions = []
        costs = []
        success_rates = []

        for ts in sorted(intervals.keys()):
            interval_metrics = intervals[ts]
            total = len(interval_metrics)
            successful = sum(1 for m in interval_metrics if m.success)

            timestamps.append(ts)
            executions.append(total)
            costs.append(sum(m.estimated_cost for m in interval_metrics))
            success_rates.append(successful / total if total > 0 else 0)

        return {
            "timestamps": timestamps,
            "executions": executions,
            "costs": costs,
            "success_rates": success_rates,
        }

    def export_csv(self, output_path: str):
        """Export metrics to CSV file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", newline="") as f:
            if not self._cache:
                return

            writer = csv.DictWriter(f, fieldnames=asdict(self._cache[0]).keys())
            writer.writeheader()

            for metrics in self._cache:
                writer.writerow(asdict(metrics))

    def export_json(self, output_path: str):
        """Export metrics to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "summary": self.get_summary(),
            "agent_stats": self.get_agent_stats(),
            "cost_breakdown": self.get_cost_breakdown(),
            "trends": self.get_trends(),
            "executions": [asdict(m) for m in self._cache],
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

    def clear(self):
        """Clear all in-memory metrics."""
        self._cache.clear()
        self._summary_cache = None
        self._cache_dirty = True

    def clear_old_metrics(self, days: int = 30):
        """
        Clear metrics older than specified days

        Args:
            days: Keep only metrics from last N days
        """
        cutoff = datetime.now().timestamp() - (days * 86400)

        # Filter cache
        old_cache = self._cache
        self._cache = deque(
            (m for m in old_cache if datetime.fromisoformat(m.timestamp).timestamp() > cutoff),
            maxlen=self.max_entries
        )
        self._cache_dirty = True

        # Rewrite file if persistence is enabled
        if self.enable_persistence:
            with open(self.metrics_file, "w") as f:
                for metrics in self._cache:
                    f.write(json.dumps(asdict(metrics)) + "\n")


def get_tracker(
    metrics_dir: str = ".claude/metrics",
    max_entries: int = 10000
) -> PerformanceTracker:
    """
    Factory function to create performance tracker

    Args:
        metrics_dir: Directory to store metrics
        max_entries: Maximum metrics to keep in memory

    Returns:
        PerformanceTracker instance
    """
    return PerformanceTracker(metrics_dir, max_entries=max_entries)
