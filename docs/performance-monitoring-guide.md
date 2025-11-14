# Performance Monitoring Implementation Guide

**For:** Claude Force v2.2.0+
**Last Updated:** 2025-11-14

---

## Quick Start

Get performance insights in 3 commands:

```bash
# View current performance summary
claude-force analytics summary

# Check last 7 days
claude-force analytics summary --days 7

# Export to CSV for analysis
claude-force analytics export --format csv --output metrics.csv
```

---

## Table of Contents

1. [Built-in Monitoring](#built-in-monitoring)
2. [Metrics Collection](#metrics-collection)
3. [Performance Analytics](#performance-analytics)
4. [Custom Monitoring Setup](#custom-monitoring-setup)
5. [Alerting & Notifications](#alerting--notifications)
6. [Dashboard Examples](#dashboard-examples)
7. [Troubleshooting](#troubleshooting)

---

## Built-in Monitoring

### Automatic Metrics Collection

Claude Force automatically tracks performance metrics for every execution. No configuration required!

**What's tracked:**
- ✅ Execution time (milliseconds)
- ✅ Token usage (input/output)
- ✅ Cost estimation (USD)
- ✅ Success/failure status
- ✅ Model used (Haiku/Sonnet/Opus)
- ✅ Agent name
- ✅ Task hash (for deduplication)
- ✅ Timestamp (ISO 8601)

**Storage location:** `.claude/metrics/executions.jsonl`

**Example metric entry:**
```json
{
  "timestamp": "2025-11-14T10:30:45.123456",
  "agent_name": "python-expert",
  "task_hash": "a3b4c5d6",
  "success": true,
  "execution_time_ms": 3456,
  "model": "claude-3-5-haiku-20241022",
  "input_tokens": 1234,
  "output_tokens": 567,
  "total_tokens": 1801,
  "estimated_cost": 0.000234
}
```

### Viewing Metrics

#### Summary Statistics

```bash
# All-time summary
claude-force analytics summary

# Last 7 days
claude-force analytics summary --days 7

# Last 30 days
claude-force analytics summary --days 30

# Specific date range
claude-force analytics summary --start 2025-11-01 --end 2025-11-14
```

**Example output:**
```
Performance Summary (Last 7 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Executions: 1,247
Success Rate: 94.3% (1,176 / 1,247)
Average Execution Time: 4,123 ms
Total Cost: $2.34 USD

Token Usage:
  Total Tokens: 3,456,789
  Average Input: 1,234 tokens
  Average Output: 567 tokens

Top Agents by Usage:
  1. python-expert (342 executions, 3.2s avg, $0.45)
  2. code-reviewer (234 executions, 5.1s avg, $0.67)
  3. api-designer (189 executions, 4.5s avg, $0.34)

Model Distribution:
  claude-3-5-haiku-20241022: 67% ($0.45)
  claude-3-5-sonnet-20241022: 31% ($1.67)
  claude-3-opus-20240229: 2% ($0.22)

Cost Savings (vs Sonnet-only): 78% ($8.12 saved)
```

#### Per-Agent Analytics

```bash
# View per-agent breakdown
claude-force analytics by-agent

# Filter by specific agent
claude-force analytics by-agent --agent python-expert

# Sort by execution time
claude-force analytics by-agent --sort-by time

# Sort by cost
claude-force analytics by-agent --sort-by cost
```

**Example output:**
```
Agent Performance Breakdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent: python-expert
  Executions: 342
  Success Rate: 96.2%
  Avg Execution Time: 3,245 ms
  Total Cost: $0.45
  Token Usage: 1,234 avg input, 567 avg output

Agent: code-reviewer
  Executions: 234
  Success Rate: 93.1%
  Avg Execution Time: 5,123 ms
  Total Cost: $0.67
  Token Usage: 2,345 avg input, 890 avg output
```

#### Cost Analysis

```bash
# View cost breakdown
claude-force analytics costs

# Cost by agent
claude-force analytics costs --by-agent

# Cost by model
claude-force analytics costs --by-model

# Cost trends over time
claude-force analytics costs --trends --interval daily
```

#### Performance Trends

```bash
# View trends (hourly intervals)
claude-force analytics trends --interval hourly

# Daily trends
claude-force analytics trends --interval daily

# Weekly trends
claude-force analytics trends --interval weekly
```

**Example output:**
```
Performance Trends (Daily)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Date         Executions  Avg Time  Success Rate  Cost
──────────────────────────────────────────────────────
2025-11-08   145         4.2s      95.2%         $0.34
2025-11-09   167         4.1s      94.6%         $0.38
2025-11-10   189         3.9s      96.3%         $0.41
2025-11-11   201         4.3s      93.5%         $0.45
2025-11-12   178         4.0s      95.1%         $0.39
2025-11-13   198         4.2s      94.9%         $0.42
2025-11-14   169         4.1s      95.6%         $0.37

Trend: ↗ +16% executions, → stable avg time
```

---

## Metrics Collection

### Configuration

Metrics collection is enabled by default. To configure:

**`.claude/claude.json`:**
```json
{
  "performance": {
    "tracking_enabled": true,
    "metrics_file": ".claude/metrics/executions.jsonl",
    "cost_tracking": true,
    "detailed_logging": false
  }
}
```

### Exporting Metrics

#### Export to CSV

```bash
# Export all metrics
claude-force analytics export --format csv --output metrics.csv

# Export with date filter
claude-force analytics export --format csv --days 30 --output last-30-days.csv

# Export specific agents
claude-force analytics export --format csv --agent python-expert --output python-expert.csv
```

**CSV columns:**
```csv
timestamp,agent_name,task_hash,success,execution_time_ms,model,input_tokens,output_tokens,total_tokens,estimated_cost,workflow_id,error_type
2025-11-14T10:30:45.123456,python-expert,a3b4c5d6,true,3456,claude-3-5-haiku-20241022,1234,567,1801,0.000234,,
```

#### Export to JSON

```bash
# Export as JSON
claude-force analytics export --format json --output metrics.json

# Pretty-printed JSON
claude-force analytics export --format json --pretty --output metrics-pretty.json
```

#### Programmatic Access

```python
from claude_force.performance_tracker import PerformanceTracker
from pathlib import Path

# Initialize tracker
tracker = PerformanceTracker(Path.home() / ".claude")

# Get all metrics
all_metrics = tracker.get_all_metrics()

# Get metrics for specific timeframe
from datetime import datetime, timedelta
start_date = datetime.now() - timedelta(days=7)
recent_metrics = tracker.get_metrics_since(start_date)

# Get metrics by agent
python_expert_metrics = tracker.get_metrics_by_agent("python-expert")

# Calculate custom statistics
avg_time = sum(m.execution_time_ms for m in all_metrics) / len(all_metrics)
total_cost = sum(m.estimated_cost for m in all_metrics)
success_rate = sum(1 for m in all_metrics if m.success) / len(all_metrics)

print(f"Average execution time: {avg_time:.0f}ms")
print(f"Total cost: ${total_cost:.2f}")
print(f"Success rate: {success_rate:.1%}")
```

---

## Performance Analytics

### Key Performance Indicators (KPIs)

#### 1. Success Rate

**Target:** >95%

**Calculation:**
```python
success_rate = (successful_executions / total_executions) * 100
```

**Monitoring:**
```bash
# Check current success rate
claude-force analytics summary | grep "Success Rate"
```

**Alert if:** Success rate drops below 95% for >1 hour

#### 2. Average Execution Time

**Target:** <5s for simple tasks, <15s for complex tasks

**Calculation:**
```python
avg_time = sum(execution_times) / len(execution_times)
```

**Monitoring:**
```bash
# Check current average
claude-force analytics summary | grep "Average Execution Time"
```

**Alert if:** P95 latency exceeds 10s for simple tasks

#### 3. Cost Per Execution

**Target:** Varies by use case

**Calculation:**
```python
cost_per_execution = total_cost / total_executions
```

**Monitoring:**
```bash
# View cost breakdown
claude-force analytics costs
```

**Alert if:** Cost per execution exceeds expected baseline by 50%

#### 4. Token Usage

**Target:** Optimized via ProgressiveSkillsManager (40-60% reduction)

**Monitoring:**
```bash
# View token usage
claude-force analytics summary | grep -A 3 "Token Usage"
```

**Alert if:** Average token usage increases by >30% week-over-week

#### 5. Model Distribution

**Target:** 60-80% Haiku usage for cost optimization

**Monitoring:**
```bash
# View model distribution
claude-force analytics summary | grep -A 5 "Model Distribution"
```

**Alert if:** Haiku usage drops below 50%

### Performance Baselines

Establish baselines for comparison:

```bash
# Create baseline from last 30 days
claude-force analytics summary --days 30 --output baseline.json
```

**Example baseline:**
```json
{
  "period": "30 days",
  "total_executions": 5234,
  "success_rate": 95.3,
  "avg_execution_time_ms": 4123,
  "p50_latency_ms": 3245,
  "p95_latency_ms": 7890,
  "p99_latency_ms": 12345,
  "total_cost": 12.34,
  "avg_cost_per_execution": 0.00236,
  "avg_input_tokens": 1234,
  "avg_output_tokens": 567,
  "model_distribution": {
    "haiku": 67.3,
    "sonnet": 30.2,
    "opus": 2.5
  }
}
```

### Regression Detection

Compare current metrics against baseline:

```python
#!/usr/bin/env python3
"""
Detect performance regressions.
"""
import json
from claude_force.performance_tracker import PerformanceTracker

def check_regressions(baseline_file: str, threshold: float = 1.15):
    """
    Check for performance regressions.

    Args:
        baseline_file: Path to baseline metrics JSON
        threshold: Allowed degradation (1.15 = 15% slower)
    """
    # Load baseline
    with open(baseline_file) as f:
        baseline = json.load(f)

    # Get current metrics (last 24 hours)
    tracker = PerformanceTracker()
    current = tracker.get_summary(days=1)

    regressions = []

    # Check latency
    if current["avg_execution_time_ms"] > baseline["avg_execution_time_ms"] * threshold:
        regressions.append({
            "metric": "Average Execution Time",
            "baseline": f"{baseline['avg_execution_time_ms']}ms",
            "current": f"{current['avg_execution_time_ms']}ms",
            "degradation": f"{((current['avg_execution_time_ms'] / baseline['avg_execution_time_ms'] - 1) * 100):.1f}%"
        })

    # Check success rate
    if current["success_rate"] < baseline["success_rate"] * 0.95:  # 5% drop
        regressions.append({
            "metric": "Success Rate",
            "baseline": f"{baseline['success_rate']:.1f}%",
            "current": f"{current['success_rate']:.1f}%",
            "degradation": f"{(baseline['success_rate'] - current['success_rate']):.1f}pp"
        })

    # Check cost
    if current["avg_cost_per_execution"] > baseline["avg_cost_per_execution"] * 1.5:
        regressions.append({
            "metric": "Cost Per Execution",
            "baseline": f"${baseline['avg_cost_per_execution']:.5f}",
            "current": f"${current['avg_cost_per_execution']:.5f}",
            "degradation": f"{((current['avg_cost_per_execution'] / baseline['avg_cost_per_execution'] - 1) * 100):.1f}%"
        })

    if regressions:
        print("⚠️  Performance Regressions Detected:\n")
        for r in regressions:
            print(f"  {r['metric']}:")
            print(f"    Baseline: {r['baseline']}")
            print(f"    Current: {r['current']}")
            print(f"    Degradation: {r['degradation']}\n")
        return False
    else:
        print("✅ No performance regressions detected")
        return True

if __name__ == "__main__":
    import sys
    success = check_regressions("baseline.json")
    sys.exit(0 if success else 1)
```

**Usage in CI/CD:**
```yaml
# .github/workflows/performance-check.yml
name: Performance Check

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .

      - name: Check for regressions
        run: |
          python scripts/check_regressions.py
```

---

## Custom Monitoring Setup

### Integration with External Tools

#### 1. Prometheus + Grafana

**Step 1: Export metrics to Prometheus format**

Create `scripts/export_prometheus.py`:

```python
#!/usr/bin/env python3
"""
Export metrics to Prometheus format.
"""
from claude_force.performance_tracker import PerformanceTracker
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from datetime import datetime, timedelta

def export_to_prometheus():
    tracker = PerformanceTracker()

    # Get metrics from last hour
    recent = tracker.get_metrics_since(datetime.now() - timedelta(hours=1))

    # Create registry
    registry = CollectorRegistry()

    # Define metrics
    execution_time = Gauge(
        'claude_force_execution_time_ms',
        'Agent execution time in milliseconds',
        ['agent_name', 'model'],
        registry=registry
    )

    success_rate = Gauge(
        'claude_force_success_rate',
        'Success rate by agent',
        ['agent_name'],
        registry=registry
    )

    cost = Gauge(
        'claude_force_cost_usd',
        'Execution cost in USD',
        ['agent_name', 'model'],
        registry=registry
    )

    token_usage = Gauge(
        'claude_force_token_usage',
        'Token usage',
        ['agent_name', 'token_type'],
        registry=registry
    )

    # Populate metrics
    agent_stats = {}
    for metric in recent:
        agent = metric.agent_name
        if agent not in agent_stats:
            agent_stats[agent] = {
                'times': [],
                'successes': 0,
                'total': 0,
                'costs': [],
                'input_tokens': [],
                'output_tokens': []
            }

        agent_stats[agent]['times'].append(metric.execution_time_ms)
        agent_stats[agent]['successes'] += 1 if metric.success else 0
        agent_stats[agent]['total'] += 1
        agent_stats[agent]['costs'].append(metric.estimated_cost)
        agent_stats[agent]['input_tokens'].append(metric.input_tokens)
        agent_stats[agent]['output_tokens'].append(metric.output_tokens)

    # Set gauges
    for agent, stats in agent_stats.items():
        avg_time = sum(stats['times']) / len(stats['times'])
        execution_time.labels(agent_name=agent, model='all').set(avg_time)

        success_pct = (stats['successes'] / stats['total']) * 100
        success_rate.labels(agent_name=agent).set(success_pct)

        total_cost = sum(stats['costs'])
        cost.labels(agent_name=agent, model='all').set(total_cost)

        avg_input = sum(stats['input_tokens']) / len(stats['input_tokens'])
        avg_output = sum(stats['output_tokens']) / len(stats['output_tokens'])
        token_usage.labels(agent_name=agent, token_type='input').set(avg_input)
        token_usage.labels(agent_name=agent, token_type='output').set(avg_output)

    # Push to Prometheus pushgateway
    push_to_gateway('localhost:9091', job='claude_force', registry=registry)
    print("✅ Metrics exported to Prometheus")

if __name__ == "__main__":
    export_to_prometheus()
```

**Step 2: Schedule periodic export**

```bash
# Add to crontab (every 5 minutes)
*/5 * * * * cd /home/user/claude-force && python scripts/export_prometheus.py
```

**Step 3: Configure Grafana dashboard**

Import dashboard JSON (see `docs/grafana-dashboard.json`)

#### 2. DataDog Integration

**Step 1: Install DataDog agent**

```bash
DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=<your_api_key> DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
```

**Step 2: Add custom metrics**

Create `scripts/export_datadog.py`:

```python
#!/usr/bin/env python3
"""
Export metrics to DataDog.
"""
from datadog import initialize, statsd
from claude_force.performance_tracker import PerformanceTracker
from datetime import datetime, timedelta

# Initialize DataDog
options = {
    'api_key': '<your_api_key>',
    'app_key': '<your_app_key>'
}
initialize(**options)

def export_to_datadog():
    tracker = PerformanceTracker()
    recent = tracker.get_metrics_since(datetime.now() - timedelta(minutes=5))

    for metric in recent:
        # Send execution time
        statsd.histogram(
            'claude_force.execution_time',
            metric.execution_time_ms,
            tags=[
                f'agent:{metric.agent_name}',
                f'model:{metric.model}',
                f'success:{metric.success}'
            ]
        )

        # Send cost
        statsd.histogram(
            'claude_force.cost',
            metric.estimated_cost,
            tags=[
                f'agent:{metric.agent_name}',
                f'model:{metric.model}'
            ]
        )

        # Send token usage
        statsd.histogram(
            'claude_force.tokens.input',
            metric.input_tokens,
            tags=[f'agent:{metric.agent_name}']
        )

        statsd.histogram(
            'claude_force.tokens.output',
            metric.output_tokens,
            tags=[f'agent:{metric.agent_name}']
        )

        # Send success/failure event
        if not metric.success:
            statsd.event(
                'Agent Execution Failed',
                f'Agent {metric.agent_name} failed',
                alert_type='error',
                tags=[f'agent:{metric.agent_name}']
            )

    print(f"✅ Exported {len(recent)} metrics to DataDog")

if __name__ == "__main__":
    export_to_datadog()
```

#### 3. ELK Stack (Elasticsearch, Logstash, Kibana)

**Step 1: Convert JSONL to Elasticsearch format**

```python
#!/usr/bin/env python3
"""
Import metrics to Elasticsearch.
"""
from elasticsearch import Elasticsearch
from claude_force.performance_tracker import PerformanceTracker
import json

def import_to_elasticsearch():
    # Connect to Elasticsearch
    es = Elasticsearch(['http://localhost:9200'])

    # Create index if not exists
    index_name = 'claude-force-metrics'
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            'mappings': {
                'properties': {
                    'timestamp': {'type': 'date'},
                    'agent_name': {'type': 'keyword'},
                    'task_hash': {'type': 'keyword'},
                    'success': {'type': 'boolean'},
                    'execution_time_ms': {'type': 'integer'},
                    'model': {'type': 'keyword'},
                    'input_tokens': {'type': 'integer'},
                    'output_tokens': {'type': 'integer'},
                    'total_tokens': {'type': 'integer'},
                    'estimated_cost': {'type': 'float'}
                }
            }
        })

    # Load and index metrics
    tracker = PerformanceTracker()
    metrics = tracker.get_all_metrics()

    for metric in metrics:
        doc = {
            'timestamp': metric.timestamp,
            'agent_name': metric.agent_name,
            'task_hash': metric.task_hash,
            'success': metric.success,
            'execution_time_ms': metric.execution_time_ms,
            'model': metric.model,
            'input_tokens': metric.input_tokens,
            'output_tokens': metric.output_tokens,
            'total_tokens': metric.total_tokens,
            'estimated_cost': metric.estimated_cost
        }

        es.index(index=index_name, body=doc)

    print(f"✅ Imported {len(metrics)} metrics to Elasticsearch")

if __name__ == "__main__":
    import_to_elasticsearch()
```

**Step 2: Create Kibana dashboard**

1. Open Kibana (http://localhost:5601)
2. Go to "Management" > "Index Patterns"
3. Create pattern: `claude-force-metrics-*`
4. Create visualizations:
   - Line chart: Execution time over time
   - Pie chart: Model distribution
   - Bar chart: Top agents by usage
   - Metric: Total cost

---

## Alerting & Notifications

### Email Alerts

Create `scripts/alert_email.py`:

```python
#!/usr/bin/env python3
"""
Send email alerts for performance issues.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from claude_force.performance_tracker import PerformanceTracker
from datetime import datetime, timedelta

def check_and_alert():
    tracker = PerformanceTracker()
    recent = tracker.get_metrics_since(datetime.now() - timedelta(hours=1))

    alerts = []

    # Check success rate
    total = len(recent)
    successes = sum(1 for m in recent if m.success)
    success_rate = (successes / total) * 100 if total > 0 else 100

    if success_rate < 95:
        alerts.append(f"⚠️ Success rate dropped to {success_rate:.1f}% (last hour)")

    # Check average latency
    avg_latency = sum(m.execution_time_ms for m in recent) / len(recent) if recent else 0
    if avg_latency > 10000:  # 10 seconds
        alerts.append(f"⚠️ Average latency increased to {avg_latency/1000:.1f}s (last hour)")

    # Check cost spike
    total_cost = sum(m.estimated_cost for m in recent)
    if total_cost > 1.0:  # $1 per hour threshold
        alerts.append(f"⚠️ Cost spike detected: ${total_cost:.2f} in last hour")

    # Send email if alerts exist
    if alerts:
        send_alert_email(alerts)

def send_alert_email(alerts: list):
    sender = "alerts@yourcompany.com"
    recipient = "ops-team@yourcompany.com"
    subject = f"Claude Force Performance Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    body = "Performance issues detected:\n\n"
    body += "\n".join(alerts)
    body += "\n\nCheck the dashboard for more details."

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send via SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, 'your_password')
        server.send_message(msg)

    print(f"✅ Alert email sent: {len(alerts)} issues")

if __name__ == "__main__":
    check_and_alert()
```

**Schedule hourly checks:**
```bash
# Add to crontab
0 * * * * cd /home/user/claude-force && python scripts/alert_email.py
```

### Slack Alerts

Create `scripts/alert_slack.py`:

```python
#!/usr/bin/env python3
"""
Send Slack alerts for performance issues.
"""
import requests
import json
from claude_force.performance_tracker import PerformanceTracker
from datetime import datetime, timedelta

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def check_and_alert_slack():
    tracker = PerformanceTracker()
    recent = tracker.get_metrics_since(datetime.now() - timedelta(hours=1))

    if not recent:
        return

    # Calculate metrics
    total = len(recent)
    successes = sum(1 for m in recent if m.success)
    success_rate = (successes / total) * 100
    avg_latency = sum(m.execution_time_ms for m in recent) / len(recent)
    total_cost = sum(m.estimated_cost for m in recent)

    # Check thresholds
    alerts = []

    if success_rate < 95:
        alerts.append({
            "color": "danger",
            "title": "Low Success Rate",
            "text": f"Success rate dropped to {success_rate:.1f}%",
            "footer": "Last 1 hour"
        })

    if avg_latency > 10000:
        alerts.append({
            "color": "warning",
            "title": "High Latency",
            "text": f"Average latency: {avg_latency/1000:.1f}s",
            "footer": "Last 1 hour"
        })

    if total_cost > 1.0:
        alerts.append({
            "color": "warning",
            "title": "Cost Spike",
            "text": f"Cost: ${total_cost:.2f}",
            "footer": "Last 1 hour"
        })

    # Send to Slack
    if alerts:
        payload = {
            "text": "🚨 Claude Force Performance Alert",
            "attachments": alerts
        }

        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            print(f"✅ Slack alert sent: {len(alerts)} issues")
        else:
            print(f"❌ Failed to send Slack alert: {response.status_code}")

if __name__ == "__main__":
    check_and_alert_slack()
```

### PagerDuty Integration

For critical production environments:

```python
#!/usr/bin/env python3
"""
Create PagerDuty incidents for critical issues.
"""
import requests
import json
from claude_force.performance_tracker import PerformanceTracker
from datetime import datetime, timedelta

PAGERDUTY_API_KEY = "your_api_key"
PAGERDUTY_SERVICE_ID = "your_service_id"

def trigger_incident(summary: str, severity: str, details: dict):
    """Trigger a PagerDuty incident."""
    url = "https://api.pagerduty.com/incidents"

    headers = {
        "Authorization": f"Token token={PAGERDUTY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.pagerduty+json;version=2"
    }

    payload = {
        "incident": {
            "type": "incident",
            "title": summary,
            "service": {
                "id": PAGERDUTY_SERVICE_ID,
                "type": "service_reference"
            },
            "urgency": "high" if severity == "critical" else "low",
            "body": {
                "type": "incident_body",
                "details": json.dumps(details, indent=2)
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f"✅ PagerDuty incident created: {summary}")
    else:
        print(f"❌ Failed to create incident: {response.status_code}")

def check_critical_issues():
    """Check for critical performance issues."""
    tracker = PerformanceTracker()
    recent = tracker.get_metrics_since(datetime.now() - timedelta(minutes=15))

    if not recent:
        return

    # Calculate metrics
    total = len(recent)
    successes = sum(1 for m in recent if m.success)
    success_rate = (successes / total) * 100

    # Critical: Success rate below 90% for 15 minutes
    if success_rate < 90:
        trigger_incident(
            summary=f"Claude Force: Critical success rate drop ({success_rate:.1f}%)",
            severity="critical",
            details={
                "success_rate": f"{success_rate:.1f}%",
                "total_executions": total,
                "failed_executions": total - successes,
                "time_window": "15 minutes"
            }
        )

if __name__ == "__main__":
    check_critical_issues()
```

---

## Dashboard Examples

### Terminal Dashboard (Simple)

Create `scripts/dashboard.py`:

```python
#!/usr/bin/env python3
"""
Simple terminal dashboard for Claude Force performance.
"""
from claude_force.performance_tracker import PerformanceTracker
from datetime import datetime, timedelta
import time
import os

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_dashboard():
    tracker = PerformanceTracker()

    # Get metrics for different time windows
    last_hour = tracker.get_metrics_since(datetime.now() - timedelta(hours=1))
    last_24h = tracker.get_metrics_since(datetime.now() - timedelta(days=1))
    last_7d = tracker.get_metrics_since(datetime.now() - timedelta(days=7))

    clear_screen()

    print("=" * 70)
    print(" Claude Force Performance Dashboard".center(70))
    print("=" * 70)
    print()

    # Last Hour Stats
    print("📊 LAST HOUR")
    print("-" * 70)
    if last_hour:
        hour_success = sum(1 for m in last_hour if m.success)
        hour_total = len(last_hour)
        hour_rate = (hour_success / hour_total) * 100
        hour_avg_time = sum(m.execution_time_ms for m in last_hour) / hour_total
        hour_cost = sum(m.estimated_cost for m in last_hour)

        print(f"  Executions: {hour_total:,}")
        print(f"  Success Rate: {hour_rate:.1f}%")
        print(f"  Avg Time: {hour_avg_time/1000:.2f}s")
        print(f"  Total Cost: ${hour_cost:.4f}")
    else:
        print("  No executions in last hour")
    print()

    # Last 24 Hours Stats
    print("📊 LAST 24 HOURS")
    print("-" * 70)
    if last_24h:
        day_success = sum(1 for m in last_24h if m.success)
        day_total = len(last_24h)
        day_rate = (day_success / day_total) * 100
        day_avg_time = sum(m.execution_time_ms for m in last_24h) / day_total
        day_cost = sum(m.estimated_cost for m in last_24h)

        print(f"  Executions: {day_total:,}")
        print(f"  Success Rate: {day_rate:.1f}%")
        print(f"  Avg Time: {day_avg_time/1000:.2f}s")
        print(f"  Total Cost: ${day_cost:.4f}")

        # Model distribution
        models = {}
        for m in last_24h:
            models[m.model] = models.get(m.model, 0) + 1

        print(f"\n  Model Distribution:")
        for model, count in sorted(models.items(), key=lambda x: x[1], reverse=True):
            pct = (count / day_total) * 100
            model_short = model.split('-')[3] if len(model.split('-')) > 3 else model
            bar = "█" * int(pct / 2)
            print(f"    {model_short:10s} {bar:30s} {pct:5.1f}%")
    else:
        print("  No executions in last 24 hours")
    print()

    # Last 7 Days Stats
    print("📊 LAST 7 DAYS")
    print("-" * 70)
    if last_7d:
        week_success = sum(1 for m in last_7d if m.success)
        week_total = len(last_7d)
        week_rate = (week_success / week_total) * 100
        week_cost = sum(m.estimated_cost for m in last_7d)

        print(f"  Total Executions: {week_total:,}")
        print(f"  Success Rate: {week_rate:.1f}%")
        print(f"  Total Cost: ${week_cost:.2f}")

        # Top agents
        agents = {}
        for m in last_7d:
            if m.agent_name not in agents:
                agents[m.agent_name] = {'count': 0, 'cost': 0}
            agents[m.agent_name]['count'] += 1
            agents[m.agent_name]['cost'] += m.estimated_cost

        print(f"\n  Top Agents:")
        for agent, stats in sorted(agents.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            pct = (stats['count'] / week_total) * 100
            print(f"    {agent:20s} {stats['count']:5,} executions ({pct:4.1f}%)  ${stats['cost']:.4f}")
    else:
        print("  No executions in last 7 days")
    print()

    print("=" * 70)
    print(f" Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    # Run continuously (update every 30 seconds)
    try:
        while True:
            print_dashboard()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")
```

**Run the dashboard:**
```bash
python scripts/dashboard.py
```

---

## Troubleshooting

### Common Issues

#### 1. Missing Metrics File

**Symptom:** `FileNotFoundError: .claude/metrics/executions.jsonl`

**Solution:**
```bash
# Create metrics directory
mkdir -p ~/.claude/metrics

# Verify performance tracking is enabled
claude-force config get performance.tracking_enabled
```

#### 2. Slow Analytics Queries

**Symptom:** `claude-force analytics summary` takes >5 seconds

**Solution:**
```bash
# Check metrics file size
ls -lh ~/.claude/metrics/executions.jsonl

# If >100MB, consider archiving old metrics
python scripts/archive_old_metrics.py

# Or use date filters
claude-force analytics summary --days 30
```

#### 3. Inaccurate Cost Estimates

**Symptom:** Cost estimates don't match actual bills

**Cause:** Pricing may have changed, or caching causing stale data

**Solution:**
```python
# Update pricing in performance_tracker.py
PRICING = {
    "claude-3-5-haiku-20241022": {
        "input": 0.00025,  # Update these values
        "output": 0.00125
    },
    # ... other models
}
```

#### 4. Export Failures

**Symptom:** `claude-force analytics export` fails

**Solution:**
```bash
# Check file permissions
ls -la ~/.claude/metrics/

# Verify output directory exists
mkdir -p exports/

# Try with explicit path
claude-force analytics export --format csv --output $(pwd)/exports/metrics.csv
```

---

## Summary

**Quick Reference:**

```bash
# View current performance
claude-force analytics summary

# Export metrics
claude-force analytics export --format csv --output metrics.csv

# Run custom dashboard
python scripts/dashboard.py

# Check for regressions
python scripts/check_regressions.py
```

**Key Metrics to Monitor:**
- ✅ Success Rate (target: >95%)
- ✅ Avg Execution Time (target: <5s simple, <15s complex)
- ✅ Cost Per Execution
- ✅ Model Distribution (target: 60-80% Haiku)
- ✅ Token Usage

**Integration Options:**
- Prometheus + Grafana (time-series monitoring)
- DataDog (APM + metrics)
- ELK Stack (log analysis)
- Slack/Email (alerting)
- PagerDuty (incident management)

---

**Next Steps:**
1. Review current performance: `claude-force analytics summary`
2. Establish baselines for your workload
3. Set up alerting for critical metrics
4. Create custom dashboards as needed

For more details, see the [Performance Analysis Report](performance-analysis.md).
