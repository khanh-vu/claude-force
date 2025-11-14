"""
Tests for AsyncAgentOrchestrator with all edge cases from expert review.

Tests cover:
- ✅ Basic async execution
- ✅ Concurrent execution
- ✅ Input validation (invalid agent names, oversized tasks)
- ✅ Timeout handling
- ✅ Concurrency limits
- ✅ Retry logic
- ✅ Error handling
"""
import pytest
import asyncio
from unittest import mock
from pathlib import Path
from typing import List, Tuple

from claude_force.async_orchestrator import AsyncAgentOrchestrator, AsyncAgentResult


# ============================================================================
# Basic Functionality Tests
# ============================================================================

@pytest.mark.asyncio
async def test_async_execute_agent():
    """Test basic async agent execution."""
    orchestrator = AsyncAgentOrchestrator(
        config_path=Path(".claude/claude.json")
    )

    # Mock the API call
    mock_response = mock.Mock()
    mock_response.content = [mock.Mock(text="Test response")]
    mock_response.usage = mock.Mock(
        input_tokens=100,
        output_tokens=50
    )
    mock_response.model = "claude-3-5-sonnet-20241022"

    with mock.patch.object(orchestrator, '_call_api_with_retry', return_value=mock_response):
        result = await orchestrator.execute_agent("python-expert", "What are decorators?")

    assert result.success is True
    assert result.output == "Test response"
    assert result.metadata['input_tokens'] == 100
    assert result.metadata['output_tokens'] == 50


@pytest.mark.asyncio
async def test_concurrent_execution():
    """Test concurrent agent execution with multiple tasks."""
    orchestrator = AsyncAgentOrchestrator(
        config_path=Path(".claude/claude.json"),
        max_concurrent=3
    )

    tasks: List[Tuple[str, str]] = [
        ("python-expert", "Explain lists"),
        ("python-expert", "Explain dicts"),
        ("python-expert", "Explain sets")
    ]

    # Mock the API call
    mock_response = mock.Mock()
    mock_response.content = [mock.Mock(text="Test response")]
    mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
    mock_response.model = "claude-3-5-sonnet-20241022"

    with mock.patch.object(orchestrator, '_call_api_with_retry', return_value=mock_response):
        import time
        start = time.time()
        results = await orchestrator.execute_multiple(tasks)
        elapsed = time.time() - start

    assert len(results) == 3
    assert all(isinstance(r, AsyncAgentResult) for r in results)
    assert all(r.success for r in results)

    # Concurrent execution should be faster than sequential
    print(f"Concurrent execution: {elapsed:.2f}s")


# ============================================================================
# Input Validation Tests (✅ NEW from expert review)
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_agent_name():
    """Test that invalid agent names are rejected."""
    orchestrator = AsyncAgentOrchestrator()

    # Test path traversal attempt
    with pytest.raises(ValueError, match="Invalid agent name"):
        await orchestrator.execute_agent("../../etc/passwd", "task")

    # Test special characters
    with pytest.raises(ValueError, match="Invalid agent name"):
        await orchestrator.execute_agent("agent; rm -rf /", "task")

    # Test SQL injection attempt
    with pytest.raises(ValueError, match="Invalid agent name"):
        await orchestrator.execute_agent("agent' OR '1'='1", "task")


@pytest.mark.asyncio
async def test_task_too_large():
    """Test that oversized tasks are rejected."""
    orchestrator = AsyncAgentOrchestrator()

    # Create task larger than 100K chars
    large_task = "x" * 200_000

    with pytest.raises(ValueError, match="Task too large"):
        await orchestrator.execute_agent("python-expert", large_task)


@pytest.mark.asyncio
async def test_valid_agent_names():
    """Test that valid agent names are accepted."""
    orchestrator = AsyncAgentOrchestrator()

    # Mock the API to avoid actual calls
    mock_response = mock.Mock()
    mock_response.content = [mock.Mock(text="Test response")]
    mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
    mock_response.model = "claude-3-5-sonnet-20241022"

    valid_names = [
        "python-expert",
        "code_reviewer",
        "agent123",
        "my-agent_v2"
    ]

    with mock.patch.object(orchestrator, '_call_api_with_retry', return_value=mock_response):
        for name in valid_names:
            # Should not raise
            with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent definition"):
                result = await orchestrator.execute_agent(name, "test task")
                assert result.success is True


