"""
Performance benchmark tests for async orchestrator and response cache.

These tests measure actual performance characteristics and validate
the expected performance improvements from the optimization plan.

Run with: pytest tests/test_performance_benchmarks.py -v -s
"""
import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Tuple
from unittest import mock
import statistics

from claude_force.async_orchestrator import AsyncAgentOrchestrator
from claude_force.response_cache import ResponseCache


# ============================================================================
# Performance Test Configuration
# ============================================================================

class PerformanceConfig:
    """Configuration for performance tests"""
    # Benchmarks
    BENCHMARK_ITERATIONS = 10
    WARMUP_ITERATIONS = 2

    # Targets (based on optimization plan)
    CACHE_HIT_TARGET_MS = 50  # <50ms for cache hits
    CONCURRENT_SPEEDUP_TARGET = 2.5  # 2.5x faster than sequential

    # Load testing
    CONCURRENT_AGENTS = [1, 2, 5, 10, 20]
    LARGE_TASK_SIZES = [1000, 10_000, 50_000]  # chars


# ============================================================================
# Mock Helpers
# ============================================================================

def create_mock_api_response(delay_ms: float = 100):
    """Create a mock API response with configurable delay"""
    async def mock_api_call(*args, **kwargs):
        await asyncio.sleep(delay_ms / 1000)  # Convert to seconds
        mock_response = mock.Mock()
        mock_response.content = [mock.Mock(text="Mock response")]
        mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
        mock_response.model = "claude-3-5-sonnet-20241022"
        return mock_response
    return mock_api_call


# ============================================================================
# Cache Performance Benchmarks
# ============================================================================

@pytest.mark.benchmark
def test_cache_hit_performance(tmp_path, benchmark):
    """
    Benchmark: Cache hit performance
    Target: <1ms average
    """
    cache = ResponseCache(cache_dir=tmp_path / "cache", cache_secret="test_secret")

    # Store entry
    cache.set("agent", "task", "model", "response" * 100, 1000, 500, 0.001)

    # Benchmark cache hits
    def cache_hit():
        result = cache.get("agent", "task", "model")
        assert result is not None
        return result

    result = benchmark(cache_hit)

    # Verify performance
    assert benchmark.stats['mean'] < 0.001  # <1ms average
    print(f"\n✓ Cache hit: {benchmark.stats['mean']*1000:.3f}ms (target: <1ms)")


@pytest.mark.benchmark
def test_cache_miss_performance(tmp_path, benchmark):
    """
    Benchmark: Cache miss performance
    Target: <1ms average
    """
    cache = ResponseCache(cache_dir=tmp_path / "cache", cache_secret="test_secret")

    # Benchmark cache misses
    def cache_miss():
        result = cache.get("nonexistent", "task", "model")
        assert result is None
        return result

    result = benchmark(cache_miss)

    # Verify performance
    assert benchmark.stats['mean'] < 0.001  # <1ms average
    print(f"\n✓ Cache miss: {benchmark.stats['mean']*1000:.3f}ms (target: <1ms)")


@pytest.mark.benchmark
def test_cache_write_performance(tmp_path, benchmark):
    """
    Benchmark: Cache write performance
    Target: <10ms average
    """
    cache = ResponseCache(cache_dir=tmp_path / "cache", cache_secret="test_secret")

    counter = [0]

    def cache_write():
        cache.set(
            f"agent{counter[0]}",
            f"task{counter[0]}",
            "model",
            "response" * 100,
            1000,
            500,
            0.001
        )
        counter[0] += 1

    benchmark(cache_write)

    # Verify performance
    assert benchmark.stats['mean'] < 0.010  # <10ms average
    print(f"\n✓ Cache write: {benchmark.stats['mean']*1000:.3f}ms (target: <10ms)")


