"""
Load testing suite for Claude Force performance optimization.

These tests simulate real-world load scenarios to validate
scalability and identify bottlenecks.

Run with: pytest tests/test_performance_load.py -v -s --durations=0
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Tuple
from unittest import mock
import statistics
import concurrent.futures

from claude_force.async_orchestrator import AsyncAgentOrchestrator
from claude_force.response_cache import ResponseCache


# ============================================================================
# Load Test Configuration
# ============================================================================


class LoadTestConfig:
    """Configuration for load tests"""

    # Light load
    LIGHT_USERS = 5
    LIGHT_DURATION_SECONDS = 10

    # Medium load
    MEDIUM_USERS = 20
    MEDIUM_DURATION_SECONDS = 30

    # Heavy load
    HEAVY_USERS = 50
    HEAVY_DURATION_SECONDS = 60

    # Stress test
    STRESS_USERS = 100
    STRESS_DURATION_SECONDS = 30

    # Throughput targets
    MIN_THROUGHPUT_PER_SECOND = 5  # Minimum requests/second


# ============================================================================
# Load Test Helpers
# ============================================================================


def create_mock_api_with_latency(min_ms: int = 50, max_ms: int = 200):
    """Create mock API with variable latency"""
    import random

    async def mock_api(*args, **kwargs):
        # Simulate variable API latency
        delay = random.randint(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)

        mock_response = mock.Mock()
        mock_response.content = [mock.Mock(text=f"Response at {time.time()}")]
        mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
        mock_response.model = "claude-3-5-sonnet-20241022"
        return mock_response

    return mock_api


class LoadTestMetrics:
    """Collect and analyze load test metrics"""

    def __init__(self):
        self.request_times = []
        self.success_count = 0
        self.failure_count = 0
        self.start_time = None
        self.end_time = None

    def record_request(self, duration: float, success: bool):
        """Record a request"""
        self.request_times.append(duration)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def get_summary(self):
        """Get summary statistics"""
        if not self.request_times:
            return {}

        total_time = (self.end_time - self.start_time) if self.start_time else 0
        total_requests = self.success_count + self.failure_count

        return {
            "total_requests": total_requests,
            "successful": self.success_count,
            "failed": self.failure_count,
            "success_rate": self.success_count / total_requests if total_requests > 0 else 0,
            "throughput": total_requests / total_time if total_time > 0 else 0,
            "avg_response_time": statistics.mean(self.request_times),
            "median_response_time": statistics.median(self.request_times),
            "p95_response_time": (
                statistics.quantiles(self.request_times, n=20)[18]
                if len(self.request_times) > 20
                else max(self.request_times)
            ),
            "p99_response_time": (
                statistics.quantiles(self.request_times, n=100)[98]
                if len(self.request_times) > 100
                else max(self.request_times)
            ),
            "min_response_time": min(self.request_times),
            "max_response_time": max(self.request_times),
            "duration": total_time,
        }

    def print_summary(self, test_name: str):
        """Print formatted summary"""
        summary = self.get_summary()
        if not summary:
            print(f"\n{test_name}: No data collected")
            return

        print(f"\n{'=' * 80}")
        print(f"{test_name}")
        print(f"{'=' * 80}")
        print(f"Duration:        {summary['duration']:.2f}s")
        print(f"Total Requests:  {summary['total_requests']}")
        print(f"Successful:      {summary['successful']} ({summary['success_rate']:.1%})")
        print(f"Failed:          {summary['failed']}")
        print(f"Throughput:      {summary['throughput']:.2f} req/s")
        print(f"\nResponse Times:")
        print(f"  Average:       {summary['avg_response_time']*1000:.1f}ms")
        print(f"  Median:        {summary['median_response_time']*1000:.1f}ms")
        print(f"  95th percentile: {summary['p95_response_time']*1000:.1f}ms")
        print(f"  99th percentile: {summary['p99_response_time']*1000:.1f}ms")
        print(f"  Min:           {summary['min_response_time']*1000:.1f}ms")
        print(f"  Max:           {summary['max_response_time']*1000:.1f}ms")
        print(f"{'=' * 80}\n")

        return summary


# ============================================================================
# Cache Load Tests
# ============================================================================


@pytest.mark.load
def test_cache_concurrent_read_load(tmp_path):
    """
    Load Test: Concurrent cache reads
    Validates that cache can handle many simultaneous reads
    """
    cache = ResponseCache(cache_dir=tmp_path / "cache", max_size_mb=100, cache_secret="test_secret")

    # Pre-populate cache
    for i in range(100):
        cache.set(f"agent{i}", f"task{i}", "model", f"response{i}" * 100, 100, 50, 0.001)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    def read_cache(task_id: int):
        """Read from cache"""
        start = time.time()
        result = cache.get(f"agent{task_id % 100}", f"task{task_id % 100}", "model")
        duration = time.time() - start
        metrics.record_request(duration, result is not None)

    # Simulate 1000 concurrent reads
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(read_cache, i) for i in range(1000)]
        concurrent.futures.wait(futures)

    metrics.end_time = time.time()
    summary = metrics.print_summary("Cache Concurrent Read Load Test")

    # Assertions
    assert summary["success_rate"] == 1.0  # All reads should succeed
    assert summary["throughput"] > LoadTestConfig.MIN_THROUGHPUT_PER_SECOND


@pytest.mark.load
def test_cache_concurrent_write_load(tmp_path):
    """
    Load Test: Concurrent cache writes
    Validates cache can handle concurrent writes without corruption
    """
    cache = ResponseCache(cache_dir=tmp_path / "cache", max_size_mb=100, cache_secret="test_secret")

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    def write_cache(task_id: int):
        """Write to cache"""
        start = time.time()
        try:
            cache.set(
                f"agent{task_id}",
                f"task{task_id}",
                "model",
                f"response{task_id}" * 100,
                100,
                50,
                0.001,
            )
            duration = time.time() - start
            metrics.record_request(duration, True)
        except Exception as e:
            duration = time.time() - start
            metrics.record_request(duration, False)

    # Simulate 500 concurrent writes
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(write_cache, i) for i in range(500)]
        concurrent.futures.wait(futures)

    metrics.end_time = time.time()
    summary = metrics.print_summary("Cache Concurrent Write Load Test")

    # Verify cache integrity
    stats = cache.get_stats()
    print(f"Cache entries: {stats['entries']}")
    print(f"Integrity failures: {stats['integrity_failures']}")

    # Assertions
    assert summary["success_rate"] > 0.95  # >95% success rate
    assert stats["integrity_failures"] == 0  # No integrity failures


@pytest.mark.load
def test_cache_mixed_load(tmp_path):
    """
    Load Test: Mixed read/write load
    Simulates realistic cache usage pattern
    """
    cache = ResponseCache(cache_dir=tmp_path / "cache", max_size_mb=100, cache_secret="test_secret")

    # Pre-populate some entries
    for i in range(50):
        cache.set(f"agent{i}", f"task{i}", "model", f"response{i}" * 100, 100, 50, 0.001)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    def mixed_operation(task_id: int):
        """Perform mixed read/write"""
        import random

        start = time.time()

        try:
            # 70% reads, 30% writes
            if random.random() < 0.7:
                result = cache.get(f"agent{task_id % 50}", f"task{task_id % 50}", "model")
                success = result is not None
            else:
                cache.set(
                    f"agent{task_id}",
                    f"task{task_id}",
                    "model",
                    f"response{task_id}" * 100,
                    100,
                    50,
                    0.001,
                )
                success = True

            duration = time.time() - start
            metrics.record_request(duration, success)
        except Exception as e:
            duration = time.time() - start
            metrics.record_request(duration, False)

    # Simulate 1000 mixed operations
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(mixed_operation, i) for i in range(1000)]
        concurrent.futures.wait(futures)

    metrics.end_time = time.time()
    summary = metrics.print_summary("Cache Mixed Load Test")

    # Assertions
    assert summary["success_rate"] > 0.95


# ============================================================================
# Async Orchestrator Load Tests
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.load
async def test_async_light_load():
    """
    Load Test: Light load (5 concurrent users)
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10)
    mock_api = create_mock_api_with_latency(50, 150)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    async def user_session(user_id: int):
        """Simulate a user making requests"""
        with mock.patch.object(orchestrator, "_call_api_with_retry", mock_api):
            with mock.patch.object(orchestrator, "load_agent_definition", return_value="Agent def"):
                for _ in range(5):  # 5 requests per user
                    start = time.time()
                    result = await orchestrator.execute_agent(
                        "python-expert", f"task from user {user_id}"
                    )
                    duration = time.time() - start
                    metrics.record_request(duration, result.success)
                    await asyncio.sleep(0.1)  # Small delay between requests

    # Run light load test
    await asyncio.gather(*[user_session(i) for i in range(LoadTestConfig.LIGHT_USERS)])

    metrics.end_time = time.time()
    summary = metrics.print_summary("Light Load Test (5 users)")

    # Assertions
    assert summary["success_rate"] > 0.98  # >98% success under light load
    assert summary["avg_response_time"] < 0.3  # <300ms average


