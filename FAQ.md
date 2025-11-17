# Frequently Asked Questions (FAQ)

## Table of Contents

- [Getting Started](#getting-started)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Agents & Workflows](#agents--workflows)
- [Performance & Cost](#performance--cost)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)
- [Contributing](#contributing)

## Getting Started

### What is Claude Force?

Claude Force is a production-ready multi-agent orchestration system for Claude. It provides:
- 19 specialized AI agents for different domains (frontend, backend, security, etc.)
- 10 pre-built workflows for common development tasks
- Cost optimization through hybrid model selection
- Response caching for 60-80% cost savings
- Marketplace integration for community plugins

### Who should use Claude Force?

Claude Force is ideal for:
- **Developers** who want AI assistance across multiple domains
- **Teams** who need consistent, governed AI interactions
- **Projects** requiring specialized expertise (security, architecture, etc.)
- **Organizations** that need cost-effective, production-ready AI orchestration

### How does it compare to using Claude directly?

| Feature | Claude Direct | Claude Force |
|---------|---------------|--------------|
| Specialized agents | No | 19 agents |
| Workflows | Manual | 10 pre-built |
| Cost optimization | Manual | Automatic (60-80% savings) |
| Response caching | No | Yes |
| Governance | No | 6-layer system |
| Performance tracking | No | Built-in |
| Skills integration | Manual | 11 integrated skills |

## Installation & Setup

### How do I install Claude Force?

```bash
# Option 1: Install from PyPI (recommended)
pip install claude-force

# Option 2: Install from source (development)
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force
pip install -e .
```

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

### What Python version do I need?

Python 3.8 or higher. We test on:
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

### Do I need an Anthropic API key?

Yes. Get one at https://console.anthropic.com/

```bash
# Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Or add to .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env
```

### Can I use Claude Force without an API key?

Yes, in demo mode:

```bash
# Run in demo mode (no API calls, shows examples)
claude-force demo
```

### What dependencies are required?

**Core dependencies** (automatically installed):
- anthropic
- click
- pathlib

**Optional dependencies**:
```bash
# For semantic agent selection
pip install -e ".[semantic]"

# For REST API server
pip install -e ".[api]"

# For development
pip install -e ".[dev]"

# All features
pip install -e ".[all]"
```

## Usage

### How do I run my first agent?

```bash
# 1. Initialize a project
claude-force init my-project --interactive

# 2. Create a task file
echo "Review the authentication code in src/auth.py" > task.txt

# 3. Run an agent
claude-force run agent security-specialist --task-file task.txt
```

### How do I choose the right agent?

**Option 1: Automatic recommendation (easiest)**
```bash
claude-force recommend --task "Your task description"
# Shows best agents with confidence scores
```

**Option 2: List all agents**
```bash
claude-force list agents
# Shows all 19 agents with descriptions
```

**Option 3: Check agent skills**
```bash
claude-force info security-specialist
# Shows detailed capabilities and use cases
```

### Can I integrate claude-force with an existing project?

Yes! Claude Force can seamlessly integrate with existing `.claude` directories (e.g., from Claude Code projects):

```bash
# Navigate to your existing project
cd my-existing-project

# Initialize claude-force (preserves existing files)
claude-force init --description "My existing project"
```

**What happens:**
- ✅ **Preserves** existing files (task.md, README.md, commands/, hooks/, etc.)
- ✅ **Adds** claude-force configuration (claude.json, agents/, contracts/)
- ✅ **Shows** what was created vs. preserved

**Example output:**
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
   ...
```

**If you already have `claude.json`:**
```bash
# Use --force to reinitialize
claude-force init --force --description "Reinitialize project"
```

### How do I run a workflow?

```bash
# Run a pre-built workflow
claude-force run workflow full-stack-feature --task "Build user dashboard"

# List available workflows
claude-force list workflows

# Compose custom workflow from goal
claude-force compose --goal "Deploy ML model to production"
```

### Can I use Claude Force programmatically?

Yes! Python API example:

```python
from claude_force import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Run an agent
result = orchestrator.run_agent(
    agent_name='code-reviewer',
    task='Review this code for security issues'
)

if result.success:
    print(result.output)
else:
    print(f"Error: {result.errors}")
```

See [examples/python/](examples/python/) for more examples.

### How do I use the REST API?

```bash
# 1. Start the API server
cd examples/api-server
uvicorn api_server:app --reload

# 2. Use the API
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "agent_name": "code-reviewer",
    "task": "Review authentication code"
  }'

# 3. Or use the Python client
from api_client import ClaudeForceClient
client = ClaudeForceClient(base_url="http://localhost:8000", api_key="...")
result = client.run_agent_sync("code-reviewer", "Review this code")
```

See [examples/api-server/README.md](examples/api-server/README.md) for full API documentation.

## Agents & Workflows

### What agents are available?

**19 specialized agents** across 7 categories:

**Critical (P1)**:
- `code-reviewer` - Code quality & security review
- `security-specialist` - Security assessment & threat modeling
- `bug-investigator` - Root cause analysis & debugging
- `frontend-architect` - Frontend architecture design
- `backend-architect` - API and service architecture
- `database-architect` - Database schema design
- `claude-code-expert` - Claude Code system orchestration

**High Priority (P2)**:
- `python-expert` - Python implementation
- `ui-components-expert` - React component library
- `frontend-developer` - Feature implementation
- `devops-architect` - Infrastructure and CI/CD
- `google-cloud-expert` - GCP architecture
- `ai-engineer` - AI/ML development & LLM integration
- `prompt-engineer` - Prompt design & optimization
- `data-engineer` - Data pipelines & ETL

**Medium Priority (P3)**:
- `deployment-integration-expert` - Deployment configuration
- `qc-automation-expert` - Testing and QA
- `document-writer-expert` - Technical documentation
- `api-documenter` - API documentation

### What workflows are available?

**10 pre-built workflows**:

1. `full-stack-feature` - Complete feature (10 agents)
2. `frontend-only` - Frontend development (5 agents)
3. `backend-only` - Backend API development (6 agents)
4. `infrastructure` - Infrastructure setup (4 agents)
5. `bug-fix` - Bug investigation and resolution (3 agents)
6. `documentation` - Documentation generation (2 agents)
7. `ai-ml-development` - AI/ML solution development (5 agents)
8. `data-pipeline` - Data engineering and ETL (4 agents)
9. `llm-integration` - LLM-powered features (5 agents)
10. `claude-code-system` - Claude Code system development (3 agents)

### Can I create custom agents?

Yes! See [CONTRIBUTING.md#adding-a-new-agent](CONTRIBUTING.md#adding-a-new-agent) for the guide.

Quick steps:
1. Create agent definition in `.claude/agents/`
2. Create contract in `.claude/contracts/`
3. Register in `claude.json`
4. Add tests

### Can I create custom workflows?

Yes! Edit `claude.json`:

```json
{
  "workflows": {
    "my-custom-workflow": [
      "agent-1",
      "agent-2",
      "agent-3"
    ]
  }
}
```

Or use the workflow composer:

```bash
claude-force compose --goal "Your workflow goal" --save-as my-workflow
```

## Performance & Cost

### How much does it cost to use Claude Force?

**API costs** (Anthropic pricing):
- **Haiku**: ~$0.001 per simple task
- **Sonnet**: ~$0.01 per complex task
- **Opus**: ~$0.05 per critical task

**Cost optimization features**:
- Hybrid orchestration: 40-60% savings
- Response caching: 60-80% savings on repeated tasks
- Progressive skills loading: 30-50% token reduction

**Example costs with optimization**:
- Simple documentation task: $0.001 (Haiku, often cached)
- Code review: $0.01 (Sonnet, cached after first run)
- Security audit: $0.05 (Opus, requires fresh analysis)

### How do I reduce costs?

**1. Enable auto model selection**
```bash
claude-force run agent document-writer-expert \
  --task "Generate docs" \
  --auto-select-model
# Automatically uses cheaper Haiku for documentation
```

**2. Use response caching**
```bash
# Enabled by default
# Caches responses for 90 days
# 60-80% cost reduction on repeated tasks
```

**3. Set cost thresholds**
```bash
claude-force run agent code-reviewer \
  --task "Review codebase" \
  --cost-threshold 0.50
# Rejects tasks estimated to cost more than $0.50
```

**4. Use progressive skills loading**
```python
# Automatically loads only relevant skills
# 30-50% token reduction (15K → 5-8K tokens)
```

### How fast is Claude Force?

**Performance benchmarks**:
- Cache hit: **1ms** (vs 800ms API call) = 800x faster
- Semantic agent selection: **30 seconds** (vs 5 minutes manual) = 10x faster
- Concurrent workflows: **10x throughput** with async orchestration

**Response times** (typical):
- Simple task (Haiku): 800ms (1ms if cached)
- Complex task (Sonnet): 2,500ms (1ms if cached)
- Full workflow (3 agents): 7,500ms (3ms if all cached)

### Does response caching affect quality?

No. Caching is based on:
- **Exact task match**: Task description must be identical
- **Same agent**: Only caches per-agent responses
- **Integrity verification**: HMAC-SHA256 prevents tampering
- **90-day TTL**: Cache expires after 90 days

If task or context changes, cache automatically misses and fresh response is generated.

### How do I monitor performance?

```bash
# View performance summary
claude-force metrics summary

# View per-agent metrics
claude-force metrics agents

# View cost analysis
claude-force metrics costs

# Export for analysis
claude-force metrics export metrics.json --format json
```

**Python API**:
```python
orchestrator = AgentOrchestrator(enable_tracking=True)

# Run agents (tracking is automatic)
result = orchestrator.run_agent("code-reviewer", task="...")

# Get metrics
summary = orchestrator.get_performance_summary()
print(f"Total cost: ${summary['total_cost']:.4f}")
print(f"Avg time: {summary['avg_execution_time_ms']:.0f}ms")
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"

**Solution**:
```bash
# Set environment variable
export ANTHROPIC_API_KEY='your-api-key-here'

# Or add to .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env

# Verify it's set
claude-force diagnose
```

### Error: "Agent not found"

**Solution**:
```bash
# List available agents
claude-force list agents

# Check agent name spelling
claude-force info security-specialist  # correct
claude-force info security-expert      # incorrect
```

### Error: "Module not found: sentence-transformers"

**Cause**: Semantic selection requires optional dependencies.

**Solution**:
```bash
# Install semantic dependencies
pip install -e ".[semantic]"

# Or disable semantic selection
claude-force run agent code-reviewer --task "..." --no-semantic
```

### Performance is slow

**Possible causes and solutions**:

1. **First-time semantic model loading** (90-420MB)
   - Normal on first use
   - Subsequent uses are fast (lazy-loaded)

2. **Large task description** (>10K tokens)
   - Solution: Simplify task description
   - Use progressive skills loading

3. **Network latency**
   - Check internet connection
   - Try again or use cached responses

4. **Too many concurrent requests**
   - Use async orchestrator with rate limiting
   - Default: 3 concurrent requests max

### Cache not working

**Check**:
```bash
# Verify cache is enabled
claude-force config show | grep cache

# Check cache size
du -sh .claude/cache

# Clear cache if corrupted
rm -rf .claude/cache/*.db
```

**Enable caching**:
```python
orchestrator = AgentOrchestrator(enable_cache=True)
```

### Tests failing

```bash
# See detailed output
python3 -m pytest tests/ -v --tb=short

# Run specific test
python3 -m pytest tests/test_orchestrator.py::test_run_agent -v

# Check test coverage
python3 -m pytest tests/ --cov=claude_force --cov-report=html
```

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Advanced Topics

### How do I integrate with GitHub Actions?

See [examples/github-actions/](examples/github-actions/) for:
- Automated code review on PRs
- Security scanning
- Documentation generation

Example:
```yaml
name: Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Claude Force
        run: pip install claude-force
      - name: Run Code Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude-force run agent code-reviewer \
            --task "Review PR changes" \
            --output review.md
```

### Can I use Claude Force in CI/CD?

Yes! Claude Force has a quiet mode for scripting:

```bash
# Quiet mode (minimal output)
claude-force run agent code-reviewer --task "..." --quiet

# JSON output for parsing
claude-force run agent security-specialist --task "..." --format json

# Exit codes for CI/CD
if claude-force run agent code-reviewer --task "..." --quiet; then
  echo "Review passed"
else
  echo "Review failed"
  exit 1
fi
```

### How do I use the MCP server?

The MCP (Model Context Protocol) server enables integration with Claude Code:

```bash
# Start MCP server
python -m claude_force.mcp_server --port 8080

# Configure in Claude Code
# Add to MCP servers list: http://localhost:8080
```

See [examples/mcp/README.md](examples/mcp/README.md) for full setup.

### How do I use the marketplace?

```bash
# Search for plugins
claude-force marketplace search "kubernetes"

# Install plugin
claude-force marketplace install wshobson-devops-toolkit

# List installed plugins
claude-force marketplace list --installed

# Uninstall plugin
claude-force marketplace uninstall wshobson-devops-toolkit
```

### Can I import agents from other repositories?

Yes! Claude Force supports agent import/export:

```bash
# Import from wshobson/agents
claude-force import wshobson kubernetes-engineer.md

# Export for sharing
claude-force export ai-engineer --format wshobson

# Bulk import
claude-force import wshobson *.md
```

### How do I contribute to the marketplace?

See [CONTRIBUTING.md](CONTRIBUTING.md) and:

```bash
# Validate your agent
claude-force contribute validate my-agent.md

# Prepare for submission
claude-force contribute prepare my-agent.md
# Generates PR template and validation report
```

### What security measures are in place?

**Multiple security layers**:
- ✅ Path traversal prevention
- ✅ Input validation and sanitization
- ✅ HMAC-SHA256 cache verification
- ✅ Secure API key handling (never logged)
- ✅ Secret scanning (prevents commits with keys)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Rate limiting

**Security Grade**: A- (Excellent)

See [SECURITY_REVIEW.md](SECURITY_REVIEW.md) for full audit.

### How do I configure logging?

```bash
# Set log level
export CLAUDE_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Log to file
export CLAUDE_LOG_FILE=claude-force.log

# Or use config
claude-force config set log_level DEBUG
claude-force config set log_file claude-force.log
```

**Python API**:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
orchestrator = AgentOrchestrator()
```

## Contributing

### How can I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

**Ways to contribute**:
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🧪 Add tests
- 🤖 Create new agents
- ⚙️ Create new skills
- 🔧 Fix issues

### Where do I report bugs?

GitHub Issues: https://github.com/khanh-vu/claude-force/issues

**Include**:
- Claude Force version (`claude-force --version`)
- Python version (`python --version`)
- Error message and stack trace
- Steps to reproduce
- Expected vs actual behavior

### How do I request features?

GitHub Issues with label `enhancement`:
https://github.com/khanh-vu/claude-force/issues/new?labels=enhancement

**Include**:
- Clear description of feature
- Use cases and benefits
- Proposed implementation (if applicable)
- Examples of similar features elsewhere

### Can I use Claude Force commercially?

Yes! Claude Force is MIT licensed. You can:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Sublicense

**Requirements**:
- Include MIT license and copyright notice
- Comply with Anthropic's API terms of service

---

## Still have questions?

- 📖 Read the [documentation](README.md)
- 🔍 Search [existing issues](https://github.com/khanh-vu/claude-force/issues)
- 💬 Start a [discussion](https://github.com/khanh-vu/claude-force/discussions)
- 📧 Contact the maintainers

**Quick Links**:
- [README.md](README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - 5-minute guide
- [INSTALLATION.md](INSTALLATION.md) - Detailed setup
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