@pytest.mark.benchmark
def test_cache_eviction_performance(tmp_path):
    """
    Benchmark: LRU eviction performance with heapq optimization
    Expected: O(k log n) where k is eviction count
    """
    cache = ResponseCache(
        cache_dir=tmp_path / "cache",
        max_size_mb=1,  # 1MB limit to trigger eviction
        cache_secret="test_secret"
    )

    # Fill cache with 1000 entries
    fill_start = time.time()
    for i in range(1000):
        cache.set(f"agent{i}", f"task{i}", "model", "x" * 2000, 100, 50, 0.001)
    fill_time = time.time() - fill_start

    # Trigger eviction by adding more entries
    eviction_start = time.time()
    for i in range(1000, 1100):
        cache.set(f"agent{i}", f"task{i}", "model", "x" * 2000, 100, 50, 0.001)
    eviction_time = time.time() - eviction_start

    print(f"\n✓ Fill 1000 entries: {fill_time:.3f}s")
    print(f"✓ Eviction (100 more entries): {eviction_time:.3f}s")
    print(f"✓ Evictions triggered: {cache.stats['evictions']}")

    # Eviction should be reasonably fast
    assert eviction_time < 1.0  # Should complete in <1s


@pytest.mark.benchmark
def test_cache_large_response_performance(tmp_path):
    """
    Benchmark: Large response caching (2MB response)
    """
    cache = ResponseCache(
        cache_dir=tmp_path / "cache",
        max_size_mb=10,
        cache_secret="test_secret"
    )

    # 2MB response
    large_response = "x" * (2 * 1024 * 1024)

    # Write
    write_start = time.time()
    cache.set("agent", "task", "model", large_response, 10000, 5000, 0.01)
    write_time = time.time() - write_start

    # Read
    read_start = time.time()
    result = cache.get("agent", "task", "model")
    read_time = time.time() - read_start

    assert result is not None
    print(f"\n✓ Cache write (2MB): {write_time*1000:.3f}ms")
    print(f"✓ Cache read (2MB): {read_time*1000:.3f}ms")

    # Should handle large responses efficiently
    assert write_time < 0.5  # <500ms for 2MB write
    assert read_time < 0.1   # <100ms for 2MB read


