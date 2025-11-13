# MCP (Model Context Protocol) Server

This directory contains the MCP server implementation for claude-force, enabling integration with Claude Code and other MCP-compatible clients.

## 🎯 What is MCP?

**MCP (Model Context Protocol)** is a standard protocol for AI agent communication that allows:
- **Discovery**: Clients can discover available agent capabilities
- **Execution**: Standardized way to execute agents and workflows
- **Integration**: Universal compatibility with MCP-compatible tools

## 🚀 Quick Start

### Start MCP Server

```bash
# Method 1: Using Python module
export ANTHROPIC_API_KEY='your-api-key'
python -m claude_force.mcp_server --port 8080

# Method 2: Programmatically
from claude_force.mcp_server import MCPServer

server = MCPServer()
server.start(port=8080, blocking=True)
```

### Server Started Successfully:
```
INFO:MCP Server starting on 0.0.0.0:8080
INFO:Available capabilities: 20
```

### Test the Server

```bash
# Health check
curl http://localhost:8080/health

# List capabilities
curl http://localhost:8080/capabilities

# Execute agent
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "code-reviewer",
    "action": "execute_agent",
    "parameters": {
      "task": "Review this code for security issues",
      "model": "claude-3-5-sonnet-20241022"
    }
  }'
```

## 📡 MCP Protocol Specification

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server information |
| GET | `/health` | Health check |
| GET | `/capabilities` | List all capabilities |
| POST | `/execute` | Execute a capability |

### Capability Types

1. **Agent** - Individual specialized agents
2. **Workflow** - Multi-agent workflows
3. **Skill** - Special capabilities (recommendations, metrics)

### Request Format

```json
{
  "capability": "agent-name or skill-name",
  "action": "execute_agent | execute_workflow | recommend_agents | get_performance",
  "parameters": {
    "task": "Task description",
    "model": "claude-3-5-sonnet-20241022",
    // ... additional parameters
  },
  "request_id": "optional-tracking-id"
}
```

### Response Format

```json
{
  "success": true,
  "request_id": "optional-tracking-id",
  "data": {
    "output": "Agent response",
    "metadata": {
      // Execution metadata
    }
  },
  "error": null,
  "metadata": {
    "agent": "agent-name",
    "execution_time": 2345.67
  }
}
```

## 🐍 Python Client

### Using the Provided Client

```python
from examples.mcp.mcp_client_example import MCPClient

# Initialize client
client = MCPClient(base_url="http://localhost:8080")

# Health check
health = client.health_check()
print(f"Status: {health['status']}")

# List capabilities
caps = client.list_capabilities()
print(f"Capabilities: {caps['count']}")

# Execute agent
result = client.execute_agent(
    agent_name="code-reviewer",
    task="Review this code for bugs",
    model="claude-3-5-sonnet-20241022"
)

if result['success']:
    print(result['data']['output'])

# Get agent recommendations
recommendations = client.recommend_agents(
    task="Review authentication for SQL injection",
    top_k=3
)

# Execute workflow
workflow_result = client.execute_workflow(
    workflow_name="bug-fix",
    task="Investigate login issue"
)

# Get performance metrics
metrics = client.get_performance_summary(hours=24)
```

### Using Requests Directly

```python
import requests
import json

# Execute agent
response = requests.post(
    "http://localhost:8080/execute",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "capability": "code-reviewer",
        "action": "execute_agent",
        "parameters": {
            "task": "Review code for security issues",
            "model": "claude-3-5-sonnet-20241022"
        }
    })
)

result = response.json()
print(result['data']['output'])
```

## 🔌 Integration with Claude Code

### Configure Claude Code

Add MCP server to your Claude Code settings:

```json
{
  "mcp_servers": {
    "claude-force": {
      "url": "http://localhost:8080",
      "protocol": "http",
      "capabilities": [
        "agents",
        "workflows",
        "semantic-selection",
        "performance-tracking"
      ]
    }
  }
}
```

### Use in Claude Code

```
# Discover capabilities
List available claude-force capabilities

# Execute agent via MCP
Use claude-force code-reviewer agent to review this code

# Get recommendations
Ask claude-force to recommend agents for this task
```

## 🌐 JavaScript/TypeScript Client

```typescript
// mcp-client.ts
class MCPClient {
  constructor(private baseUrl: string) {}

  async executeAgent(
    agentName: string,
    task: string,
    model: string = 'claude-3-5-sonnet-20241022'
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        capability: agentName,
        action: 'execute_agent',
        parameters: { task, model }
      })
    });

    return await response.json();
  }

  async listCapabilities(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/capabilities`);
    return await response.json();
  }
}

// Usage
const client = new MCPClient('http://localhost:8080');

const result = await client.executeAgent(
  'code-reviewer',
  'Review this TypeScript code'
);

console.log(result.data.output);
```

## 🔧 Configuration Options

### Server Configuration

```bash
# Bind to specific host/port
python -m claude_force.mcp_server --host 0.0.0.0 --port 8080

