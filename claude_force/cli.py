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
    """Run a single agent with optional hybrid model orchestration"""
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

        # Use HybridOrchestrator if auto-select-model is enabled
        if args.auto_select_model:
            from .hybrid_orchestrator import HybridOrchestrator

            orchestrator = HybridOrchestrator(
                config_path=args.config,
                anthropic_api_key=args.api_key,
                auto_select_model=True,
                prefer_cheaper=True,
                cost_threshold=args.cost_threshold
            )

            # Show cost estimate if requested
            if args.estimate_cost:
                estimate = orchestrator.estimate_cost(task, args.agent, args.model)

                print("📊 Cost Estimate:\n")
                print(f"   Model: {estimate.model}")
                print(f"   Estimated tokens: {estimate.estimated_input_tokens:,} input + {estimate.estimated_output_tokens:,} output")
                print(f"   Estimated cost: ${estimate.estimated_cost:.6f}\n")

                if not args.yes:
                    proceed = input("Proceed? [Y/n]: ").strip().lower()
                    if proceed and proceed != 'y':
                        print("Cancelled")
                        sys.exit(0)

            result = orchestrator.run_agent(
                agent_name=args.agent,
                task=task,
                model=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                auto_select=True
            )

        else:
            # Use standard orchestrator
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
    """Initialize a new claude-force project with intelligent template selection"""
    try:
        from .quick_start import get_quick_start_orchestrator

        target_dir = Path(args.directory if args.directory != '.' else Path.cwd())
        claude_dir = target_dir / ".claude"

        # Check if .claude already exists
        if claude_dir.exists():
            if not args.force:
                print(f"❌ Error: .claude directory already exists in {target_dir}", file=sys.stderr)
                print("   Use --force to reinitialize", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"⚠️  Warning: Reinitializing existing .claude directory\n")

        print(f"🚀 Initializing claude-force project in {target_dir}\n")

        # Initialize orchestrator
        orchestrator = get_quick_start_orchestrator(use_semantic=not args.no_semantic)

        # Get project details
        if args.interactive:
            # Interactive mode
            print("📋 Project Setup (Interactive Mode)\n")

            project_name = input("Project name: ").strip()
            if not project_name:
                project_name = target_dir.name
                print(f"   Using directory name: {project_name}")

            print("\nDescribe your project:")
            print("(What are you building? Be specific about features and goals)")
            description = input("> ").strip()

            if not description:
                print("❌ Error: Project description is required", file=sys.stderr)
                sys.exit(1)

            tech_input = input("\nTech stack (comma-separated, optional): ").strip()
            tech_stack = [t.strip() for t in tech_input.split(",")] if tech_input else None

        else:
            # Non-interactive mode
            project_name = args.name or target_dir.name
            description = args.description

            if not description:
                print("❌ Error: --description required in non-interactive mode", file=sys.stderr)
                sys.exit(1)

            tech_stack = args.tech.split(",") if args.tech else None

        # Match templates
        print(f"\n🔍 Finding best templates for your project...\n")

        if args.template:
            # User specified template
            template = None
            for t in orchestrator.templates:
                if t.id == args.template:
                    template = t
                    break

            if not template:
                print(f"❌ Error: Template '{args.template}' not found", file=sys.stderr)
                print(f"\nAvailable templates:")
                for t in orchestrator.templates:
                    print(f"  - {t.id}: {t.name}")
                sys.exit(1)

            matched_templates = [template]
        else:
            # Auto-match templates
            matched_templates = orchestrator.match_templates(
                description=description,
                tech_stack=tech_stack,
                top_k=3
            )

        # Display matched templates
        if len(matched_templates) > 1:
            print("📊 Recommended Templates:\n")
            for i, template in enumerate(matched_templates, 1):
                confidence_pct = template.confidence * 100
                bar_length = int(confidence_pct / 5)
                bar = "█" * bar_length + "░" * (20 - bar_length)

                print(f"{i}. {template.name}")
                print(f"   Match: {bar} {confidence_pct:.1f}%")
                print(f"   {template.description}")
                print(f"   Difficulty: {template.difficulty} | Setup: {template.estimated_setup_time}")
                print(f"   Agents: {len(template.agents)} | Workflows: {len(template.workflows)}")
                print()

            if args.interactive:
                choice = input(f"Select template (1-{len(matched_templates)}) [1]: ").strip()
                choice = int(choice) if choice else 1
                if choice < 1 or choice > len(matched_templates):
                    print(f"❌ Error: Invalid choice", file=sys.stderr)
                    sys.exit(1)
                selected_template = matched_templates[choice - 1]
            else:
                selected_template = matched_templates[0]
        else:
            selected_template = matched_templates[0]

        print(f"✅ Selected: {selected_template.name}\n")

        # Generate configuration
        config = orchestrator.generate_config(
            template=selected_template,
            project_name=project_name,
            description=description
        )

        # Initialize project
        print("📁 Creating project structure...\n")
        result = orchestrator.initialize_project(
            config=config,
            output_dir=str(claude_dir),
            create_examples=not args.no_examples
        )

        # Display results
        print("✅ Project initialized successfully!\n")
        print(f"📂 Created {len(result['created_files'])} files:")
        for file in result['created_files']:
            rel_path = Path(file).relative_to(target_dir)
            print(f"   ✓ {rel_path}")

        print(f"\n📋 Configuration:")
        print(f"   Name: {config.name}")
        print(f"   Template: {config.template_id}")
        print(f"   Agents: {len(config.agents)}")
        print(f"   Workflows: {len(config.workflows)}")
        print(f"   Skills: {len(config.skills)}")

        print(f"\n🚀 Next Steps:")
        print(f"   1. Edit {claude_dir / 'task.md'} with your first task")
        print(f"   2. Run: claude-force recommend --task-file {claude_dir / 'task.md'}")
        print(f"   3. Run: claude-force run agent <agent-name> --task-file {claude_dir / 'task.md'}")
        print(f"   4. Review output in {claude_dir / 'work.md'}")

        print(f"\n📚 Learn More:")
        print(f"   • README: {claude_dir / 'README.md'}")
        print(f"   • Agents: {claude_dir / 'agents/'}")
        print(f"   • Workflows: claude-force list workflows")

    except ImportError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if "sentence_transformers" in str(e):
            print("\n💡 For semantic template matching, install sentence-transformers:")
            print("   pip install sentence-transformers")
            print("\nOr use --no-semantic for keyword-based matching")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


