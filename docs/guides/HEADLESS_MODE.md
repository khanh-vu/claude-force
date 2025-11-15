# Headless Mode - Using Claude-Force Programmatically

**Headless mode** refers to using claude-force without the Claude Code UI, enabling programmatic access for automation, CI/CD pipelines, web applications, and server deployments.

claude-force provides **multiple headless execution modes** to suit different integration needs.

---

## 🎯 Overview

### Available Headless Modes

| Mode | Use Case | Interface | Best For |
|------|----------|-----------|----------|
| **Python API** | Scripts, automation, notebooks | Python | Python developers, data science |
| **CLI** | Terminal automation, scripts | Command line | Shell scripts, local automation |
| **REST API** | Web apps, microservices | HTTP/JSON | Language-agnostic integration |
| **MCP Server** | Claude Code integration | HTTP/MCP | Claude Code ecosystem |
| **GitHub Actions** | CI/CD pipelines | YAML workflows | Automated code review, testing |

---

## 1. Python API (Recommended for Python)

### Installation

```bash
pip install -e /path/to/claude-force
# Or when published: pip install claude-force
```

### Basic Usage

```python
from claude_force import AgentOrchestrator

# Initialize (reads .claude/claude.json by default)
orchestrator = AgentOrchestrator(
    anthropic_api_key="your-api-key",  # Or set ANTHROPIC_API_KEY
    enable_tracking=True  # Automatic performance tracking
)

# Run a single agent
result = orchestrator.run_agent(
    agent_name="code-reviewer",
    task="Review this code for security issues: ...",
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096
)

if result.success:
    print(result.output)
else:
    print(f"Error: {result.errors}")
```

### Advanced Usage

```python
# Run a workflow
result = orchestrator.run_workflow(
    workflow_name="bug-fix",
    initial_task="Investigate 500 errors in /api/users",
    model="claude-3-5-sonnet-20241022"
)

# Get agent recommendations (P1 feature)
recommendations = orchestrator.recommend_agents(
    task="Review authentication for SQL injection",
    top_k=3,
    min_confidence=0.3
)

for rec in recommendations:
    print(f"{rec['agent']}: {rec['confidence']*100:.1f}% - {rec['reasoning']}")

# View performance metrics (P1 feature)
summary = orchestrator.get_performance_summary(hours=24)
print(f"Total cost: ${summary['total_cost']:.4f}")
print(f"Success rate: {summary['success_rate']:.1%}")

# Export metrics
orchestrator.export_performance_metrics("metrics.json", format="json")
```

### Batch Processing

```python
# Process multiple tasks in parallel
import concurrent.futures

tasks = [
    ("code-reviewer", "Review auth.py"),
    ("code-reviewer", "Review database.py"),
    ("code-reviewer", "Review api.py"),
]

def process_task(agent, task):
    result = orchestrator.run_agent(agent_name=agent, task=task)
    return result.output if result.success else None

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(lambda x: process_task(*x), tasks))

for i, output in enumerate(results):
    print(f"Task {i+1}: {output[:100]}...")
```

### Error Handling

```python
try:
    result = orchestrator.run_agent(
        agent_name="code-reviewer",
        task="Review code"
    )

    if result.success:
        # Process successful result
        print(result.output)

        # Access metadata
        print(f"Execution time: {result.metadata.get('execution_time_ms')}ms")
        print(f"Tokens used: {result.metadata.get('tokens_used')}")
    else:
        # Handle errors
        for error in result.errors:
            print(f"Error: {error}")

except Exception as e:
    # Handle exceptions (network errors, API errors, etc.)
    print(f"Exception: {e}")
```

---

## 2. Command Line Interface (CLI)

### Installation

```bash
pip install -e /path/to/claude-force
```

### Basic Usage