# ============================================================================
# Async Orchestrator Performance Benchmarks
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_async_single_agent_latency():
    """
    Benchmark: Single agent execution latency
    Measures overhead of async implementation
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10)

    # Mock fast API (100ms)
    mock_api = create_mock_api_response(delay_ms=100)

    times = []

    with mock.patch.object(orchestrator, '_call_api_with_retry', mock_api):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent def"):
            # Warmup
            for _ in range(PerformanceConfig.WARMUP_ITERATIONS):
                await orchestrator.execute_agent("python-expert", "task")

            # Benchmark
            for _ in range(PerformanceConfig.BENCHMARK_ITERATIONS):
                start = time.time()
                result = await orchestrator.execute_agent("python-expert", "task")
                elapsed = time.time() - start
                times.append(elapsed)
                assert result.success

    mean_time = statistics.mean(times)
    overhead = mean_time - 0.1  # Subtract API time

    print(f"\n✓ Single agent execution: {mean_time*1000:.1f}ms")
    print(f"✓ Async overhead: {overhead*1000:.1f}ms")

    # Overhead should be minimal (<10ms)
    assert overhead < 0.010


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_concurrent_execution_speedup():
    """
    Benchmark: Concurrent execution speedup
    Target: 2.5x+ faster than sequential for 5 agents
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10)

    # Mock API with 200ms delay
    mock_api = create_mock_api_response(delay_ms=200)

    num_agents = 5
    tasks: List[Tuple[str, str]] = [
        ("python-expert", f"task{i}") for i in range(num_agents)
    ]

    with mock.patch.object(orchestrator, '_call_api_with_retry', mock_api):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent def"):
            # Sequential execution time (simulated)
            sequential_time = 0.2 * num_agents  # 200ms per agent

            # Concurrent execution
            concurrent_start = time.time()
            results = await orchestrator.execute_multiple(tasks)
            concurrent_time = time.time() - concurrent_start

            assert len(results) == num_agents
            assert all(r.success for r in results)

    speedup = sequential_time / concurrent_time

    print(f"\n✓ Sequential (estimated): {sequential_time*1000:.1f}ms")
    print(f"✓ Concurrent: {concurrent_time*1000:.1f}ms")
    print(f"✓ Speedup: {speedup:.2f}x")

    # Should achieve 2.5x+ speedup
    assert speedup >= PerformanceConfig.CONCURRENT_SPEEDUP_TARGET


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_concurrency_scaling():
    """
    Benchmark: How execution time scales with concurrent agents
    Validates that concurrency limits work correctly
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10)

    mock_api = create_mock_api_response(delay_ms=100)

    results = {}

    with mock.patch.object(orchestrator, '_call_api_with_retry', mock_api):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent def"):
            for num_agents in PerformanceConfig.CONCURRENT_AGENTS:
                tasks: List[Tuple[str, str]] = [
                    ("python-expert", f"task{i}") for i in range(num_agents)
                ]

                start = time.time()
                agent_results = await orchestrator.execute_multiple(tasks)
                elapsed = time.time() - start

                results[num_agents] = elapsed
                assert len(agent_results) == num_agents

    print("\n✓ Concurrency Scaling:")
    for num_agents, elapsed in results.items():
        expected_time = 0.1 * ((num_agents + 9) // 10)  # With max_concurrent=10
        print(f"  {num_agents:2d} agents: {elapsed*1000:6.1f}ms (expected ~{expected_time*1000:.0f}ms)")

    # Verify scaling is reasonable
    # With 10 concurrent, 20 agents should take ~2x the time of 10 agents
    if 10 in results and 20 in results:
        ratio = results[20] / results[10]
        assert 1.8 < ratio < 2.5  # Allow some variance


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_timeout_performance():
    """
    Benchmark: Timeout handling performance
    Ensures timeouts work correctly and don't add overhead
    """
    orchestrator = AsyncAgentOrchestrator(
        max_concurrent=10,
        timeout_seconds=1  # 1 second timeout
    )

    # Mock API that times out
    async def slow_api(*args, **kwargs):
        await asyncio.sleep(10)  # Intentionally slow
        return mock.Mock()

    with mock.patch.object(orchestrator, 'async_client') as mock_client:
        mock_client.messages.create = slow_api

        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent def"):
            start = time.time()
            result = await orchestrator.execute_agent("python-expert", "task")
            elapsed = time.time() - start

    # Should timeout quickly (within 1.5s including overhead)
    assert elapsed < 1.5
    assert not result.success

    print(f"\n✓ Timeout triggered in: {elapsed*1000:.1f}ms")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_retry_performance():
    """
    Benchmark: Retry logic performance
    Measures overhead and exponential backoff timing
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10, max_retries=3)

    call_count = [0]
    call_times = []

    async def flaky_api(*args, **kwargs):
        call_times.append(time.time())
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError("Network error")
        # Third call succeeds
        mock_response = mock.Mock()
        mock_response.content = [mock.Mock(text="Success")]
        mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
        mock_response.model = "claude-3-5-sonnet-20241022"
        return mock_response

    with mock.patch.object(orchestrator.async_client.messages, 'create', flaky_api):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent def"):
            start = time.time()
            result = await orchestrator.execute_agent("python-expert", "task")
            elapsed = time.time() - start

    assert result.success
    assert call_count[0] == 3

    # Calculate backoff times
    if len(call_times) >= 3:
        backoff1 = call_times[1] - call_times[0]
        backoff2 = call_times[2] - call_times[1]
        print(f"\n✓ Retry succeeded after {call_count[0]} attempts in {elapsed*1000:.1f}ms")
        print(f"✓ First backoff: {backoff1*1000:.1f}ms")
        print(f"✓ Second backoff: {backoff2*1000:.1f}ms")

        # Exponential backoff should increase
        assert backoff2 > backoff1


