# Quick Start Guide

Get started with Claude Force in 5 minutes.

## Installation

### Option 1: PyPI (Recommended)

```bash
# Install
pip install claude-force

# Set API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Verify
claude-force --version
```

### Option 2: From Source

```bash
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force
pip install -e .
```

## Your First Command

### List Available Agents

```bash
claude-force list agents
```

**Output:**
```
📋 Available Agents (19)

Architecture:
  frontend-architect    - React, Next.js, component design
  backend-architect     - API design, microservices
  database-architect    - Schema design, optimization
  devops-architect      - Infrastructure, CI/CD

Development:
  frontend-developer    - React implementation
  python-expert         - Python best practices
  ui-components-expert  - Component libraries

Quality & Security:
  code-reviewer         - Code quality, best practices
  qc-automation-expert  - Testing, automation
  security-specialist   - Security audits, compliance

Support:
  bug-investigator      - Debugging, root cause
  document-writer-expert - Technical documentation
  api-documenter        - API documentation

Specialized:
  ai-engineer           - ML/AI development
  data-engineer         - Data pipelines
  prompt-engineer       - LLM optimization
  deployment-integration-expert - Deployment automation
  google-cloud-expert   - GCP infrastructure
  claude-code-expert    - Claude Code systems
```

### Run Your First Agent

```bash
claude-force run agent code-reviewer \
  --task "Review this function: def add(a, b): return a + b"
```

**Output:**
```
🤖 Running agent: code-reviewer
⏱️  Execution time: 1.2s
💰 Cost: $0.0024

📄 Review Results:
---
The function is simple but can be improved:

Issues:
1. Missing type hints
2. No docstring
3. No input validation

Recommended:
```python
def add(a: int | float, b: int | float) -> int | float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a + b
```

Congratulations! 🎉 You've run your first agent!

## Core Workflows

### 1. Run a Workflow

Execute multi-agent workflows for complex tasks:

```bash
claude-force run workflow full-stack-feature \
  --task "Build user authentication with email and password"
```

This runs 8 agents in sequence:
1. Frontend Architect → Design UI
2. Database Architect → Design schema
3. Backend Architect → Design API
4. Python Expert → Implement backend
5. UI Components Expert → Design components
6. Frontend Developer → Implement UI
7. QC Automation Expert → Create tests
8. Deployment Integration Expert → Setup deployment

### 2. Initialize a Project

```bash
# Interactive mode
claude-force init my-project --interactive

# Direct mode
claude-force init my-project \
  --template llm-app \
  --description "RAG chatbot with vector search"
```

**Creates:**
```
my-project/
├── .claude/
│   ├── claude.json       # Configuration
│   ├── task.md           # Task template
│   ├── agents/           # Agent definitions
│   ├── contracts/        # Contracts
│   ├── hooks/            # Governance
│   ├── skills/           # Skills
│   └── workflows/        # Workflows
└── ...
```

**Integrate with Existing Claude Code Projects:**

If you already have a `.claude` directory (e.g., from Claude Code), `claude-force` will automatically merge:

```bash
cd my-existing-project  # Already has .claude/ directory
claude-force init --description "My existing project"
```

**Output:**
```
📁 Detected existing .claude directory (Claude Code project)
   Preserving existing files and adding claude-force configuration

✅ Project initialized successfully!

📂 Created 2 files:
   ✓ .claude/claude.json
   ✓ .claude/examples/example-task.md

📌 Preserved 15 existing files:
   ⊙ .claude/task.md
   ⊙ .claude/README.md
   ⊙ .claude/commands/custom-command.md
   ⊙ .claude/hooks/pre-run.md
   ...
```

Your existing commands, hooks, and task files are preserved! 🎉

### 3. Use Python API

```python
from claude_force import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()

# Run single agent
result = orchestrator.run_agent(
    agent_name='security-specialist',
    task='Review authentication code for vulnerabilities'
)

if result.success:
    print(result.output)
else:
    print(f"Error: {result.errors}")

# Run workflow
results = orchestrator.run_workflow(
    workflow_name='bug-investigation',
    task='Users cannot reset passwords'
)

# Check results
for agent_name, result in results.items():
    print(f"{agent_name}: {'✅' if result.success else '❌'}")
```

## Key Features

### Hybrid Model Orchestration

Save 40-60% on costs by auto-selecting the right model:

```bash
# Auto-select model (Haiku for simple, Sonnet for complex)
claude-force run agent document-writer-expert \
  --task "Generate API documentation" \
  --auto-select-model
# → Uses Haiku (60-80% cost savings)

# Force specific model
claude-force run agent frontend-architect \
  --task "Design architecture" \
  --model sonnet