# ============================================================================
# Timeout Tests (✅ NEW from expert review)
# ============================================================================

@pytest.mark.asyncio
async def test_timeout_protection():
    """Test that operations timeout correctly."""
    orchestrator = AsyncAgentOrchestrator(timeout_seconds=1, enable_cache=False)

    # Mock slow API call
    async def slow_response(*args, **kwargs):
        await asyncio.sleep(10)  # Sleep longer than timeout
        return mock.Mock()

    with mock.patch.object(orchestrator.async_client.messages, 'create', side_effect=slow_response):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent definition"):
            result = await orchestrator.execute_agent("python-expert", "unique-timeout-test-task")

            # Should fail due to timeout
            assert result.success is False
            assert result.errors is not None
            # Check for timeout in error message (could be "timeout" or "timed out")
            assert any("time" in str(e).lower() and "out" in str(e).lower() for e in result.errors)


@pytest.mark.asyncio
async def test_configurable_timeout():
    """Test that timeout is configurable."""
    orchestrator = AsyncAgentOrchestrator(timeout_seconds=5)

    assert orchestrator.timeout_seconds == 5

    # Update timeout
    orchestrator.timeout_seconds = 10
    assert orchestrator.timeout_seconds == 10


# ============================================================================
# Concurrency Limit Tests (✅ NEW from expert review)
# ============================================================================

@pytest.mark.asyncio
async def test_concurrency_limit():
    """Test that semaphore limits concurrency."""
    orchestrator = AsyncAgentOrchestrator(max_concurrent=2)

    # Track concurrent executions
    concurrent_count = 0
    max_concurrent = 0
    lock = asyncio.Lock()

    async def tracked_execute(agent, task, **kwargs):
        nonlocal concurrent_count, max_concurrent

        async with lock:
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)

        # Simulate work
        await asyncio.sleep(0.1)

        async with lock:
            concurrent_count -= 1

        # Return mock result
        return AsyncAgentResult(
            agent_name=agent,
            success=True,
            output="result",
            metadata={}
        )

    # Patch execute_agent to use our tracked version
    with mock.patch.object(orchestrator, 'execute_agent', tracked_execute):
        tasks: List[Tuple[str, str]] = [
            ("agent", f"task{i}") for i in range(10)
        ]
        results = await orchestrator.execute_multiple(tasks)

    assert len(results) == 10
    assert all(r.success for r in results)
    # Max concurrent should not exceed semaphore limit
    assert max_concurrent <= 2
    print(f"Max concurrent executions: {max_concurrent}")


@pytest.mark.asyncio
async def test_semaphore_initialization():
    """Test that semaphore is properly initialized."""
    orchestrator = AsyncAgentOrchestrator(max_concurrent=5)

    # Semaphore should be lazy-loaded
    assert orchestrator._semaphore is None

    # Access should create it (using async method now)
    semaphore = await orchestrator._get_semaphore()
    assert semaphore is not None
    assert semaphore._value == 5


# ============================================================================
# Retry Logic Tests (✅ NEW from expert review)
# ============================================================================

@pytest.mark.asyncio
async def test_retry_on_transient_failure():
    """Test that transient failures are retried."""
    orchestrator = AsyncAgentOrchestrator(max_retries=3)

    # Mock API that fails twice then succeeds
    call_count = 0

    async def flaky_api(*args, **kwargs):
        nonlocal call_count
        call_count += 1

        if call_count < 3:
            raise ConnectionError("Network error")

        # Third call succeeds
        mock_response = mock.Mock()
        mock_response.content = [mock.Mock(text="Success")]
        mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
        mock_response.model = "claude-3-5-sonnet-20241022"
        return mock_response

    with mock.patch.object(orchestrator.async_client.messages, 'create', side_effect=flaky_api):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent definition"):
            result = await orchestrator.execute_agent("python-expert", "task")

    assert call_count == 3  # Should have retried twice
    assert result.success is True


