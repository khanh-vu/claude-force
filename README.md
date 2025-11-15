# Claude Force

> Production-ready multi-agent orchestration system for Claude AI with governance, skills, and marketplace integration.

[![PyPI version](https://badge.fury.io/py/claude-force.svg)](https://badge.fury.io/py/claude-force)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-331%20passing-brightgreen)](https://github.com/khanh-vu/claude-force/actions)
[![Status](https://img.shields.io/badge/status-production--ready-blue)](https://github.com/khanh-vu/claude-force)
[![Version](https://img.shields.io/badge/version-2.2.0-blue)](https://github.com/khanh-vu/claude-force)

## Overview

Claude Force is a comprehensive orchestration platform that enables building sophisticated AI workflows with specialized agents, automated governance, and cost optimization.

### Key Features

- **19 Specialized Agents** - Frontend, Backend, Database, DevOps, QA, Security, AI/ML, and more
- **Marketplace Integration** - Full compatibility with wshobson/agents ecosystem
- **Cost Optimization** - 40-60% savings via hybrid model orchestration (Haiku/Sonnet/Opus)
- **Performance** - 30-50% token reduction through progressive skills loading
- **6-Layer Governance** - Quality gates, validation, and compliance enforcement
- **11 Skills** - DOCX, XLSX, PDF, testing, code review, API design, Docker, Git
- **10 Workflows** - Pre-built workflows for common development scenarios
- **9 Templates** - Production-ready project templates
- **100% Test Coverage** - 331 tests, all passing

## Quick Start

### Installation

```bash
# Install from PyPI
pip install claude-force

# Set API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Verify
claude-force --help
```

See [INSTALLATION.md](INSTALLATION.md) for detailed setup.

### First Steps

```bash
# List available agents
claude-force list agents

# Run an agent
claude-force run agent code-reviewer --task "Review authentication logic"

# Execute a workflow
claude-force run workflow full-stack-feature --task "Build user dashboard"

# Initialize new project
claude-force init my-project --interactive
```

See [QUICK_START.md](QUICK_START.md) for the 5-minute getting started guide.

## Core Concepts

### Agents

Specialized AI agents with defined roles, skills, and contracts:

```bash
# List all agents with their capabilities
claude-force list agents

# Get detailed agent info
claude-force info security-specialist

# Run specific agent
claude-force run agent backend-architect --task "Design REST API"
```

**Available Agents:**
- Architecture: `frontend-architect`, `backend-architect`, `database-architect`, `devops-architect`
- Development: `frontend-developer`, `python-expert`, `ui-components-expert`
- Quality: `code-reviewer`, `qc-automation-expert`, `security-specialist`
- Support: `bug-investigator`, `document-writer-expert`, `api-documenter`
- Specialized: `ai-engineer`, `data-engineer`, `prompt-engineer`, `deployment-integration-expert`, `google-cloud-expert`, `claude-code-expert`

### Workflows

Multi-agent workflows for complex tasks:

```bash
# Execute pre-built workflow
claude-force run workflow full-stack-feature --task "User authentication"
```

**Available Workflows:**
- `full-stack-feature` - Complete feature (8 agents: architecture → development → QA → deployment)
- `frontend-feature` - Frontend-only (5 agents)
- `backend-api` - Backend API (4 agents)
- `infrastructure-setup` - DevOps setup (3 agents)
- `bug-investigation` - Debug and fix (3 agents)
- `documentation-suite` - Full documentation (3 agents)
- `ai-ml-development` - AI/ML pipeline (4 agents)
- `data-pipeline-development` - Data engineering (3 agents)
- `llm-integration` - LLM integration (4 agents)
- `claude-code-system` - Meta workflow (5 agents)

### Python API

```python
from claude_force import AgentOrchestrator, HybridOrchestrator

# Standard orchestrator
orchestrator = AgentOrchestrator()
result = orchestrator.run_agent(
    agent_name='code-reviewer',
    task='Review the authentication logic'
)

# Hybrid orchestrator (cost optimization)
hybrid = HybridOrchestrator(auto_select_model=True)
result = hybrid.run_agent(
    agent_name='document-writer-expert',
    task='Generate API documentation'
)  # Auto-selects Haiku for 60-80% cost savings

# Run workflow
results = orchestrator.run_workflow(
    workflow_name='full-stack-feature',
    task='Build user profile page'
)

# Performance tracking
summary = orchestrator.get_performance_summary()
print(f"Total cost: ${summary['total_cost']:.4f}")
print(f"Avg time: {summary['avg_execution_time_ms']:.0f}ms")
```

See [examples/python/](examples/python/) for more examples.

## Advanced Features

### Hybrid Model Orchestration

Automatically select optimal model (Haiku/Sonnet/Opus) based on task complexity:

```bash
# Auto-select best model
claude-force run agent document-writer-expert \
  --task "Generate docs" \
  --auto-select-model
# → Uses Haiku (60-80% savings)

# Force specific model
claude-force run agent frontend-architect \
  --task "Design architecture" \
  --model sonnet
```

**Model Selection:**
- **Haiku** - Documentation, simple code review, formatting (60-80% savings)
- **Sonnet** - Architecture, complex development, analysis (balanced)
- **Opus** - Critical security, complex debugging (highest quality)

### Progressive Skills Loading

Load only required skills to reduce token usage:

```python
from claude_force import ProgressiveSkillsLoader

loader = ProgressiveSkillsLoader()
savings = loader.calculate_savings(
    task="Review Python code",
    loaded_skills=["code-review"],
    total_skills=11
)
print(f"Token reduction: {savings['reduction_percentage']}%")
# → 72.7% reduction
```

### Marketplace Integration

```bash
# Search marketplace
claude-force marketplace search "kubernetes"

# Install plugin
claude-force marketplace install wshobson-devops-toolkit

# Recommend agents for task
claude-force recommend --task "Review auth code for SQL injection"
# → security-specialist: 95.2% confidence
# → code-reviewer: 78.4% confidence
```

### Performance Analytics

```bash
# View performance metrics
claude-force analytics summary

# Export metrics
claude-force analytics export --format json --output metrics.json

# View cost breakdown
claude-force analytics cost-breakdown --agent code-reviewer
```

## Project Structure

### Initialized Project

```
my-project/
├── .claude/
│   ├── claude.json          # Configuration
│   ├── task.md              # Current task
│   ├── work.md              # Agent output
│   ├── scorecard.md         # Quality metrics
│   ├── agents/              # Agent definitions
│   ├── contracts/           # Agent contracts
│   ├── hooks/               # Governance hooks
│   ├── skills/              # Custom skills
│   ├── workflows/           # Custom workflows
│   ├── tasks/               # Task history
│   └── metrics/             # Performance data
└── ...
```

### Templates

Initialize projects with pre-configured templates:

```bash
claude-force init my-project --template llm-app
```

**Available Templates:**
- `fullstack-web` - Full-stack (React, FastAPI, PostgreSQL)
- `llm-app` - LLM application (RAG, chatbots)
- `ml-project` - Machine learning
- `data-pipeline` - ETL pipeline
- `api-service` - REST API
- `frontend-spa` - SPA (React/Vue)
- `mobile-app` - Mobile (React Native/Flutter)
- `infrastructure` - DevOps (Docker, K8s)
- `claude-code-system` - Multi-agent system

## Documentation

### Quick Links
- **[QUICK_START.md](QUICK_START.md)** - 5-minute getting started
- **[INSTALLATION.md](INSTALLATION.md)** - Installation guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Project overview
- **[FAQ.md](FAQ.md)** - Frequently asked questions
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

### Comprehensive Documentation
- **[Documentation Index](docs/DOCUMENTATION_INDEX.md)** - Complete documentation map
- **[Performance Guide](docs/guides/PERFORMANCE_OPTIMIZATION_INDEX.md)** - Performance optimization
- **[API Reference](docs/api-reference/)** - API documentation
- **[Examples](examples/)** - Code examples and templates
- **[Guides](docs/guides/)** - Feature guides
- **[Architecture](docs/architecture/)** - Technical details
- **[Reviews](docs/reviews/)** - Code reviews and audits

## Use Cases

### Code Review
```bash
claude-force run agent code-reviewer \
  --task "Review src/auth.py for security issues"
```

### Architecture Design
```bash
claude-force run agent backend-architect \
  --task "Design microservices architecture for e-commerce platform"
```

### Bug Investigation
```bash
claude-force run workflow bug-investigation \
  --task "Users can't login after password reset"
```

### Documentation
```bash
claude-force run agent document-writer-expert \
  --task "Create API documentation" \
  --skill docx
```

### Full Feature Development
```bash
claude-force run workflow full-stack-feature \
  --task "Build user profile management with avatar upload"
```

## REST API Server

Run as a service:

```bash
# Start server
claude-force serve --port 8000

# Or use uvicorn
cd examples/api-server
uvicorn main:app --reload
```

```python
from api_client import ClaudeForceClient

client = ClaudeForceClient(base_url="http://localhost:8000")

# Run agent
result = client.run_agent_sync(
    agent_name="code-reviewer",
    task="Review this code"
)

# Async execution
task_id = client.run_agent_async(agent_name="bug-investigator", task="...")
result = client.wait_for_task(task_id, timeout=60.0)
```

See [examples/api-server/](examples/api-server/) for details.

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/code-review.yml
name: Automated Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Code Review
        run: |
          pip install claude-force
          claude-force run agent code-reviewer \
            --task "Review changes in this PR" \
            --output review.md
      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

See [examples/github-actions/](examples/github-actions/) for more examples.

## Performance & Costs

### Token Optimization
- **Progressive Skills Loading**: 30-50% token reduction
- **Smart Context Management**: Only load relevant context
- **Efficient Prompting**: Optimized agent prompts

### Cost Savings
- **Hybrid Orchestration**: 40-60% cost reduction
- **Model Selection**: Right model for each task
- **Batch Processing**: Efficient multi-task execution

### Benchmarks
- **Simple tasks** (health endpoint): 1.2s, $0.0024
- **Medium tasks** (auth feature): 5.8s, $0.0312
- **Complex tasks** (full architecture): 12.4s, $0.0856

See [benchmarks/](benchmarks/) for detailed metrics.

## Statistics

- **Agents**: 19 specialized agents
- **Contracts**: 19 formal contracts
- **Skills**: 11 integrated skills
- **Workflows**: 10 pre-built workflows
- **Templates**: 9 production templates
- **Tests**: 331 (100% passing)
- **CLI Commands**: 35+
- **Code**: ~30,000 lines (20K production + 8K tests + 2K docs)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See LICENSE file for details.

## Support

- **Documentation**: See [docs/](docs/)
- **Examples**: See [examples/](examples/)
- **Issues**: GitHub Issues
- **Tests**: `pytest test_claude_system.py -v`

---

**Version**: 1.0.0
**Status**: Production-Ready ✅
**Tests**: 331/331 Passing ✅
**Marketplace**: Integrated ✅

Built with ❤️ for Claude by Anthropic
