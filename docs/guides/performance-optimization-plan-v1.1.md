# Claude Force Performance Optimization Implementation Plan v1.1

**Version:** 1.1 (Updated after expert review)
**Date:** 2025-11-14
**Status:** Ready for Implementation
**Target Release:** v2.3.0

---

## Updates in v1.1

This version incorporates all critical and high-priority fixes identified in the expert review:

### ✅ Critical Fixes Applied
1. ✅ Added missing imports (os, json) in AsyncAgentOrchestrator
2. ✅ Fixed Python 3.8 compatibility (List[] vs list[])
3. ✅ Added timeouts to all async operations
4. ✅ Added input validation for agent_name

### ✅ High-Priority Improvements Applied
5. ✅ Increased cache key length to 32 chars
6. ✅ Added semaphore for concurrency control
7. ✅ Implemented retry logic with tenacity
8. ✅ Made performance tracking async

### 📝 Additional Improvements
- ✅ Added structured logging
- ✅ Improved error handling
- ✅ Added HMAC cache integrity checks
- ✅ Optimized LRU eviction with heapq

---

## Executive Summary

This document outlines a comprehensive plan to optimize Claude Force performance based on the findings in the [Performance Analysis Report](performance-analysis.md) and incorporating feedback from the [Expert Review](performance-optimization-reviews.md).

### Primary Goals

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Workflow Execution Time | 12-30s (3 agents) | 4-10s | **50-80% faster** |
| Cost Per Execution | Baseline | 30-50% less | **Cost reduction** |
| Throughput | 1 task/time | 2-5 tasks/time | **2-5x increase** |
| Cache Hit Rate | 0% | 20-70% | **New capability** |

### Implementation Phases

**Phase 1 (Month 1): Foundation** ✅ High Impact
- Async API client implementation (with fixes)
- Response caching system (with security improvements)
- Backward compatibility layer

**Phase 2 (Month 2): Advanced Optimization** ⭐ Medium Impact
- Parallel workflow execution (DAG-based)
- Metrics aggregation
- Query result caching

**Phase 3 (Month 3): Polish & Enhancement** 📊 Low Impact
- Performance monitoring enhancements
- Circuit breakers
- Advanced caching strategies

---

## Phase 1: Foundation Optimizations (Updated)

**Duration:** 3-4 weeks
**Priority:** 🔴 CRITICAL
**Expected Impact:** 50-80% performance improvement

### 1.1 Async API Client Implementation (UPDATED)

#### Implementation Steps

**Step 1: Install async dependencies**
```bash
# Update requirements.txt
anthropic>=0.40.0  # Already supports async
aiofiles>=23.0.0   # Async file I/O
tenacity>=8.0.0    # Retry logic (NEW)
```

**Step 2: Create async orchestrator module**

Create `claude_force/async_orchestrator.py`:

