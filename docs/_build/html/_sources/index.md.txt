# Claude-Force Documentation

**Production-Ready Multi-Agent Orchestration System for Claude**

Welcome to the comprehensive documentation for claude-force, a powerful framework for orchestrating multiple Claude AI agents to solve complex software engineering tasks.

## Quick Links

- **[Installation Guide](installation.md)** - Get started in 30 seconds
- **[Quick Start](quickstart.md)** - Build your first multi-agent workflow
- **[API Reference](api-reference/index.md)** - Complete API documentation
- **[Guides](guides/index.md)** - In-depth tutorials and best practices
- **[Examples](examples/index.md)** - Real-world usage examples

## What is Claude-Force?

Claude-Force is a Python framework that enables you to:

- **Orchestrate Multiple AI Agents**: Coordinate specialized Claude agents for different tasks
- **Semantic Agent Selection**: Automatically recommend the best agent for your task using embeddings
- **Hybrid Model Orchestration**: Optimize costs by automatically selecting Haiku/Sonnet/Opus based on task complexity
- **Performance Tracking**: Monitor execution time, token usage, and costs
- **Workflow Composition**: Create custom multi-agent workflows
- **Marketplace Integration**: Install and share community agents

## Key Features

### 🧠 Semantic Agent Recommendation
```bash
claude-force recommend --task "Review authentication code for security"
# → Recommends: security-specialist (confidence: 0.92)
```

### ⚡ Hybrid Model Orchestration
Automatically selects the optimal Claude model based on task complexity:
- **Haiku** for simple tasks (typo fixes, formatting)
- **Sonnet** for moderate tasks (code reviews, refactoring)
- **Opus** for complex tasks (architecture design, security audits)

### 📊 Performance Analytics
```bash
claude-force analyze performance
# Shows: execution times, token usage, costs, success rates
```

### 🎨 Project Initialization
```bash
claude-force init ./my-project \
  --description "Build a chat application" \
  --name "chat-app"
# Creates optimized .claude/ configuration
```

## Installation

### From PyPI (Recommended)
```bash
pip install claude-force
claude-force --help
```

### From Source
```bash
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force
pip install -e .
```

## Quick Example

```python
from claude_force.orchestrator import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator(
    config_path=".claude/claude.json",
    enable_tracking=True
)

# Run single agent
result = orchestrator.run_agent(
    agent_name="code-reviewer",
    task="Review this authentication function for security issues"
)

print(result.output)

# Run multi-agent workflow
results = orchestrator.run_workflow(
    workflow_name="full-stack-feature",
    task="Implement user authentication with JWT"
)

for result in results:
    print(f"{result.agent_name}: {result.success}")
```

## Architecture

Claude-Force consists of several key components:

- **[AgentOrchestrator](api-reference/orchestrator.md)**: Core execution engine
- **[SemanticAgentSelector](api-reference/semantic-selector.md)**: AI-powered agent recommendation
- **[HybridOrchestrator](api-reference/hybrid-orchestrator.md)**: Model selection and cost optimization
- **[PerformanceTracker](api-reference/performance-tracker.md)**: Metrics collection and analytics
- **[WorkflowComposer](api-reference/workflow-composer.md)**: Custom workflow creation
- **[AgentMarketplace](api-reference/marketplace.md)**: Community agent sharing

## Documentation Sections

### For Users

- **[Installation](installation.md)**: System requirements and installation methods
- **[Quick Start](quickstart.md)**: Get started in minutes
- **[CLI Reference](api-reference/cli.md)**: All command-line commands
- **[Guides](guides/index.md)**: Tutorials and best practices

### For Developers

- **[API Reference](api-reference/index.md)**: Complete Python API documentation
- **[Architecture](guides/architecture.md)**: System design and internals
- **[Contributing](guides/contributing.md)**: How to contribute to claude-force
- **[Testing](guides/testing.md)**: Running and writing tests

### Advanced Topics

- **[Semantic Selection](guides/semantic-selection.md)**: How agent recommendation works
- **[Performance Optimization](guides/performance.md)**: Cost and latency optimization
- **[Custom Workflows](guides/workflows.md)**: Building multi-agent workflows
- **[Marketplace](guides/marketplace.md)**: Publishing and installing agents

## System Requirements

- Python 3.8 or higher (3.10+ recommended)
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- 100MB disk space

### Optional Dependencies

- `sentence-transformers`: For semantic agent selection (recommended)
- `numpy`: For vector operations (required if using semantic selection)

## Support

- **GitHub Issues**: [https://github.com/khanh-vu/claude-force/issues](https://github.com/khanh-vu/claude-force/issues)
- **Documentation**: [https://claude-force.readthedocs.io](https://claude-force.readthedocs.io)
- **Source Code**: [https://github.com/khanh-vu/claude-force](https://github.com/khanh-vu/claude-force)

## License

MIT License - see [LICENSE](https://github.com/khanh-vu/claude-force/blob/main/LICENSE) file for details.

## Next Steps

- **New Users**: Start with the [Quick Start Guide](quickstart.md)
- **Developers**: Check out the [API Reference](api-reference/index.md)
- **Advanced Users**: Explore [Guides](guides/index.md) for in-depth topics

---

**Version**: 2.1.0
**Last Updated**: 2025-11-14
**Status**: Production Ready