@pytest.mark.asyncio
async def test_retry_exhaustion():
    """Test that retry logic gives up after max attempts."""
    orchestrator = AsyncAgentOrchestrator(max_retries=2, enable_cache=False)

    # Mock API that always fails
    async def always_fail(*args, **kwargs):
        raise ConnectionError("Network error")

    with mock.patch.object(orchestrator.async_client.messages, 'create', side_effect=always_fail):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent definition"):
            result = await orchestrator.execute_agent("python-expert", "unique-retry-exhaustion-task")

    assert result.success is False
    assert result.errors is not None


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_agent_not_found():
    """Test handling of non-existent agent."""
    orchestrator = AsyncAgentOrchestrator()

    result = await orchestrator.execute_agent("nonexistent-agent", "task")

    assert result.success is False
    assert result.errors is not None
    assert any("not found" in str(e).lower() for e in result.errors)


@pytest.mark.asyncio
async def test_api_error_handling():
    """Test handling of API errors."""
    orchestrator = AsyncAgentOrchestrator(enable_cache=False)

    # Mock API error
    async def api_error(*args, **kwargs):
        raise Exception("API Error: Rate limit exceeded")

    with mock.patch.object(orchestrator, '_call_api_with_retry', side_effect=api_error):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent definition"):
            result = await orchestrator.execute_agent("python-expert", "unique-api-error-task")

    assert result.success is False
    assert result.errors is not None
    assert "Rate limit exceeded" in result.errors[0]


@pytest.mark.asyncio
async def test_performance_tracking():
    """Test that performance is tracked."""
    orchestrator = AsyncAgentOrchestrator(enable_tracking=True, enable_cache=False)

    # Mock the API call
    mock_response = mock.Mock()
    mock_response.content = [mock.Mock(text="Test response")]
    mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
    mock_response.model = "claude-3-5-sonnet-20241022"

    with mock.patch.object(orchestrator, '_call_api_with_retry', return_value=mock_response):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent definition"):
            # Mock the performance tracking
            with mock.patch.object(orchestrator, '_track_performance_async') as mock_track:
                result = await orchestrator.execute_agent("python-expert", "unique-tracking-task")

                # Should have called tracking
                assert mock_track.called
                call_args = mock_track.call_args[1]
                assert call_args['agent_name'] == "python-expert"
                assert call_args['success'] is True
                assert 'execution_time_ms' in call_args


# ============================================================================
# Resource Cleanup Tests
# ============================================================================

@pytest.mark.asyncio
async def test_client_cleanup():
    """Test that async client is properly cleaned up."""
    orchestrator = AsyncAgentOrchestrator()

    # Initialize client
    _ = orchestrator.async_client

    assert orchestrator._async_client is not None

    # Close
    await orchestrator.close()

    assert orchestrator._async_client is None


# ============================================================================
# Python 3.8 Compatibility Tests
# ============================================================================

def test_type_hints_compatibility():
    """Test that type hints are Python 3.8 compatible."""
    import inspect
    from typing import get_type_hints

    # Get type hints for execute_multiple
    hints = get_type_hints(AsyncAgentOrchestrator.execute_multiple)

    # Should work without errors (Python 3.8+ compatible)
    assert 'tasks' in hints
    assert 'return' in hints


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_workflow():
    """Integration test for complete workflow."""
    orchestrator = AsyncAgentOrchestrator(
        max_concurrent=2,
        timeout_seconds=30,
        enable_tracking=True
    )

    tasks: List[Tuple[str, str]] = [
        ("python-expert", "What are decorators?"),
        ("code-reviewer", "Review: def foo(): pass")
    ]

    # Mock API responses
    mock_response = mock.Mock()
    mock_response.content = [mock.Mock(text="Test response")]
    mock_response.usage = mock.Mock(input_tokens=100, output_tokens=50)
    mock_response.model = "claude-3-5-sonnet-20241022"

    with mock.patch.object(orchestrator, '_call_api_with_retry', return_value=mock_response):
        with mock.patch.object(orchestrator, 'load_agent_definition', return_value="Agent definition"):
            results = await orchestrator.execute_multiple(tasks)

    assert len(results) == 2
    assert all(r.success for r in results)

    await orchestrator.close()
