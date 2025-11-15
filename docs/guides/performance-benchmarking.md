# Performance Benchmarking Guide

**For:** Claude Force v2.2.0+
**Last Updated:** 2025-11-14

---

## Quick Start

Run comprehensive benchmarks in one command:

```bash
cd /home/user/claude-force
python benchmarks/run_benchmarks.py --report
```

View results in `benchmarks/results/dashboard.html`

---

## Table of Contents

1. [Benchmark Types](#benchmark-types)
2. [Running Benchmarks](#running-benchmarks)
3. [Custom Benchmarks](#custom-benchmarks)
4. [Load Testing](#load-testing)
5. [Performance Profiling](#performance-profiling)
6. [Regression Testing](#regression-testing)
7. [CI/CD Integration](#cicd-integration)

---

## Benchmark Types

### 1. Latency Benchmarks

Measure execution time for various task complexities.

**What it measures:**
- Agent execution time (end-to-end)
- API call latency
- Local processing overhead
- Model-specific performance

**Example scenarios:**
- Simple code explanation (Haiku, ~2-4s)
- Medium code review (Sonnet, ~4-6s)
- Complex refactoring (Opus, ~8-15s)

### 2. Cost Benchmarks

Measure cost efficiency and optimization effectiveness.

**What it measures:**
- Cost per execution
- Token usage (input/output)
- Model selection accuracy
- Cost savings vs baseline (Sonnet-only)

**Key metrics:**
- Average cost per task type
- Haiku usage % (target: 60-80%)
- Total cost for benchmark suite

### 3. Throughput Benchmarks

Measure system capacity under load.

**What it measures:**
- Tasks per minute
- Concurrent execution capability
- Resource utilization
- Queue wait times

**Test configurations:**
- Sequential (1 task at a time)
- Low concurrency (5 concurrent)
- Medium concurrency (10 concurrent)
- High concurrency (20 concurrent)

### 4. Accuracy Benchmarks

Measure agent selection and task routing accuracy.

**What it measures:**
- Semantic selection accuracy
- Hybrid orchestrator routing accuracy
- Skills analysis accuracy
- Context relevance

**Evaluation:**
- Manual review of agent selection
- Task completion success rate
- Output quality assessment

---

## Running Benchmarks

### Built-in Benchmark Suite

#### Basic Usage

```bash
# Run all benchmarks
python benchmarks/run_benchmarks.py

# Run specific scenario
python benchmarks/run_benchmarks.py --scenario simple_code_review

# Run with custom iterations
python benchmarks/run_benchmarks.py --iterations 10

# Generate HTML report
python benchmarks/run_benchmarks.py --report --output benchmarks/results/
```

#### Available Scenarios

1. **simple_task** - Basic code explanation (Haiku)
2. **medium_task** - Code review with suggestions (Sonnet)
3. **complex_task** - Comprehensive refactoring (Opus)
4. **workflow_test** - Multi-agent workflow execution

### Single Agent Benchmark

```bash
# Create benchmark_agent.py
cat > benchmark_agent.py << 'EOF'
#!/usr/bin/env python3
"""
Benchmark a specific agent.
"""
import time
import sys
from claude_force.orchestrator import AgentOrchestrator

def benchmark_agent(agent_name: str, task: str, iterations: int = 10):
    """Benchmark a specific agent."""
    orchestrator = AgentOrchestrator()

    results = {
        'times': [],
        'successes': 0,
        'failures': 0,
        'tokens_input': [],
        'tokens_output': [],
        'costs': []
    }

    print(f"Benchmarking: {agent_name}")
    print(f"Task: {task[:50]}...")
    print(f"Iterations: {iterations}\n")

    for i in range(iterations):
        print(f"  Iteration {i+1}/{iterations}... ", end='', flush=True)

        start = time.time()
        try:
            result = orchestrator.execute_agent(agent_name, task)
            elapsed = (time.time() - start) * 1000  # ms

            results['times'].append(elapsed)
            results['successes'] += 1

            # Get metrics from last execution
            tracker = orchestrator.performance_tracker
            last_metric = tracker.get_all_metrics()[-1]

            results['tokens_input'].append(last_metric.input_tokens)
            results['tokens_output'].append(last_metric.output_tokens)
            results['costs'].append(last_metric.estimated_cost)

            print(f"{elapsed:.0f}ms ✓")

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            results['times'].append(elapsed)
            results['failures'] += 1
            print(f"FAILED ({elapsed:.0f}ms) ✗")
            print(f"    Error: {str(e)}")

    # Calculate statistics
    times = results['times']
    times_sorted = sorted(times)

    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS: {agent_name}")
    print(f"{'='*60}\n")

    print(f"Success Rate: {results['successes']}/{iterations} ({results['successes']/iterations*100:.1f}%)")
    print()

    print("Latency:")
    print(f"  Mean:   {sum(times) / len(times):.0f}ms")
    print(f"  Median: {times_sorted[len(times)//2]:.0f}ms")
    print(f"  Min:    {min(times):.0f}ms")
    print(f"  Max:    {max(times):.0f}ms")
    print(f"  P95:    {times_sorted[int(len(times)*0.95)]:.0f}ms")
    print(f"  P99:    {times_sorted[int(len(times)*0.99)]:.0f}ms")
    print()

    if results['tokens_input']:
        print("Token Usage:")
        print(f"  Avg Input:  {sum(results['tokens_input']) / len(results['tokens_input']):.0f} tokens")
        print(f"  Avg Output: {sum(results['tokens_output']) / len(results['tokens_output']):.0f} tokens")
        print(f"  Total:      {sum(results['tokens_input']) + sum(results['tokens_output']):,} tokens")
        print()

    if results['costs']:
        total_cost = sum(results['costs'])
        avg_cost = total_cost / len(results['costs'])
        print("Cost:")
        print(f"  Per execution: ${avg_cost:.6f}")
        print(f"  Total:         ${total_cost:.4f}")
        print()

    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python benchmark_agent.py <agent_name> <task> [iterations]")
        sys.exit(1)

    agent_name = sys.argv[1]
    task = sys.argv[2]
    iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    benchmark_agent(agent_name, task, iterations)
EOF

chmod +x benchmark_agent.py
```

**Usage:**
```bash
# Benchmark python-expert
python benchmark_agent.py python-expert "Explain list comprehensions in Python" 10

# Benchmark code-reviewer
python benchmark_agent.py code-reviewer "Review this function for best practices" 5
```

### Workflow Benchmark

```bash
# Create benchmark_workflow.py
cat > benchmark_workflow.py << 'EOF'
#!/usr/bin/env python3
"""
Benchmark workflow execution.
"""
import time
from claude_force.orchestrator import AgentOrchestrator

def benchmark_workflow(workflow_name: str, iterations: int = 5):
    """Benchmark workflow execution."""
    orchestrator = AgentOrchestrator()

    results = {
        'times': [],
        'successes': 0,
        'failures': 0,
        'step_times': {},
        'total_cost': 0
    }

    print(f"Benchmarking workflow: {workflow_name}")
    print(f"Iterations: {iterations}\n")

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}:")

        start = time.time()
        try:
            # Load workflow
            workflow = orchestrator.config['workflows'].get(workflow_name)
            if not workflow:
                raise ValueError(f"Workflow '{workflow_name}' not found")

            # Execute each step
            step_start_time = time.time()
            for j, step in enumerate(workflow['steps']):
                step_name = f"  Step {j+1}: {step['agent']}"
                print(f"{step_name:30s} ", end='', flush=True)

                step_start = time.time()
                orchestrator.execute_agent(step['agent'], step['task'])
                step_elapsed = (time.time() - step_start) * 1000

                if step['agent'] not in results['step_times']:
                    results['step_times'][step['agent']] = []
                results['step_times'][step['agent']].append(step_elapsed)

                print(f"{step_elapsed:.0f}ms ✓")

            elapsed = (time.time() - start) * 1000
            results['times'].append(elapsed)
            results['successes'] += 1

            print(f"  {'Total:':<30s} {elapsed:.0f}ms\n")

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            results['times'].append(elapsed)
            results['failures'] += 1
            print(f"  FAILED: {str(e)}\n")

    # Calculate statistics
    times = results['times']
    times_sorted = sorted(times)

    print(f"{'='*60}")
    print(f"WORKFLOW BENCHMARK RESULTS: {workflow_name}")
    print(f"{'='*60}\n")

    print(f"Success Rate: {results['successes']}/{iterations} ({results['successes']/iterations*100:.1f}%)")
    print()

    print("Total Workflow Time:")
    print(f"  Mean:   {sum(times) / len(times):.0f}ms")
    print(f"  Median: {times_sorted[len(times)//2]:.0f}ms")
    print(f"  Min:    {min(times):.0f}ms")
    print(f"  Max:    {max(times):.0f}ms")
    print()

    print("Average Time per Step:")
    for agent, step_times in sorted(results['step_times'].items()):
        avg_time = sum(step_times) / len(step_times)
        print(f"  {agent:30s} {avg_time:.0f}ms")
    print()

    return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python benchmark_workflow.py <workflow_name> [iterations]")
        sys.exit(1)

    workflow_name = sys.argv[1]
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    benchmark_workflow(workflow_name, iterations)
EOF

chmod +x benchmark_workflow.py
```

**Usage:**
```bash
# Benchmark code-quality-check workflow
python benchmark_workflow.py code-quality-check 5

# Benchmark documentation-generation workflow
python benchmark_workflow.py documentation-generation 3
```

---

## Custom Benchmarks

### Create Custom Benchmark Suite

```python
#!/usr/bin/env python3
"""
Custom benchmark suite for your specific use cases.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from claude_force.orchestrator import AgentOrchestrator

class CustomBenchmark:
    def __init__(self, output_dir: str = "benchmark_results"):
        self.orchestrator = AgentOrchestrator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []

    def run_scenario(self, name: str, agent: str, task: str, iterations: int = 10):
        """Run a benchmark scenario."""
        print(f"\n{'='*60}")
        print(f"Scenario: {name}")
        print(f"{'='*60}")

        scenario_results = {
            'name': name,
            'agent': agent,
            'task': task,
            'iterations': iterations,
            'timestamp': datetime.now().isoformat(),
            'executions': []
        }

        for i in range(iterations):
            print(f"  [{i+1}/{iterations}] ", end='', flush=True)

            start = time.time()
            try:
                result = self.orchestrator.execute_agent(agent, task)
                elapsed = (time.time() - start) * 1000

                # Get last metric
                last_metric = self.orchestrator.performance_tracker.get_all_metrics()[-1]

                execution_result = {
                    'iteration': i + 1,
                    'success': True,
                    'execution_time_ms': elapsed,
                    'input_tokens': last_metric.input_tokens,
                    'output_tokens': last_metric.output_tokens,
                    'estimated_cost': last_metric.estimated_cost,
                    'model': last_metric.model
                }

                scenario_results['executions'].append(execution_result)
                print(f"{elapsed:.0f}ms ✓")

            except Exception as e:
                elapsed = (time.time() - start) * 1000
                execution_result = {
                    'iteration': i + 1,
                    'success': False,
                    'execution_time_ms': elapsed,
                    'error': str(e)
                }
                scenario_results['executions'].append(execution_result)
                print(f"FAILED ✗")

        # Calculate summary statistics
        successful = [e for e in scenario_results['executions'] if e['success']]
        if successful:
            times = [e['execution_time_ms'] for e in successful]
            times_sorted = sorted(times)

            scenario_results['summary'] = {
                'success_rate': len(successful) / iterations,
                'mean_time_ms': sum(times) / len(times),
                'median_time_ms': times_sorted[len(times)//2],
                'min_time_ms': min(times),
                'max_time_ms': max(times),
                'p95_time_ms': times_sorted[int(len(times)*0.95)],
                'avg_input_tokens': sum(e['input_tokens'] for e in successful) / len(successful),
                'avg_output_tokens': sum(e['output_tokens'] for e in successful) / len(successful),
                'total_cost': sum(e['estimated_cost'] for e in successful)
            }

            print(f"\n  Success Rate: {scenario_results['summary']['success_rate']:.1%}")
            print(f"  Mean Time: {scenario_results['summary']['mean_time_ms']:.0f}ms")
            print(f"  Total Cost: ${scenario_results['summary']['total_cost']:.4f}")
        else:
            scenario_results['summary'] = {
                'success_rate': 0,
                'error': 'All iterations failed'
            }

        self.results.append(scenario_results)
        return scenario_results

    def save_results(self, filename: str = None):
        """Save benchmark results to JSON."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"benchmark_{timestamp}.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'scenarios': self.results
            }, f, indent=2)

        print(f"\n✅ Results saved to: {output_path}")
        return output_path

    def print_summary(self):
        """Print overall benchmark summary."""
        print(f"\n{'='*60}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*60}\n")

        total_scenarios = len(self.results)
        total_executions = sum(r['iterations'] for r in self.results)
        total_successes = sum(
            sum(1 for e in r['executions'] if e.get('success', False))
            for r in self.results
        )

        print(f"Total Scenarios: {total_scenarios}")
        print(f"Total Executions: {total_executions}")
        print(f"Overall Success Rate: {total_successes/total_executions:.1%}")
        print()

        print("Scenario Results:")
        for result in self.results:
            summary = result.get('summary', {})
            if 'mean_time_ms' in summary:
                print(f"  {result['name']:30s} "
                      f"{summary['success_rate']:>6.1%}  "
                      f"{summary['mean_time_ms']:>7.0f}ms  "
                      f"${summary['total_cost']:>8.4f}")
            else:
                print(f"  {result['name']:30s} FAILED")
        print()

# Example usage
if __name__ == "__main__":
    benchmark = CustomBenchmark()

    # Define your scenarios
    scenarios = [
        {
            'name': 'Simple Python Question',
            'agent': 'python-expert',
            'task': 'What are list comprehensions?',
            'iterations': 10
        },
        {
            'name': 'Code Review',
            'agent': 'code-reviewer',
            'task': 'Review this function: def add(a, b): return a + b',
            'iterations': 5
        },
        {
            'name': 'API Design',
            'agent': 'api-designer',
            'task': 'Design a REST API for a todo application',
            'iterations': 5
        }
    ]

    # Run all scenarios
    for scenario in scenarios:
        benchmark.run_scenario(**scenario)

    # Print and save results
    benchmark.print_summary()
    benchmark.save_results()
```

**Save and run:**
```bash
# Save to file
cat > custom_benchmark.py << 'EOF'
# ... (paste the code above)
EOF

# Run benchmark
python custom_benchmark.py
```

---

## Load Testing

### Concurrent Execution Test

```python
#!/usr/bin/env python3
"""
Load test with concurrent agent execution.
"""
import asyncio
import time
from datetime import datetime
from claude_force.orchestrator import AgentOrchestrator

async def execute_task_async(orchestrator, agent, task, task_id):
    """Execute single task asynchronously (simulated)."""
    start = time.time()
    try:
        # Note: Current implementation is synchronous
        # This simulates async by running in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            orchestrator.execute_agent,
            agent,
            task
        )
        elapsed = (time.time() - start) * 1000
        return {
            'task_id': task_id,
            'success': True,
            'time_ms': elapsed
        }
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return {
            'task_id': task_id,
            'success': False,
            'time_ms': elapsed,
            'error': str(e)
        }

async def load_test(num_tasks, concurrency):
    """Run load test with specified concurrency."""
    orchestrator = AgentOrchestrator()

    # Generate tasks
    tasks = [
        {
            'id': i,
            'agent': 'python-expert',
            'task': f'Explain concept {i % 10}'
        }
        for i in range(num_tasks)
    ]

    print(f"{'='*60}")
    print(f"LOAD TEST")
    print(f"{'='*60}")
    print(f"Total Tasks: {num_tasks}")
    print(f"Concurrency: {concurrency}")
    print()

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(concurrency)

    async def execute_with_semaphore(task):
        async with semaphore:
            return await execute_task_async(
                orchestrator,
                task['agent'],
                task['task'],
                task['id']
            )

    # Execute all tasks
    start_time = time.time()

    results = await asyncio.gather(*[
        execute_with_semaphore(task)
        for task in tasks
    ])

    total_time = time.time() - start_time

    # Analyze results
    successes = sum(1 for r in results if r['success'])
    failures = num_tasks - successes
    success_rate = (successes / num_tasks) * 100

    execution_times = [r['time_ms'] for r in results if r['success']]
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        times_sorted = sorted(execution_times)
        p50 = times_sorted[len(times_sorted)//2]
        p95 = times_sorted[int(len(times_sorted)*0.95)]
    else:
        avg_time = min_time = max_time = p50 = p95 = 0

    throughput = num_tasks / total_time

    # Print results
    print(f"{'='*60}")
    print("RESULTS")
    print(f"{'='*60}\n")

    print(f"Total Time: {total_time:.2f}s")
    print(f"Success Rate: {successes}/{num_tasks} ({success_rate:.1f}%)")
    print(f"Throughput: {throughput:.2f} tasks/second")
    print()

    print("Latency:")
    print(f"  Average: {avg_time:.0f}ms")
    print(f"  P50:     {p50:.0f}ms")
    print(f"  P95:     {p95:.0f}ms")
    print(f"  Min:     {min_time:.0f}ms")
    print(f"  Max:     {max_time:.0f}ms")
    print()

    return results

if __name__ == "__main__":
    import sys

    num_tasks = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    asyncio.run(load_test(num_tasks, concurrency))
```

**Usage:**
```bash
# 50 tasks, 5 concurrent
python load_test.py 50 5

# 100 tasks, 10 concurrent
python load_test.py 100 10

# 200 tasks, 20 concurrent
python load_test.py 200 20
```

---

## Performance Profiling

### CPU Profiling

```bash
# Install profiling tool
pip install py-spy

# Profile agent execution
py-spy record -o profile.svg -- python benchmark_agent.py python-expert "Explain decorators" 10

# View flame graph
open profile.svg  # or firefox profile.svg
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Create profiled script
cat > profile_memory.py << 'EOF'
from memory_profiler import profile
from claude_force.orchestrator import AgentOrchestrator

@profile
def run_agent():
    orchestrator = AgentOrchestrator()
    result = orchestrator.execute_agent("python-expert", "Explain list comprehensions")
    return result

if __name__ == "__main__":
    run_agent()
EOF

# Run profiler
python -m memory_profiler profile_memory.py
```

### Line-by-Line Profiling

```bash
# Install line_profiler
pip install line_profiler

# Add @profile decorator to functions you want to profile
# Then run:
kernprof -l -v your_script.py
```

---

## Regression Testing

### Automated Regression Detection

```python
#!/usr/bin/env python3
"""
Automated performance regression testing.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def load_baseline(baseline_file):
    """Load baseline metrics."""
    with open(baseline_file) as f:
        return json.load(f)

def run_current_benchmarks():
    """Run current benchmarks and return results."""
    from custom_benchmark import CustomBenchmark

    benchmark = CustomBenchmark()

    # Run same scenarios as baseline
    scenarios = [
        {
            'name': 'Simple Python Question',
            'agent': 'python-expert',
            'task': 'What are list comprehensions?',
            'iterations': 10
        },
        {
            'name': 'Code Review',
            'agent': 'code-reviewer',
            'task': 'Review this function: def add(a, b): return a + b',
            'iterations': 5
        }
    ]

    for scenario in scenarios:
        benchmark.run_scenario(**scenario)

    return benchmark.results

def detect_regressions(baseline, current, threshold=1.15):
    """
    Detect performance regressions.

    Args:
        baseline: Baseline benchmark results
        current: Current benchmark results
        threshold: Allowed degradation (1.15 = 15% slower)

    Returns:
        List of regressions
    """
    regressions = []

    # Match scenarios by name
    baseline_by_name = {s['name']: s for s in baseline['scenarios']}

    for current_scenario in current:
        scenario_name = current_scenario['name']
        baseline_scenario = baseline_by_name.get(scenario_name)

        if not baseline_scenario:
            continue

        current_summary = current_scenario.get('summary', {})
        baseline_summary = baseline_scenario.get('summary', {})

        if not (current_summary and baseline_summary):
            continue

        # Check latency regression
        current_time = current_summary.get('mean_time_ms', 0)
        baseline_time = baseline_summary.get('mean_time_ms', 0)

        if current_time > baseline_time * threshold:
            regressions.append({
                'scenario': scenario_name,
                'metric': 'Mean Execution Time',
                'baseline': f"{baseline_time:.0f}ms",
                'current': f"{current_time:.0f}ms",
                'degradation': f"{((current_time / baseline_time - 1) * 100):.1f}%"
            })

        # Check success rate regression
        current_success = current_summary.get('success_rate', 0)
        baseline_success = baseline_summary.get('success_rate', 0)

        if current_success < baseline_success * 0.95:  # 5% drop
            regressions.append({
                'scenario': scenario_name,
                'metric': 'Success Rate',
                'baseline': f"{baseline_success:.1%}",
                'current': f"{current_success:.1%}",
                'degradation': f"{(baseline_success - current_success):.1%}pp"
            })

        # Check cost regression
        current_cost = current_summary.get('total_cost', 0)
        baseline_cost = baseline_summary.get('total_cost', 0)

        if current_cost > baseline_cost * 1.5:  # 50% cost increase
            regressions.append({
                'scenario': scenario_name,
                'metric': 'Total Cost',
                'baseline': f"${baseline_cost:.4f}",
                'current': f"${current_cost:.4f}",
                'degradation': f"{((current_cost / baseline_cost - 1) * 100):.1f}%"
            })

    return regressions

def main():
    baseline_file = "benchmark_results/baseline.json"

    if not Path(baseline_file).exists():
        print("❌ Baseline file not found. Create baseline first:")
        print(f"   python custom_benchmark.py")
        print(f"   mv benchmark_results/benchmark_*.json {baseline_file}")
        sys.exit(1)

    print("Loading baseline...")
    baseline = load_baseline(baseline_file)

    print("Running current benchmarks...")
    current = run_current_benchmarks()

    print("\nDetecting regressions...")
    regressions = detect_regressions(baseline, current)

    if regressions:
        print("\n⚠️  PERFORMANCE REGRESSIONS DETECTED:\n")
        for r in regressions:
            print(f"  Scenario: {r['scenario']}")
            print(f"  Metric: {r['metric']}")
            print(f"    Baseline:    {r['baseline']}")
            print(f"    Current:     {r['current']}")
            print(f"    Degradation: {r['degradation']}")
            print()

        sys.exit(1)
    else:
        print("\n✅ No performance regressions detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/performance-test.yml
name: Performance Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  benchmark:
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
          pip install pytest pytest-benchmark

      - name: Run benchmarks
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python custom_benchmark.py

      - name: Check for regressions
        run: |
          python regression_test.py

      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark_results/

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('benchmark_results/benchmark_latest.json'));

            let comment = '## Performance Benchmark Results\n\n';
            comment += '| Scenario | Success Rate | Avg Time | Cost |\n';
            comment += '|----------|--------------|----------|------|\n';

            for (const scenario of results.scenarios) {
              const summary = scenario.summary;
              comment += `| ${scenario.name} | ${(summary.success_rate * 100).toFixed(1)}% | ${summary.mean_time_ms.toFixed(0)}ms | $${summary.total_cost.toFixed(4)} |\n`;
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### GitLab CI

```yaml
# .gitlab-ci.yml
performance-test:
  stage: test
  image: python:3.11
  script:
    - pip install -e .
    - python custom_benchmark.py
    - python regression_test.py
  artifacts:
    paths:
      - benchmark_results/
    expire_in: 30 days
  only:
    - main
    - merge_requests
```

---

## Summary

**Quick Commands:**

```bash
# Run built-in benchmarks
python benchmarks/run_benchmarks.py --report

# Benchmark specific agent
python benchmark_agent.py python-expert "Explain decorators" 10

# Benchmark workflow
python benchmark_workflow.py code-quality-check 5

# Run custom benchmark suite
python custom_benchmark.py

# Load test
python load_test.py 100 10

# Check for regressions
python regression_test.py
```

**Best Practices:**

1. **Establish baseline** before making changes
2. **Run benchmarks regularly** (nightly, pre-release)
3. **Compare results** against baseline
4. **Set performance budgets** (latency, cost, success rate)
5. **Profile when optimizing** (CPU, memory)
6. **Test under load** (concurrency, stress tests)
7. **Automate in CI/CD** (catch regressions early)

**Key Metrics:**

- ✅ Execution time (P50, P95, P99)
- ✅ Success rate (>95% target)
- ✅ Cost per execution
- ✅ Token usage
- ✅ Throughput (tasks/second)

---

For detailed analysis and monitoring, see:
- [Performance Analysis Report](performance-analysis.md)
- [Performance Monitoring Guide](performance-monitoring-guide.md)