def cmd_marketplace_list(args):
    """List available plugins from marketplace"""
    try:
        from .marketplace import get_marketplace_manager

        manager = get_marketplace_manager()
        plugins = manager.list_available(
            category=args.category,
            source=args.source,
            installed_only=args.installed
        )

        if not plugins:
            print("No plugins found matching criteria")
            return

        print(f"\n📦 Available Plugins ({len(plugins)})\n")
        print("=" * 80)

        current_category = None
        for plugin in sorted(plugins, key=lambda p: (p.category.value, p.name)):
            # Print category header
            if plugin.category.value != current_category:
                current_category = plugin.category.value
                print(f"\n{plugin.category.value.upper().replace('-', ' ')}")
                print("-" * 80)

            # Plugin details
            status = "✅ INSTALLED" if plugin.installed else ""
            print(f"\n{plugin.name} ({plugin.id}) {status}")
            print(f"  {plugin.description}")
            print(f"  Source: {plugin.source.value} | Version: {plugin.version}")
            print(f"  Agents: {len(plugin.agents)} | Skills: {len(plugin.skills)} | Workflows: {len(plugin.workflows)}")

        print("\n" + "=" * 80)
        print(f"\n💡 Install: claude-force marketplace install <plugin-id>")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_marketplace_search(args):
    """Search marketplace for plugins"""
    try:
        from .marketplace import get_marketplace_manager

        manager = get_marketplace_manager()
        results = manager.search(args.query)

        if not results:
            print(f"No plugins found matching '{args.query}'")
            return

        print(f"\n🔍 Search Results for '{args.query}' ({len(results)} found)\n")
        print("=" * 80)

        for plugin in results:
            status = "✅ INSTALLED" if plugin.installed else ""
            print(f"\n📦 {plugin.name} ({plugin.id}) {status}")
            print(f"   {plugin.description}")
            print(f"   Source: {plugin.source.value} | Category: {plugin.category.value}")
            print(f"   Agents: {', '.join(plugin.agents[:3])}" + (" ..." if len(plugin.agents) > 3 else ""))

        print("\n" + "=" * 80)
        print(f"\n💡 Install: claude-force marketplace install <plugin-id>")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_marketplace_install(args):
    """Install a plugin from marketplace"""
    try:
        from .marketplace import get_marketplace_manager

        manager = get_marketplace_manager()

        print(f"📦 Installing plugin '{args.plugin_id}'...\n")

        result = manager.install_plugin(
            plugin_id=args.plugin_id,
            force=args.force
        )

        if not result.success:
            print(f"❌ Installation failed", file=sys.stderr)
            for error in result.errors:
                print(f"   {error}", file=sys.stderr)
            for warning in result.warnings:
                print(f"⚠️  {warning}")
            sys.exit(1)

        print(f"✅ Successfully installed {result.plugin.name}")
        print(f"\n📊 Installation Summary:")
        print(f"   Agents added:    {result.agents_added}")
        print(f"   Skills added:    {result.skills_added}")
        print(f"   Workflows added: {result.workflows_added}")
        print(f"   Tools added:     {result.tools_added}")

        if result.plugin.agents:
            print(f"\n💡 Try running an agent:")
            print(f"   claude-force run agent {result.plugin.agents[0]} --task 'Your task'")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_marketplace_uninstall(args):
    """Uninstall a plugin"""
    try:
        from .marketplace import get_marketplace_manager

        manager = get_marketplace_manager()

        print(f"🗑️  Uninstalling plugin '{args.plugin_id}'...")

        success = manager.uninstall_plugin(args.plugin_id)

        if success:
            print(f"✅ Successfully uninstalled '{args.plugin_id}'")
        else:
            print(f"❌ Failed to uninstall '{args.plugin_id}'", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_marketplace_info(args):
    """Show detailed information about a plugin"""
    try:
        from .marketplace import get_marketplace_manager

        manager = get_marketplace_manager()
        plugin = manager.get_plugin(args.plugin_id)

        if not plugin:
            print(f"❌ Plugin '{args.plugin_id}' not found", file=sys.stderr)
            sys.exit(1)

        print(f"\n📦 {plugin.name}")
        print("=" * 80)
        print(f"\nID:          {plugin.id}")
        print(f"Version:     {plugin.version}")
        print(f"Source:      {plugin.source.value}")
        print(f"Category:    {plugin.category.value}")
        print(f"Installed:   {'Yes (v' + plugin.installed_version + ')' if plugin.installed else 'No'}")

        if plugin.author:
            print(f"Author:      {plugin.author}")
        if plugin.repository:
            print(f"Repository:  {plugin.repository}")

        print(f"\nDescription:")
        print(f"  {plugin.description}")

        if plugin.agents:
            print(f"\nAgents ({len(plugin.agents)}):")
            for agent in plugin.agents:
                print(f"  • {agent}")

        if plugin.skills:
            print(f"\nSkills ({len(plugin.skills)}):")
            for skill in plugin.skills:
                print(f"  • {skill}")

        if plugin.workflows:
            print(f"\nWorkflows ({len(plugin.workflows)}):")
            for workflow in plugin.workflows:
                print(f"  • {workflow}")

        if plugin.keywords:
            print(f"\nKeywords: {', '.join(plugin.keywords)}")

        if plugin.dependencies:
            print(f"\nDependencies: {', '.join(plugin.dependencies)}")

        print("\n" + "=" * 80)

        if not plugin.installed:
            print(f"\n💡 Install: claude-force marketplace install {plugin.id}")

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
    run_agent_parser = run_subparsers.add_parser("agent", help="Run a single agent with optional hybrid model orchestration")
    run_agent_parser.add_argument("agent", help="Agent name")
    run_agent_parser.add_argument("--task", help="Task description")
    run_agent_parser.add_argument("--task-file", help="Read task from file")
    run_agent_parser.add_argument("--output", "-o", help="Save output to file")
    run_agent_parser.add_argument("--model", help="Claude model to use (auto-selected if --auto-select-model is enabled)")
    run_agent_parser.add_argument("--max-tokens", type=int, default=4096, help="Maximum tokens")
    run_agent_parser.add_argument("--temperature", type=float, default=1.0, help="Temperature (0.0-1.0)")
    run_agent_parser.add_argument("--json", action="store_true", help="Output metadata as JSON")
    # Hybrid orchestration options
    run_agent_parser.add_argument("--auto-select-model", action="store_true", help="Enable hybrid model orchestration (auto-select Haiku/Sonnet/Opus)")
    run_agent_parser.add_argument("--estimate-cost", action="store_true", help="Show cost estimate before running")
    run_agent_parser.add_argument("--cost-threshold", type=float, help="Maximum cost per task in USD")
    run_agent_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")
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
    init_parser = subparsers.add_parser("init", help="Initialize a new claude-force project with intelligent template selection")
    init_parser.add_argument("directory", nargs="?", default=".", help="Target directory (default: current directory)")
    init_parser.add_argument("--description", "-d", help="Project description (required for non-interactive mode)")
    init_parser.add_argument("--name", "-n", help="Project name (default: directory name)")
    init_parser.add_argument("--template", "-t", help="Template ID to use (skips auto-matching)")
    init_parser.add_argument("--tech", help="Tech stack (comma-separated)")
    init_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode with prompts")
    init_parser.add_argument("--no-semantic", action="store_true", help="Disable semantic matching (use keyword-based)")
    init_parser.add_argument("--no-examples", action="store_true", help="Don't create example files")
    init_parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing .claude directory")
    init_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    init_parser.set_defaults(func=cmd_init)

    # Marketplace command
    marketplace_parser = subparsers.add_parser("marketplace", help="Manage plugins from marketplace")
    marketplace_subparsers = marketplace_parser.add_subparsers(dest="marketplace_command")

    # Marketplace list
    list_parser = marketplace_subparsers.add_parser("list", help="List available plugins")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--source", help="Filter by source (builtin, wshobson, custom)")
    list_parser.add_argument("--installed", action="store_true", help="Show only installed plugins")
    list_parser.set_defaults(func=cmd_marketplace_list)

    # Marketplace search
    search_parser = marketplace_subparsers.add_parser("search", help="Search marketplace for plugins")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=cmd_marketplace_search)

    # Marketplace install
    install_parser = marketplace_subparsers.add_parser("install", help="Install a plugin")
    install_parser.add_argument("plugin_id", help="Plugin ID to install")
    install_parser.add_argument("--force", "-f", action="store_true", help="Force reinstall if already installed")
    install_parser.set_defaults(func=cmd_marketplace_install)

    # Marketplace uninstall
    uninstall_parser = marketplace_subparsers.add_parser("uninstall", help="Uninstall a plugin")
    uninstall_parser.add_argument("plugin_id", help="Plugin ID to uninstall")
    uninstall_parser.set_defaults(func=cmd_marketplace_uninstall)

    # Marketplace info
    info_parser_mp = marketplace_subparsers.add_parser("info", help="Show plugin information")
    info_parser_mp.add_argument("plugin_id", help="Plugin ID")
    info_parser_mp.set_defaults(func=cmd_marketplace_info)

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