# ============================================================================
# Task Size Performance Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_large_task_performance():
    """
    Benchmark: Performance with different task sizes
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10)

    mock_api = create_mock_api_response(delay_ms=100)

    results = {}

    with mock.patch.object(orchestrator, '_call_api_with_retry', mock_api):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent def"):
            for size in PerformanceConfig.LARGE_TASK_SIZES:
                task = "x" * size

                start = time.time()
                result = await orchestrator.execute_agent("python-expert", task)
                elapsed = time.time() - start

                results[size] = elapsed
                assert result.success

    print("\n✓ Task Size Performance:")
    for size, elapsed in results.items():
        print(f"  {size:6d} chars: {elapsed*1000:6.1f}ms")

    # Performance should not degrade significantly with larger tasks
    # (within reason, since we're just passing strings)
    max_time = max(results.values())
    min_time = min(results.values())
    ratio = max_time / min_time

    assert ratio < 1.5  # <50% variance across task sizes


# ============================================================================
# Memory Performance Tests
# ============================================================================

@pytest.mark.benchmark
def test_cache_memory_efficiency(tmp_path):
    """
    Benchmark: Memory efficiency of cache
    """
    import sys

    cache = ResponseCache(
        cache_dir=tmp_path / "cache",
        max_size_mb=10,
        cache_secret="test_secret"
    )

    # Measure memory before
    initial_entries = 0

    # Add 1000 small entries
    for i in range(1000):
        cache.set(f"agent{i}", f"task{i}", "model", "response" * 10, 100, 50, 0.001)

    entries = len(cache._memory_cache)
    cache_size_mb = cache.stats['size_bytes'] / (1024 * 1024)

    print(f"\n✓ Cache entries: {entries}")
    print(f"✓ Cache size: {cache_size_mb:.2f} MB")
    print(f"✓ Avg entry size: {cache.stats['size_bytes']/entries:.0f} bytes")

    # Should stay within memory limits
    assert cache_size_mb < 10


# ============================================================================
# End-to-End Performance Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.benchmark
@pytest.mark.slow
async def test_realistic_workflow_performance():
    """
    Benchmark: Realistic multi-agent workflow
    Simulates a typical use case with 3 sequential agents
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10)

    # Mock API with realistic delays (2-5s)
    async def realistic_api(*args, **kwargs):
        import random
        await asyncio.sleep(random.uniform(0.5, 1.0))  # 500ms-1s
        mock_response = mock.Mock()
        mock_response.content = [mock.Mock(text="Realistic response " * 100)]
        mock_response.usage = mock.Mock(input_tokens=500, output_tokens=300)
        mock_response.model = "claude-3-5-sonnet-20241022"
        return mock_response

    workflow_agents = [
        ("python-expert", "Analyze code"),
        ("code-reviewer", "Review implementation"),
        ("bug-investigator", "Check for issues")
    ]

    with mock.patch.object(orchestrator, '_call_api_with_retry', realistic_api):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent def"):
            # Sequential workflow
            sequential_start = time.time()
            for agent_name, task in workflow_agents:
                result = await orchestrator.execute_agent(agent_name, task)
                assert result.success
            sequential_time = time.time() - sequential_start

            # Concurrent workflow (if agents are independent)
            concurrent_start = time.time()
            results = await orchestrator.execute_multiple(workflow_agents)
            concurrent_time = time.time() - concurrent_start

            assert len(results) == 3
            assert all(r.success for r in results)

    speedup = sequential_time / concurrent_time

    print(f"\n✓ Realistic Workflow:")
    print(f"  Sequential: {sequential_time:.2f}s")
    print(f"  Concurrent: {concurrent_time:.2f}s")
    print(f"  Speedup: {speedup:.2f}x")

    # Should see significant speedup for independent agents
    assert speedup >= 2.0


# ============================================================================
# Performance Summary
# ============================================================================

@pytest.mark.benchmark
def test_performance_summary():
    """
    Display performance test summary
    """
    print("\n" + "=" * 80)
    print("PERFORMANCE OPTIMIZATION - BENCHMARK SUMMARY")
    print("=" * 80)
    print("\nExpected Performance Gains (from optimization plan):")
    print("  • Sequential 3 agents: 12-30s (baseline)")
    print("  • Concurrent 3 agents: 4-10s (2-3x faster)")
    print("  • Cached response: <50ms (40-200x faster)")
    print("\nTargets:")
    print("  • Cache hit: <1ms")
    print("  • Concurrent speedup: 2.5x+")
    print("  • Single agent overhead: <10ms")
    print("=" * 80)
