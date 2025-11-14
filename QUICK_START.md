# Claude-Force Quick Start Guide

**Version**: 2.1.0
**Get started with the Claude Multi-Agent Orchestration System in 5 minutes**

---

## 🚀 Installation (30 seconds)

### Option 1: Install from PyPI (Recommended)

```bash
# Install
pip install claude-force

# Verify
claude-force --version
# Output: claude-force 2.1.0

# Set API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Option 2: Install from Source

```bash
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force
pip install -e .
```

---

## 🎯 Your First Command (1 minute)

### List Available Agents

```bash
claude-force list agents
```

**Output**:
```
📋 Available Agents

Name                           Priority   Domains
--------------------------------------------------------------------------------
code-reviewer                  Critical   code-quality, security, performance
bug-investigator               Critical   debugging, root-cause, investigation
security-specialist            Critical   security, compliance, threat-modeling
frontend-architect             High       architecture, react, nextjs
backend-architect              High       api-design, microservices
...

Total: 19 agents
```

### Run Your First Agent

```bash
claude-force run agent code-reviewer --task "Review this code: def add(a, b): return a + b"
```

**Output**:
```
🤖 Running agent: code-reviewer
📝 Task: Review this code: def add(a, b): return a + b

✅ Agent completed successfully!

📊 Performance:
   Execution time: 1,234ms
   Tokens: 156 input, 289 output
   Cost: $0.0024

📄 Output:
The code is simple and functional but lacks:
1. Type hints
2. Docstring
3. Input validation

Improved version:
def add(a: int | float, b: int | float) -> int | float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b
```

**Congratulations!** 🎉 You've run your first agent!

---

## 💡 Key Features (v2.1)

### 1. 🧠 Semantic Agent Recommendation

**Don't know which agent to use?** Let AI recommend the best one!

```bash
# Get agent recommendations for your task
claude-force recommend --task "Fix authentication bug in login endpoint"
```

**Output**:
```
🔍 Analyzing task... Done!

📊 Recommended Agents:

1. bug-investigator (87% confidence)
   Reasoning: Task involves debugging and root cause analysis of authentication issues.
   Keywords matched: bug, fix, endpoint

2. security-specialist (76% confidence)
   Reasoning: Authentication issues often have security implications.
   Keywords matched: authentication, login

3. backend-architect (65% confidence)
   Reasoning: Login endpoints are backend API concerns.
   Keywords matched: endpoint

Run recommended agent:
  claude-force run agent bug-investigator --task "Fix authentication bug in login endpoint"
```

### 2. 🎨 Project Initialization

**Start a new project with AI-guided setup:**

```bash
# Interactive mode - AI asks questions and recommends templates
claude-force init my-project --interactive
```

**Example Interaction**:
```
? Project name: my-awesome-app
? Project description: Build a RAG chatbot with Claude
? Tech stack (comma-separated): Python,FastAPI,Pinecone,React

🤖 Analyzing project requirements...

✅ Recommended template: llm-app
   Reason: LLM-powered application with RAG and vector search

Creating project structure...
✅ Created .claude/
✅ Created .claude/agents/ (19 agents)
✅ Created .claude/contracts/ (19 contracts)
✅ Created .claude/task.md
✅ Created README.md

🎉 Project initialized! Next steps:
   cd my-project
   claude-force run agent ai-engineer --task "Design RAG architecture"
```

**Non-interactive mode**:
```bash
claude-force init my-api \
  --description "REST API for e-commerce" \
  --tech "Python,FastAPI,PostgreSQL"
```

**Available Templates**:
- `fullstack-web` - Full-Stack Web Application
- `llm-app` - LLM-Powered Application (RAG, chatbots)
- `ml-project` - Machine Learning Project
- `data-pipeline` - Data Engineering Pipeline
- `api-service` - REST API Service
- `frontend-spa` - Frontend SPA
- `mobile-app` - Mobile Application
- `infrastructure` - Infrastructure & DevOps

### 3. ⚡ Hybrid Model Orchestration

**Automatically select the best model (Haiku/Sonnet/Opus) to optimize cost:**

```bash
# Auto-select model based on task complexity
claude-force run agent document-writer-expert \
  --task "Generate API documentation" \
  --auto-select-model
# → Selects Haiku (60-80% cost savings)

# Show cost estimate before running
claude-force run agent frontend-architect \
  --task "Design component architecture" \
  --auto-select-model \
  --estimate-cost
```

**Output**:
```
📊 Cost Estimate:
   Task complexity: Medium
   Selected model: claude-3-5-sonnet-20241022
   Estimated tokens: 2,500 input + 2,000 output
   Estimated cost: $0.037500

