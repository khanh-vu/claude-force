# AgentOrchestrator

Core orchestration engine for running Claude agents and workflows.

## Overview

`AgentOrchestrator` is the main class for executing agents and multi-agent workflows. It handles:

- Loading agent definitions and contracts
- Calling the Claude API
- Managing performance tracking
- Executing multi-agent workflows
- Error handling and result formatting

## Class Reference

### Constructor

```python
AgentOrchestrator(
    config_path: str = ".claude/claude.json",
    anthropic_api_key: Optional[str] = None,
    enable_tracking: bool = True
)
```

**Parameters**:

- `config_path` (str): Path to claude.json configuration file. Defaults to `.claude/claude.json`.
- `anthropic_api_key` (str, optional): Anthropic API key. If not provided, reads from `ANTHROPIC_API_KEY` environment variable.
- `enable_tracking` (bool): Enable performance tracking. Defaults to `True`.

**Raises**:

- `ValueError`: If API key is not provided or found in environment
- `FileNotFoundError`: If config file doesn't exist
- `ImportError`: If `anthropic` package is not installed

**Example**:

```python
from claude_force.orchestrator import AgentOrchestrator

# Using environment variable for API key
orchestrator = AgentOrchestrator(config_path=".claude/claude.json")

# Providing API key explicitly
orchestrator = AgentOrchestrator(
    config_path=".claude/claude.json",
    anthropic_api_key="your-api-key-here",
    enable_tracking=True
)
```

---

### run_agent()

Run a single agent on a task.

```python
run_agent(
    agent_name: str,
    task: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 4096,
    temperature: float = 1.0,
    workflow_name: Optional[str] = None,
    workflow_position: Optional[int] = None
) -> AgentResult
```

**Parameters**:

- `agent_name` (str): Name of agent to run (must exist in config)
- `task` (str): Task description or content to process
- `model` (str): Claude model to use. Options:
  - `claude-3-haiku-20240307` (cheapest, fastest)
  - `claude-3-5-sonnet-20241022` (balanced, recommended)
  - `claude-3-opus-20240229` (most capable)
- `max_tokens` (int): Maximum tokens in response (default: 4096)
- `temperature` (float): Temperature for generation 0.0-1.0 (default: 1.0)
- `workflow_name` (str, optional): Internal use for workflow tracking
- `workflow_position` (int, optional): Internal use for workflow tracking

**Returns**:

`AgentResult` object with:
- `agent_name` (str): Name of agent that ran
- `success` (bool): Whether execution succeeded
- `output` (str): Agent's response
- `metadata` (dict): Execution metadata (model, tokens, duration, cost)
- `errors` (List[str]): Error messages if any

**Raises**:

- `ValueError`: If agent_name not found in configuration
- `FileNotFoundError`: If agent definition file not found
- `APIError`: If Claude API call fails

**Example**:

```python
orchestrator = AgentOrchestrator()

# Simple execution
result = orchestrator.run_agent(
    agent_name="code-reviewer",
    task="Review this code for security issues:\n\ndef login(user, password):\n    return user.password == password"
)

print(f"Success: {result.success}")
print(f"Output:\n{result.output}")
print(f"Tokens used: {result.metadata['total_tokens']}")
print(f"Cost: ${result.metadata['estimated_cost']:.4f}")

# Custom model selection
result = orchestrator.run_agent(
    agent_name="backend-architect",
    task="Design a scalable microservices architecture",
    model="claude-3-opus-20240229",  # Use most capable model
    max_tokens=8192,  # Longer response
    temperature=0.7   # More focused
)
```

---

### run_workflow()

Run a multi-agent workflow.

```python
run_workflow(
    workflow_name: str,
    task: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 4096,
    temperature: float = 1.0,
    stop_on_error: bool = False
) -> List[AgentResult]
```

**Parameters**:

- `workflow_name` (str): Name of workflow defined in config
- `task` (str): Task description for the workflow
- `model` (str): Claude model to use for all agents
- `max_tokens` (int): Maximum tokens per agent
- `temperature` (float): Temperature for generation
- `stop_on_error` (bool): Stop workflow if any agent fails (default: False)

**Returns**:

List of `AgentResult` objects, one per agent in workflow

**Example**:

```python
orchestrator = AgentOrchestrator()

# Run predefined workflow
results = orchestrator.run_workflow(
    workflow_name="full-stack-feature",
    task="Implement user authentication with JWT"
)

# Check results
for i, result in enumerate(results):
    print(f"\n{i+1}. {result.agent_name}")
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Output: {result.output[:100]}...")
    else:
        print(f"   Errors: {result.errors}")

# Stop on first failure
results = orchestrator.run_workflow(
    workflow_name="code-review-fix-test",
    task="Fix authentication bug",
    stop_on_error=True  # Stops if any agent fails
)
```

---

### list_agents()

Get list of available agents.

```python
list_agents() -> List[str]
```

**Returns**:

List of agent names defined in configuration

**Example**:

```python
orchestrator = AgentOrchestrator()

agents = orchestrator.list_agents()
print(f"Available agents: {', '.join(agents)}")
# Output: Available agents: code-reviewer, backend-developer, security-specialist, ...
```

---

### get_agent_info()

Get detailed information about an agent.

```python
get_agent_info(agent_name: str) -> Dict[str, Any]
```

**Parameters**:

- `agent_name` (str): Name of agent

**Returns**:

Dictionary with:
- `name` (str): Agent name
- `file` (str): Path to agent definition
- `contract` (str): Path to agent contract
- `domains` (List[str]): Agent expertise domains
- `priority` (int): Agent priority level

**Example**:

