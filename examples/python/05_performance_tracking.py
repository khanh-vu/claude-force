#!/usr/bin/env python3
"""
Performance Tracking Example

Demonstrates how to use built-in performance tracking to monitor execution time,
token usage, and costs.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from claude_force import AgentOrchestrator


def main():
    """Demonstrate performance tracking"""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    print("=" * 70)
    print("PERFORMANCE TRACKING EXAMPLE")
    print("=" * 70 + "\n")

    # Initialize orchestrator (tracking enabled by default)
    try:
        orchestrator = AgentOrchestrator(enable_tracking=True)
        print("✅ AgentOrchestrator initialized with performance tracking\n")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)

    # Run a few test executions
    tasks = [
        ("code-reviewer", "Review this function for security:\ndef login(user, pass): return True"),
        ("bug-investigator", "500 error in /api/users endpoint"),
        ("security-specialist", "Check auth code for SQL injection"),
    ]

    print("Running test executions...\n")

    for agent_name, task in tasks:
        try:
            print(f"🔄 Running {agent_name}...")
            result = orchestrator.run_agent(
                agent_name=agent_name, task=task, model="claude-3-5-sonnet-20241022"
            )

            status = "✅" if result.success else "❌"
            time_ms = result.metadata.get("execution_time_ms", 0)
            tokens = result.metadata.get("tokens_used", 0)

            print(f"   {status} Completed in {time_ms:.0f}ms, {tokens:,} tokens\n")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            continue

    # View performance summary
    print("=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70 + "\n")

    try:
        summary = orchestrator.get_performance_summary()

        print(f"Total Executions:     {summary['total_executions']}")
        print(f"Successful:           {summary['successful_executions']}")
        print(f"Failed:               {summary['failed_executions']}")
        print(f"Success Rate:         {summary['success_rate']:.1%}\n")

        print(f"Total Tokens:         {summary['total_tokens']:,}")
        print(f"  Input Tokens:       {summary['total_input_tokens']:,}")
        print(f"  Output Tokens:      {summary['total_output_tokens']:,}\n")

        print(f"💰 Total Cost:        ${summary['total_cost']:.4f}")
        print(f"💰 Avg Cost/Execution: ${summary['avg_cost_per_execution']:.4f}")
        print(f"⏱️  Avg Execution Time: {summary['avg_execution_time_ms']:.0f}ms")

    except Exception as e:
        print(f"❌ Error getting summary: {e}")

    # View per-agent statistics
    print("\n" + "=" * 70)
    print("PER-AGENT STATISTICS")
    print("=" * 70 + "\n")

    try:
        agent_stats = orchestrator.get_agent_performance()

        print(f"{'Agent':<30} {'Runs':>6} {'Success':>8} {'Avg Time':>10} {'Cost':>10}")
        print("-" * 70)

        for agent, data in sorted(
            agent_stats.items(), key=lambda x: x[1]["executions"], reverse=True
        ):
            success_rate = f"{data['success_rate']:.1%}"
            avg_time = f"{data['avg_execution_time_ms']:.0f}ms"
            cost = f"${data['total_cost']:.4f}"

            print(
                f"{agent:<30} {data['executions']:>6} {success_rate:>8} {avg_time:>10} {cost:>10}"
            )

    except Exception as e:
        print(f"❌ Error getting agent stats: {e}")

    # View cost breakdown
    print("\n" + "=" * 70)
    print("COST BREAKDOWN")
    print("=" * 70 + "\n")

    try:
        costs = orchestrator.get_cost_breakdown()

        print(f"Total Cost: ${costs['total']:.4f}\n")

        print("By Agent:")
        for agent, cost in costs["by_agent"].items():
            pct = (cost / costs["total"] * 100) if costs["total"] > 0 else 0
            bar_length = int(pct / 2)  # 0-50 chars
            bar = "█" * bar_length

            print(f"  {agent:<30} ${cost:>8.4f} {bar} {pct:.1f}%")

        print("\nBy Model:")
        for model, cost in costs["by_model"].items():
            pct = (cost / costs["total"] * 100) if costs["total"] > 0 else 0
            print(f"  {model:<40} ${cost:>8.4f} ({pct:.1f}%)")

    except Exception as e:
        print(f"❌ Error getting cost breakdown: {e}")

    # Export metrics
    print("\n" + "=" * 70)
    print("EXPORTING METRICS")
    print("=" * 70 + "\n")

    try:
        # Export to JSON
        json_path = "metrics_example.json"
        orchestrator.export_performance_metrics(json_path, format="json")
        print(f"✅ Exported to: {json_path}")

        # Export to CSV
        csv_path = "metrics_example.csv"
        orchestrator.export_performance_metrics(csv_path, format="csv")
        print(f"✅ Exported to: {csv_path}")

    except Exception as e:
        print(f"❌ Error exporting: {e}")

    # Usage summary
    print("\n" + "=" * 70)
    print("USAGE IN YOUR CODE")
    print("=" * 70 + "\n")

    print(
        """
# Enable tracking (default)
orchestrator = AgentOrchestrator(enable_tracking=True)

# Run agents (tracking automatic)
result = orchestrator.run_agent("code-reviewer", task="...")

# View metrics
summary = orchestrator.get_performance_summary(hours=24)
agent_stats = orchestrator.get_agent_performance()
costs = orchestrator.get_cost_breakdown()

# Export for analysis
orchestrator.export_performance_metrics("metrics.json", format="json")
orchestrator.export_performance_metrics("metrics.csv", format="csv")

# CLI usage:
# claude-force metrics summary
# claude-force metrics agents
# claude-force metrics costs
# claude-force metrics export metrics.json
    """
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
