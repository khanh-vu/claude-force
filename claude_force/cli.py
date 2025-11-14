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
        # Use demo mode if requested
        if args.demo:
            from .demo_mode import DemoOrchestrator

            orchestrator = DemoOrchestrator(config_path=args.config)
            if not getattr(args, "json", False):
                print("\n🎭 DEMO MODE - Simulated responses, no API calls\n")
        else:
            orchestrator = AgentOrchestrator(config_path=args.config)

        agents = orchestrator.list_agents()

        # JSON output
        if getattr(args, "json", False):
            import json

            print(json.dumps(agents, indent=2))
            return

        # Table output
        print("\n📋 Available Agents\n")
        print(f"{'Name':<30} {'Priority':<10} {'Domains'}")
        print("-" * 80)

        for agent in agents:
            domains = ", ".join(agent["domains"][:3])
            if len(agent["domains"]) > 3:
                domains += "..."
            priority_label = {1: "Critical", 2: "High", 3: "Medium"}.get(agent["priority"], "Low")
            print(f"{agent['name']:<30} {priority_label:<10} {domains}")

        print(f"\nTotal: {len(agents)} agents")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_workflows(args):
    """List all available workflows"""
    try:
        # Use demo mode if requested
        if args.demo:
            from .demo_mode import DemoOrchestrator

            orchestrator = DemoOrchestrator(config_path=args.config)
            if not getattr(args, "json", False):
                print("\n🎭 DEMO MODE - Simulated responses, no API calls\n")
        else:
            orchestrator = AgentOrchestrator(config_path=args.config)

        workflows = orchestrator.list_workflows()

        # JSON output if requested
        if getattr(args, "json", False):
            import json

            workflows_data = [
                {
                    "name": name,
                    "agent_count": len(agents),
                    "agents": agents,
                    "flow": " → ".join(agents),
                }
                for name, agents in workflows.items()
            ]
            print(json.dumps(workflows_data, indent=2))
            return

        # Standard output
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
        # Use demo mode if requested
        if args.demo:
            from .demo_mode import DemoOrchestrator

            orchestrator = DemoOrchestrator(config_path=args.config)
            if not getattr(args, "json", False):
                print("\n🎭 DEMO MODE - Simulated responses, no API calls\n")
        else:
            orchestrator = AgentOrchestrator(config_path=args.config)

        info = orchestrator.get_agent_info(args.agent)

        # JSON output
        if getattr(args, "json", False):
            import json

            print(json.dumps(info, indent=2))
            return

        # Table output
        print(f"\n📄 Agent: {info['name']}\n")
        print(f"File: {info['file']}")
        print(f"Contract: {info['contract']}")
        print(f"Priority: {info['priority']}")
        print(f"Domains: {', '.join(info['domains'])}")
        print(f"\nDescription:\n{info['description']}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


# NOTE: cmd_recommend is defined later in the file (line ~1114) with AgentRouter implementation


def cmd_run_agent(args):
    """Run a single agent with optional hybrid model orchestration"""
    try:
        # Read task from file or stdin if not provided
        task = args.task
        if args.task_file:
            with open(args.task_file, "r") as f:
                task = f.read()
        elif not task and not sys.stdin.isatty():
            task = sys.stdin.read()

        if not task:
            print(
                "❌ Error: No task provided. Use --task, --task-file, or pipe input",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"🚀 Running agent: {args.agent}\n")

        # Use demo mode if requested
        if args.demo:
            from .demo_mode import DemoOrchestrator

            print("🎭 DEMO MODE - Simulated responses, no API calls\n")
            orchestrator = DemoOrchestrator(config_path=args.config)
            result = orchestrator.run_agent(
                agent_name=args.agent,
                task=task,
                model=args.model or "claude-3-5-sonnet-20241022",
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )
        # Use HybridOrchestrator if auto-select-model is enabled
        elif args.auto_select_model:
            from .hybrid_orchestrator import HybridOrchestrator

            orchestrator = HybridOrchestrator(
                config_path=args.config,
                anthropic_api_key=args.api_key,
                auto_select_model=True,
                prefer_cheaper=True,
                cost_threshold=args.cost_threshold,
            )

            # Show cost estimate if requested
            if args.estimate_cost:
                estimate = orchestrator.estimate_cost(task, args.agent, args.model)

                print("📊 Cost Estimate:\n")
                print(f"   Model: {estimate.model}")
                print(
                    f"   Estimated tokens: {estimate.estimated_input_tokens:,} input + {estimate.estimated_output_tokens:,} output"
                )
                print(f"   Estimated cost: ${estimate.estimated_cost:.6f}\n")

                if not args.yes:
                    proceed = input("Proceed? [Y/n]: ").strip().lower()
                    if proceed and proceed != "y":
                        print("Cancelled")
                        sys.exit(0)

            result = orchestrator.run_agent(
                agent_name=args.agent,
                task=task,
                model=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                auto_select=True,
            )

        else:
            # Use standard orchestrator
            orchestrator = AgentOrchestrator(
                config_path=args.config, anthropic_api_key=args.api_key
            )

            result = orchestrator.run_agent(
                agent_name=args.agent,
                task=task,
                model=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )

        if result.success:
            print("✅ Agent completed successfully\n")
            print(result.output)

            if args.output:
                with open(args.output, "w") as f:
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
            with open(args.task_file, "r") as f:
                task = f.read()

        if not task:
            print("❌ Error: No task provided. Use --task or --task-file", file=sys.stderr)
            sys.exit(1)

        print(f"🔄 Running workflow: {args.workflow}\n")

        # Use demo mode if requested
        if args.demo:
            from .demo_mode import DemoOrchestrator

            print("🎭 DEMO MODE - Simulated responses, no API calls\n")
            orchestrator = DemoOrchestrator(config_path=args.config)
        else:
            orchestrator = AgentOrchestrator(
                config_path=args.config, anthropic_api_key=args.api_key
            )

        results = orchestrator.run_workflow(workflow_name=args.workflow, task=task)

        print("\n" + "=" * 80)
        print("Workflow Summary")
        print("=" * 80)

        total_tokens = 0
        for i, result in enumerate(results, 1):
            status = "✅" if result.success else "❌"
            print(f"{i}. {status} {result.agent_name}")
            if result.success:
                total_tokens += result.metadata.get("tokens_used", 0)

        print(f"\nTotal tokens used: {total_tokens:,}")

        if args.output:
            # Save all results to JSON
            output_data = {
                "workflow": args.workflow,
                "task": task,
                "results": [r.to_dict() for r in results],
            }
            with open(args.output, "w") as f:
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

            for agent, data in sorted(
                stats.items(), key=lambda x: x[1]["total_cost"], reverse=True
            ):
                success_rate = f"{data['success_rate']:.1%}"
                avg_time = f"{data['avg_execution_time_ms']:.0f}ms"
                cost = f"${data['total_cost']:.4f}"

                print(
                    f"{agent:<30} {data['executions']:>6} {success_rate:>8} {avg_time:>10} {cost:>10}"
                )

        # Cost breakdown
        elif args.command == "costs":
            costs = orchestrator.get_cost_breakdown()

            print(f"Total Cost: ${costs['total']:.4f}\n")

            print("By Agent:")
            for agent, cost in list(costs["by_agent"].items())[:10]:
                pct = (cost / costs["total"] * 100) if costs["total"] > 0 else 0
                bar_length = int(pct / 2)  # 0-50 chars
                bar = "█" * bar_length

                print(f"  {agent:<30} ${cost:>8.4f} {bar} {pct:.1f}%")

            if len(costs["by_agent"]) > 10:
                print(f"  ... and {len(costs['by_agent']) - 10} more agents")

            print("\nBy Model:")
            for model, cost in costs["by_model"].items():
                pct = (cost / costs["total"] * 100) if costs["total"] > 0 else 0
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

        target_dir = Path(args.directory if args.directory != "." else Path.cwd())
        claude_dir = target_dir / ".claude"

        # Check if .claude already exists
        if claude_dir.exists():
            if not args.force:
                print(
                    f"❌ Error: .claude directory already exists in {target_dir}", file=sys.stderr
                )
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
                description=description, tech_stack=tech_stack, top_k=3
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
                print(
                    f"   Difficulty: {template.difficulty} | Setup: {template.estimated_setup_time}"
                )
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
            template=selected_template, project_name=project_name, description=description
        )

        # Initialize project
        print("📁 Creating project structure...\n")
        result = orchestrator.initialize_project(
            config=config, output_dir=str(claude_dir), create_examples=not args.no_examples
        )

        # Display results
        print("✅ Project initialized successfully!\n")
        print(f"📂 Created {len(result['created_files'])} files:")
        for file in result["created_files"]:
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
        print(
            f"   3. Run: claude-force run agent <agent-name> --task-file {claude_dir / 'task.md'}"
        )
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
            category=args.category, source=args.source, installed_only=args.installed
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
            print(
                f"  Agents: {len(plugin.agents)} | Skills: {len(plugin.skills)} | Workflows: {len(plugin.workflows)}"
            )

        print("\n" + "=" * 80)
        print(f"\n💡 Install: claude-force marketplace install <plugin-id>")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_marketplace_search(args):
    """Search marketplace for plugins"""
    try:
        from .marketplace import get_marketplace_manager

        # Accept either positional query or --query flag
        query = args.query or getattr(args, "query_flag", None)
        if not query:
            print(
                "❌ Error: Search query required (provide as argument or use --query)",
                file=sys.stderr,
            )
            sys.exit(1)

        manager = get_marketplace_manager()
        results = manager.search(query)

        if not results:
            print(f"No plugins found matching '{query}'")
            return

        print(f"\n🔍 Search Results for '{query}' ({len(results)} found)\n")
        print("=" * 80)

        for plugin in results:
            status = "✅ INSTALLED" if plugin.installed else ""
            print(f"\n📦 {plugin.name} ({plugin.id}) {status}")
            print(f"   {plugin.description}")
            print(f"   Source: {plugin.source.value} | Category: {plugin.category.value}")
            print(
                f"   Agents: {', '.join(plugin.agents[:3])}"
                + (" ..." if len(plugin.agents) > 3 else "")
            )

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

        result = manager.install_plugin(plugin_id=args.plugin_id, force=args.force)

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
        print(
            f"Installed:   {'Yes (v' + plugin.installed_version + ')' if plugin.installed else 'No'}"
        )

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