Proceed? [Y/n]:
```

**Model Selection Rules**:
- **Haiku** (Fast, cheap): Documentation, formatting, simple transforms
- **Sonnet** (Powerful): Architecture, code generation, complex reasoning
- **Opus** (Critical): Security audits, production deployments

**Benefits**:
- ⚡ 60-80% cost savings for simple tasks
- 🚀 3-5x faster execution
- 💰 Cost estimation and thresholds

### 4. 📊 Performance Metrics

**Track agent performance, costs, and success rates:**

```bash
# Summary statistics
claude-force metrics summary
```

**Output**:
```
📊 Performance Summary

Total Executions:      156
Success Rate:          94.2%
Failed Executions:     9
Total Cost:            $12.34
Avg Execution Time:    2,456ms
Total Tokens:          1.2M (750K input, 450K output)

Top Agents:
1. code-reviewer      45 runs  100.0% success
2. bug-investigator   32 runs   93.8% success
3. frontend-architect 28 runs   96.4% success
```

```bash
# Per-agent breakdown
claude-force metrics agents
```

**Output**:
```
📊 Agent Performance

Agent                  Runs  Success   Avg Time    Cost      Tokens
--------------------------------------------------------------------------------
code-reviewer          45    100.0%    1,234ms     $3.45     156K
bug-investigator       32     93.8%    2,567ms     $5.67     203K
frontend-architect     28     96.4%    3,123ms     $4.89     187K
...
```

```bash
# Cost breakdown
claude-force metrics costs
```

**Output**:
```
💰 Cost Breakdown

Total Cost: $12.34

By Agent:
  code-reviewer       $3.45  ███████░░░░░░░ 28.0%
  bug-investigator    $5.67  ████████████░░ 46.0%
  frontend-architect  $4.89  ██████████░░░░ 39.6%

By Model:
  claude-3-5-sonnet   $8.90  ████████████░░ 72.1%
  claude-3-haiku      $3.44  ███████░░░░░░░ 27.9%
```

### 5. 🛒 Marketplace

**Discover and install community plugins:**

```bash
# Browse marketplace
claude-force marketplace list
```

**Output**:
```
🛒 Claude-Force Marketplace

Available Plugins (12)

Name                    Version   Category       Downloads
--------------------------------------------------------------------------------
advanced-code-reviewer  1.2.0     Quality        1,234
terraform-expert        0.9.0     Infrastructure   892
rust-developer          1.0.1     Languages        567
...
```

```bash
# Search for plugins
claude-force marketplace search "kubernetes"
```

**Output**:
```
🔍 Search Results (3)

1. kubernetes-expert (1.1.0)
   Deploy and manage Kubernetes clusters
   Keywords: k8s, containers, orchestration

2. k8s-security-scanner (0.8.0)
   Security analysis for Kubernetes configs
   Keywords: security, k8s, compliance
...
```

```bash
# Install a plugin
claude-force marketplace install advanced-code-reviewer

# Uninstall a plugin
claude-force marketplace uninstall advanced-code-reviewer
```

### 6. 🔄 Workflow Composer

**Let AI generate multi-agent workflows from high-level goals:**

```bash
claude-force compose --goal "Build a user authentication system"
```

**Output**:
```
🤖 Analyzing goal... Done!

📋 Generated Workflow: user-authentication-system

Agents:
1. security-specialist    - Design authentication architecture
2. backend-architect      - Design API endpoints
3. database-architect     - Design user schema
4. python-expert          - Implement auth logic
5. qc-automation-expert   - Create test suite

Estimated Duration: 45-60 minutes
Estimated Cost: $1.20 - $1.80

💾 Workflow saved to: .claude/workflows/user-authentication-system.md

Run workflow:
  claude-force run workflow user-authentication-system --task-file .claude/task.md
```

### 7. 📈 Agent Comparison

**Compare agents for your specific task:**

```bash
claude-force analyze compare \
  --task "Review code for security vulnerabilities" \
  --agents code-reviewer security-specialist
```

**Output**:
```
📊 Agent Comparison

Task: Review code for security vulnerabilities

Agent: code-reviewer
  Suitability: 72%
  Strengths: Code quality analysis, performance review
  Weaknesses: May miss advanced security patterns
  Estimated Cost: $0.025
  Estimated Time: 1,200ms

Agent: security-specialist
  Suitability: 94%
  Strengths: Security expertise, threat modeling, vulnerability detection
  Weaknesses: Less focus on code style
  Estimated Cost: $0.035
  Estimated Time: 2,100ms

