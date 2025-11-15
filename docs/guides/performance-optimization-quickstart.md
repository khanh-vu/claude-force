# Performance Optimization Quick Start Guide

**Get started with Claude Force performance optimizations in minutes!**

This guide provides step-by-step instructions to implement the high-impact optimizations identified in the [Performance Analysis](performance-analysis.md) and [Optimization Plan](performance-optimization-plan.md).

---

## 🚀 Quick Wins (Start Here!)

### Priority 1: Enable Async Execution (2-3 hours)

**Impact:** 50-80% faster workflows
**Difficulty:** Medium
**Time:** 2-3 hours

#### Step 1: Install Dependencies

```bash
# Already have anthropic>=0.40.0, add async file I/O
pip install aiofiles>=23.0.0
```

#### Step 2: Create Minimal Async Wrapper

Create `claude_force/simple_async.py`:

```python
"""
Simple async wrapper for quick wins.
"""
import asyncio
from anthropic import AsyncAnthropic
import os

class SimpleAsyncOrchestrator:
    """Minimal async wrapper for parallel execution."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def execute_task(self, prompt: str, model: str = "claude-3-5-haiku-20241022"):
        """Execute a single task."""
        response = await self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def execute_parallel(self, prompts: list[str]):
        """Execute multiple prompts in parallel."""
        results = await asyncio.gather(*[
            self.execute_task(prompt)
            for prompt in prompts
        ])
        return results

# Usage example
async def main():
    orchestrator = SimpleAsyncOrchestrator()

    prompts = [
        "Explain Python lists",
        "Explain Python dicts",
        "Explain Python sets"
    ]

    import time
    start = time.time()
    results = await orchestrator.execute_parallel(prompts)
    elapsed = time.time() - start

    print(f"Completed {len(results)} tasks in {elapsed:.2f}s")
    print(f"Throughput: {len(results) / elapsed:.2f} tasks/second")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Step 3: Test It!

```bash
# Run the async example
python claude_force/simple_async.py
```

**Expected Output:**
```
Completed 3 tasks in 3.5s
Throughput: 0.86 tasks/second
```

Compare to sequential (9-12s for 3 tasks) → **2-3x faster!** ✅

---

### Priority 2: Basic Response Caching (1-2 hours)

**Impact:** 30-50% cost reduction
**Difficulty:** Easy
**Time:** 1-2 hours

#### Step 1: Create Simple Cache

Create `claude_force/simple_cache.py`:

```python
"""
Simple file-based response cache.
"""
import hashlib
import json
import time
from pathlib import Path
from typing import Optional

class SimpleCache:
    """Basic TTL-based cache."""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600

    def _key(self, prompt: str) -> str:
        """Generate cache key."""
        return hashlib.md5(prompt.encode()).hexdigest()

    def get(self, prompt: str) -> Optional[str]:
        """Get cached response."""
        key = self._key(prompt)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        # Check TTL
        age = time.time() - cache_file.stat().st_mtime
        if age > self.ttl_seconds:
            cache_file.unlink()
            return None

        # Load from cache
        with open(cache_file) as f:
            data = json.load(f)
            return data['response']

    def set(self, prompt: str, response: str):
        """Cache response."""
        key = self._key(prompt)
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, 'w') as f:
            json.dump({
                'prompt': prompt,
                'response': response,
                'timestamp': time.time()
            }, f)

# Usage example
def main():
    from anthropic import Anthropic
    import os

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    cache = SimpleCache()

    prompt = "What are Python decorators?"

    # Try cache first
    cached = cache.get(prompt)
    if cached:
        print("✅ Cache hit!")
        print(cached)
        return

    # Cache miss - call API
    print("❌ Cache miss - calling API...")
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.content[0].text

    # Cache the response
    cache.set(prompt, result)
    print("✅ Response cached")
    print(result)

if __name__ == "__main__":
    main()
```

#### Step 2: Test It!

```bash
# First run - cache miss
python claude_force/simple_cache.py

# Second run - cache hit (should be instant!)
python claude_force/simple_cache.py
```

**Expected:**
- First run: 2-4 seconds (API call)
- Second run: <100ms (cache hit) → **~40x faster!** ✅

---

### Priority 3: Parallel Workflow Pattern (30 minutes)

**Impact:** 2-3x throughput for workflows
**Difficulty:** Easy
**Time:** 30 minutes

#### Simple Pattern

```python
"""
Simple parallel workflow pattern.
"""
import asyncio
from anthropic import AsyncAnthropic
import os