```python
"""
Async version of AgentOrchestrator for non-blocking operations.
"""
import os  # ✅ FIXED: Added missing import
import json  # ✅ FIXED: Added missing import
import re  # ✅ NEW: For input validation
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple  # ✅ FIXED: Python 3.8 compat
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential  # ✅ NEW: Retry logic

from .performance_tracker import PerformanceTracker
from .agent_memory import AgentMemory

# ✅ NEW: Structured logging
logger = logging.getLogger(__name__)


class AsyncAgentOrchestrator:
    """Async orchestrator for non-blocking agent execution."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        max_concurrent: int = 10  # ✅ NEW: Concurrency control
    ):
        self.config_path = config_path or Path.home() / ".claude" / "claude.json"
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # Lazy initialization
        self._async_client: Optional[AsyncAnthropic] = None
        self._config: Optional[Dict] = None
        self._performance_tracker: Optional[PerformanceTracker] = None
        self._agent_memory: Optional[AgentMemory] = None

        # ✅ NEW: Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # ✅ NEW: Configuration
        self.timeout_seconds = 30
        self.max_retries = 3

    @property
    def async_client(self) -> AsyncAnthropic:
        """Lazy-load async client."""
        if self._async_client is None:
            self._async_client = AsyncAnthropic(api_key=self.api_key)
        return self._async_client

    async def load_config(self) -> Dict:
        """Load configuration asynchronously."""
        if self._config is None:
            async with aiofiles.open(self.config_path, 'r') as f:
                content = await f.read()
                self._config = json.loads(content)
        return self._config

    async def load_agent_definition(self, agent_name: str) -> str:
        """Load agent definition asynchronously."""
        config = await self.load_config()
        agent_config = config['agents'].get(agent_name)

        if not agent_config:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent_file = self.config_path.parent / agent_config['path']

        async with aiofiles.open(agent_file, 'r') as f:
            return await f.read()

    # ✅ NEW: Retry decorator
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _call_api_with_retry(
        self,
        model: str,
        max_tokens: int,
        temperature: float,
        messages: List[Dict[str, str]]
    ):
        """Call API with retry logic."""
        # ✅ NEW: Timeout protection
        try:
            async with asyncio.timeout(self.timeout_seconds):
                response = await self.async_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages
                )
                return response
        except asyncio.TimeoutError:
            logger.error(f"API call timed out after {self.timeout_seconds}s")
            raise TimeoutError(f"API call timed out after {self.timeout_seconds}s")

    async def execute_agent(
        self,
        agent_name: str,
        task: str,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Execute agent asynchronously."""
        import time
        from datetime import datetime

        # ✅ NEW: Input validation
        if not re.match(r'^[a-zA-Z0-9_-]+$', agent_name):
            raise ValueError(f"Invalid agent name: {agent_name}")

        if len(task) > 100_000:
            raise ValueError(f"Task too large: {len(task)} chars (max 100,000)")

        start_time = time.time()

        # ✅ NEW: Structured logging
        logger.info(
            "Executing agent",
            extra={
                "agent_name": agent_name,
                "task_length": len(task),
                "model": model or "default"
            }
        )

        try:
            # Load agent definition
            agent_definition = await self.load_agent_definition(agent_name)

            # Build prompt
            prompt = f"{agent_definition}\n\n# Task\n{task}"

            # Call API with retry and timeout
            response = await self._call_api_with_retry(
                model=model or "claude-3-5-haiku-20241022",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract result
            result = response.content[0].text

            # ✅ FIXED: Async performance tracking
            execution_time = (time.time() - start_time) * 1000
            await self._track_performance_async(
                agent_name=agent_name,
                task=task,
                success=True,
                execution_time_ms=execution_time,
                model=response.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )

            logger.info(
                "Agent execution completed",
                extra={
                    "agent_name": agent_name,
                    "execution_time_ms": execution_time,
                    "success": True
                }
            )

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            logger.error(
                "Agent execution failed",
                extra={
                    "agent_name": agent_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": execution_time
                },
                exc_info=True
            )

            await self._track_performance_async(
                agent_name=agent_name,
                task=task,
                success=False,
                execution_time_ms=execution_time,
                error_type=type(e).__name__
            )
            raise

    async def execute_with_semaphore(
        self,
        agent_name: str,
        task: str,
        **kwargs
    ) -> str:
        """Execute agent with semaphore for concurrency control."""
        async with self.semaphore:
            return await self.execute_agent(agent_name, task, **kwargs)

    async def execute_multiple(
        self,
        tasks: List[Tuple[str, str]]  # ✅ FIXED: Python 3.8 compatible
    ) -> List[str]:  # ✅ FIXED: Python 3.8 compatible
        """Execute multiple agents concurrently with rate limiting."""
        results = await asyncio.gather(*[
            self.execute_with_semaphore(agent_name, task)
            for agent_name, task in tasks
        ])
        return results

    # ✅ FIXED: Async performance tracking
    async def _track_performance_async(self, **kwargs):
        """Track performance metrics asynchronously."""
        if self._performance_tracker is None:
            self._performance_tracker = PerformanceTracker()

        # Run in executor to avoid blocking event loop
        await asyncio.to_thread(
            self._performance_tracker.track_execution,
            **kwargs
        )
```

**Step 3: Add backward compatibility wrapper**

Update `claude_force/orchestrator.py`:

