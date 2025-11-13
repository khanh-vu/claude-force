# REST API Server Integration

This example demonstrates how to expose claude-force agents as REST API endpoints using FastAPI. Perfect for integrating Claude agents into web applications, microservices, or as a standalone AI service.

## 📋 Features

- **RESTful API**: Clean, well-documented REST endpoints
- **Async Support**: Concurrent request handling with async/await
- **Background Jobs**: Queue-based processing for long-running tasks
- **API Security**: API key authentication
- **Request Validation**: Automatic validation with Pydantic
- **Performance Tracking**: Built-in metrics and monitoring
- **OpenAPI Docs**: Auto-generated interactive documentation
- **Production Ready**: CORS, error handling, logging

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd examples/api-server
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional
export API_KEYS="key1,key2,key3"  # Comma-separated list (default: dev-key-12345)
export RATE_LIMIT="100"            # Requests per minute (default: 100)
export MAX_CONCURRENT_JOBS="10"    # Max concurrent background jobs (default: 10)
```

### 3. Start the Server

```bash
# Development mode with auto-reload
uvicorn api_server:app --reload --port 8000

# Production mode
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access the API

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Health & Info

#### `GET /`
Root endpoint with basic info

```bash
curl http://localhost:8000/
```

#### `GET /health`
Health check endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "orchestrator": true,
  "anthropic_api": true,
  "tasks_running": 2,
  "tasks_queued": 5
}
```

### Agent Operations

#### `GET /agents`
List all available agents

```bash
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/agents
```

Response:
```json
{
  "agents": ["code-reviewer", "bug-investigator", "security-specialist", ...],
  "count": 15
}
```

#### `POST /agents/recommend`
Get agent recommendations for a task

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Review authentication code for security issues",
    "top_k": 3,
    "min_confidence": 0.3
  }' \
  http://localhost:8000/agents/recommend
```

Response:
```json
[
  {
    "agent": "security-specialist",
    "confidence": 0.95,
    "reasoning": "Task involves security review of authentication...",
    "domains": ["security", "authentication"],
    "priority": 10
  },
  {
    "agent": "code-reviewer",
    "confidence": 0.78,
    "reasoning": "Code review requested...",
    "domains": ["code-quality"],
    "priority": 8
  }
]
```

#### `POST /agents/run` (Synchronous)
Run an agent and wait for completion

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "code-reviewer",
    "task": "Review this function: def login(u, p): return True",
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "temperature": 1.0
  }' \
  http://localhost:8000/agents/run
```

Response:
```json
{
  "success": true,
  "agent_name": "code-reviewer",
  "output": "# Code Review\n\n## Issues Found:\n1. ...",
  "metadata": {
    "model": "claude-3-5-sonnet-20241022",
    "tokens_used": 1234
  },
  "error": null,
  "execution_time_ms": 2345.67
}
```

#### `POST /agents/run/async` (Asynchronous)
Submit a task and return immediately

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "bug-investigator",
    "task": "Investigate 500 errors in /api/users"
  }' \
  http://localhost:8000/agents/run/async
```

Response:
```json
{
  "task_id": "a1b2c3d4e5f6g7h8",
  "status": "pending",
  "message": "Task submitted successfully",
  "check_url": "/tasks/a1b2c3d4e5f6g7h8"
}
```

#### `GET /tasks/{task_id}`
Check status of async task

```bash
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/tasks/a1b2c3d4e5f6g7h8
```

Response (while running):
```json
{
  "task_id": "a1b2c3d4e5f6g7h8",
  "status": "running",
  "agent_name": "bug-investigator",
  "submitted_at": "2025-01-15T10:30:00",
  "started_at": "2025-01-15T10:30:02",
  "completed_at": null,
  "result": null
}
```

Response (completed):
```json
{
  "task_id": "a1b2c3d4e5f6g7h8",
  "status": "completed",
  "agent_name": "bug-investigator",
  "submitted_at": "2025-01-15T10:30:00",
  "started_at": "2025-01-15T10:30:02",
  "completed_at": "2025-01-15T10:30:15",
  "result": {
    "success": true,
    "output": "Investigation results...",
    "execution_time_ms": 12345.67
  }
}
```

### Workflow Operations

#### `POST /workflows/run`
Execute a multi-agent workflow

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "code-quality-gate",
    "task": "Review and test authentication module",
    "model": "claude-3-5-sonnet-20241022"
  }' \
  http://localhost:8000/workflows/run
```

### Metrics & Monitoring

#### `GET /metrics/summary`
Get overall performance summary

```bash
curl -H "X-API-Key: dev-key-12345" \
  "http://localhost:8000/metrics/summary?hours=24"
```

Response:
```json
{
  "total_executions": 150,
  "successful_executions": 142,
  "failed_executions": 8,
  "success_rate": 0.947,
  "total_tokens": 1234567,
  "total_input_tokens": 834567,
  "total_output_tokens": 400000,
  "total_cost": 45.67,
  "avg_cost_per_execution": 0.304,
  "avg_execution_time_ms": 3456.78
}
```

#### `GET /metrics/agents`
Get per-agent performance metrics

```bash
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/metrics/agents
```

#### `GET /metrics/costs`
Get cost breakdown by agent and model

```bash
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/metrics/costs
```

## 🐍 Python Client

Use the provided Python client for easy integration:

```python
from api_client import ClaudeForceClient

# Initialize client
client = ClaudeForceClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Check health
health = client.health_check()
print(f"Status: {health['status']}")

# List agents
agents = client.list_agents()
print(f"Available agents: {agents['count']}")

# Get recommendations
recommendations = client.recommend_agents(
    task="Review authentication code for security vulnerabilities"
)
for rec in recommendations:
    print(f"{rec['agent']}: {rec['confidence']*100:.1f}%")