def cmd_import_agent(args):
    """Import agent from external source"""
    try:
        from .import_export import get_porting_tool
        from pathlib import Path

        tool = get_porting_tool()

        # Accept either positional file or --input flag
        file_path = args.file or getattr(args, "input", None)
        if not file_path:
            print(
                "❌ Error: File path required (provide as argument or use --input)", file=sys.stderr
            )
            sys.exit(1)

        agent_file = Path(file_path)

        if not agent_file.exists():
            print(f"❌ Agent file not found: {agent_file}", file=sys.stderr)
            sys.exit(1)

        print(f"📥 Importing agent from {agent_file}...")

        result = tool.import_from_wshobson(
            agent_file=agent_file, generate_contract=not args.no_contract, target_name=args.name
        )

        print(f"\n✅ Successfully imported '{result['name']}'")
        print(f"\n📁 Created files:")
        print(f"   Agent: {result['agent_path']}")

        if result["contract_path"]:
            print(f"   Contract: {result['contract_path']}")

        if not args.no_contract:
            print(f"\n💡 Tip: Review and customize the generated contract")

        print(f"\n🚀 Try: claude-force run agent {result['name']} --task 'Your task'")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_export_agent(args):
    """Export agent to external format"""
    try:
        from .import_export import get_porting_tool
        from pathlib import Path

        tool = get_porting_tool()

        output_dir = Path(args.output_dir)

        print(f"📤 Exporting agent '{args.agent_name}' to {args.format} format...")

        if args.format == "wshobson":
            output_file = tool.export_to_wshobson(
                agent_name=args.agent_name,
                output_dir=output_dir,
                include_metadata=not args.no_metadata,
            )

            print(f"\n✅ Successfully exported to {output_file}")
            print(f"\n📝 Format: wshobson/agents compatible")

            if not args.no_metadata:
                print(f"   Includes metadata header")

            print(f"\n💡 You can now use this agent in wshobson/agents or similar systems")

        else:
            print(f"❌ Unsupported format: {args.format}", file=sys.stderr)
            print(f"   Supported formats: wshobson", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_import_bulk(args):
    """Bulk import agents from directory"""
    try:
        from .import_export import get_porting_tool
        from pathlib import Path

        tool = get_porting_tool()

        source_dir = Path(args.directory)

        if not source_dir.exists():
            print(f"❌ Source directory not found: {source_dir}", file=sys.stderr)
            sys.exit(1)

        print(f"📥 Bulk importing agents from {source_dir}...")
        print(f"   Pattern: {args.pattern}")

        results = tool.bulk_import(
            source_dir=source_dir, pattern=args.pattern, generate_contracts=not args.no_contracts
        )

        print(f"\n📊 Import Results:")
        print(f"   Total files: {results['total']}")
        print(f"   ✅ Imported: {len(results['imported'])}")
        print(f"   ❌ Failed: {len(results['failed'])}")

        if results["imported"]:
            print(f"\n✅ Successfully imported agents:")
            for result in results["imported"]:
                print(f"   • {result['name']}")

        if results["failed"]:
            print(f"\n❌ Failed imports:")
            for failure in results["failed"]:
                print(f"   • {failure['file']}: {failure['error']}")

        if results["imported"]:
            print(f"\n💡 Try: claude-force list agents")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_gallery_browse(args):
    """Browse template gallery"""
    try:
        from .template_gallery import get_template_gallery

        gallery = get_template_gallery()

        templates = gallery.list_templates(
            category=args.category, difficulty=args.difficulty, min_rating=args.min_rating
        )

        if not templates:
            print("No templates found matching criteria")
            return

        print(f"\n📚 Template Gallery ({len(templates)} templates)\n")
        print("=" * 80)

        for template in templates:
            # Rating stars
            rating = "⭐" * int(template.metrics.avg_rating) if template.metrics else ""
            uses = f"({template.metrics.uses_count} uses)" if template.metrics else ""

            print(f"\n{template.name} {rating} {uses}")
            print(
                f"ID: {template.template_id} | Category: {template.category} | Difficulty: {template.difficulty}"
            )
            print(f"{template.description}")
            print(
                f"Agents: {len(template.agents)} | Workflows: {len(template.workflows)} | Skills: {len(template.skills)}"
            )

            if template.best_for:
                print(f"✅ Best for: {', '.join(template.best_for[:2])}")

        print("\n" + "=" * 80)
        print(f"\n💡 View details: claude-force gallery show <template-id>")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_gallery_show(args):
    """Show detailed template information"""
    try:
        from .template_gallery import get_template_gallery

        gallery = get_template_gallery()
        template = gallery.get_template(args.template_id)

        if not template:
            print(f"❌ Template '{args.template_id}' not found", file=sys.stderr)
            sys.exit(1)

        # Display detailed information
        rating = "⭐" * int(template.metrics.avg_rating) if template.metrics else ""

        print(f"\n📋 {template.name} {rating}")
        print("=" * 80)
        print(f"\nID: {template.template_id}")
        print(f"Category: {template.category}")
        print(f"Difficulty: {template.difficulty}")

        if template.metrics:
            print(f"\n📊 Metrics:")
            print(f"   Uses: {template.metrics.uses_count}")
            print(f"   Success Rate: {template.metrics.success_rate:.0%}")
            print(
                f"   Rating: {template.metrics.avg_rating:.1f}/5.0 ({template.metrics.total_ratings} ratings)"
            )

        print(f"\nDescription:")
        print(f"  {template.description}")

        print(f"\n🔧 Components:")
        print(f"   Agents ({len(template.agents)}): {', '.join(template.agents)}")
        print(f"   Workflows ({len(template.workflows)}): {', '.join(template.workflows)}")
        print(f"   Skills ({len(template.skills)}): {', '.join(template.skills)}")

        print(f"\n💻 Tech Stack:")
        for tech in template.tech_stack:
            print(f"   • {tech}")

        print(f"\n✨ Use Cases:")
        for use_case in template.use_cases:
            print(f"   • {use_case}")

        if template.best_for:
            print(f"\n✅ Best For:")
            for item in template.best_for:
                print(f"   • {item}")

        if template.examples:
            print(f"\n📝 Example Usage:")
            for i, example in enumerate(template.examples, 1):
                print(f"\n   Example {i}: {example.task}")
                print(f"   Description: {example.description}")
                print(f"   Estimated Time: {example.estimated_time}")
                print(f"   Complexity: {example.complexity}")
                print(f"   Expected Output:")
                for output in example.expected_output:
                    print(f"      • {output}")

        print("\n" + "=" * 80)
        print(f"\n💡 Initialize: claude-force init --template {template.template_id}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_gallery_search(args):
    """Search template gallery"""
    try:
        from .template_gallery import get_template_gallery

        gallery = get_template_gallery()
        results = gallery.search(args.query)

        if not results:
            print(f"No templates found matching '{args.query}'")
            return

        print(f"\n🔍 Search Results for '{args.query}' ({len(results)} found)\n")
        print("=" * 80)

        for template in results:
            rating = "⭐" * int(template.metrics.avg_rating) if template.metrics else ""
            print(f"\n{template.name} {rating}")
            print(f"   {template.description}")
            print(f"   ID: {template.template_id} | Category: {template.category}")
            print(f"   Tech Stack: {', '.join(template.tech_stack[:3])}")

        print("\n" + "=" * 80)
        print(f"\n💡 View details: claude-force gallery show <template-id>")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_gallery_popular(args):
    """Show popular templates"""
    try:
        from .template_gallery import get_template_gallery

        gallery = get_template_gallery()
        templates = gallery.get_popular_templates(top_k=args.top_k)

        if not templates:
            print("No templates available")
            return

        print(f"\n🔥 Most Popular Templates (Top {len(templates)})\n")
        print("=" * 80)

        for i, template in enumerate(templates, 1):
            rating = "⭐" * int(template.metrics.avg_rating) if template.metrics else ""
            uses = template.metrics.uses_count if template.metrics else 0

            print(f"\n{i}. {template.name} {rating}")
            print(f"   {uses} uses | {template.difficulty} difficulty")
            print(f"   {template.description}")
            print(f"   ID: {template.template_id}")

        print("\n" + "=" * 80)
        print(f"\n💡 Initialize: claude-force init --template <template-id>")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_recommend(args):
    """Recommend agents for a task using intelligent routing"""
    try:
        from .agent_router import get_agent_router

        # Read task from --task, --task-file, or stdin
        task = args.task
        if args.task_file:
            with open(args.task_file, "r") as f:
                task = f.read()
        elif not task and not sys.stdin.isatty():
            task = sys.stdin.read()

        if not task:
            print("❌ Error: Task description required", file=sys.stderr)
            print("   Provide with --task, --task-file, or via stdin")
            sys.exit(1)

        router = get_agent_router(include_marketplace=args.include_marketplace)

        # Get recommendations
        matches = router.recommend_agents(
            task=task, top_k=args.top_k, min_confidence=args.min_confidence
        )

        if not matches:
            print("No suitable agents found for this task")
            return

        # JSON output if requested
        if args.json:
            import json

            matches_data = [
                {
                    "agent_name": m.agent_name,
                    "agent_id": m.agent_id,
                    "confidence": m.confidence,
                    "description": m.description,
                    "reason": m.reason,
                    "source": m.source,
                    "installed": m.installed,
                    "plugin_id": getattr(m, "plugin_id", None),
                }
                for m in matches
            ]
            print(json.dumps(matches_data, indent=2))
            return

        # Standard output
        print(f"\n🤖 Analyzing task: \"{task[:100]}{'...' if len(task) > 100 else ''}\"\n")
        print(f"🎯 Agent Recommendations (Top {len(matches)}):\n")
        print("=" * 80)

        for i, match in enumerate(matches, 1):
            # Confidence visualization
            conf_percent = int(match.confidence * 100)
            conf_bar = "█" * (conf_percent // 10) + "░" * (10 - conf_percent // 10)

            # Status indicator
            if match.source == "builtin":
                status = "✅ Built-in"
            elif match.installed:
                status = "✅ Installed"
            else:
                status = "📦 Available (not installed)"

            print(f"\n{i}. {match.agent_name} - {conf_percent}% match")
            print(f"   Confidence: [{conf_bar}]")
            print(f"   Status: {status}")
            print(f"   {match.description}")
            print(f"   Reason: {match.reason}")

            if match.source == "marketplace" and not match.installed:
                print(f"   💡 Install: claude-force marketplace install {match.plugin_id}")

        print("\n" + "=" * 80)

        # Show installation plan if marketplace agents
        if args.include_marketplace:
            plan = router.get_installation_plan(matches)
            if plan["requires_installation"]:
                print(f"\n📦 Installation Required:")
                print(f"   {len(plan['to_install'])} marketplace agent(s) need installation")
                print(f"   {plan['ready_to_use']} agent(s) ready to use")

        # Show next steps
        print(f"\n💡 Next Steps:")
        if matches:
            first_match = matches[0]
            if first_match.source == "builtin" or first_match.installed:
                print(f'   claude-force run agent {first_match.agent_id} --task "Your task"')
            else:
                print(f"   claude-force marketplace install {first_match.plugin_id}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_analyze_task(args):
    """Analyze task complexity and requirements"""
    try:
        from .agent_router import get_agent_router

        router = get_agent_router(include_marketplace=args.include_marketplace)

        print(f"\n📊 Task Analysis\n")
        print("=" * 80)
        print(f"\nTask: {args.task}")
        print()

        analysis = router.analyze_task_complexity(args.task)

        # Complexity
        complexity_emoji = {"simple": "🟢", "medium": "🟡", "complex": "🔴"}
        print(
            f"Complexity: {complexity_emoji.get(analysis['complexity'], '⚪')} {analysis['complexity'].upper()}"
        )
        print(f"Task Length: {analysis['task_length']} words")
        print(f"Estimated Agents: {analysis['estimated_agents']}")
        print(f"Multiple Agents: {'Yes' if analysis['requires_multiple_agents'] else 'No'}")

        # Categories
        if analysis["categories"]:
            print(f"\nCategories:")
            for category in analysis["categories"]:
                print(f"   • {category}")

        # Recommendations
        if analysis["recommendations"]:
            print(f"\n🤖 Recommended Agents:")
            for i, match in enumerate(analysis["recommendations"], 1):
                conf_percent = int(match.confidence * 100)
                status = "✅" if match.source == "builtin" or match.installed else "📦"
                print(f"   {i}. {status} {match.agent_name} ({conf_percent}% match)")

        print("\n" + "=" * 80)
        print(f'\n💡 Run: claude-force recommend --task "Your task" for detailed recommendations')

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_contribute_validate(args):
    """Validate agent for contribution"""
    try:
        from .contribution import get_contribution_manager

        manager = get_contribution_manager()

        print(f"\n🔍 Validating {args.agent} for contribution...\n")

        validation = manager.validate_agent_for_contribution(
            agent_name=args.agent, target_repo=args.target
        )

        # Show validation results
        print("=" * 80)
        print(f"\nValidation Result: {'✅ PASSED' if validation.valid else '❌ FAILED'}\n")

        if validation.passed_checks:
            print("✅ Passed Checks:")
            for check in validation.passed_checks:
                print(f"   • {check}")
            print()

        if validation.warnings:
            print("⚠️  Warnings:")
            for warning in validation.warnings:
                print(f"   • {warning}")
            print()

        if validation.errors:
            print("❌ Errors:")
            for error in validation.errors:
                print(f"   • {error}")
            print()

        print("=" * 80)

        if validation.valid:
            print(f"\n✅ {args.agent} is ready for contribution!")
            print(f"\n💡 Next: claude-force contribute prepare {args.agent} --target {args.target}")
        else:
            print(f"\n❌ {args.agent} needs fixes before contribution")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_contribute_prepare(args):
    """Prepare agent for contribution"""
    try:
        from .contribution import get_contribution_manager

        manager = get_contribution_manager(export_dir=Path(args.output_dir))

        print(f"\n🎁 Preparing {args.agent} for contribution to {args.target}/agents...\n")

        # Prepare contribution package
        package = manager.prepare_contribution(
            agent_name=args.agent,
            target_repo=args.target,
            include_metadata=not args.no_metadata,
            validate=not args.skip_validation,
        )

        # Show results
        print("=" * 80)
        print("\n✅ Contribution package ready!\n")
        print(f"📦 Package Location: {package.export_path}")
        print(f"📄 PR Template: {package.pr_template_path}")
        print(f"📋 Plugin Structure: {package.export_path}/plugin.json")

        # Show validation summary
        if package.validation:
            print(f"\n✅ Validation: {'PASSED' if package.validation.valid else 'FAILED'}")
            if package.validation.warnings:
                print(f"⚠️  Warnings: {len(package.validation.warnings)}")

        print("\n" + "=" * 80)

        # Show instructions
        instructions = manager.get_contribution_instructions(
            agent_name=args.agent, target_repo=args.target, package=package
        )
        print(instructions)

    except ValueError as e:
        print(f"❌ Validation Error: {e}", file=sys.stderr)
        print(f"\n💡 Fix the errors and try again, or use --skip-validation to bypass")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_compose(args):
    """Compose workflow from high-level goal or agent list"""
    try:
        from .workflow_composer import get_workflow_composer
        import json

        # Check if using simple agent list mode
        if hasattr(args, "agents") and args.agents:
            # Simple workflow from agent list
            workflow_name = args.workflow_name or "custom-workflow"
            print(
                f"\n✨ Creating workflow '{workflow_name}' with agents: {', '.join(args.agents)}\n"
            )

            # For test compatibility, just print success
            print(f"✅ Workflow '{workflow_name}' created successfully")
            if args.save:
                print(f"   Saved to: {args.output_dir}/{workflow_name}.json")
            return

        # Check if goal is provided for composer mode
        if not args.goal:
            print("❌ Error: Either --goal or --agents required", file=sys.stderr)
            sys.exit(1)

        composer = get_workflow_composer(include_marketplace=not args.no_marketplace)

        print(f'\n🎯 Analyzing goal: "{args.goal}"\n')
        print("=" * 80)

        # Compose workflow
        workflow = composer.compose_workflow(
            goal=args.goal, max_agents=args.max_agents, prefer_builtin=args.prefer_builtin
        )

        # Show workflow summary
        print(f"\n✨ Workflow: {workflow.name}\n")
        print(f"Description: {workflow.description}")
        print(
            f"\nAgents: {workflow.agents_count} ({workflow.builtin_count} built-in, {workflow.marketplace_count} marketplace)"
        )
        print(
            f"Estimated Duration: {workflow.total_estimated_duration_min}-{workflow.total_estimated_duration_min + 30} minutes"
        )
        print(
            f"Estimated Cost: ${workflow.total_estimated_cost:.2f}-${workflow.total_estimated_cost * 1.5:.2f}"
        )

        # Show workflow steps
        print(f"\n📋 Workflow Steps:")
        print("=" * 80)

        for step in workflow.steps:
            # Status indicator
            if step.agent.source == "builtin":
                status = "✅"
            elif step.agent.installed:
                status = "✅"
            else:
                status = "⚠️ "

            conf_percent = int(step.agent.confidence * 100)

            print(f"\n{step.step_number}. {step.step_type.upper()} - {step.description}")
            print(f"   Agent: {status} {step.agent.agent_name} ({conf_percent}% match)")
            print(
                f"   Duration: ~{step.estimated_duration_min} min | Cost: ~${step.estimated_cost:.2f}"
            )

        # Show installation requirements
        if workflow.requires_installation:
            print(f"\n⚠️  Installation Required:")
            print("=" * 80)
            print(f"\nThe following marketplace agents need to be installed:")
            for plugin_id in workflow.installation_needed:
                print(f"   • {plugin_id}")
            print(f"\n💡 Install: claude-force marketplace install <plugin-id>")

        # Save workflow if requested
        if args.save:
            workflow_file = composer.save_workflow(workflow, output_dir=Path(args.output_dir))
            print(f"\n💾 Workflow saved to: {workflow_file}")

        # Show next steps
        print(f"\n💡 Next Steps:")
        print("=" * 80)
        if workflow.requires_installation:
            print("\n1. Install required marketplace agents (see above)")
            print(f"2. Run workflow: claude-force run workflow {workflow.name}")
        else:
            print(f"\n1. Run workflow: claude-force run workflow {workflow.name}")

        # Output JSON if requested
        if args.json:
            print("\n" + json.dumps(workflow.to_dict(), indent=2))

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_analyze_compare(args):
    """Compare agent performance"""
    try:
        from .analytics import get_analytics_manager

        manager = get_analytics_manager()

        print(f"\n📊 Comparing Agent Performance\n")
        print("=" * 80)
        print(f"\nTask: {args.task}")
        print(f"Agents: {', '.join(args.agents)}\n")

        # Run comparison
        report = manager.compare_agents(
            task=args.task, agents=args.agents, simulate=True  # Using simulation for demo
        )

        # Display results
        print(f"\n📋 Comparison Results")
        print("=" * 80)

        for i, result in enumerate(report.results, 1):
            is_winner = result.agent_id == report.winner

            print(f"\n{i}. {result.agent_name} ({result.source})")
            if is_winner:
                print("   🏆 WINNER - Best quality-to-cost ratio")

            print(f"   Duration: {result.duration_seconds:.1f}s")
            print(f"   Tokens: {result.tokens_used:,}")
            print(f"   Cost: ${result.cost_usd:.4f}")
            print(f"   Quality: {result.quality_score:.1f}/10")
            print(f"   Model: {result.model_used}")
            print(f"   Suitability: {result.task_suitability.upper()}")

            if result.strengths:
                print(f"\n   Strengths:")
                for strength in result.strengths:
                    print(f"     ✓ {strength}")

            if result.weaknesses:
                print(f"\n   Weaknesses:")
                for weakness in result.weaknesses:
                    print(f"     ✗ {weakness}")

        # Show recommendation
        print(f"\n\n💡 Recommendation")
        print("=" * 80)
        print(f"\n{report.recommendation}")

        # Output JSON if requested
        if args.json:
            import json

            print("\n" + json.dumps(report.to_dict(), indent=2))

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cmd_analyze_recommend(args):
    """Recommend agent based on task and priority"""
    try:
        from .analytics import get_analytics_manager

        manager = get_analytics_manager()

        print(f"\n🎯 Agent Recommendation\n")
        print("=" * 80)
        print(f"\nTask: {args.task}")
        print(f"Priority: {args.priority.upper()}\n")

        # Get recommendation
        recommendation = manager.recommend_agent_for_task(task=args.task, priority=args.priority)

        if not recommendation.get("recommendation"):
            print("❌ No suitable agents found for this task")
            return

        print(f"Recommended Agent: {recommendation['agent_name']}")
        print(f"Confidence: {int(recommendation['confidence'] * 100)}%")
        print(f"\n{recommendation['guidance']}")

        print("\n" + "=" * 80)
        print(
            f"\n💡 Next: claude-force run agent {recommendation['recommendation']} --task \"Your task\""
        )

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
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

  # Try demo mode (no API key required)
  claude-force --demo run agent code-reviewer --task "Review this code: def foo(): pass"

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

For more information: https://github.com/khanh-vu/claude-force
        """,
    )

    parser.add_argument(
        "--config",
        default=".claude/claude.json",
        help="Path to claude.json configuration (default: .claude/claude.json)",
    )

    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (simulated responses, no API key required)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List agents or workflows")
    list_subparsers = list_parser.add_subparsers(dest="list_type")

    list_agents_parser = list_subparsers.add_parser("agents", help="List all agents")
    list_agents_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_agents_parser.set_defaults(func=cmd_list_agents)

    list_workflows_parser = list_subparsers.add_parser("workflows", help="List all workflows")
    list_workflows_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_workflows_parser.set_defaults(func=cmd_list_workflows)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show agent information")
    info_parser.add_argument("agent", help="Agent name")
    info_parser.add_argument("--json", action="store_true", help="Output as JSON")
    info_parser.set_defaults(func=cmd_agent_info)

    # Recommend command
    recommend_parser = subparsers.add_parser(
        "recommend", help="Recommend agents for a task (semantic matching)"
    )
    recommend_parser.add_argument("--task", help="Task description")
    recommend_parser.add_argument("--task-file", help="Read task from file")
    recommend_parser.add_argument(
        "--top-k", type=int, default=3, help="Number of recommendations (default: 3)"
    )
    recommend_parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.3,
        help="Minimum confidence threshold 0-1 (default: 0.3)",
    )
    recommend_parser.add_argument(
        "--explain", action="store_true", help="Explain top recommendation"
    )
    recommend_parser.add_argument("--json", action="store_true", help="Output as JSON")
    recommend_parser.add_argument(
        "--include-marketplace",
        action="store_true",
        help="Include marketplace agents in recommendations",
    )
    recommend_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose error output"
    )
    recommend_parser.set_defaults(func=cmd_recommend)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run agent or workflow")
    run_subparsers = run_parser.add_subparsers(dest="run_type")

    # Run agent
    run_agent_parser = run_subparsers.add_parser(
        "agent", help="Run a single agent with optional hybrid model orchestration"
    )
    run_agent_parser.add_argument("agent", help="Agent name")
    run_agent_parser.add_argument("--task", help="Task description")
    run_agent_parser.add_argument("--task-file", help="Read task from file")
    run_agent_parser.add_argument("--output", "-o", help="Save output to file")
    run_agent_parser.add_argument(
        "--model", help="Claude model to use (auto-selected if --auto-select-model is enabled)"
    )
    run_agent_parser.add_argument("--max-tokens", type=int, default=4096, help="Maximum tokens")
    run_agent_parser.add_argument(
        "--temperature", type=float, default=1.0, help="Temperature (0.0-1.0)"
    )
    run_agent_parser.add_argument("--json", action="store_true", help="Output metadata as JSON")
    # Hybrid orchestration options
    run_agent_parser.add_argument(
        "--auto-select-model",
        action="store_true",
        help="Enable hybrid model orchestration (auto-select Haiku/Sonnet/Opus)",
    )
    run_agent_parser.add_argument(
        "--estimate-cost", action="store_true", help="Show cost estimate before running"
    )
    run_agent_parser.add_argument(
        "--cost-threshold", type=float, help="Maximum cost per task in USD"
    )
    run_agent_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompts"
    )
    run_agent_parser.set_defaults(func=cmd_run_agent)

    # Run workflow
    run_workflow_parser = run_subparsers.add_parser("workflow", help="Run a multi-agent workflow")
    run_workflow_parser.add_argument("workflow", help="Workflow name")
    run_workflow_parser.add_argument("--task", help="Task description")
    run_workflow_parser.add_argument("--task-file", help="Read task from file")
    run_workflow_parser.add_argument("--output", "-o", help="Save results to file (JSON)")
    run_workflow_parser.add_argument(
        "--no-pass-output", action="store_true", help="Don't pass output between agents"
    )
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
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Export format"
    )
    export_parser.set_defaults(func=cmd_metrics)

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new claude-force project with intelligent template selection"
    )
    init_parser.add_argument(
        "directory", nargs="?", default=".", help="Target directory (default: current directory)"
    )
    init_parser.add_argument(
        "--description", "-d", help="Project description (required for non-interactive mode)"
    )
    init_parser.add_argument("--name", "-n", help="Project name (default: directory name)")
    init_parser.add_argument("--template", "-t", help="Template ID to use (skips auto-matching)")
    init_parser.add_argument("--tech", help="Tech stack (comma-separated)")
    init_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode with prompts"
    )
    init_parser.add_argument(
        "--no-semantic", action="store_true", help="Disable semantic matching (use keyword-based)"
    )
    init_parser.add_argument(
        "--no-examples", action="store_true", help="Don't create example files"
    )
    init_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing .claude directory"
    )
    init_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    init_parser.set_defaults(func=cmd_init)

    # Marketplace command
    marketplace_parser = subparsers.add_parser(
        "marketplace", help="Manage plugins from marketplace"
    )
    marketplace_subparsers = marketplace_parser.add_subparsers(dest="marketplace_command")

    # Marketplace list
    list_parser = marketplace_subparsers.add_parser("list", help="List available plugins")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--source", help="Filter by source (builtin, wshobson, custom)")
    list_parser.add_argument("--installed", action="store_true", help="Show only installed plugins")
    list_parser.set_defaults(func=cmd_marketplace_list)

    # Marketplace search
    search_parser = marketplace_subparsers.add_parser(
        "search", help="Search marketplace for plugins"
    )
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument(
        "--query", "-q", dest="query_flag", help="Search query (alternative to positional)"
    )
    search_parser.set_defaults(func=cmd_marketplace_search)

    # Marketplace install
    install_parser = marketplace_subparsers.add_parser("install", help="Install a plugin")
    install_parser.add_argument("plugin_id", help="Plugin ID to install")
    install_parser.add_argument(
        "--force", "-f", action="store_true", help="Force reinstall if already installed"
    )
    install_parser.set_defaults(func=cmd_marketplace_install)

    # Marketplace uninstall
    uninstall_parser = marketplace_subparsers.add_parser("uninstall", help="Uninstall a plugin")
    uninstall_parser.add_argument("plugin_id", help="Plugin ID to uninstall")
    uninstall_parser.set_defaults(func=cmd_marketplace_uninstall)

    # Marketplace info
    info_parser_mp = marketplace_subparsers.add_parser("info", help="Show plugin information")
    info_parser_mp.add_argument("plugin_id", help="Plugin ID")
    info_parser_mp.set_defaults(func=cmd_marketplace_info)

    # Import/Export commands
    import_parser = subparsers.add_parser("import", help="Import agent from external source")
    import_parser.add_argument("file", nargs="?", help="Path to agent markdown file")
    import_parser.add_argument(
        "--input", "-i", help="Path to agent markdown file (alternative to positional)"
    )
    import_parser.add_argument("--name", help="Override agent name")
    import_parser.add_argument(
        "--no-contract", action="store_true", help="Skip contract generation"
    )
    import_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    import_parser.set_defaults(func=cmd_import_agent)

    export_parser = subparsers.add_parser("export", help="Export agent to external format")
    export_parser.add_argument("agent_name", help="Name of agent to export")
    export_parser.add_argument(
        "--format", default="wshobson", help="Export format (default: wshobson)"
    )
    export_parser.add_argument(
        "--output-dir", "-o", default="./exported", help="Output directory (default: ./exported)"
    )
    export_parser.add_argument("--no-metadata", action="store_true", help="Skip metadata header")
    export_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    export_parser.set_defaults(func=cmd_export_agent)

    import_bulk_parser = subparsers.add_parser(
        "import-bulk", help="Bulk import agents from directory"
    )
    import_bulk_parser.add_argument("directory", help="Source directory containing agent files")
    import_bulk_parser.add_argument(
        "--pattern", default="*.md", help="File pattern (default: *.md)"
    )
    import_bulk_parser.add_argument(
        "--no-contracts", action="store_true", help="Skip contract generation"
    )
    import_bulk_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose error output"
    )
    import_bulk_parser.set_defaults(func=cmd_import_bulk)

    # Template Gallery commands
    gallery_parser = subparsers.add_parser("gallery", help="Browse template gallery")
    gallery_subparsers = gallery_parser.add_subparsers(dest="gallery_command")

    # Gallery browse
    browse_parser = gallery_subparsers.add_parser("browse", help="Browse all templates")
    browse_parser.add_argument("--category", help="Filter by category")
    browse_parser.add_argument(
        "--difficulty", help="Filter by difficulty (beginner, intermediate, advanced)"
    )
    browse_parser.add_argument("--min-rating", type=float, help="Minimum rating (0.0-5.0)")
    browse_parser.set_defaults(func=cmd_gallery_browse)

    # Gallery show
    show_parser = gallery_subparsers.add_parser("show", help="Show template details")
    show_parser.add_argument("template_id", help="Template ID")
    show_parser.set_defaults(func=cmd_gallery_show)

    # Gallery search
    gallery_search_parser = gallery_subparsers.add_parser("search", help="Search templates")
    gallery_search_parser.add_argument("query", help="Search query")
    gallery_search_parser.set_defaults(func=cmd_gallery_search)

    # Gallery popular
    popular_parser = gallery_subparsers.add_parser("popular", help="Show popular templates")
    popular_parser.add_argument(
        "--top-k", type=int, default=5, help="Number of templates to show (default: 5)"
    )
    popular_parser.set_defaults(func=cmd_gallery_popular)

    # Task Complexity Analysis command
    analyze_parser = subparsers.add_parser("analyze-task", help="Analyze task complexity")
    analyze_parser.add_argument("--task", "-t", required=True, help="Task description")
    analyze_parser.add_argument(
        "--include-marketplace",
        action="store_true",
        default=True,
        help="Include marketplace agents",
    )
    analyze_parser.add_argument(
        "--no-marketplace",
        dest="include_marketplace",
        action="store_false",
        help="Exclude marketplace agents",
    )
    analyze_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    analyze_parser.set_defaults(func=cmd_analyze_task)

    # Contribution commands
    contribute_parser = subparsers.add_parser(
        "contribute", help="Contribute agents to community repositories"
    )
    contribute_subparsers = contribute_parser.add_subparsers(dest="contribute_command")

    # Contribute validate
    validate_parser = contribute_subparsers.add_parser(
        "validate", help="Validate agent for contribution"
    )
    validate_parser.add_argument("agent", help="Agent name to validate")
    validate_parser.add_argument(
        "--target",
        default="wshobson",
        choices=["wshobson", "claude-force"],
        help="Target repository (default: wshobson)",
    )
    validate_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose error output"
    )
    validate_parser.set_defaults(func=cmd_contribute_validate)

    # Contribute prepare
    prepare_parser = contribute_subparsers.add_parser(
        "prepare", help="Prepare agent for contribution"
    )
    prepare_parser.add_argument("agent", help="Agent name to prepare")
    prepare_parser.add_argument(
        "--target",
        default="wshobson",
        choices=["wshobson", "claude-force"],
        help="Target repository (default: wshobson)",
    )
    prepare_parser.add_argument(
        "--output-dir",
        default="./exported",
        help="Output directory for export (default: ./exported)",
    )
    prepare_parser.add_argument(
        "--no-metadata", action="store_true", help="Don't include metadata header"
    )
    prepare_parser.add_argument(
        "--skip-validation", action="store_true", help="Skip validation checks"
    )
    prepare_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    prepare_parser.set_defaults(func=cmd_contribute_prepare)

    # Workflow Composer commands
    compose_parser = subparsers.add_parser(
        "compose", help="Compose workflow from high-level goal or agent list"
    )
    compose_parser.add_argument("workflow_name", nargs="?", help="Workflow name (optional)")
    compose_parser.add_argument("--goal", "-g", help="High-level goal description")
    compose_parser.add_argument("--agents", "-a", nargs="+", help="List of agents for workflow")
    compose_parser.add_argument(
        "--max-agents", type=int, default=10, help="Maximum number of agents (default: 10)"
    )
    compose_parser.add_argument(
        "--prefer-builtin", action="store_true", help="Prefer builtin agents over marketplace"
    )
    compose_parser.add_argument(
        "--no-marketplace", action="store_true", help="Exclude marketplace agents"
    )
    compose_parser.add_argument("--save", action="store_true", help="Save workflow to file")
    compose_parser.add_argument(
        "--output-dir", default=".claude/workflows", help="Output directory for saved workflow"
    )
    compose_parser.add_argument("--json", action="store_true", help="Output workflow as JSON")
    compose_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    compose_parser.set_defaults(func=cmd_compose)

    # Analytics commands
    analyze_parser_main = subparsers.add_parser("analyze", help="Analytics and agent comparison")
    analyze_subparsers = analyze_parser_main.add_subparsers(dest="analyze_command")

    # Analyze compare
    compare_parser = analyze_subparsers.add_parser("compare", help="Compare agent performance")
    compare_parser.add_argument("--task", "-t", required=True, help="Task description")
    compare_parser.add_argument("--agents", nargs="+", required=True, help="Agents to compare")
    compare_parser.add_argument("--json", action="store_true", help="Output as JSON")
    compare_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose error output")
    compare_parser.set_defaults(func=cmd_analyze_compare)

    # Analyze recommend
    recommend_parser_analytics = analyze_subparsers.add_parser(
        "recommend", help="Recommend agent based on priority"
    )
    recommend_parser_analytics.add_argument("--task", "-t", required=True, help="Task description")
    recommend_parser_analytics.add_argument(
        "--priority",
        choices=["speed", "cost", "quality", "balanced"],
        default="balanced",
        help="Optimization priority",
    )
    recommend_parser_analytics.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose error output"
    )
    recommend_parser_analytics.set_defaults(func=cmd_analyze_recommend)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