```bash
# Set API key
export ANTHROPIC_API_KEY='your-api-key'

# List agents
claude-force list agents

# List workflows
claude-force list workflows

# Get agent info
claude-force info code-reviewer

# Run agent with inline task
claude-force run agent code-reviewer \
  --task "Review this code for bugs"

# Run agent with task from file
claude-force run agent code-reviewer \
  --task-file task.md

# Run agent with task from stdin
echo "Review this code" | claude-force run agent code-reviewer

# Run workflow
claude-force run workflow bug-fix \
  --task "Investigate login errors"

# Get agent recommendations (P1)
claude-force recommend \
  --task "Review authentication for SQL injection" \
  --top-k 3

# View performance metrics (P1)
claude-force metrics summary
claude-force metrics agents
claude-force metrics costs
claude-force metrics export metrics.json
```

### JSON Output (for scripts)

```bash
# Output as JSON for parsing
claude-force run agent code-reviewer \
  --task "Review code" \
  --json > result.json

# Parse with jq
claude-force run agent code-reviewer \
  --task "Review code" \
  --json | jq '.output'
```

### Shell Scripts

```bash
#!/bin/bash
# review-all.sh - Review all Python files

for file in src/*.py; do
    echo "Reviewing $file..."

    claude-force run agent code-reviewer \
        --task "Review this file for issues" \
        --task-file "$file" \
        --output "reviews/$(basename $file).review.md"

    if [ $? -eq 0 ]; then
        echo "✅ $file reviewed successfully"
    else
        echo "❌ $file review failed"
    fi
done
```

---

## 3. REST API Server

### Start Server

```bash
cd examples/api-server

# Install dependencies
pip install -r requirements.txt

# Start server
export ANTHROPIC_API_KEY='your-api-key'
uvicorn api_server:app --host 0.0.0.0 --port 8000

# Or with more workers
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Python Client

```python
from api_client import ClaudeForceClient

client = ClaudeForceClient(
    base_url="http://localhost:8000",
    api_key="dev-key-12345"
)

# Synchronous execution
result = client.run_agent_sync(
    agent_name="code-reviewer",
    task="Review code for security"
)

# Asynchronous execution
task_id = client.run_agent_async(
    agent_name="bug-investigator",
    task="Investigate login errors"
)

# Poll for completion
result = client.wait_for_task(task_id, timeout=60.0)

# Get metrics
summary = client.get_metrics_summary()
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# List agents
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/agents

# Execute agent
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "code-reviewer",
    "task": "Review this code for bugs",
    "model": "claude-3-5-sonnet-20241022"
  }' \
  http://localhost:8000/agents/run

# Execute async
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "bug-investigator",
    "task": "Investigate errors"
  }' \
  http://localhost:8000/agents/run/async

# Check task status
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/tasks/{task_id}
```

### JavaScript/Node.js

```javascript
// node-client.js
const fetch = require('node-fetch');

async function executeAgent(agentName, task) {
  const response = await fetch('http://localhost:8000/agents/run', {
    method: 'POST',
    headers: {
      'X-API-Key': 'dev-key-12345',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      agent_name: agentName,
      task: task,
      model: 'claude-3-5-sonnet-20241022'
    })
  });

  const result = await response.json();
  return result;
}

// Usage
const result = await executeAgent('code-reviewer', 'Review code');
console.log(result.output);
```

---

## 4. MCP (Model Context Protocol) Server

### Start MCP Server

```bash
# Start MCP server
export ANTHROPIC_API_KEY='your-api-key'
python -m claude_force.mcp_server --port 8080

# Or with custom config
python -m claude_force.mcp_server \
  --port 8080 \
  --config /path/to/claude.json
```

### Python Client

```python
from examples.mcp.mcp_client_example import MCPClient

client = MCPClient(base_url="http://localhost:8080")

# List capabilities
caps = client.list_capabilities()
print(f"Available: {caps['count']} capabilities")

# Execute agent
result = client.execute_agent(
    agent_name="code-reviewer",
    task="Review code",
    request_id="req-001"
)

# Execute workflow
workflow_result = client.execute_workflow(
    workflow_name="bug-fix",
    task="Investigate errors"
)

# Get recommendations
recs = client.recommend_agents(
    task="Review auth for SQL injection",
    top_k=3
)
```

### cURL Examples

```bash
# List capabilities
curl http://localhost:8080/capabilities