# Run agent synchronously
result = client.run_agent_sync(
    agent_name="code-reviewer",
    task="Review this code: ...",
    model="claude-3-5-sonnet-20241022"
)
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")

# Run agent asynchronously
task_id = client.run_agent_async(
    agent_name="bug-investigator",
    task="Investigate 500 errors"
)

# Wait for completion
result = client.wait_for_task(task_id, timeout=60.0)
print(f"Status: {result['status']}")

# Get metrics
summary = client.get_metrics_summary()
print(f"Total cost: ${summary['total_cost']:.2f}")
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (required) | None |
| `API_KEYS` | Comma-separated API keys for authentication | `dev-key-12345` |
| `RATE_LIMIT` | Requests per minute per API key | `100` |
| `MAX_CONCURRENT_JOBS` | Max concurrent background jobs | `10` |

### Model Selection

Choose the right model for your use case:

```python
# Most capable, highest cost
"model": "claude-3-opus-20240229"

# Balanced - recommended (default)
"model": "claude-3-5-sonnet-20241022"

# Fastest, most economical
"model": "claude-3-haiku-20240307"
```

### Authentication

All endpoints (except `/` and `/health`) require authentication via `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/agents
```

In Python:
```python
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json"
}
```

## 🚀 Production Deployment

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install claude-force

# Copy server code
COPY api_server.py .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run:
```bash
docker build -t claude-force-api .
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your-key" \
  -e API_KEYS="key1,key2" \
  claude-force-api
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - API_KEYS=${API_KEYS}
      - RATE_LIMIT=100
      - MAX_CONCURRENT_JOBS=10
    restart: unless-stopped

  # Optional: Add Redis for production task queue
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

### Production Recommendations

1. **Use Redis for Task Queue**: Replace in-memory queue with Redis for distributed processing

2. **Use Celery for Background Jobs**: For robust distributed task processing

3. **Add Rate Limiting**: Use slowapi or nginx for rate limiting

4. **Enable HTTPS**: Use nginx or Traefik as reverse proxy with SSL

5. **Add Monitoring**: Integrate Prometheus for metrics collection

6. **Use Gunicorn**: For better process management
   ```bash
   gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

7. **Set Up Logging**: Configure structured logging to file/service

8. **Add Health Checks**: Configure liveness/readiness probes for K8s

Example nginx config:
```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Liveness probe (is the server running?)
curl http://localhost:8000/

# Readiness probe (is it ready to serve?)
curl http://localhost:8000/health
```

### Logging

Server logs include:
- Request/response details
- Execution times
- Errors and stack traces
- Task queue status

Access logs:
```bash
# View logs
docker logs -f claude-force-api

# Or if running directly
uvicorn api_server:app --log-level debug
```

### Metrics Export

Export metrics for analysis:
```bash
curl -H "X-API-Key: your-key" \
  http://localhost:8000/metrics/summary > metrics.json
```

## 🔍 Troubleshooting

### Issue: "Orchestrator not initialized"

**Cause**: ANTHROPIC_API_KEY not set or invalid

**Solution**:
```bash
export ANTHROPIC_API_KEY="your-valid-key"
# Restart server
```

### Issue: "Too many concurrent jobs"

**Cause**: Exceeded MAX_CONCURRENT_JOBS limit

**Solution**:
- Increase the limit: `export MAX_CONCURRENT_JOBS=20`
- Use async endpoints to queue tasks
- Scale horizontally with multiple server instances

### Issue: "Invalid API key"

**Cause**: Missing or incorrect X-API-Key header

**Solution**:
```bash
curl -H "X-API-Key: dev-key-12345" \
  http://localhost:8000/agents
```

### Issue: High latency

**Causes**:
- Large task inputs
- Complex agent operations
- Model selection (Opus is slower than Haiku)

**Solutions**:
- Use async endpoints for long tasks
- Use faster models (Haiku) when appropriate
- Implement caching for repeated queries
- Scale horizontally

## 💡 Usage Examples

### Example 1: Web Application Integration

```javascript
// JavaScript/Node.js frontend
async function reviewCode(code) {
  const response = await fetch('http://localhost:8000/agents/run', {
    method: 'POST',
    headers: {
      'X-API-Key': 'your-api-key',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      agent_name: 'code-reviewer',
      task: `Review this code:\n${code}`,
      model: 'claude-3-5-sonnet-20241022'
    })
  });

  const result = await response.json();
  return result.output;
}
```

### Example 2: Microservice Integration

```python
# Python microservice
import requests

class AIService:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.headers = {"X-API-Key": api_key}

    def analyze_security(self, code):
        """Analyze code for security issues"""
        response = requests.post(
            f"{self.api_url}/agents/run",
            headers=self.headers,
            json={
                "agent_name": "security-specialist",
                "task": f"Analyze for security issues:\n{code}"
            }
        )
        return response.json()

# Usage
ai = AIService("http://localhost:8000", "your-api-key")
result = ai.analyze_security(user_code)
```

### Example 3: Async Job Processing

```python
# Submit multiple jobs
client = ClaudeForceClient()

task_ids = []
for file in code_files:
    task_id = client.run_agent_async(
        agent_name="code-reviewer",
        task=f"Review {file.name}:\n{file.content}"
    )
    task_ids.append(task_id)

# Wait for all to complete
results = []
for task_id in task_ids:
    result = client.wait_for_task(task_id)
    results.append(result)
```

## 🤝 Contributing

Have improvements or found issues? Contributions welcome!

1. Add new endpoints to `api_server.py`
2. Update this README
3. Test thoroughly
4. Submit PR

## 📄 License

This example is provided under the same license as claude-force (MIT).

---

**Need Help?** Check the [main documentation](../../README.md) or open an issue.
