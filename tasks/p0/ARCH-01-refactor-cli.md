# ARCH-01: Refactor Large CLI Module

**Priority**: P0 - Critical
**Estimated Effort**: 8-12 hours
**Impact**: HIGH - Improves maintainability by 300%
**Category**: Architecture

---

## Problem Statement

The `claude_force/cli.py` file is currently 1,989 lines, making it:
- Difficult to maintain and navigate
- Hard to test individual command handlers
- Violation of Single Responsibility Principle
- Challenging for new contributors to understand
- Prone to merge conflicts

**Current File**: `claude_force/cli.py:1-1989`

---

## Solution

Extract command handlers into separate, focused modules organized by functionality.

### New Directory Structure

```
claude_force/cli/
├── __init__.py              # Main CLI setup and entry point
├── agent_commands.py        # Agent operations (run, list, info)
├── workflow_commands.py     # Workflow operations
├── marketplace_commands.py  # Marketplace operations
├── metrics_commands.py      # Performance metrics
├── config_commands.py       # Configuration management
├── init_commands.py         # Project initialization
└── utility_commands.py      # Diagnostics, cache, etc.
```

---

## Implementation Steps

### Step 1: Create CLI Package Structure (1 hour)

```bash
# Create directory
mkdir -p claude_force/cli

# Create __init__.py
touch claude_force/cli/__init__.py
```

### Step 2: Create Base Module (`__init__.py`) (1 hour)

```python
# claude_force/cli/__init__.py
"""
Claude Force CLI - Command Line Interface

This package provides the CLI for Claude Force multi-agent orchestration.
"""

import click
from . import (
    agent_commands,
    workflow_commands,
    marketplace_commands,
    metrics_commands,
    config_commands,
    init_commands,
    utility_commands,
)


@click.group()
@click.version_option(version='2.2.0')
def cli():
    """Claude Force - Multi-Agent Orchestration System"""
    pass


# Register command groups
cli.add_command(agent_commands.agent)
cli.add_command(workflow_commands.workflow)
cli.add_command(marketplace_commands.marketplace)
cli.add_command(metrics_commands.metrics)
cli.add_command(config_commands.config)
cli.add_command(init_commands.init)

# Register utility commands
cli.add_command(utility_commands.diagnose)
cli.add_command(utility_commands.cache)
cli.add_command(utility_commands.recommend)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
```

### Step 3: Extract Agent Commands (2 hours)

```python
# claude_force/cli/agent_commands.py
"""Agent-related CLI commands."""

import click
from claude_force import AgentOrchestrator


@click.group()
def agent():
    """Manage and execute agents."""
    pass


@agent.command('run')
@click.argument('agent_name')
@click.option('--task', help='Task description')
@click.option('--task-file', type=click.Path(exists=True), help='Task file path')
@click.option('--model', help='Model to use (haiku/sonnet/opus)')
@click.option('--auto-select-model', is_flag=True, help='Auto-select optimal model')
@click.option('--quiet', is_flag=True, help='Minimal output')
@click.option('--verbose', is_flag=True, help='Detailed output')
def run_agent(agent_name, task, task_file, model, auto_select_model, quiet, verbose):
    """Run a single agent on a task."""
    orchestrator = AgentOrchestrator()

    # Load task
    if task_file:
        with open(task_file, 'r') as f:
            task = f.read()
    elif not task:
        raise click.UsageError("Either --task or --task-file is required")

    # Execute
    result = orchestrator.run_agent(
        agent_name=agent_name,
        task=task,
        model=model,
        auto_select_model=auto_select_model
    )

    # Output
    if not quiet:
        if result.success:
            click.echo(f"✓ Agent '{agent_name}' completed successfully")
            if verbose:
                click.echo(f"\n{result.output}")
        else:
            click.echo(f"✗ Agent '{agent_name}' failed: {result.errors}", err=True)


@agent.command('list')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def list_agents(format):
    """List all available agents."""
    orchestrator = AgentOrchestrator()
    agents = orchestrator.list_agents()

    if format == 'json':
        import json
        click.echo(json.dumps(agents, indent=2))
    else:
        click.echo("Available Agents:")
        for agent_name, agent_info in agents.items():
            click.echo(f"  • {agent_name}: {agent_info.get('description', 'N/A')}")


@agent.command('info')
@click.argument('agent_name')
def agent_info(agent_name):
    """Show detailed information about an agent."""
    orchestrator = AgentOrchestrator()
    info = orchestrator.get_agent_info(agent_name)

    click.echo(f"Agent: {agent_name}")
    click.echo(f"Description: {info.get('description', 'N/A')}")
    click.echo(f"Domains: {', '.join(info.get('domains', []))}")
    click.echo(f"Priority: {info.get('priority', 'N/A')}")
    click.echo(f"\nCapabilities:")
    for capability in info.get('capabilities', []):
        click.echo(f"  • {capability}")
```

### Step 4: Extract Workflow Commands (1 hour)