```python
info = orchestrator.get_agent_info("code-reviewer")
print(f"Domains: {info['domains']}")
print(f"Priority: {info['priority']}")
# Output:
# Domains: ['code-quality', 'security', 'performance']
# Priority: 1
```

---

### list_workflows()

Get list of available workflows.

```python
list_workflows() -> List[str]
```

**Returns**:

List of workflow names defined in configuration

**Example**:

```python
workflows = orchestrator.list_workflows()
for workflow in workflows:
    print(f"- {workflow}")
# Output:
# - full-stack-feature
# - bug-fix
# - code-review-test
```

---

### get_workflow_info()

Get detailed information about a workflow.

```python
get_workflow_info(workflow_name: str) -> Dict[str, Any]
```

**Parameters**:

- `workflow_name` (str): Name of workflow

**Returns**:

Dictionary with:
- `name` (str): Workflow name
- `agents` (List[str]): List of agent names in workflow
- `steps` (int): Number of steps

**Example**:

```python
info = orchestrator.get_workflow_info("full-stack-feature")
print(f"Agents in workflow: {info['agents']}")
print(f"Total steps: {info['steps']}")
# Output:
# Agents in workflow: ['backend-architect', 'backend-developer', 'code-reviewer']
# Total steps: 3
```

---

## Data Classes

### AgentResult

Result object returned by `run_agent()` and `run_workflow()`.

**Attributes**:

- `agent_name` (str): Name of agent that executed
- `success` (bool): Whether execution succeeded
- `output` (str): Agent's response text
- `metadata` (Dict[str, Any]): Execution metadata
  - `model` (str): Claude model used
  - `input_tokens` (int): Input tokens consumed
  - `output_tokens` (int): Output tokens generated
  - `total_tokens` (int): Total tokens used
  - `execution_time_ms` (float): Execution time in milliseconds
  - `estimated_cost` (float): Estimated cost in USD
- `errors` (List[str], optional): Error messages if execution failed

**Methods**:

- `to_dict()`: Convert result to dictionary

**Example**:

```python
result = orchestrator.run_agent("code-reviewer", "Review code")

# Access attributes
if result.success:
    print(result.output)
    print(f"Took {result.metadata['execution_time_ms']:.0f}ms")
    print(f"Cost: ${result.metadata['estimated_cost']:.4f}")
else:
    print(f"Errors: {result.errors}")

# Convert to dict for JSON export
result_dict = result.to_dict()
import json
print(json.dumps(result_dict, indent=2))
```

---

## Performance Tracking

When `enable_tracking=True`, the orchestrator automatically records execution metrics:

```python
orchestrator = AgentOrchestrator(enable_tracking=True)

# Metrics are automatically recorded
result = orchestrator.run_agent("code-reviewer", "Review code")

# Access tracker
if orchestrator.tracker:
    summary = orchestrator.tracker.get_summary()
    print(f"Total executions: {summary['total_executions']}")
    print(f"Total cost: ${summary['total_cost']:.2f}")
```

Metrics are stored in `.claude/metrics/executions.jsonl` and can be analyzed using the `PerformanceTracker` API or `claude-force analyze` CLI command.

---

## Error Handling

The orchestrator provides detailed error handling:

```python
from claude_force.orchestrator import AgentOrchestrator

try:
    orchestrator = AgentOrchestrator(config_path=".claude/claude.json")
    result = orchestrator.run_agent("code-reviewer", "Review this code")

    if not result.success:
        print(f"Agent execution failed: {result.errors}")

except FileNotFoundError as e:
    print(f"Config file not found: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except ImportError:
    print("Install anthropic package: pip install anthropic")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Configuration

The orchestrator requires a `claude.json` configuration file:

```json
{
  "name": "my-project",
  "version": "1.0",
  "agents": {
    "code-reviewer": {
      "file": "agents/code-reviewer.md",
      "contract": "contracts/code-reviewer.contract",
      "domains": ["code-quality", "security"],
      "priority": 1
    }
  },
  "workflows": {
    "review-fix-test": ["code-reviewer", "backend-developer", "qa-engineer"]
  }
}
```

---

## Advanced Usage

### Custom Workflow Context

Pass context between agents in a workflow:

```python
# First agent generates code
result1 = orchestrator.run_agent(
    "backend-developer",
    "Implement login endpoint"
)

# Second agent reviews the generated code
result2 = orchestrator.run_agent(
    "code-reviewer",
    f"Review this code:\n\n{result1.output}"
)

# Third agent writes tests based on code
result3 = orchestrator.run_agent(
    "qa-engineer",
    f"Write tests for:\n\n{result1.output}"
)
```

### Model Selection Strategy

Choose models based on task complexity:

```python
# Simple tasks: use Haiku (cheapest)
result = orchestrator.run_agent(
    "code-reviewer",
    "Fix typo in README",
    model="claude-3-haiku-20240307"
)

# Moderate tasks: use Sonnet (balanced)
result = orchestrator.run_agent(
    "backend-developer",
    "Implement REST endpoint",
    model="claude-3-5-sonnet-20241022"
)

# Complex tasks: use Opus (most capable)
result = orchestrator.run_agent(
    "backend-architect",
    "Design complete microservices architecture",
    model="claude-3-opus-20240229"
)
```

---

## Related

- [HybridOrchestrator](hybrid-orchestrator.md) - Automatic model selection
- [SemanticAgentSelector](semantic-selector.md) - AI-powered agent recommendation
- [PerformanceTracker](performance-tracker.md) - Metrics and analytics
- [CLI Reference](cli.md) - Command-line usage

---

**See Also**: [Quick Start Guide](../quickstart.md), [Workflow Guide](../guides/workflows.md)