# Custom config file
python -m claude_force.mcp_server --config /path/to/claude.json

# API key via argument
python -m claude_force.mcp_server --api-key your-key-here
```

### Programmatic Configuration

```python
from claude_force.mcp_server import MCPServer
from claude_force import AgentOrchestrator

# Custom orchestrator
orchestrator = AgentOrchestrator(
    config_path="/path/to/claude.json",
    anthropic_api_key="your-key",
    enable_tracking=True
)

# Create MCP server with custom orchestrator
server = MCPServer(orchestrator=orchestrator)

# Start in background thread
server.start(port=8080, blocking=False)

# ... do other work ...

# Stop server
server.stop()
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install claude-force
COPY . .
RUN pip install -e .

# Expose MCP port
EXPOSE 8080

# Start MCP server
CMD ["python", "-m", "claude_force.mcp_server", "--host", "0.0.0.0", "--port", "8080"]
```

### Build and Run

```bash
# Build image
docker build -t claude-force-mcp .

# Run container
docker run -p 8080:8080 \
  -e ANTHROPIC_API_KEY="your-key" \
  claude-force-mcp
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
```

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f mcp-server
```

## 📊 Available Capabilities

The MCP server exposes all claude-force capabilities:

### Agents (15)
- code-reviewer
- security-specialist
- bug-investigator
- frontend-architect
- backend-architect
- database-architect
- python-expert
- ui-components-expert
- frontend-developer
- devops-architect
- google-cloud-expert
- deployment-integration-expert
- qc-automation-expert
- document-writer-expert
- api-documenter

### Workflows (6)
- full-stack-feature
- frontend-only
- backend-only
- infrastructure
- bug-fix
- documentation

### Skills (2)
- recommend-agents - Semantic agent selection
- performance-summary - Performance metrics

## 🔒 Security Considerations

### API Key Security

```bash
# Never hardcode API keys
# Use environment variables
export ANTHROPIC_API_KEY='your-key'

# Or use a secrets manager
python -m claude_force.mcp_server --api-key $(get-secret anthropic-key)
```

### Network Security

```bash
# Bind to localhost only (for local dev)
python -m claude_force.mcp_server --host 127.0.0.1

# Use reverse proxy for production (nginx, traefik)
# nginx.conf
location /mcp/ {
    proxy_pass http://localhost:8080/;
    proxy_set_header Host $host;
}
```

### CORS Configuration

The server allows all origins by default. For production:

```python
# Modify MCPRequestHandler._send_json_response()
# to restrict CORS origins
self.send_header('Access-Control-Allow-Origin', 'https://your-domain.com')
```

## 🧪 Testing

### Test with cURL

```bash
# Health check
curl http://localhost:8080/health

# List capabilities
curl http://localhost:8080/capabilities | jq '.count'

# Execute code review
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "code-reviewer",
    "action": "execute_agent",
    "parameters": {
      "task": "Review: def unsafe_login(user, pwd): return exec(user)"
    }
  }' | jq '.data.output'
```

### Test with Python

```bash
# Run the example client
python examples/mcp/mcp_client_example.py
```

### Load Testing

```bash
# Install apache bench
apt-get install apache2-utils

# Simple load test
ab -n 100 -c 10 http://localhost:8080/health

# POST request load test
ab -n 10 -c 2 -p payload.json -T application/json \
  http://localhost:8080/execute
```

## 🔍 Troubleshooting

### Server Won't Start

**Issue**: `ANTHROPIC_API_KEY not set`
**Solution**:
```bash
export ANTHROPIC_API_KEY='your-api-key'
python -m claude_force.mcp_server
```

### Connection Refused

**Issue**: Client can't connect to server
**Solution**:
1. Verify server is running: `curl http://localhost:8080/health`
2. Check firewall settings
3. Ensure correct host/port configuration

### Slow Response Times

**Issue**: Agent execution takes too long
**Solutions**:
- Use faster models (haiku instead of opus)
- Reduce max_tokens parameter
- Implement caching for repeated queries
- Run server on machine with good network connection to Anthropic API

### Out of Memory

**Issue**: Server crashes with large requests
**Solutions**:
- Limit max_tokens parameter
- Implement request size limits
- Add request queue with size limits
- Deploy with more RAM

## 📚 Additional Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [Model Context Protocol Spec](https://github.com/anthropics/anthropic-sdk-python)
- [Claude-Force Main README](../../README.md)
- [Headless Mode Documentation](../../docs/HEADLESS_MODE.md)

## 🤝 Contributing

Improvements to the MCP server are welcome! Areas for enhancement:

1. WebSocket support for real-time updates
2. Streaming responses for long-running agents
3. Rate limiting per client
4. Authentication beyond API keys
5. Request queuing and priority
6. Metrics export (Prometheus, StatsD)

---

**Need help?** Open an issue or check the main documentation.