✅ Recommendation: security-specialist
   Better suited for security-focused review
```

---

## 📚 Common Use Cases

### Use Case 1: Code Review

```bash
# Simple review
claude-force run agent code-reviewer --task "Review src/api.py"

# From file
claude-force run agent code-reviewer --task-file .claude/task.md

# With auto-model selection
claude-force run agent code-reviewer --task "Review src/api.py" --auto-select-model
```

### Use Case 2: Bug Investigation

```bash
# Investigate a bug
claude-force run agent bug-investigator --task "Login fails with 500 error"

# Get agent recommendation first
claude-force recommend --task "Login fails with 500 error"
# → Then run recommended agent
```

### Use Case 3: Architecture Design

```bash
# Design frontend architecture
claude-force run agent frontend-architect \
  --task "Design component architecture for e-commerce product page"

# Design backend API
claude-force run agent backend-architect \
  --task "Design REST API for user management"
```

### Use Case 4: Complete Workflow

```bash
# Run pre-built workflow
claude-force run workflow bug-fix --task-file .claude/task.md

# Or compose custom workflow
claude-force compose --goal "Add payment processing feature"
```

### Use Case 5: Import/Export Agents

```bash
# Export agent to wshobson format
claude-force export code-reviewer --format wshobson

# Import agent
claude-force import custom-agent.md

# Bulk import
claude-force import-bulk ./agents/
```

---

## 🐍 Python API

### Basic Usage

```python
from claude_force import AgentOrchestrator

# Create orchestrator
orchestrator = AgentOrchestrator()

# Run a single agent
result = orchestrator.run_agent(
    agent_name='code-reviewer',
    task='Review the authentication logic in src/auth.py'
)

if result.success:
    print(f"✅ Success! Output:\n{result.output}")
    print(f"💰 Cost: ${result.cost:.4f}")
    print(f"⏱️  Time: {result.execution_time_ms}ms")
else:
    print(f"❌ Failed: {result.errors}")
```

### Semantic Agent Selection

```python
from claude_force import SemanticAgentSelector

selector = SemanticAgentSelector()

# Get recommendations
recommendations = selector.recommend_agents(
    task="Fix authentication bug in login endpoint",
    top_k=3,
    min_confidence=0.3
)

for match in recommendations:
    print(f"{match.agent_name}: {match.confidence:.0%} confidence")
    print(f"  Reasoning: {match.reasoning}\n")

# Output:
# bug-investigator: 87% confidence
#   Reasoning: Task involves debugging and root cause analysis...
# security-specialist: 76% confidence
#   Reasoning: Authentication issues have security implications...
```

### Hybrid Orchestration

```python
from claude_force import HybridOrchestrator

orchestrator = HybridOrchestrator(
    auto_select_model=True,
    cost_threshold=1.0  # Max $1 per task
)

# Auto-selects optimal model (Haiku/Sonnet/Opus)
result = orchestrator.run_agent(
    agent_name='document-writer-expert',
    task='Generate API documentation for payment service'
)
# → Automatically selects Haiku (cheap for documentation)

print(f"Model used: {result.model}")
print(f"Cost: ${result.cost:.4f}")
```

### Run Workflow

```python
# Run workflow
results = orchestrator.run_workflow(
    workflow_name='bug-fix',
    task='Fix login authentication error'
)

# Check results
for i, result in enumerate(results, 1):
    print(f"Step {i}: {result.agent_name}")
    print(f"  Status: {'✅' if result.success else '❌'}")
    print(f"  Time: {result.execution_time_ms}ms")
    print(f"  Cost: ${result.cost:.4f}\n")
```

### Performance Tracking

```python
# Get performance summary
summary = orchestrator.get_performance_summary()

print(f"Total executions: {summary['total_executions']}")
print(f"Success rate: {summary['success_rate']:.1%}")
print(f"Total cost: ${summary['total_cost']:.2f}")
print(f"Avg time: {summary['avg_execution_time_ms']:.0f}ms")

# Get cost breakdown
costs = orchestrator.get_cost_breakdown()
for agent, cost in costs['by_agent'].items():
    print(f"{agent}: ${cost:.2f}")
```

### Custom Agent Configuration

```python
# Load custom configuration
orchestrator = AgentOrchestrator(
    config_path='/custom/path/claude.json',
    api_key='your-api-key'
)

# Or pass API key directly
orchestrator = AgentOrchestrator(api_key='sk-ant-...')
```

---

## 🎓 Advanced Features

### 1. Task Complexity Analysis

```bash
claude-force analyze-task --task "Implement OAuth2 authentication flow with JWT tokens"
```

**Output**:
```
📊 Task Analysis

