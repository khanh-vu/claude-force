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

  # Run a single agent
  claude-force run agent code-reviewer --task "Review this code: def foo(): pass"

  # Run a workflow
  claude-force run workflow bug-fix --task-file task.md

  # Get agent information
  claude-force info code-reviewer

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
