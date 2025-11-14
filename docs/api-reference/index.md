# API Reference

Complete API documentation for claude-force Python package.

## Core Components

### Orchestration

- **[AgentOrchestrator](orchestrator.md)** - Main orchestration engine for running agents and workflows
- **[HybridOrchestrator](hybrid-orchestrator.md)** - Intelligent model selection and cost optimization
- **[WorkflowComposer](workflow-composer.md)** - Create and manage custom multi-agent workflows

### Agent Selection

- **[SemanticAgentSelector](semantic-selector.md)** - AI-powered agent recommendation using embeddings
- **[AgentRouter](agent-router.md)** - Agent routing and matching logic

### Performance & Analytics

- **[PerformanceTracker](performance-tracker.md)** - Track execution metrics, costs, and performance
- **[Analytics](analytics.md)** - Advanced analytics and reporting

### Marketplace & Skills

- **[AgentMarketplace](marketplace.md)** - Install and share community agents
- **[SkillsManager](skills-manager.md)** - Manage agent skills and capabilities
- **[TemplateGallery](template-gallery.md)** - Project templates and scaffolding

### Command-Line Interface

- **[CLI Commands](cli.md)** - All command-line interface commands and options

### Utilities

- **[ImportExport](import-export.md)** - Configuration import/export utilities
- **[QuickStart](quick-start.md)** - Project initialization and setup
- **[Contribution](contribution.md)** - Contribution workflow helpers

## Quick API Examples

### Basic Agent Execution

```python
from claude_force.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(
    config_path=".claude/claude.json",
    enable_tracking=True
)

result = orchestrator.run_agent(
    agent_name="code-reviewer",
    task="Review authentication module"
)

print(f"Success: {result.success}")
print(f"Output: {result.output}")
```

### Semantic Agent Recommendation

```python
from claude_force.semantic_selector import SemanticAgentSelector

selector = SemanticAgentSelector(config_path=".claude/claude.json")

matches = selector.match_agents(
    task_description="Find and fix security vulnerabilities",
    top_k=3
)

for match in matches:
    print(f"{match.agent_name}: {match.confidence:.2f}")
```

### Hybrid Model Selection

```python
from claude_force.hybrid_orchestrator import HybridOrchestrator

hybrid = HybridOrchestrator(
    auto_select_model=True,
    cost_threshold=0.50
)

# Automatically selects Haiku for simple tasks
result = hybrid.run_agent(
    "code-reviewer",
    "Fix typo in README"
)

# Automatically selects Sonnet/Opus for complex tasks
result = hybrid.run_agent(
    "backend-architect",
    "Design microservices architecture"
)
```

### Performance Tracking

```python
from claude_force.performance_tracker import PerformanceTracker

tracker = PerformanceTracker(metrics_dir=".claude/metrics")

# Record execution
tracker.record_execution(
    agent_name="code-reviewer",
    task="Review code",
    success=True,
    execution_time_ms=1500.0,
    model="claude-3-5-sonnet-20241022",
    input_tokens=150,
    output_tokens=250
)

# Get analytics
analytics = tracker.get_summary()
print(f"Total executions: {analytics['total_executions']}")
print(f"Total cost: ${analytics['total_cost']:.4f}")
print(f"Success rate: {analytics['success_rate']:.1%}")
```

### Workflow Composition

```python
from claude_force.workflow_composer import WorkflowComposer

composer = WorkflowComposer()

workflow = composer.compose(
    goal="Implement user authentication with security review and testing",
    include_marketplace=True
)

print(f"Workflow: {workflow.name}")
print(f"Steps: {len(workflow.steps)}")
print(f"Estimated cost: ${workflow.total_estimated_cost:.2f}")

for step in workflow.steps:
    print(f"  {step.step_number}. {step.agent.agent_name}: {step.description}")
```

### Marketplace Operations

```python
from claude_force.marketplace import AgentMarketplace

marketplace = AgentMarketplace()

# List available agents
agents = marketplace.list_agents(category="security")

# Search
results = marketplace.search("authentication security")

# Install agent
marketplace.install_agent(
    agent_name="oauth-specialist",
    target_dir=".claude"
)
```

## API Conventions

### Error Handling

All claude-force APIs use exception-based error handling:

```python
from claude_force.orchestrator import AgentOrchestrator
from claude_force.exceptions import (
    AgentNotFoundError,
    APIKeyMissingError,
    ConfigurationError
)

try:
    orchestrator = AgentOrchestrator(config_path=".claude/claude.json")
    result = orchestrator.run_agent("code-reviewer", "Review code")
except APIKeyMissingError:
    print("Set ANTHROPIC_API_KEY environment variable")
except AgentNotFoundError as e:
    print(f"Agent not found: {e}")
except ConfigurationError as e:
    print(f"Invalid configuration: {e}")
```

### Return Types

Most methods return typed objects:

- `AgentResult` - Result of agent execution
- `AgentMatch` - Agent recommendation with confidence
- `ExecutionMetrics` - Performance metrics
- `ComposedWorkflow` - Workflow composition
- `MarketplaceAgent` - Marketplace agent information

### Async Support

Currently, claude-force is synchronous. Async support is planned for v3.0.

## Module Index

- **claude_force.orchestrator** - Core orchestration
- **claude_force.semantic_selector** - Semantic agent selection
- **claude_force.hybrid_orchestrator** - Model selection
- **claude_force.performance_tracker** - Performance tracking
- **claude_force.workflow_composer** - Workflow composition
- **claude_force.marketplace** - Agent marketplace
- **claude_force.skills_manager** - Skills management
- **claude_force.analytics** - Analytics and reporting
- **claude_force.agent_router** - Agent routing
- **claude_force.template_gallery** - Project templates
- **claude_force.import_export** - Import/export utilities
- **claude_force.quick_start** - Project initialization
- **claude_force.cli** - Command-line interface

## Type Annotations

All claude-force APIs use type hints:

```python
from typing import List, Optional, Dict, Any
from claude_force.orchestrator import AgentResult

def run_agent(
    agent_name: str,
    task: str,
    model: Optional[str] = None
) -> AgentResult:
    """Run an agent with type-safe parameters"""
    pass
```

## Configuration

Most APIs accept a `config_path` parameter pointing to `claude.json`:

```python
orchestrator = AgentOrchestrator(config_path=".claude/claude.json")
selector = SemanticAgentSelector(config_path=".claude/claude.json")
```

## Next Steps

- Explore detailed documentation for each component
- Check out [Guides](../guides/index.md) for tutorials
- See [Examples](../examples/index.md) for real-world usage

---

**Need help?** Open an issue on [GitHub](https://github.com/khanh-vu/claude-force/issues).
