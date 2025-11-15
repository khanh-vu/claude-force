"""
Cross-Repository Analytics for claude-force.

Provides analytics and performance comparison between claude-force and
wshobson/agents, helping users choose optimal agents for their tasks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for a single agent."""

    agent_id: str
    agent_name: str
    source: str  # "builtin" or "marketplace"
    duration_seconds: float
    tokens_used: int
    cost_usd: float
    quality_score: float  # 0.0-10.0
    model_used: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Additional metrics
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    task_suitability: str = ""  # "excellent", "good", "fair", "poor"


@dataclass
class ComparisonReport:
    """Comparison report for multiple agents."""

    task_description: str
    agents_compared: int
    results: List[AgentPerformanceMetrics]
    winner: Optional[str] = None  # agent_id of best performer
    recommendation: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "task_description": self.task_description,
            "agents_compared": self.agents_compared,
            "results": [
                {
                    "agent_id": r.agent_id,
                    "agent_name": r.agent_name,
                    "source": r.source,
                    "duration_seconds": r.duration_seconds,
                    "tokens_used": r.tokens_used,
                    "cost_usd": r.cost_usd,
                    "quality_score": r.quality_score,
                    "model_used": r.model_used,
                    "strengths": r.strengths,
                    "weaknesses": r.weaknesses,
                    "task_suitability": r.task_suitability,
                }
                for r in self.results
            ],
            "winner": self.winner,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat(),
        }