```

**Model Selection:**
- **Haiku** - Docs, simple reviews, formatting (cheapest)
- **Sonnet** - Architecture, development, analysis (balanced)
- **Opus** - Security, critical debugging (highest quality)

### Marketplace Integration

Access the wshobson/agents ecosystem:

```bash
# Search for plugins
claude-force marketplace search "kubernetes"

# Install plugin
claude-force marketplace install wshobson-devops-toolkit

# Get recommendations
claude-force recommend \
  --task "Review code for SQL injection vulnerabilities"
```

**Output:**
```
🎯 Recommended Agents:

1. security-specialist (95.2% confidence)
   Reasoning: Security review for SQL injection detection

2. code-reviewer (78.4% confidence)
   Reasoning: Code review with security focus
```

### Performance Tracking

```bash
# View metrics
claude-force analytics summary

# Export data
claude-force analytics export --format json --output metrics.json
```

## Common Use Cases

### 1. Code Review

```bash
claude-force run agent code-reviewer \
  --task "Review src/auth.py for security issues"
```

### 2. Architecture Design

```bash
claude-force run agent backend-architect \
  --task "Design REST API for e-commerce platform"
```

### 3. Bug Investigation

```bash
claude-force run workflow bug-investigation \
  --task "Login fails after password reset"
```

### 4. Documentation

```bash
claude-force run agent document-writer-expert \
  --task "Create user guide for API" \
  --skill docx
```

### 5. Full Feature

```bash
claude-force run workflow full-stack-feature \
  --task "User profile page with avatar upload"
```

## Available Templates

Initialize projects with pre-configured setups:

```bash
claude-force init my-project --template <template-name>
```

**Templates:**
- `fullstack-web` - Full-stack app (React, FastAPI, PostgreSQL)
- `llm-app` - LLM application (RAG, chatbots, semantic search)
- `ml-project` - Machine learning (training, deployment)
- `data-pipeline` - Data engineering (ETL, Airflow, Spark)
- `api-service` - REST API (microservices)
- `frontend-spa` - Frontend SPA (React/Vue)
- `mobile-app` - Mobile (React Native/Flutter)
- `infrastructure` - Infrastructure (Docker, K8s)
- `claude-code-system` - Multi-agent system

## Available Workflows

Pre-built multi-agent workflows:

| Workflow | Agents | Use Case |
|----------|--------|----------|
| `full-stack-feature` | 8 | Complete feature development |
| `frontend-feature` | 5 | Frontend-only development |
| `backend-api` | 4 | Backend API development |
| `infrastructure-setup` | 3 | Infrastructure setup |
| `bug-investigation` | 3 | Debug and fix issues |
| `documentation-suite` | 3 | Complete documentation |
| `ai-ml-development` | 4 | AI/ML pipeline |
| `data-pipeline-development` | 3 | Data engineering |
| `llm-integration` | 4 | LLM integration |
| `claude-code-system` | 5 | Meta workflow |

## Configuration

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY='your-key'

# Optional
export CLAUDE_FORCE_MODEL='claude-3-5-sonnet-20241022'  # Default model
export CLAUDE_FORCE_MAX_TOKENS=4096                      # Max tokens
export CLAUDE_FORCE_TEMPERATURE=0.7                      # Temperature
```

### Project Configuration

Edit `.claude/claude.json`:

```json
{
  "version": "2.2.0",
  "governance": {
    "validation_mode": "strict",
    "require_contracts": true,
    "enable_analytics": true
  },
  "orchestration": {
    "auto_select_model": true,
    "enable_caching": true,
    "max_parallel_agents": 3
  }
}
```

## Next Steps

### Learn More
- **[README.md](README.md)** - Complete overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Detailed project info

### Deep Dive
- **[Documentation Index](docs/DOCUMENTATION_INDEX.md)** - All documentation
- **[Performance Guide](docs/guides/PERFORMANCE_OPTIMIZATION_INDEX.md)** - Optimization
- **[Examples](examples/)** - Code examples

### Get Help
- **[FAQ.md](FAQ.md)** - Frequently asked questions
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Troubleshooting

### Installation Issues

```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -v claude-force
```

### API Key Issues

```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Test connection
claude-force run agent code-reviewer --task "Review: print('hello')"
```

### Import Errors

```bash
# Reinstall
pip uninstall claude-force
pip install claude-force

# Or install in development mode
pip install -e .
```

## Support

- **Issues**: [GitHub Issues](https://github.com/khanh-vu/claude-force/issues)
- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)
- **Tests**: `pytest test_claude_system.py -v`

---

**You're ready to build with Claude Force!** 🚀

For detailed guides, see the [Documentation Index](docs/DOCUMENTATION_INDEX.md).