Complexity: High
Estimated Duration: 2-3 hours
Recommended Model: claude-3-5-sonnet (requires complex reasoning)
Estimated Cost: $0.45 - $0.75

Suggested Agents:
1. security-specialist (primary)
2. backend-architect (supporting)
3. python-expert (implementation)

Suggested Approach:
1. Design authentication architecture (30min)
2. Implement OAuth2 flow (60min)
3. Implement JWT handling (30min)
4. Write tests (30min)
5. Security review (20min)
```

### 2. Template Gallery

```bash
# Browse templates
claude-force gallery browse

# Search templates
claude-force gallery search "machine learning"

# Use template in init
claude-force init my-ml-project --template ml-project
```

### 3. Contribution

```bash
# Validate agent before contributing
claude-force contribute validate code-reviewer

# Prepare for contribution
claude-force contribute prepare code-reviewer

# Export for sharing
claude-force export code-reviewer --format marketplace
```

---

## 🔧 Configuration

### Environment Variables

```bash
# API key
export ANTHROPIC_API_KEY='your-api-key'

# Custom config path
export CLAUDE_FORCE_CONFIG='/path/to/claude.json'

# Default model
export CLAUDE_FORCE_DEFAULT_MODEL='claude-3-5-sonnet-20241022'
```

### Config File (`.claude/claude.json`)

```json
{
  "version": "2.1.0",
  "default_model": "claude-3-5-sonnet-20241022",
  "agents": {
    "code-reviewer": {
      "role": "Code Review Expert",
      "priority": "Critical",
      "domains": ["code-quality", "security", "performance"]
    }
  },
  "workflows": {
    "bug-fix": {
      "agents": ["bug-investigator", "code-reviewer", "qc-automation-expert"]
    }
  }
}
```

---

## 🆘 Troubleshooting

### Issue: `command not found: claude-force`

**Solution**:
```bash
# Reinstall
pip install --upgrade claude-force

# Check installation
pip show claude-force
which claude-force
```

### Issue: `ValueError: Anthropic API key required`

**Solution**:
```bash
# Set environment variable
export ANTHROPIC_API_KEY='your-api-key'

# Or pass on command line
claude-force --api-key your-api-key run agent code-reviewer --task "..."
```

### Issue: Agent not found

**Solution**:
```bash
# List available agents
claude-force list agents

# Get agent info
claude-force info <agent-name>
```

### Issue: Config file not found

**Solution**:
```bash
# Initialize project first
claude-force init my-project

# Or specify config path
claude-force --config /path/to/claude.json run agent ...
```

---

## 📖 Next Steps

**You're now ready to use Claude-Force!** Here are some next steps:

1. **Try Examples**: Work through the use cases above
2. **Explore Agents**: `claude-force list agents`
3. **Read Full Docs**: See [README.md](README.md)
4. **Join Community**: [GitHub Discussions](https://github.com/khanh-vu/claude-force/discussions)
5. **Contribute**: See [Contributing Guide](CONTRIBUTING.md)

### Learning Resources

- **Full Documentation**: [README.md](README.md)
- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md) (coming soon)
- **Examples**: [examples/](examples/)
- **Benchmarks**: [benchmarks/](benchmarks/)

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/khanh-vu/claude-force/issues)
- **Discussions**: [Ask questions](https://github.com/khanh-vu/claude-force/discussions)
- **Documentation**: [Read the docs](https://github.com/khanh-vu/claude-force)

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Installation
pip install claude-force

# List agents
claude-force list agents

# Get recommendations
claude-force recommend --task "Your task here"

# Run agent
claude-force run agent <agent-name> --task "Your task"

# Run workflow
claude-force run workflow <workflow-name> --task "Your task"

# Initialize project
claude-force init my-project --interactive

# View metrics
claude-force metrics summary

# Browse marketplace
claude-force marketplace list
```

### Key Features

- 🧠 **Semantic Agent Selection** - AI recommends best agents
- 🎨 **Project Initialization** - AI-guided project setup
- ⚡ **Hybrid Orchestration** - Auto-select Haiku/Sonnet/Opus
- 📊 **Performance Metrics** - Track costs and success rates
- 🛒 **Marketplace** - Discover community plugins
- 🔄 **Workflow Composer** - Generate multi-agent workflows
- 📈 **Agent Comparison** - Compare agents for your task

---

**Happy Orchestrating!** 🚀

For more information, see the [full documentation](README.md).