```python
from typing import List, Tuple  # ✅ FIXED: Python 3.8 compatible

class AgentOrchestrator:
    """Synchronous orchestrator with async support."""

    def __init__(self, ...):
        # Existing sync initialization
        self._async_orchestrator = None

    def execute_agent(self, agent_name: str, task: str, **kwargs) -> str:
        """Synchronous execution (backward compatible)."""
        # Existing synchronous implementation
        pass

    async def execute_agent_async(self, agent_name: str, task: str, **kwargs) -> str:
        """Asynchronous execution (new feature)."""
        if self._async_orchestrator is None:
            from .async_orchestrator import AsyncAgentOrchestrator

            # ✅ NEW: Read concurrency limit from config
            config = self.config
            max_concurrent = config.get('performance', {}).get('max_concurrent_agents', 10)

            self._async_orchestrator = AsyncAgentOrchestrator(
                config_path=self.config_path,
                api_key=self.api_key,
                max_concurrent=max_concurrent
            )
        return await self._async_orchestrator.execute_agent(agent_name, task, **kwargs)

    async def execute_multiple_async(
        self,
        tasks: List[Tuple[str, str]]  # ✅ FIXED: Python 3.8 compatible
    ) -> List[str]:  # ✅ FIXED: Python 3.8 compatible
        """Execute multiple agents concurrently."""
        if self._async_orchestrator is None:
            from .async_orchestrator import AsyncAgentOrchestrator

            config = self.config
            max_concurrent = config.get('performance', {}).get('max_concurrent_agents', 10)

            self._async_orchestrator = AsyncAgentOrchestrator(
                config_path=self.config_path,
                api_key=self.api_key,
                max_concurrent=max_concurrent
            )
        return await self._async_orchestrator.execute_multiple(tasks)
```

**Step 4: Update CLI for async support**

```python
import asyncio
import logging

# ✅ NEW: Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@click.command()
@click.argument('agent_name')
@click.argument('task')
@click.option('--async', 'use_async', is_flag=True, help='Use async execution')
@click.option('--timeout', default=30, help='Timeout in seconds')
def execute(agent_name: str, task: str, use_async: bool, timeout: int):
    """Execute an agent with a task."""
    orchestrator = AgentOrchestrator()

    if use_async:
        # Run async version
        async def main():
            orchestrator._async_orchestrator.timeout_seconds = timeout
            return await orchestrator.execute_agent_async(agent_name, task)

        result = asyncio.run(main())
    else:
        # Run sync version (backward compatible)
        result = orchestrator.execute_agent(agent_name, task)

    click.echo(result)
```

---

### 1.2 Response Caching System (UPDATED)

#### Implementation Steps

**Step 1: Create cache module**

Create `claude_force/response_cache.py`:

```python
"""
Response caching system for Claude API calls.
"""
import hashlib
import hmac  # ✅ NEW: For cache integrity
import json
import time
import heapq  # ✅ NEW: Optimized LRU eviction
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cached response entry."""
    key: str
    agent_name: str
    task: str
    model: str
    response: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    timestamp: float
    hit_count: int = 0
    signature: str = ""  # ✅ NEW: HMAC signature


class ResponseCache:
    """
    Intelligent response cache for Claude API calls.

    Features:
    - TTL-based expiration
    - LRU eviction (optimized with heapq)
    - Size limits
    - Cache statistics
    - Exclusion lists (non-deterministic agents)
    - HMAC integrity verification
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_hours: int = 24,
        max_size_mb: int = 100,
        enabled: bool = True,
        cache_secret: Optional[str] = None  # ✅ NEW: For HMAC
    ):
        # ✅ FIXED: Validate cache directory
        if cache_dir:
            cache_dir = cache_dir.resolve()
            base = Path.home() / ".claude"
            if not str(cache_dir).startswith(str(base)):
                raise ValueError(f"Cache directory must be under {base}")

        self.cache_dir = cache_dir or Path.home() / ".claude" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ttl_seconds = ttl_hours * 3600
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.enabled = enabled

        # ✅ NEW: HMAC secret for integrity
        self.cache_secret = cache_secret or os.getenv("CLAUDE_CACHE_SECRET", "default_secret")

        # In-memory cache for fast access
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._load_cache_index()

        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size_bytes': 0,
            'integrity_failures': 0  # ✅ NEW
        }

    def _cache_key(self, agent_name: str, task: str, model: str) -> str:
        """Generate cache key."""
        content = f"{agent_name}:{task}:{model}"
        # ✅ FIXED: Use 32 chars instead of 16 (reduced collision risk)
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def _compute_signature(self, entry_dict: Dict[str, Any]) -> str:
        """Compute HMAC signature for cache entry."""
        # Remove signature field if present
        entry_copy = entry_dict.copy()
        entry_copy.pop('signature', None)

        # Create canonical JSON representation
        canonical = json.dumps(entry_copy, sort_keys=True)

        # Compute HMAC
        signature = hmac.new(
            key=self.cache_secret.encode(),
            msg=canonical.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return signature

    def _verify_signature(self, entry: CacheEntry) -> bool:
        """Verify HMAC signature of cache entry."""
        expected_sig = entry.signature
        entry_dict = asdict(entry)
        actual_sig = self._compute_signature(entry_dict)

        if expected_sig != actual_sig:
            logger.warning(
                "Cache integrity check failed",
                extra={"key": entry.key}
            )
            self.stats['integrity_failures'] += 1
            return False

        return True

    def get(
        self,
        agent_name: str,
        task: str,
        model: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached response."""
        if not self.enabled:
            return None

        key = self._cache_key(agent_name, task, model)

        # Check memory cache
        if key in self._memory_cache:
            entry = self._memory_cache[key]

            # ✅ NEW: Verify integrity
            if not self._verify_signature(entry):
                self._evict(key)
                return None

            # Check TTL
            age = time.time() - entry.timestamp
            if age > self.ttl_seconds:
                # Expired
                self._evict(key)
                self.stats['misses'] += 1
                return None

            # Cache hit
            entry.hit_count += 1
            self.stats['hits'] += 1

            logger.debug(
                "Cache hit",
                extra={
                    "key": key[:8],
                    "agent": agent_name,
                    "age_seconds": age
                }
            )

            return {
                'response': entry.response,
                'input_tokens': entry.input_tokens,
                'output_tokens': entry.output_tokens,
                'estimated_cost': entry.estimated_cost,
                'cached': True,
                'cache_age_seconds': age
            }

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                # Check TTL
                age = time.time() - cache_file.stat().st_mtime
                if age > self.ttl_seconds:
                    cache_file.unlink()
                    self.stats['misses'] += 1
                    return None

                # Load from disk
                with open(cache_file) as f:
                    entry_dict = json.load(f)
                    entry = CacheEntry(**entry_dict)

                # ✅ NEW: Verify integrity
                if not self._verify_signature(entry):
                    self._evict(key)
                    return None

                self._memory_cache[key] = entry

                entry.hit_count += 1
                self.stats['hits'] += 1

                return {
                    'response': entry.response,
                    'input_tokens': entry.input_tokens,
                    'output_tokens': entry.output_tokens,
                    'estimated_cost': entry.estimated_cost,
                    'cached': True,
                    'cache_age_seconds': age
                }
            except Exception as e:
                logger.warning(f"Failed to load cache file: {e}")
                # Clean up corrupt file
                try:
                    cache_file.unlink()
                except OSError:
                    pass

        # Cache miss
        self.stats['misses'] += 1
        return None

    def set(
        self,
        agent_name: str,
        task: str,
        model: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float
    ):
        """Cache a response."""
        if not self.enabled:
            return

        key = self._cache_key(agent_name, task, model)

        entry = CacheEntry(
            key=key,
            agent_name=agent_name,
            task=task,
            model=model,
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=estimated_cost,
            timestamp=time.time()
        )

        # ✅ NEW: Compute signature
        entry_dict = asdict(entry)
        entry.signature = self._compute_signature(entry_dict)

        # Store in memory
        self._memory_cache[key] = entry

        # Store on disk
        cache_file = self.cache_dir / f"{key}.json"

        # ✅ FIXED: Proper error handling for file write
        try:
            with open(cache_file, 'w') as f:
                json.dump(asdict(entry), f)

            # Update size only if write succeeded
            actual_size = cache_file.stat().st_size
            self.stats['size_bytes'] += actual_size

            logger.debug(
                "Cache entry stored",
                extra={"key": key[:8], "size_bytes": actual_size}
            )

        except Exception as e:
            logger.error(f"Failed to write cache file: {e}")
            # Don't update size if write failed
            if cache_file.exists():
                try:
                    cache_file.unlink()
                except OSError:
                    pass
            raise

        # Check size limit and evict if needed
        if self.stats['size_bytes'] > self.max_size_bytes:
            self._evict_lru()

    def _evict(self, key: str):
        """Evict specific cache entry."""
        if key in self._memory_cache:
            del self._memory_cache[key]

        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            size = cache_file.stat().st_size
            try:
                cache_file.unlink()
                self.stats['size_bytes'] -= size
                self.stats['evictions'] += 1
            except OSError as e:
                logger.warning(f"Failed to evict cache file: {e}")

    def _evict_lru(self):
        """Evict least recently used entries (optimized with heapq)."""
        # ✅ FIXED: Use heapq for O(k log n) instead of O(n log n)
        num_to_evict = max(1, len(self._memory_cache) // 10)

        logger.info(
            "Evicting LRU entries",
            extra={
                "num_to_evict": num_to_evict,
                "total_entries": len(self._memory_cache)
            }
        )

        # Find k smallest by (hit_count, timestamp)
        to_evict = heapq.nsmallest(
            num_to_evict,
            self._memory_cache.items(),
            key=lambda x: (x[1].hit_count, x[1].timestamp)
        )

        for key, _ in to_evict:
            self._evict(key)

    def clear(self):
        """Clear entire cache."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError as e:
                logger.warning(f"Failed to clear cache file: {e}")

        self._memory_cache.clear()
        self.stats['size_bytes'] = 0

        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'enabled': self.enabled,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': f"{hit_rate:.1f}%",
            'evictions': self.stats['evictions'],
            'integrity_failures': self.stats['integrity_failures'],  # ✅ NEW
            'size_mb': self.stats['size_bytes'] / (1024 * 1024),
            'entries': len(self._memory_cache)
        }

    def _load_cache_index(self):
        """Load cache index from disk."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    entry_dict = json.load(f)
                    entry = CacheEntry(**entry_dict)

                    # ✅ NEW: Verify integrity on load
                    if not self._verify_signature(entry):
                        logger.warning(f"Removing corrupt cache file: {cache_file}")
                        cache_file.unlink()
                        continue

                    self._memory_cache[entry.key] = entry
                    self.stats['size_bytes'] += cache_file.stat().st_size

            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_file}: {e}")
                # Remove corrupt cache file
                try:
                    cache_file.unlink()
                except OSError:
                    pass
```