async def parallel_workflow_example():
    """Execute workflow steps in parallel where possible."""
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def call_api(prompt: str):
        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    import time
    start = time.time()

    # Step 1: Run independent checks in parallel
    print("Running parallel checks...")
    linter, type_check, security = await asyncio.gather(
        call_api("Check Python code style"),
        call_api("Check Python type hints"),
        call_api("Check for security issues")
    )

    print(f"  Parallel checks completed in {time.time() - start:.2f}s")

    # Step 2: Run final review with results
    print("Running final review...")
    review_prompt = f"""
    Based on these findings:
    - Linter: {linter[:100]}...
    - Type Check: {type_check[:100]}...
    - Security: {security[:100]}...

    Provide final code review.
    """

    final_review = await call_api(review_prompt)

    total_time = time.time() - start
    print(f"\n✅ Workflow completed in {total_time:.2f}s")
    print(f"   (Sequential would take ~{total_time * 1.5:.2f}s)")

if __name__ == "__main__":
    asyncio.run(parallel_workflow_example())
```

**Test:**
```bash
python parallel_workflow_example.py
```

**Expected:** 3 independent steps complete in ~4s (vs ~12s sequential) → **3x faster!** ✅

---

## 🎯 Implementation Checklist

### Phase 1: Foundation (Week 1-4)

#### Week 1-2: Async Implementation

- [ ] Install `aiofiles>=23.0.0`
- [ ] Create `claude_force/async_orchestrator.py`
- [ ] Add async methods to existing `AgentOrchestrator`
- [ ] Write unit tests for async operations
- [ ] Update CLI with `--async` flag
- [ ] Test backward compatibility

**Validation:**
```bash
# Test async execution
python -m pytest tests/test_async_orchestrator.py -v

# Benchmark speedup
python benchmarks/benchmark_async_vs_sync.py
```

#### Week 3-4: Response Caching

- [ ] Create `claude_force/response_cache.py`
- [ ] Implement TTL-based expiration
- [ ] Add LRU eviction logic
- [ ] Integrate with orchestrator
- [ ] Add cache CLI commands
- [ ] Test cache correctness

**Validation:**
```bash
# Test cache functionality
python -m pytest tests/test_response_cache.py -v

# Check cache stats
claude-force cache stats
```

### Phase 2: Advanced (Week 5-8)

#### Week 5-6: Parallel Workflows

- [ ] Create `claude_force/workflow_dag.py`
- [ ] Update workflow schema with dependencies
- [ ] Implement DAG executor
- [ ] Add cycle detection
- [ ] Test parallel execution

**Validation:**
```bash
# Test DAG execution
python -m pytest tests/test_workflow_dag.py -v

# Benchmark workflow speedup
python benchmarks/benchmark_parallel_workflow.py
```

#### Week 7: Metrics & Caching

- [ ] Implement metrics aggregation
- [ ] Add query result caching (LRU)
- [ ] Optimize analytics queries

**Validation:**
```bash
# Test aggregation
python -m pytest tests/test_metrics_aggregation.py -v

# Verify query performance
python benchmarks/benchmark_query_cache.py
```

---

## 🔧 Development Setup

### 1. Create Feature Branch

```bash
cd /home/user/claude-force
git checkout -b feature/performance-optimization-v2.3
```

### 2. Set Up Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"
pip install aiofiles>=23.0.0

# Install testing tools
pip install pytest pytest-asyncio pytest-cov pytest-benchmark

# Install profiling tools
pip install py-spy memory_profiler line_profiler
```

### 3. Run Baseline Benchmarks

```bash
# Create baseline for comparison
python benchmarks/run_benchmarks.py --output baseline_v2.2.0.json

# Save baseline
cp baseline_v2.2.0.json benchmarks/results/
```

---

## 🧪 Testing Strategy

### Unit Tests

```bash
# Test async operations
pytest tests/test_async_orchestrator.py -v

# Test caching
pytest tests/test_response_cache.py -v

# Test DAG execution
pytest tests/test_workflow_dag.py -v

# Run all tests with coverage
pytest --cov=claude_force --cov-report=html
```

### Integration Tests

```bash
# Test full async workflow
pytest tests/integration/test_async_workflows.py -v

# Test cache integration
pytest tests/integration/test_cache_integration.py -v

# Test parallel execution
pytest tests/integration/test_parallel_execution.py -v
```