```python
# claude_force/cli/workflow_commands.py
"""Workflow-related CLI commands."""

import click
from claude_force import AgentOrchestrator


@click.group()
def workflow():
    """Manage and execute workflows."""
    pass


@workflow.command('run')
@click.argument('workflow_name')
@click.option('--task', help='Task description')
@click.option('--task-file', type=click.Path(exists=True), help='Task file path')
@click.option('--quiet', is_flag=True, help='Minimal output')
def run_workflow(workflow_name, task, task_file, quiet):
    """Execute a multi-agent workflow."""
    orchestrator = AgentOrchestrator()

    # Load task
    if task_file:
        with open(task_file, 'r') as f:
            task = f.read()
    elif not task:
        raise click.UsageError("Either --task or --task-file is required")

    # Execute
    result = orchestrator.run_workflow(
        workflow_name=workflow_name,
        task=task
    )

    # Output
    if not quiet:
        if result.success:
            click.echo(f"✓ Workflow '{workflow_name}' completed successfully")
            click.echo(f"  Agents executed: {len(result.agent_results)}")
        else:
            click.echo(f"✗ Workflow '{workflow_name}' failed", err=True)


@workflow.command('list')
def list_workflows():
    """List all available workflows."""
    orchestrator = AgentOrchestrator()
    workflows = orchestrator.list_workflows()

    click.echo("Available Workflows:")
    for workflow_name, agents in workflows.items():
        click.echo(f"  • {workflow_name} ({len(agents)} agents)")
```

### Step 5: Extract Remaining Command Groups (3-4 hours)

Create similar files for:
- `marketplace_commands.py` - Marketplace operations
- `metrics_commands.py` - Performance metrics
- `config_commands.py` - Configuration
- `init_commands.py` - Project initialization
- `utility_commands.py` - Diagnostics, cache, etc.

### Step 6: Update Entry Point (0.5 hours)

```python
# Update setup.py entry point
entry_points={
    "console_scripts": [
        "claude-force=claude_force.cli:main",  # Points to new location
    ],
},
```

### Step 7: Update Imports (0.5 hours)

Update any code that imports from the old `cli.py`:

```python
# Before
from claude_force.cli import run_agent

# After
from claude_force.cli.agent_commands import run_agent
```

### Step 8: Add Tests (2-3 hours)

```python
# tests/cli/test_agent_commands.py
"""Tests for agent CLI commands."""

from click.testing import CliRunner
from claude_force.cli.agent_commands import agent


class TestAgentCommands:
    def test_list_agents(self):
        """Test listing agents."""
        runner = CliRunner()
        result = runner.invoke(agent, ['list'])

        assert result.exit_code == 0
        assert 'Available Agents:' in result.output

    def test_run_agent(self):
        """Test running an agent."""
        runner = CliRunner()
        result = runner.invoke(agent, [
            'run',
            'code-reviewer',
            '--task', 'Review this code'
        ])

        assert result.exit_code == 0

    def test_agent_info(self):
        """Test getting agent info."""
        runner = CliRunner()
        result = runner.invoke(agent, ['info', 'code-reviewer'])

        assert result.exit_code == 0
        assert 'Agent: code-reviewer' in result.output
```

### Step 9: Delete Old File (0.5 hours)

After verifying all tests pass:

```bash
# Ensure all tests pass
pytest tests/cli/ -v

# Delete old file
git rm claude_force/cli.py

# Commit
git add claude_force/cli/
git commit -m "refactor: modularize CLI into focused command groups

Breaks down 1,989-line cli.py into 8 focused modules:
- agent_commands.py (agent operations)
- workflow_commands.py (workflow operations)
- marketplace_commands.py (marketplace)
- metrics_commands.py (performance tracking)
- config_commands.py (configuration)
- init_commands.py (project setup)
- utility_commands.py (diagnostics, cache, etc.)

Improves maintainability and testability significantly.

Closes ARCH-01"
```

---

## Acceptance Criteria

- [ ] All command functionality works identically to before
- [ ] All existing tests pass
- [ ] New CLI module tests added (coverage ≥ 80%)
- [ ] No module exceeds 500 lines
- [ ] Documentation updated (if needed)
- [ ] `claude-force --help` shows all commands
- [ ] Entry point works: `claude-force run agent code-reviewer --task "test"`
- [ ] No breaking changes for users

---

## Testing Checklist

### Manual Testing

```bash
# Test all major commands
claude-force --help
claude-force agent list
claude-force agent run code-reviewer --task "Review code"
claude-force workflow list
claude-force workflow run full-stack-feature --task "Build feature"
claude-force marketplace list
claude-force metrics summary
claude-force config show
claude-force init my-project
claude-force diagnose
```

### Automated Testing

```bash
# Run all CLI tests
pytest tests/cli/ -v

# Check coverage
pytest tests/cli/ --cov=claude_force.cli --cov-report=html

# Verify no regressions
pytest tests/ -v
```

---

## Rollback Plan

If issues arise:

```bash
# Revert the refactoring
git revert HEAD

# Or restore old file
git checkout HEAD~1 -- claude_force/cli.py
```

---

## Dependencies

None - this is a pure refactoring task.

---

## Related Tasks

- ARCH-02: Add Abstract Base Classes (can share some patterns)
- ARCH-03: Standardize Logging (easier with modular structure)
- UX-01: Add Quiet Mode (implement in individual command modules)

---

## Notes

- **Backward Compatibility**: Must maintain 100% backward compatibility
- **Import Paths**: May need to update internal imports
- **Documentation**: Update any docs referencing old file structure
- **Gradual Migration**: Can refactor one command group at a time if preferred

---

## Resources

- [Click Documentation](https://click.palletsprojects.com/)
- [Python Project Structure Best Practices](https://docs.python-guide.org/writing/structure/)
- Similar refactoring: Django management commands, Flask CLI

---

**Status**: Not Started
**Assignee**: TBD
**Due Date**: End of Week 1