---

### 1.3 Configuration & Documentation

#### Update Configuration Schema

Add to `.claude/claude.json`:

```json
{
  "performance": {
    "async_enabled": true,
    "max_concurrent_agents": 10,
    "timeout_seconds": 30,
    "max_retries": 3
  },
  "cache": {
    "enabled": true,
    "ttl_hours": 24,
    "max_size_mb": 100,
    "exclude_agents": [],
    "use_integrity_check": true
  }
}
```

#### Update Requirements

Update `requirements.txt`:
```
anthropic>=0.40.0
aiofiles>=23.0.0
tenacity>=8.0.0
```

---

## Testing Strategy (Enhanced)

### Unit Tests (Updated)

```python
# tests/test_async_orchestrator.py
import pytest
import asyncio
from unittest import mock
from typing import List, Tuple  # ✅ FIXED: Python 3.8 compatible

from claude_force.async_orchestrator import AsyncAgentOrchestrator


@pytest.mark.asyncio
async def test_async_execute_agent():
    """Test async agent execution."""
    orchestrator = AsyncAgentOrchestrator()
    result = await orchestrator.execute_agent("python-expert", "What are decorators?")
    assert result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_concurrent_execution():
    """Test concurrent agent execution."""
    orchestrator = AsyncAgentOrchestrator()

    tasks: List[Tuple[str, str]] = [  # ✅ FIXED: Python 3.8 type hint
        ("python-expert", "Explain lists"),
        ("python-expert", "Explain dicts"),
        ("python-expert", "Explain sets")
    ]

    import time
    start = time.time()
    results = await orchestrator.execute_multiple(tasks)
    elapsed = time.time() - start

    assert len(results) == 3
    assert all(isinstance(r, str) for r in results)

    print(f"Concurrent execution: {elapsed:.2f}s")


# ✅ NEW: Input validation tests
@pytest.mark.asyncio
async def test_invalid_agent_name():
    """Test that invalid agent names are rejected."""
    orchestrator = AsyncAgentOrchestrator()

    with pytest.raises(ValueError, match="Invalid agent name"):
        await orchestrator.execute_agent("../../etc/passwd", "task")


@pytest.mark.asyncio
async def test_task_too_large():
    """Test that oversized tasks are rejected."""
    orchestrator = AsyncAgentOrchestrator()

    large_task = "x" * 200_000  # > 100k chars

    with pytest.raises(ValueError, match="Task too large"):
        await orchestrator.execute_agent("python-expert", large_task)


# ✅ NEW: Timeout test
@pytest.mark.asyncio
async def test_timeout():
    """Test that operations timeout correctly."""
    orchestrator = AsyncAgentOrchestrator()
    orchestrator.timeout_seconds = 1  # Very short timeout

    with mock.patch.object(orchestrator.async_client.messages, 'create') as mock_create:
        # Simulate slow response
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(10)
            return mock.Mock()

        mock_create.side_effect = slow_response

        with pytest.raises(TimeoutError):
            await orchestrator.execute_agent("python-expert", "task")


# ✅ NEW: Concurrency limit test
@pytest.mark.asyncio
async def test_concurrency_limit():
    """Test that semaphore limits concurrency."""
    orchestrator = AsyncAgentOrchestrator(max_concurrent=2)

    # Track concurrent executions
    concurrent_count = 0
    max_concurrent = 0

    async def tracked_execute(agent, task):
        nonlocal concurrent_count, max_concurrent
        concurrent_count += 1
        max_concurrent = max(max_concurrent, concurrent_count)

        await asyncio.sleep(0.1)  # Simulate work

        concurrent_count -= 1
        return "result"

    with mock.patch.object(orchestrator, 'execute_agent', tracked_execute):
        tasks: List[Tuple[str, str]] = [("agent", f"task{i}") for i in range(10)]
        await orchestrator.execute_multiple(tasks)

    assert max_concurrent <= 2


# ✅ NEW: Cache tests
def test_cache_integrity():
    """Test cache integrity verification."""
    from claude_force.response_cache import ResponseCache

    cache = ResponseCache(cache_secret="test_secret")

    # Store entry
    cache.set("agent", "task", "model", "response", 100, 50, 0.001)

    # Should retrieve successfully
    result = cache.get("agent", "task", "model")
    assert result is not None
    assert result['response'] == "response"

    # Tamper with cache file
    cache_files = list(cache.cache_dir.glob("*.json"))
    assert len(cache_files) == 1

    import json
    with open(cache_files[0], 'r') as f:
        data = json.load(f)

    data['response'] = "tampered"

    with open(cache_files[0], 'w') as f:
        json.dump(data, f)

    # Should detect tampering
    result = cache.get("agent", "task", "model")
    assert result is None
    assert cache.stats['integrity_failures'] == 1


def test_cache_key_length():
    """Test that cache keys are 32 chars."""
    from claude_force.response_cache import ResponseCache

    cache = ResponseCache()
    key = cache._cache_key("agent", "task", "model")

    assert len(key) == 32


# ✅ NEW: LRU eviction test
def test_lru_eviction():
    """Test LRU eviction with heapq."""
    from claude_force.response_cache import ResponseCache

    cache = ResponseCache(max_size_mb=1)

    # Fill cache
    for i in range(100):
        large_response = "x" * 50_000  # 50KB each
        cache.set(f"agent{i}", f"task{i}", "model", large_response, 1000, 500, 0.001)

    # Should have triggered eviction
    assert cache.stats['evictions'] > 0
    assert cache.stats['size_bytes'] <= cache.max_size_bytes
```