### Performance Tests

```bash
# Benchmark async vs sync
python benchmarks/benchmark_async_vs_sync.py

# Benchmark cache effectiveness
python benchmarks/benchmark_cache.py

# Benchmark parallel workflows
python benchmarks/benchmark_parallel_workflow.py

# Full benchmark suite
python benchmarks/run_benchmarks.py --report
```

---

## 📊 Performance Validation

### Before Starting

Run baseline benchmarks:

```bash
# Sequential execution (3 agents)
time python -c "
from claude_force.orchestrator import AgentOrchestrator
orch = AgentOrchestrator()
for i in range(3):
    orch.execute_agent('python-expert', f'Task {i}')
"
```

**Expected:** 9-15 seconds

### After Async Implementation

Run async benchmarks:

```bash
# Parallel execution (3 agents)
time python -c "
import asyncio
from claude_force.async_orchestrator import AsyncAgentOrchestrator

async def test():
    orch = AsyncAgentOrchestrator()
    await orch.execute_multiple([
        ('python-expert', 'Task 0'),
        ('python-expert', 'Task 1'),
        ('python-expert', 'Task 2')
    ])

asyncio.run(test())
"
```

**Expected:** 3-5 seconds → **2-3x faster!** ✅

### After Caching Implementation

```bash
# First run (cache miss)
time claude-force execute python-expert "Explain decorators"

# Second run (cache hit)
time claude-force execute python-expert "Explain decorators"
```

**Expected:**
- First run: 2-4 seconds
- Second run: <100ms → **~40x faster!** ✅

---

## 🐛 Common Issues & Solutions

### Issue 1: "RuntimeError: This event loop is already running"

**Cause:** Trying to call `asyncio.run()` inside an existing event loop

**Solution:**
```python
# Instead of:
asyncio.run(my_async_function())

# Use:
await my_async_function()  # If already in async context

# Or:
import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(my_async_function())
```

### Issue 2: Cache returning stale data

**Cause:** TTL too long or cache not invalidating

**Solution:**
```python
# Reduce TTL
cache = ResponseCache(ttl_hours=1)  # Instead of 24

# Or clear cache
claude-force cache clear

# Or exclude specific agents
config['cache']['exclude_agents'] = ['creative-writer']
```

### Issue 3: "Too many open files"

**Cause:** Running many concurrent async operations

**Solution:**
```python
# Limit concurrency with semaphore
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

async def execute_with_limit(task):
    async with semaphore:
        return await execute_task(task)
```

### Issue 4: Tests hanging

**Cause:** Async operations not completing

**Solution:**
```python
# Add timeout to tests
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_async_operation():
    result = await orchestrator.execute_agent_async(...)
    assert result

# Or use asyncio timeout
async with asyncio.timeout(10):
    result = await long_operation()
```

---

## 📚 Code Examples

### Example 1: Basic Async Usage

```python
import asyncio
from claude_force.async_orchestrator import AsyncAgentOrchestrator

async def main():
    orch = AsyncAgentOrchestrator()

    # Single async execution
    result = await orch.execute_agent("python-expert", "Explain async/await")
    print(result)

    # Multiple async executions
    results = await orch.execute_multiple([
        ("python-expert", "Explain lists"),
        ("python-expert", "Explain dicts"),
        ("code-reviewer", "Review my code")
    ])

    for i, result in enumerate(results):
        print(f"Task {i}: {result[:100]}...")

asyncio.run(main())
```

### Example 2: Cache-Aware Execution

```python
from claude_force.orchestrator import AgentOrchestrator

# Enable caching in config
orch = AgentOrchestrator()

# First call - cache miss
result1 = orch.execute_agent("python-expert", "Explain decorators")
print("First call:", result1[:100])

# Second call - cache hit (same prompt)
result2 = orch.execute_agent("python-expert", "Explain decorators")
print("Second call (cached):", result2[:100])

# Check cache stats
stats = orch.response_cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate']}")
```

### Example 3: Parallel Workflow

