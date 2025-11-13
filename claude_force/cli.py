"""
Command-Line Interface for Claude-Force

Provides command-line access to the multi-agent orchestration system.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from .orchestrator import AgentOrchestrator


def cmd_list_agents(args):
    """List all available agents"""
    try:
        orchestrator = AgentOrchestrator(config_path=args.config)
        agents = orchestrator.list_agents()

        print("\n📋 Available Agents\n")
        print(f"{'Name':<30} {'Priority':<10} {'Domains'}")
        print("-" * 80)

        for agent in agents:
            domains = ", ".join(agent['domains'][:3])
            if len(agent['domains']) > 3:
                domains += "..."
            priority_label = {1: "Critical", 2: "High", 3: "Medium"}.get(agent['priority'], "Low")
            print(f"{agent['name']:<30} {priority_label:<10} {domains}")

        print(f"\nTotal: {len(agents)} agents")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_workflows(args):
    """List all available workflows"""
    try:
        orchestrator = AgentOrchestrator(config_path=args.config)
        workflows = orchestrator.list_workflows()

        print("\n🔄 Available Workflows\n")

        for name, agents in workflows.items():
            print(f"  {name}:")
            print(f"    Agents: {len(agents)}")
            print(f"    Flow: {' → '.join(agents)}")
            print()

        print(f"Total: {len(workflows)} workflows")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_agent_info(args):
    """Show detailed information about an agent"""
    try:
        orchestrator = AgentOrchestrator(config_path=args.config)
        info = orchestrator.get_agent_info(args.agent)

        print(f"\n📄 Agent: {info['name']}\n")
        print(f"File: {info['file']}")
        print(f"Contract: {info['contract']}")
        print(f"Priority: {info['priority']}")
        print(f"Domains: {', '.join(info['domains'])}")
        print(f"\nDescription:\n{info['description']}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_recommend(args):
    """Recommend agents for a task using semantic similarity"""
    try:
        # Read task
        task = args.task
        if args.task_file:
            with open(args.task_file, 'r') as f:
                task = f.read()
        elif not task and not sys.stdin.isatty():
            task = sys.stdin.read()

        if not task:
            print("❌ Error: Task description required", file=sys.stderr)
            print("   Provide with --task, --task-file, or via stdin")
            sys.exit(1)

        orchestrator = AgentOrchestrator(config_path=args.config)

        print(f"\n🔍 Analyzing task (semantic matching)...\n")

        # Get recommendations
        recommendations = orchestrator.recommend_agents(
            task,
            top_k=args.top_k,
            min_confidence=args.min_confidence
        )

        if not recommendations:
            print("❌ No agents match this task with sufficient confidence")
            print(f"   Try lowering --min-confidence (current: {args.min_confidence})")
            sys.exit(1)

        # Display recommendations
        print(f"📊 Top {len(recommendations)} Agent Recommendations:\n")
        for i, rec in enumerate(recommendations, 1):
            confidence_pct = rec['confidence'] * 100
            bar_length = int(confidence_pct / 5)  # 0-20 chars
            bar = "█" * bar_length + "░" * (20 - bar_length)

            print(f"{i}. {rec['agent']}")
            print(f"   Confidence: {bar} {confidence_pct:.1f}%")
            print(f"   Reasoning: {rec['reasoning']}")
            print(f"   Domains: {', '.join(rec['domains'])}")
            print()

        # Explain top choice if requested
        if args.explain and recommendations:
            top_agent = recommendations[0]['agent']
            print(f"\n💡 Detailed Explanation for '{top_agent}':\n")
            explanation = orchestrator.explain_agent_selection(task, top_agent)
            print(f"Selected: {'Yes' if explanation['selected'] else 'No'}")
            print(f"Rank: {explanation.get('rank', 'N/A')}")
            print(f"Confidence: {explanation.get('confidence', 0):.3f}")
            print(f"Reasoning: {explanation.get('reasoning', 'N/A')}")

            if 'all_candidates' in explanation:
                print(f"\nAll Candidates:")
                for candidate in explanation['all_candidates']:
                    print(f"  • {candidate['agent']}: {candidate['confidence']:.3f}")

        # JSON output if requested
        if args.json:
            import json
            print("\n" + json.dumps(recommendations, indent=2))

    except ImportError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        print("\n💡 To use semantic agent selection, install sentence-transformers:")
        print("   pip install sentence-transformers")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_run_agent(args):
    """Run a single agent"""
    try:
        # Read task from file or stdin if not provided
        task = args.task
        if args.task_file:
            with open(args.task_file, 'r') as f:
                task = f.read()
        elif not task and not sys.stdin.isatty():
            task = sys.stdin.read()

        if not task:
            print("❌ Error: No task provided. Use --task, --task-file, or pipe input", file=sys.stderr)
            sys.exit(1)

        print(f"🚀 Running agent: {args.agent}\n")

        orchestrator = AgentOrchestrator(
            config_path=args.config,
            anthropic_api_key=args.api_key
        )

        result = orchestrator.run_agent(
            agent_name=args.agent,
            task=task,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )

        if result.success:
            print("✅ Agent completed successfully\n")
            print(result.output)

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(result.output)
                print(f"\n📝 Output saved to: {args.output}")

            if args.json:
                print(f"\n📊 Metadata:\n{json.dumps(result.metadata, indent=2)}")

        else:
            print("❌ Agent execution failed\n", file=sys.stderr)
            for error in result.errors:
                print(f"  {error}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_run_workflow(args):
    """Run a multi-agent workflow"""
    try:
        # Read task
        task = args.task
        if args.task_file:
            with open(args.task_file, 'r') as f:
                task = f.read()

        if not task:
            print("❌ Error: No task provided. Use --task or --task-file", file=sys.stderr)
            sys.exit(1)

        print(f"🔄 Running workflow: {args.workflow}\n")

        orchestrator = AgentOrchestrator(
            config_path=args.config,
            anthropic_api_key=args.api_key
        )

        results = orchestrator.run_workflow(
            workflow_name=args.workflow,
            task=task,
            pass_output_to_next=not args.no_pass_output
        )

        print("\n" + "=" * 80)
        print("Workflow Summary")
        print("=" * 80)

        total_tokens = 0
        for i, result in enumerate(results, 1):
            status = "✅" if result.success else "❌"
            print(f"{i}. {status} {result.agent_name}")
            if result.success:
                total_tokens += result.metadata.get('tokens_used', 0)

        print(f"\nTotal tokens used: {total_tokens:,}")

        if args.output:
            # Save all results to JSON
            output_data = {
                "workflow": args.workflow,
                "task": task,
                "results": [r.to_dict() for r in results]
            }
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"📝 Results saved to: {args.output}")

        # Exit with error if any agent failed
        if any(not r.success for r in results):
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_metrics(args):
    """Show performance metrics"""
    try:
        orchestrator = AgentOrchestrator(config_path=args.config)

        if not orchestrator.tracker:
            print("❌ Performance tracking is not enabled", file=sys.stderr)
            sys.exit(1)

        print("\n" + "=" * 70)
        print("PERFORMANCE METRICS")
        print("=" * 70 + "\n")

        # Summary
        if args.command == "summary":
            summary = orchestrator.get_performance_summary(hours=args.hours)

            print(f"Time Period: {summary.get('time_period', 'all time')}\n")
            print(f"Total Executions:     {summary['total_executions']}")
            print(f"Successful:           {summary['successful_executions']}")
            print(f"Failed:               {summary['failed_executions']}")
            print(f"Success Rate:         {summary['success_rate']:.1%}\n")

            print(f"Total Tokens:         {summary['total_tokens']:,}")
            print(f"  Input Tokens:       {summary['total_input_tokens']:,}")
            print(f"  Output Tokens:      {summary['total_output_tokens']:,}\n")

            print(f"Total Cost:           ${summary['total_cost']:.4f}")
            print(f"Avg Cost/Execution:   ${summary['avg_cost_per_execution']:.4f}")
            print(f"Avg Execution Time:   {summary['avg_execution_time_ms']:.0f}ms")

        # Per-agent stats
        elif args.command == "agents":
            stats = orchestrator.get_agent_performance()

            if not stats:
                print("No agent executions recorded yet")
                return

            print("Per-Agent Statistics:\n")
            print(f"{'Agent':<30} {'Runs':>6} {'Success':>8} {'Avg Time':>10} {'Cost':>10}")
            print("-" * 70)

            for agent, data in sorted(stats.items(), key=lambda x: x[1]['total_cost'], reverse=True):
                success_rate = f"{data['success_rate']:.1%}"
                avg_time = f"{data['avg_execution_time_ms']:.0f}ms"
                cost = f"${data['total_cost']:.4f}"

                print(f"{agent:<30} {data['executions']:>6} {success_rate:>8} {avg_time:>10} {cost:>10}")

        # Cost breakdown
        elif args.command == "costs":
            costs = orchestrator.get_cost_breakdown()

            print(f"Total Cost: ${costs['total']:.4f}\n")

            print("By Agent:")
            for agent, cost in list(costs['by_agent'].items())[:10]:
                pct = (cost / costs['total'] * 100) if costs['total'] > 0 else 0
                bar_length = int(pct / 2)  # 0-50 chars
                bar = "█" * bar_length

                print(f"  {agent:<30} ${cost:>8.4f} {bar} {pct:.1f}%")

            if len(costs['by_agent']) > 10:
                print(f"  ... and {len(costs['by_agent']) - 10} more agents")

            print("\nBy Model:")
            for model, cost in costs['by_model'].items():
                pct = (cost / costs['total'] * 100) if costs['total'] > 0 else 0
                print(f"  {model:<40} ${cost:>8.4f} ({pct:.1f}%)")

        # Export
        elif args.command == "export":
            orchestrator.export_performance_metrics(args.output, args.format)
            print(f"✅ Metrics exported to: {args.output}")

        print("\n" + "=" * 70)

    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_init(args):
    """Initialize a new claude-force project"""
    try:
        target_dir = Path(args.directory)

        if target_dir.exists() and list(target_dir.iterdir()):
            print(f"❌ Error: Directory {target_dir} is not empty", file=sys.stderr)
            sys.exit(1)

        print(f"🚀 Initializing claude-force project in {target_dir}\n")

        # This would copy template files from the package
        # For now, just give instructions
        print("To initialize a claude-force project:")
        print("1. Clone the repository: git clone https://github.com/YOUR_USERNAME/claude-force.git")
        print("2. Or copy the .claude/ directory from an existing project")
        print("\nComing soon: claude-force init will create a new project from template")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="claude-force",
        description="Multi-Agent Orchestration System for Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all agents
  claude-force list agents

  # Recommend agents for a task (semantic matching)
  claude-force recommend --task "Fix authentication bug in login endpoint"

  # Run a single agent
  claude-force run agent code-reviewer --task "Review this code: def foo(): pass"

  # Run a workflow
  claude-force run workflow bug-fix --task-file task.md

  # Get agent information
  claude-force info code-reviewer

  # View performance metrics
  claude-force metrics summary
  claude-force metrics agents
  claude-force metrics costs

For more information: https://github.com/YOUR_USERNAME/claude-force
        """
    )

    parser.add_argument(
        "--config",
        default=".claude/claude.json",
        help="Path to claude.json configuration (default: .claude/claude.json)"
    )

    parser.add_argument(
        "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List agents or workflows")
    list_subparsers = list_parser.add_subparsers(dest="list_type")

    list_agents_parser = list_subparsers.add_parser("agents", help="List all agents")
    list_agents_parser.set_defaults(func=cmd_list_agents)

    list_workflows_parser = list_subparsers.add_parser("workflows", help="List all workflows")
    list_workflows_parser.set_defaults(func=cmd_list_workflows)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show agent information")
    info_parser.add_argument("agent", help="Agent name")
    info_parser.set_defaults(func=cmd_agent_info)

    # Recommend command
    recommend_parser = subparsers.add_parser("recommend", help="Recommend agents for a task (semantic matching)")
    recommend_parser.add_argument("--task", help="Task description")
    recommend_parser.add_argument("--task-file", help="Read task from file")
    recommend_parser.add_argument("--top-k", type=int, default=3, help="Number of recommendations (default: 3)")
    recommend_parser.add_argument("--min-confidence", type=float, default=0.3, help="Minimum confidence threshold 0-1 (default: 0.3)")
    recommend_parser.add_argument("--explain", action="store_true", help="Explain top recommendation")
    recommend_parser.add_argument("--json", action="store_true", help="Output as JSON")
    recommend_parser.set_defaults(func=cmd_recommend)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run agent or workflow")
    run_subparsers = run_parser.add_subparsers(dest="run_type")

    # Run agent
    run_agent_parser = run_subparsers.add_parser("agent", help="Run a single agent")
    run_agent_parser.add_argument("agent", help="Agent name")
    run_agent_parser.add_argument("--task", help="Task description")
    run_agent_parser.add_argument("--task-file", help="Read task from file")
    run_agent_parser.add_argument("--output", "-o", help="Save output to file")
    run_agent_parser.add_argument("--model", default="claude-3-5-sonnet-20241022", help="Claude model to use")
    run_agent_parser.add_argument("--max-tokens", type=int, default=4096, help="Maximum tokens")
    run_agent_parser.add_argument("--temperature", type=float, default=1.0, help="Temperature (0.0-1.0)")
    run_agent_parser.add_argument("--json", action="store_true", help="Output metadata as JSON")
    run_agent_parser.set_defaults(func=cmd_run_agent)

    # Run workflow
    run_workflow_parser = run_subparsers.add_parser("workflow", help="Run a multi-agent workflow")
    run_workflow_parser.add_argument("workflow", help="Workflow name")
    run_workflow_parser.add_argument("--task", help="Task description")
    run_workflow_parser.add_argument("--task-file", help="Read task from file")
    run_workflow_parser.add_argument("--output", "-o", help="Save results to file (JSON)")
    run_workflow_parser.add_argument("--no-pass-output", action="store_true", help="Don't pass output between agents")
    run_workflow_parser.set_defaults(func=cmd_run_workflow)

    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Show performance metrics")
    metrics_subparsers = metrics_parser.add_subparsers(dest="command")

    # Metrics summary
    summary_parser = metrics_subparsers.add_parser("summary", help="Show summary statistics")
    summary_parser.add_argument("--hours", type=int, help="Only last N hours (default: all time)")
    summary_parser.set_defaults(func=cmd_metrics)

    # Metrics per agent
    agents_parser = metrics_subparsers.add_parser("agents", help="Show per-agent statistics")
    agents_parser.set_defaults(func=cmd_metrics)

    # Cost breakdown
    costs_parser = metrics_subparsers.add_parser("costs", help="Show cost breakdown")
    costs_parser.set_defaults(func=cmd_metrics)

    # Export metrics
    export_parser = metrics_subparsers.add_parser("export", help="Export metrics to file")
    export_parser.add_argument("output", help="Output file path")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    export_parser.set_defaults(func=cmd_metrics)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new claude-force project")
    init_parser.add_argument("directory", nargs="?", default=".", help="Target directory")
    init_parser.set_defaults(func=cmd_init)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