@pytest.mark.asyncio
@pytest.mark.load
async def test_async_medium_load():
    """
    Load Test: Medium load (20 concurrent users)
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=10)
    mock_api = create_mock_api_with_latency(50, 200)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    async def user_session(user_id: int):
        """Simulate a user making requests"""
        with mock.patch.object(orchestrator, "_call_api_with_retry", mock_api):
            with mock.patch.object(orchestrator, "load_agent_definition", return_value="Agent def"):
                for _ in range(3):  # 3 requests per user
                    start = time.time()
                    result = await orchestrator.execute_agent(
                        "python-expert", f"task from user {user_id}"
                    )
                    duration = time.time() - start
                    metrics.record_request(duration, result.success)
                    await asyncio.sleep(0.2)

    # Run medium load test
    await asyncio.gather(*[user_session(i) for i in range(LoadTestConfig.MEDIUM_USERS)])

    metrics.end_time = time.time()
    summary = metrics.print_summary("Medium Load Test (20 users)")

    # Assertions
    assert summary["success_rate"] > 0.95  # >95% success under medium load
    assert summary["avg_response_time"] < 0.5  # <500ms average


@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.slow
async def test_async_heavy_load():
    """
    Load Test: Heavy load (50 concurrent users)
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=20)
    mock_api = create_mock_api_with_latency(100, 300)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    async def user_session(user_id: int):
        """Simulate a user making requests"""
        with mock.patch.object(orchestrator, "_call_api_with_retry", mock_api):
            with mock.patch.object(orchestrator, "load_agent_definition", return_value="Agent def"):
                for _ in range(2):  # 2 requests per user
                    start = time.time()
                    result = await orchestrator.execute_agent(
                        "python-expert", f"task from user {user_id}"
                    )
                    duration = time.time() - start
                    metrics.record_request(duration, result.success)
                    await asyncio.sleep(0.3)

    # Run heavy load test
    await asyncio.gather(*[user_session(i) for i in range(LoadTestConfig.HEAVY_USERS)])

    metrics.end_time = time.time()
    summary = metrics.print_summary("Heavy Load Test (50 users)")

    # Assertions
    assert summary["success_rate"] > 0.90  # >90% success under heavy load