```python
import asyncio
from claude_force.workflow_dag import WorkflowDAG
from claude_force.async_orchestrator import AsyncAgentOrchestrator

async def run_workflow():
    orch = AsyncAgentOrchestrator()
    dag = WorkflowDAG(orch)

    workflow = {
        'name': 'Code Quality Check',
        'steps': [
            {
                'id': 'linter',
                'agent': 'linter',
                'task': 'Check code style',
                'dependencies': []
            },
            {
                'id': 'type-check',
                'agent': 'type-checker',
                'task': 'Check types',
                'dependencies': []
            },
            {
                'id': 'review',
                'agent': 'code-reviewer',
                'task': 'Final review',
                'dependencies': ['linter', 'type-check']
            }
        ]
    }

    result = await dag.execute_workflow(workflow)
    print(f"Completed in {result['total_time_seconds']:.2f}s")
    print(f"Execution order: {result['execution_order']}")

asyncio.run(run_workflow())
```

---

## 🎓 Best Practices

### 1. Async Operations

**DO:**
- ✅ Use `async/await` for I/O-bound operations
- ✅ Limit concurrency with semaphores
- ✅ Add timeouts to prevent hanging
- ✅ Handle exceptions in async code

**DON'T:**
- ❌ Mix sync and async without proper handling
- ❌ Run CPU-intensive tasks in async (use threading/multiprocessing)
- ❌ Forget to await async functions
- ❌ Create unbounded concurrent operations

### 2. Caching

**DO:**
- ✅ Use conservative TTL values (24 hours)
- ✅ Exclude non-deterministic agents
- ✅ Monitor cache hit rates
- ✅ Implement cache size limits

**DON'T:**
- ❌ Cache forever (use TTL)
- ❌ Cache sensitive data without encryption
- ❌ Ignore cache invalidation
- ❌ Let cache grow unbounded

### 3. Parallel Workflows

**DO:**
- ✅ Identify truly independent steps
- ✅ Use dependency tracking
- ✅ Test for race conditions
- ✅ Monitor for deadlocks

**DON'T:**
- ❌ Assume all steps can run in parallel
- ❌ Forget dependency order
- ❌ Ignore shared state
- ❌ Skip error handling

---

## 📈 Measuring Success

### Key Metrics to Track

```python
# Track before and after
metrics = {
    'workflow_time_before': 15.3,  # seconds
    'workflow_time_after': 5.2,    # seconds
    'speedup': 2.94,               # 2.94x faster

    'cost_before': 0.002,          # USD per execution
    'cost_after': 0.0008,          # USD per execution
    'cost_savings': 0.60,          # 60% savings

    'cache_hit_rate': 0.45,        # 45% cache hits
    'throughput_before': 60,       # tasks/hour
    'throughput_after': 180        # tasks/hour (3x)
}
```

### Performance Dashboard

```bash
# View performance summary
claude-force analytics summary --days 7

# Compare before/after
claude-force analytics compare \
  --baseline baseline_v2.2.0.json \
  --current current_v2.3.0.json
```

---

## 🚀 Quick Start Checklist

**Hour 1: Async Basics**
- [ ] Install `aiofiles`
- [ ] Create `simple_async.py`
- [ ] Test parallel execution
- [ ] Measure speedup

**Hour 2-3: Basic Caching**
- [ ] Create `simple_cache.py`
- [ ] Test cache hit/miss
- [ ] Measure latency improvement
- [ ] Measure cost savings

**Hour 4-6: Integration**
- [ ] Integrate async into orchestrator
- [ ] Integrate cache into orchestrator
- [ ] Write tests
- [ ] Update documentation

**Week 2+: Advanced Features**
- [ ] Implement parallel workflows
- [ ] Add metrics aggregation
- [ ] Enhance monitoring
- [ ] Production deployment

---

## 🎯 Success Criteria

After implementing these quick wins, you should see:

- ✅ **2-3x faster** execution for concurrent tasks
- ✅ **<100ms** response time for cached queries
- ✅ **30-50%** cost reduction (with caching)
- ✅ **2-5x** throughput improvement
- ✅ **All tests passing** (backward compatibility)

---

## 📞 Need Help?

**Resources:**
- [Full Implementation Plan](performance-optimization-plan.md)
- [Performance Analysis](performance-analysis.md)
- [Roadmap](performance-optimization-roadmap.md)

**Common Questions:**
- Q: "My async code is hanging" → Check for timeouts and proper await usage
- Q: "Cache not working" → Verify TTL and check cache stats
- Q: "No speedup observed" → Ensure tasks are actually running in parallel

---

**Ready to optimize? Start with Priority 1 and work your way down!** 🚀