# Execute via MCP
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "code-reviewer",
    "action": "execute_agent",
    "parameters": {
      "task": "Review code",
      "model": "claude-3-5-sonnet-20241022"
    },
    "request_id": "req-001"
  }'
```

### Integration with Claude Code

```json
// Claude Code configuration
{
  "mcp_servers": {
    "claude-force": {
      "url": "http://localhost:8080",
      "protocol": "http",
      "capabilities": ["agents", "workflows"]
    }
  }
}
```

---

## 5. GitHub Actions (CI/CD)

### Code Review Workflow

```yaml
# .github/workflows/code-review.yml
name: Claude Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install claude-force
        run: pip install -e .

      - name: Review code
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude-force run agent code-reviewer \
            --task-file changed-files.txt \
            --output code-review.md

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('code-review.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

See [examples/github-actions/](../examples/github-actions/) for complete workflows.

---

## 6. Integration Patterns

### Web Application (Flask)

```python
from flask import Flask, request, jsonify
from claude_force import AgentOrchestrator

app = Flask(__name__)
orchestrator = AgentOrchestrator()

@app.route('/api/review', methods=['POST'])
def review_code():
    data = request.json
    code = data.get('code', '')

    result = orchestrator.run_agent(
        agent_name='code-reviewer',
        task=f"Review this code:\n{code}"
    )

    return jsonify({
        'success': result.success,
        'review': result.output,
        'errors': result.errors
    })

if __name__ == '__main__':
    app.run(port=5000)
```

### Jupyter Notebooks

```python
# In Jupyter notebook cell
from claude_force import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()

# Run agent
result = orchestrator.run_agent(
    agent_name='code-reviewer',
    task='Review this code for performance issues'
)

# Display result
from IPython.display import Markdown, display
display(Markdown(result.output))

# View metrics
summary = orchestrator.get_performance_summary()
display(summary)
```

### AWS Lambda

```python
# lambda_function.py
import os
from claude_force import AgentOrchestrator

orchestrator = AgentOrchestrator(
    anthropic_api_key=os.environ['ANTHROPIC_API_KEY']
)

def lambda_handler(event, context):
    agent_name = event.get('agent_name', 'code-reviewer')
    task = event.get('task', '')

    result = orchestrator.run_agent(
        agent_name=agent_name,
        task=task
    )

    return {
        'statusCode': 200 if result.success else 500,
        'body': {
            'output': result.output,
            'errors': result.errors
        }
    }
```

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install claude-force
COPY . .
RUN pip install -e .

# Set up entry point
COPY headless_runner.py .
CMD ["python", "headless_runner.py"]
```

```python
# headless_runner.py
import os
import sys
from claude_force import AgentOrchestrator

def main():
    agent_name = os.getenv('AGENT_NAME', 'code-reviewer')
    task = sys.stdin.read()

    orchestrator = AgentOrchestrator()
    result = orchestrator.run_agent(agent_name=agent_name, task=task)

    if result.success:
        print(result.output)
        return 0
    else:
        print(f"Error: {result.errors}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

```bash
# Run container
echo "Review this code" | docker run -i \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e AGENT_NAME="code-reviewer" \
  claude-force-headless
```

---

## 7. Configuration

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY='your-api-key'

# Optional
export CLAUDE_FORCE_CONFIG='/path/to/claude.json'
export CLAUDE_FORCE_MODEL='claude-3-5-sonnet-20241022'
export CLAUDE_FORCE_MAX_TOKENS='4096'
export CLAUDE_FORCE_TEMPERATURE='1.0'
```

### Programmatic Configuration

```python
from claude_force import AgentOrchestrator

orchestrator = AgentOrchestrator(
    config_path='/custom/path/claude.json',
    anthropic_api_key='your-key',
    enable_tracking=True  # Performance tracking
)

# Override defaults per execution
result = orchestrator.run_agent(
    agent_name='code-reviewer',
    task='Review code',
    model='claude-3-opus-20240229',  # Use more capable model
    max_tokens=8000,  # Longer response
    temperature=0.3  # More focused
)
```

---

## 8. Performance Optimization

### Async Execution

```python
import asyncio
from claude_force import AgentOrchestrator

async def review_files(files):
    orchestrator = AgentOrchestrator()
    tasks = []

    for file in files:
        task = asyncio.create_task(
            run_agent_async(orchestrator, 'code-reviewer', file)
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results

async def run_agent_async(orchestrator, agent, task):
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        orchestrator.run_agent,
        agent,
        task
    )

# Usage
asyncio.run(review_files(['file1.py', 'file2.py', 'file3.py']))
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_agent_recommendation(task_hash):
    """Cache agent recommendations"""
    orchestrator = AgentOrchestrator()
    return orchestrator.recommend_agents(task=task_hash)

# Usage
import hashlib
task = "Review auth code"
task_hash = hashlib.md5(task.encode()).hexdigest()
recommendations = get_agent_recommendation(task_hash)
```

---

## 9. Monitoring & Observability

### Built-in Performance Tracking

```python
orchestrator = AgentOrchestrator(enable_tracking=True)

# Metrics are automatically collected
result = orchestrator.run_agent('code-reviewer', task='...')

# View metrics
summary = orchestrator.get_performance_summary(hours=24)
print(f"Executions: {summary['total_executions']}")
print(f"Cost: ${summary['total_cost']:.4f}")
print(f"Success rate: {summary['success_rate']:.1%}")

# Export for analysis
orchestrator.export_performance_metrics('metrics.json', format='json')
```

### Custom Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claude-force.log'),
        logging.StreamHandler()
    ]
)

# Use orchestrator (logging is automatic)
orchestrator = AgentOrchestrator()
result = orchestrator.run_agent('code-reviewer', task='...')
```

---

## 10. Security Best Practices

### API Key Management

```python
# ✅ Good: Use environment variables
import os
api_key = os.getenv('ANTHROPIC_API_KEY')

# ✅ Good: Use secrets manager
from boto3 import client
secrets = client('secretsmanager')
api_key = secrets.get_secret_value(SecretId='anthropic-key')['SecretString']

# ❌ Bad: Hardcode API keys
api_key = 'sk-ant-...'  # NEVER DO THIS
```

### Input Validation

```python
def safe_execute_agent(agent_name, task):
    # Validate agent name
    valid_agents = ['code-reviewer', 'security-specialist', 'bug-investigator']
    if agent_name not in valid_agents:
        raise ValueError(f"Invalid agent: {agent_name}")

    # Validate task length
    if len(task) > 10000:
        raise ValueError("Task too long")

    # Execute
    orchestrator = AgentOrchestrator()
    return orchestrator.run_agent(agent_name=agent_name, task=task)
```

---

## 11. Troubleshooting

### Common Issues

**Issue**: `ANTHROPIC_API_KEY not set`
```python
# Solution: Set environment variable
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key'

# Or pass directly
orchestrator = AgentOrchestrator(anthropic_api_key='your-key')
```

**Issue**: `Agent not found`
```python
# Solution: List available agents
orchestrator = AgentOrchestrator()
print(orchestrator.list_agents())

# Check agent exists
agent_info = orchestrator.get_agent_info('agent-name')
```

**Issue**: `Timeout errors`
```python
# Solution: Reduce max_tokens or increase timeout
result = orchestrator.run_agent(
    agent_name='code-reviewer',
    task='...',
    max_tokens=2000  # Reduce from default 4096
)
```

---

## 12. Examples

See complete examples in:
- [examples/python/](../examples/python/) - Python API examples
- [examples/api-server/](../examples/api-server/) - REST API examples
- [examples/mcp/](../examples/mcp/) - MCP server examples
- [examples/github-actions/](../examples/github-actions/) - CI/CD examples

---

## 📚 Additional Resources

- [Main README](../README.md)
- [Installation Guide](../INSTALLATION.md)
- [API Documentation](../BUILD_DOCUMENTATION.md)
- [MCP Server Documentation](../examples/mcp/README.md)
- [REST API Documentation](../examples/api-server/README.md)

---

**Questions?** Open an issue or check the comprehensive documentation.