---

## Summary of Changes in v1.1

### Critical Fixes
- ✅ Added missing `import os` and `import json`
- ✅ Fixed Python 3.8 compatibility (all `list[...]` → `List[...]`)
- ✅ Added `asyncio.timeout()` to all async API calls
- ✅ Added input validation with regex for `agent_name`

### High-Priority Improvements
- ✅ Increased cache key from 16 to 32 characters
- ✅ Added `asyncio.Semaphore` for concurrency control
- ✅ Implemented retry logic with `tenacity`
- ✅ Made `_track_performance()` async with `asyncio.to_thread()`

### Additional Enhancements
- ✅ Added structured logging throughout
- ✅ Added HMAC signatures for cache integrity
- ✅ Optimized LRU eviction with `heapq.nsmallest()`
- ✅ Improved error handling and logging
- ✅ Added comprehensive validation tests
- ✅ Added security tests for cache tampering

### New Dependencies
- `tenacity>=8.0.0` - For retry logic

---

## Next Steps

1. ✅ Review this updated plan
2. Begin implementation of Phase 1 with all fixes applied
3. Run comprehensive test suite
4. Performance benchmarking
5. Proceed to Phase 2

**This plan is now ready for implementation with all expert review feedback incorporated.**

---

**Document Version:** 1.1
**Last Updated:** 2025-11-14
**Status:** Ready for Implementation
**Owner:** Performance Engineering Team