class CrossRepoAnalytics:
    """
    Analytics across claude-force and wshobson/agents.

    Features:
    - Agent performance comparison
    - Cost vs quality analysis
    - Speed vs quality tradeoffs
    - Recommendation engine
    - Historical metrics tracking
    """

    # Model-based cost estimates (per 1M tokens)
    MODEL_COSTS = {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    }

    # Typical agent characteristics (for simulation/estimation)
    AGENT_PROFILES = {
        "frontend-architect": {
            "typical_duration": 45,
            "typical_tokens": 12500,
            "model": "claude-3-5-sonnet-20241022",
            "quality_range": (8.0, 9.5),
            "strengths": ["Comprehensive architecture", "Best practices", "Modern frameworks"],
            "weaknesses": ["Longer response time", "Higher cost"],
        },
        "backend-architect": {
            "typical_duration": 50,
            "typical_tokens": 15000,
            "model": "claude-3-5-sonnet-20241022",
            "quality_range": (8.5, 9.5),
            "strengths": ["Scalable design", "Security focus", "Performance optimization"],
            "weaknesses": ["Longer response time", "Higher token usage"],
        },
        "code-reviewer": {
            "typical_duration": 40,
            "typical_tokens": 10000,
            "model": "claude-3-5-sonnet-20241022",
            "quality_range": (8.0, 9.0),
            "strengths": ["Thorough analysis", "OWASP coverage", "Detailed recommendations"],
            "weaknesses": ["Higher cost for simple reviews"],
        },
        # Simulated marketplace agents (faster, cheaper, but simpler)
        "quick-frontend": {
            "typical_duration": 18,
            "typical_tokens": 4500,
            "model": "claude-3-haiku-20240307",
            "quality_range": (6.5, 7.5),
            "strengths": ["Very fast", "Low cost", "Good for quick checks"],
            "weaknesses": ["Less detailed", "May miss edge cases"],
        },
        "quick-backend": {
            "typical_duration": 20,
            "typical_tokens": 5000,
            "model": "claude-3-haiku-20240307",
            "quality_range": (6.5, 7.5),
            "strengths": ["Fast iteration", "Cost effective", "Basic validation"],
            "weaknesses": ["Limited depth", "May miss complex issues"],
        },
    }

    def __init__(self, metrics_dir: Optional[Path] = None):
        """
        Initialize analytics manager.

        Args:
            metrics_dir: Directory for storing metrics
        """
        self.metrics_dir = metrics_dir or Path(".claude/metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def compare_agents(
        self, task: str, agents: List[str], simulate: bool = True
    ) -> ComparisonReport:
        """
        Compare multiple agents on same task.

        Args:
            task: Task description
            agents: List of agent IDs to compare
            simulate: Use simulated metrics (for demo/estimation)

        Returns:
            ComparisonReport with performance comparison
        """
        results = []

        for agent_id in agents:
            if simulate:
                metrics = self._simulate_agent_performance(agent_id, task)
            else:
                # In production, would actually run the agent
                metrics = self._run_agent_and_measure(agent_id, task)

            results.append(metrics)

        # Determine winner (best quality-to-cost ratio)
        winner = self._determine_winner(results)

        # Generate recommendation
        recommendation = self._generate_recommendation(task, results, winner)

        report = ComparisonReport(
            task_description=task,
            agents_compared=len(agents),
            results=results,
            winner=winner,
            recommendation=recommendation,
        )

        # Save report
        self._save_report(report)

        return report

    def _simulate_agent_performance(self, agent_id: str, task: str) -> AgentPerformanceMetrics:
        """
        Simulate agent performance metrics.

        This provides realistic estimates based on agent profiles.
        In production, replace with actual agent execution.
        """
        import random

        # Get agent profile or use default
        profile = self.AGENT_PROFILES.get(
            agent_id,
            {
                "typical_duration": 30,
                "typical_tokens": 8000,
                "model": "claude-3-5-sonnet-20241022",
                "quality_range": (7.0, 8.5),
                "strengths": ["General purpose"],
                "weaknesses": ["No specialization"],
            },
        )

        # Add some randomness (±20%)
        duration = profile["typical_duration"] * random.uniform(0.8, 1.2)
        tokens = int(profile["typical_tokens"] * random.uniform(0.8, 1.2))
        quality = random.uniform(*profile["quality_range"])

        # Calculate cost
        model = profile["model"]
        cost_info = self.MODEL_COSTS.get(model, self.MODEL_COSTS["claude-3-5-sonnet-20241022"])

        # Assume 70% input, 30% output ratio
        input_tokens = int(tokens * 0.7)
        output_tokens = int(tokens * 0.3)

        cost = (input_tokens / 1_000_000) * cost_info["input"] + (
            output_tokens / 1_000_000
        ) * cost_info["output"]

        # Determine source (builtin vs marketplace)
        builtin_agents = list(self.AGENT_PROFILES.keys())[:3]  # First 3 are builtin
        source = "builtin" if agent_id in builtin_agents else "marketplace"

        # Task suitability based on quality
        if quality >= 8.5:
            suitability = "excellent"
        elif quality >= 7.5:
            suitability = "good"
        elif quality >= 6.5:
            suitability = "fair"
        else:
            suitability = "poor"

        return AgentPerformanceMetrics(
            agent_id=agent_id,
            agent_name=agent_id.replace("-", " ").title(),
            source=source,
            duration_seconds=duration,
            tokens_used=tokens,
            cost_usd=cost,
            quality_score=quality,
            model_used=model,
            strengths=profile.get("strengths", []),
            weaknesses=profile.get("weaknesses", []),
            task_suitability=suitability,
        )

    def _run_agent_and_measure(self, agent_id: str, task: str) -> AgentPerformanceMetrics:
        """
        Actually run agent and measure performance.

        This would integrate with AgentOrchestrator to run agents
        and collect real metrics. For now, falls back to simulation.

        Note: Full agent execution integration is a planned enhancement.
        Current simulation provides realistic metrics for testing and demos.
        """
        logger.info(f"Running agent '{agent_id}' in simulation mode for task: {task[:50]}...")
        return self._simulate_agent_performance(agent_id, task)

    def _determine_winner(self, results: List[AgentPerformanceMetrics]) -> Optional[str]:
        """
        Determine best agent based on quality-to-cost ratio.

        Args:
            results: List of agent metrics

        Returns:
            Agent ID of winner
        """
        if not results:
            return None

        # Calculate score: quality / (cost * duration_factor)
        scored_results = []
        for r in results:
            # Normalize duration to 0-1 scale (assuming max 120s)
            duration_factor = min(r.duration_seconds / 120.0, 1.0)

            # Quality-to-cost ratio with duration penalty
            score = r.quality_score / (r.cost_usd + 0.01) / (1.0 + duration_factor)

            scored_results.append((r.agent_id, score))

        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[1], reverse=True)

        return scored_results[0][0]

    def _generate_recommendation(
        self, task: str, results: List[AgentPerformanceMetrics], winner: Optional[str]
    ) -> str:
        """Generate recommendation text."""
        if not results:
            return "No agents to compare"

        if not winner:
            return "Unable to determine best agent"

        winner_metrics = next((r for r in results if r.agent_id == winner), None)
        if not winner_metrics:
            return "Winner metrics not found"

        # Build recommendation
        recommendation = f"Recommended: {winner_metrics.agent_name} "
        recommendation += f"({winner_metrics.source})\n"
        recommendation += f"Quality: {winner_metrics.quality_score:.1f}/10, "
        recommendation += f"Cost: ${winner_metrics.cost_usd:.3f}, "
        recommendation += f"Duration: {winner_metrics.duration_seconds:.0f}s"

        # Add use case guidance
        if winner_metrics.cost_usd < 0.01:
            recommendation += "\nBest for: Quick iterations, prototyping, frequent use"
        elif winner_metrics.quality_score >= 8.5:
            recommendation += (
                "\nBest for: Production code, critical systems, comprehensive analysis"
            )
        else:
            recommendation += "\nBest for: General purpose development, balanced needs"

        return recommendation

    def _save_report(self, report: ComparisonReport):
        """Save comparison report to metrics directory."""
        timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
        report_file = self.metrics_dir / f"comparison_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

        logger.info(f"Saved comparison report to {report_file}")

    def get_agent_statistics(self, agent_id: str, days: int = 30) -> Dict:
        """
        Get historical statistics for an agent.

        Args:
            agent_id: Agent to analyze
            days: Number of days to look back

        Returns:
            Statistics dictionary

        Note: Historical metrics aggregation is a planned enhancement.
        Requires persistent storage backend (database) for time-series data.
        Current implementation returns placeholder data.
        """
        logger.info(
            f"Historical metrics for '{agent_id}' (last {days} days) - Feature in development"
        )
        return {
            "agent_id": agent_id,
            "period_days": days,
            "total_runs": 0,
            "avg_duration": 0.0,
            "avg_cost": 0.0,
            "avg_quality": 0.0,
            "status": "feature_in_development",
            "note": "Historical metrics aggregation requires database backend (planned enhancement)",
        }

    def recommend_agent_for_task(
        self, task: str, priority: str = "balanced"  # "speed", "cost", "quality", "balanced"
    ) -> Dict:
        """
        Recommend best agent based on task and priority.

        Args:
            task: Task description
            priority: Optimization priority

        Returns:
            Recommendation dictionary
        """
        from claude_force.agent_router import get_agent_router

        router = get_agent_router()
        matches = router.recommend_agents(task, top_k=3)

        if not matches:
            return {"recommendation": None, "reason": "No suitable agents found"}

        # For now, return top match with priority context
        top_match = matches[0]

        priority_guidance = {
            "speed": "Consider using Haiku-based agents for faster response",
            "cost": "Haiku-based agents offer best cost efficiency",
            "quality": "Sonnet/Opus-based agents provide highest quality",
            "balanced": "Balance between speed, cost, and quality",
        }

        return {
            "recommendation": top_match.agent_id,
            "agent_name": top_match.agent_name,
            "confidence": top_match.confidence,
            "priority": priority,
            "guidance": priority_guidance.get(priority, ""),
        }


def get_analytics_manager(metrics_dir: Optional[Path] = None) -> CrossRepoAnalytics:
    """
    Get singleton analytics manager instance.

    Args:
        metrics_dir: Metrics directory

    Returns:
        CrossRepoAnalytics instance
    """
    return CrossRepoAnalytics(metrics_dir=metrics_dir)