@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.slow
async def test_async_stress_test():
    """
    Stress Test: Very heavy load (100 concurrent users)
    Tests system limits and degradation
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=30)
    mock_api = create_mock_api_with_latency(100, 400)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    async def user_session(user_id: int):
        """Simulate a user making requests"""
        with mock.patch.object(orchestrator, "_call_api_with_retry", mock_api):
            with mock.patch.object(orchestrator, "load_agent_definition", return_value="Agent def"):
                start = time.time()
                try:
                    result = await orchestrator.execute_agent(
                        "python-expert", f"task from user {user_id}"
                    )
                    duration = time.time() - start
                    metrics.record_request(duration, result.success)
                except Exception as e:
                    duration = time.time() - start
                    metrics.record_request(duration, False)

    # Run stress test
    await asyncio.gather(*[user_session(i) for i in range(LoadTestConfig.STRESS_USERS)])

    metrics.end_time = time.time()
    summary = metrics.print_summary("Stress Test (100 users)")

    # More lenient assertions for stress test
    assert summary["success_rate"] > 0.80  # >80% success even under stress


# ============================================================================
# Sustained Load Tests
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.slow
async def test_sustained_load():
    """
    Load Test: Sustained load over time
    Validates system can maintain performance over extended period
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=15)
    mock_api = create_mock_api_with_latency(50, 150)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()

    duration = 30  # 30 seconds
    users = 10

    async def sustained_user(user_id: int, duration: int):
        """User making requests for duration"""
        end_time = time.time() + duration

        with mock.patch.object(orchestrator, "_call_api_with_retry", mock_api):
            with mock.patch.object(orchestrator, "load_agent_definition", return_value="Agent def"):
                while time.time() < end_time:
                    start = time.time()
                    result = await orchestrator.execute_agent(
                        "python-expert", f"task from user {user_id}"
                    )
                    request_duration = time.time() - start
                    metrics.record_request(request_duration, result.success)
                    await asyncio.sleep(1)  # 1 request per second per user

    await asyncio.gather(*[sustained_user(i, duration) for i in range(users)])

    metrics.end_time = time.time()
    summary = metrics.print_summary(f"Sustained Load Test ({duration}s, {users} users)")

    # Assertions
    assert summary["success_rate"] > 0.95
    assert summary["throughput"] >= users * 0.8  # ~0.8-1 req/s per user


# ============================================================================
# Ramp-Up Test
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.load
@pytest.mark.slow
async def test_ramp_up_load():
    """
    Load Test: Gradual ramp-up
    Tests how system handles increasing load
    """
    orchestrator = AsyncAgentOrchestrator(max_concurrent=20)
    mock_api = create_mock_api_with_latency(50, 150)

    metrics_by_level = {}

    async def load_level(level: int, users: int):
        """Run a load level"""
        print(f"\nRamp-up Level {level}: {users} users")

        metrics = LoadTestMetrics()
        metrics.start_time = time.time()

        async def user_task(user_id: int):
            with mock.patch.object(orchestrator, "_call_api_with_retry", mock_api):
                with mock.patch.object(
                    orchestrator, "load_agent_definition", return_value="Agent def"
                ):
                    start = time.time()
                    result = await orchestrator.execute_agent(
                        "python-expert", f"task from user {user_id}"
                    )
                    duration = time.time() - start
                    metrics.record_request(duration, result.success)

        await asyncio.gather(*[user_task(i) for i in range(users)])

        metrics.end_time = time.time()
        summary = metrics.get_summary()
        metrics_by_level[users] = summary

        print(f"  Success rate: {summary['success_rate']:.1%}")
        print(f"  Avg response: {summary['avg_response_time']*1000:.1f}ms")
        print(f"  Throughput: {summary['throughput']:.2f} req/s")

    # Ramp up: 5 -> 10 -> 20 -> 40 users
    for users in [5, 10, 20, 40]:
        await load_level(users // 5, users)
        await asyncio.sleep(1)  # Small pause between levels

    print(f"\n{'=' * 80}")
    print("Ramp-Up Test Summary")
    print(f"{'=' * 80}")
    for users, summary in metrics_by_level.items():
        degradation = (
            summary["avg_response_time"] / metrics_by_level[5]["avg_response_time"] - 1
        ) * 100
        print(
            f"{users:2d} users: {summary['success_rate']:.1%} success, "
            f"{summary['avg_response_time']*1000:5.1f}ms avg "
            f"({degradation:+.0f}% vs baseline)"
        )

    # Performance should not degrade linearly with load
    # due to concurrency benefits
    baseline = metrics_by_level[5]["avg_response_time"]
    heavy = metrics_by_level[40]["avg_response_time"]
    degradation_ratio = heavy / baseline

    assert degradation_ratio < 4  # <4x slowdown at 8x load


# ============================================================================
# Cache Hit Rate Under Load
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.load
async def test_cache_hit_rate_under_load(tmp_path):
    """
    Load Test: Cache effectiveness under realistic load
    """
    cache = ResponseCache(cache_dir=tmp_path / "cache", max_size_mb=100, cache_secret="test_secret")

    # Simulate realistic access pattern (Zipf distribution)
    # Some tasks are very popular, most are rare
    import random

    popular_tasks = [f"popular_task_{i}" for i in range(10)]
    rare_tasks = [f"rare_task_{i}" for i in range(1000)]

    def get_task():
        """Get task with Zipf distribution"""
        if random.random() < 0.7:  # 70% hit popular tasks
            return random.choice(popular_tasks)
        else:
            return random.choice(rare_tasks)

    metrics = LoadTestMetrics()
    metrics.start_time = time.time()
    cache_hits = 0
    cache_misses = 0

    async def user_requests(user_id: int):
        nonlocal cache_hits, cache_misses

        for _ in range(20):  # 20 requests per user
            task = get_task()

            start = time.time()

            # Check cache
            cached = cache.get("agent", task, "model")
            if cached:
                cache_hits += 1
            else:
                cache_misses += 1
                # Simulate API call and cache
                await asyncio.sleep(0.1)  # 100ms API call
                cache.set("agent", task, "model", f"response for {task}", 100, 50, 0.001)

            duration = time.time() - start
            metrics.record_request(duration, True)

    # Run load test with 20 users
    await asyncio.gather(*[user_requests(i) for i in range(20)])

    metrics.end_time = time.time()
    summary = metrics.print_summary("Cache Hit Rate Under Load Test")

    cache_stats = cache.get_stats()
    hit_rate = cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0

    print(f"\nCache Performance:")
    print(f"  Total requests: {cache_hits + cache_misses}")
    print(f"  Cache hits: {cache_hits} ({hit_rate:.1%})")
    print(f"  Cache misses: {cache_misses}")
    print(f"  Cache entries: {cache_stats['entries']}")

    # Should achieve good hit rate on popular tasks
    assert hit_rate > 0.4  # >40% hit rate with Zipf distribution


# ============================================================================
# Load Test Summary
# ============================================================================


@pytest.mark.load
def test_load_test_summary():
    """
    Display load test summary and recommendations
    """
    print("\n" + "=" * 80)
    print("LOAD TESTING - SUMMARY")
    print("=" * 80)
    print("\nLoad Test Scenarios:")
    print("  • Light:     5 users,  5 req/user  (25 total)")
    print("  • Medium:   20 users,  3 req/user  (60 total)")
    print("  • Heavy:    50 users,  2 req/user  (100 total)")
    print("  • Stress:  100 users,  1 req/user  (100 total)")
    print("  • Sustained: 10 users, 30s continuous")
    print("  • Ramp-up:  5→10→20→40 users")
    print("\nSuccess Rate Targets:")
    print("  • Light load:  >98%")
    print("  • Medium load: >95%")
    print("  • Heavy load:  >90%")
    print("  • Stress:      >80%")
    print("\nPerformance Targets:")
    print("  • Throughput: >5 req/s")
    print("  • P95 latency: <500ms (under normal load)")
    print("  • Cache hit rate: >40% (Zipf distribution)")
    print("=" * 80)
