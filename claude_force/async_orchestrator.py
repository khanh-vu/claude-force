"""
Async version of AgentOrchestrator for non-blocking operations.

All critical and high-priority fixes from expert review applied:
- ✅ Added missing imports (os, json, re)
- ✅ Python 3.8 compatibility (List[] instead of list[])
- ✅ Timeout protection on all async operations
- ✅ Input validation for agent_name
- ✅ Semaphore for concurrency control
- ✅ Retry logic with tenacity
- ✅ Async performance tracking
- ✅ Structured logging
"""

import os
import json
import re
import asyncio
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

try:
    from anthropic import AsyncAnthropic
except ImportError:
    raise ImportError("anthropic package required. Install with: pip install anthropic")

try:
    from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
except ImportError:
    # Tenacity is optional - if not available, retry functionality will be disabled
    retry = None
    stop_after_attempt = None
    wait_exponential = None
    RetryError = Exception

from .performance_tracker import PerformanceTracker, PRICING
from .agent_memory import AgentMemory
from .response_cache import ResponseCache
from .constants import (
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_CACHE_TTL_HOURS,
    MAX_CACHE_SIZE_MB,
    MAX_TOKEN_LIMIT,
)

# ✅ Structured logging
logger = logging.getLogger(__name__)


# ✅ Python 3.8 compatibility helper for asyncio.to_thread
async def _run_in_thread(func, *args, **kwargs):
    """
    Run synchronous function in thread pool (Python 3.8 compatible).

    asyncio.to_thread() was added in Python 3.9, so we use
    run_in_executor() for Python 3.8 compatibility.
    """
    loop = asyncio.get_event_loop()
    if args or kwargs:
        # Wrap function with arguments
        import functools

        partial_func = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, partial_func)
    else:
        return await loop.run_in_executor(None, func)


@dataclass
class AsyncAgentResult:
    """Result from an async agent execution"""

    agent_name: str
    success: bool
    output: str
    metadata: Dict[str, Any]
    errors: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)


class AsyncAgentOrchestrator:
    """
    Async orchestrator for non-blocking agent execution.

    Features:
    - Non-blocking async API calls
    - Concurrent agent execution with rate limiting
    - Timeout protection on all operations
    - Input validation and security checks
    - Retry logic for transient failures
    - Performance tracking
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        max_concurrent: int = 10,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = 3,
        enable_tracking: bool = True,
        enable_memory: bool = True,
        enable_cache: bool = True,
        cache_ttl_hours: int = DEFAULT_CACHE_TTL_HOURS,
        cache_max_size_mb: int = MAX_CACHE_SIZE_MB,
    ):
        """
        Initialize async orchestrator.

        Args:
            config_path: Path to claude.json config
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            max_concurrent: Maximum concurrent agent executions
            timeout_seconds: Timeout for API calls
            max_retries: Number of retry attempts for transient failures
            enable_tracking: Enable performance tracking
            enable_memory: Enable agent memory system
            enable_cache: Enable response caching (default: True)
            cache_ttl_hours: Cache TTL in hours (default: 24)
            cache_max_size_mb: Maximum cache size in MB (default: 100)
        """
        self.config_path = config_path or Path.home() / ".claude" / "claude.json"
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # Configuration
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.enable_tracking = enable_tracking
        self.enable_memory = enable_memory
        self.enable_cache = enable_cache
        self.cache_ttl_hours = cache_ttl_hours
        self.cache_max_size_mb = cache_max_size_mb

        # Lazy initialization
        self._async_client: Optional[AsyncAnthropic] = None
        self._config: Optional[Dict] = None
        self._performance_tracker: Optional[PerformanceTracker] = None
        self._agent_memory: Optional[AgentMemory] = None
        self._response_cache: Optional[ResponseCache] = None

        # ✅ Semaphore for concurrency control (with lock for thread safety)
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._semaphore_lock = asyncio.Lock()

    async def _get_semaphore(self) -> asyncio.Semaphore:
        """
        Lazy-load semaphore with thread safety.

        ✅ FIXED: Uses lock to prevent race condition during initialization
        """
        if self._semaphore is None:
            async with self._semaphore_lock:
                # Double-check pattern
                if self._semaphore is None:
                    self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

    @property
    def cache(self) -> Optional[ResponseCache]:
        """Lazy-load response cache."""
        if self._response_cache is None and self.enable_cache:
            cache_dir = self.config_path.parent / "cache"
            self._response_cache = ResponseCache(
                cache_dir=cache_dir,
                ttl_hours=self.cache_ttl_hours,
                max_size_mb=self.cache_max_size_mb,
                enabled=self.enable_cache,
            )
        return self._response_cache

    @property
    def memory(self):
        """Lazy-load agent memory system."""
        if self._agent_memory is None and self.enable_memory:
            try:
                from claude_force.agent_memory import AgentMemory

                memory_path = self.config_path.parent / "sessions.db"
                self._agent_memory = AgentMemory(db_path=str(memory_path))
            except Exception as e:
                logger.warning(f"Agent memory disabled: {e}")
        return self._agent_memory

    @property
    def async_client(self) -> AsyncAnthropic:
        """Lazy-load async client."""
        if self._async_client is None:
            if not self.api_key:
                raise ValueError(
                    "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                    "or pass api_key parameter."
                )
            self._async_client = AsyncAnthropic(api_key=self.api_key)
        return self._async_client

    async def load_config(self) -> Dict:
        """Load configuration asynchronously."""
        if self._config is None:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")

            # Use thread pool for file I/O to avoid blocking (Python 3.8 compatible)
            def _read_config():
                with open(self.config_path, "r") as f:
                    return json.load(f)

            self._config = await _run_in_thread(_read_config)

        return self._config

    async def load_agent_definition(self, agent_name: str) -> str:
        """Load agent definition asynchronously."""
        config = await self.load_config()
        agent_config = config["agents"].get(agent_name)

        if not agent_config:
            all_agents = list(config["agents"].keys())
            raise ValueError(
                f"Agent '{agent_name}' not found. Available agents: {', '.join(all_agents)}"
            )

        agent_file = self.config_path.parent / agent_config["file"]

        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

        # Use thread pool for file I/O (Python 3.8 compatible)
        def _read_file():
            with open(agent_file, "r") as f:
                return f.read()

        return await _run_in_thread(_read_file)

    def _create_retry_decorator(self):
        """Create retry decorator if tenacity is available."""
        if retry is None:
            # No retry - return identity decorator
            def no_retry(func):
                return func

            return no_retry

        return retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True,
        )

    async def _call_api_with_retry(
        self, model: str, max_tokens: int, temperature: float, messages: List[Dict[str, str]]
    ):
        """
        Call API with retry logic and timeout protection.

        ✅ Implements timeout protection (Python 3.8+ compatible)
        ✅ Implements retry logic (if tenacity available)
        """
        # ✅ Timeout protection using asyncio.wait_for() (Python 3.8+ compatible)
        try:
            # If tenacity is available, use retry decorator
            if retry is not None:
                retry_decorator = self._create_retry_decorator()

                @retry_decorator
                async def _call():
                    return await self.async_client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=messages,
                    )

                # Wrap with timeout using asyncio.wait_for (Python 3.8+)
                return await asyncio.wait_for(_call(), timeout=self.timeout_seconds)
            else:
                # No retry - direct call with timeout
                return await asyncio.wait_for(
                    self.async_client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=messages,
                    ),
                    timeout=self.timeout_seconds,
                )

        except asyncio.TimeoutError:
            logger.error("API call timed out", extra={"timeout_seconds": self.timeout_seconds})
            raise TimeoutError(f"API call timed out after {self.timeout_seconds}s")

    def _sanitize_task(self, task: str) -> str:
        """
        Sanitize task to prevent prompt injection.

        ✅ FIXED: Adds basic protection against prompt injection attacks

        Removes common prompt injection patterns:
        - System prompt markers
        - Role switching attempts
        - Instruction overrides
        """
        # Remove common injection patterns
        dangerous_patterns = [
            "# System",
            "## System",
            "SYSTEM:",
            "[SYSTEM]",
            "# Assistant",
            "## Assistant",
            "ASSISTANT:",
            "[ASSISTANT]",
            "Ignore previous instructions",
            "Ignore all previous",
            "Disregard previous",
            "New instructions:",
            "From now on,",
        ]

        sanitized = task
        for pattern in dangerous_patterns:
            # Case-insensitive replacement
            sanitized = re.sub(
                re.escape(pattern), f"[SANITIZED: {pattern}]", sanitized, flags=re.IGNORECASE
            )

        # Limit consecutive newlines (prevent prompt structure manipulation)
        sanitized = re.sub(r"\n{4,}", "\n\n\n", sanitized)

        if sanitized != task:
            logger.warning(
                "Task content sanitized - potential prompt injection detected",
                extra={"original_length": len(task), "sanitized_length": len(sanitized)},
            )

        return sanitized

    async def execute_agent(
        self,
        agent_name: str,
        task: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        workflow_name: Optional[str] = None,
        workflow_position: Optional[int] = None,
        use_memory: bool = True,
    ) -> AsyncAgentResult:
        """
        Execute agent asynchronously.

        ✅ Input validation
        ✅ Structured logging
        ✅ Timeout protection
        ✅ Retry logic
        ✅ Async performance tracking
        ✅ Response caching
        ✅ Prompt injection protection
        ✅ Agent memory integration

        Args:
            agent_name: Name of agent to run
            task: Task description
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation (0.0-1.0)
            workflow_name: Name of workflow (internal use)
            workflow_position: Position in workflow (internal use)

        Returns:
            AsyncAgentResult with output and metadata
        """
        start_time = time.time()

        # ✅ Input validation
        if not re.match(r"^[a-zA-Z0-9_-]+$", agent_name):
            raise ValueError(
                f"Invalid agent name: {agent_name}. "
                "Agent names must contain only alphanumeric characters, hyphens, and underscores."
            )

        if len(task) > MAX_TOKEN_LIMIT:
            raise ValueError(
                f"Task too large: {len(task)} chars (max {MAX_TOKEN_LIMIT:,}). "
                "Please reduce task size."
            )

        # ✅ Sanitize task to prevent prompt injection
        sanitized_task = self._sanitize_task(task)

        # ✅ Check cache first
        if self.cache:
            cached_result = self.cache.get(agent_name, sanitized_task, model)
            if cached_result:
                execution_time_ms = (time.time() - start_time) * 1000

                logger.info(
                    "Cache hit - returning cached response",
                    extra={
                        "agent_name": agent_name,
                        "cache_age_seconds": cached_result.get("cache_age_seconds", 0),
                        "execution_time_ms": execution_time_ms,
                    },
                )

                return AsyncAgentResult(
                    agent_name=agent_name,
                    success=True,
                    output=cached_result["response"],
                    metadata={
                        "model": model,
                        "input_tokens": cached_result["input_tokens"],
                        "output_tokens": cached_result["output_tokens"],
                        "execution_time_ms": execution_time_ms,
                        "cached": True,
                        "cache_age_seconds": cached_result.get("cache_age_seconds", 0),
                        "estimated_cost": cached_result.get("estimated_cost", 0),
                    },
                )

        # ✅ Structured logging
        logger.info(
            "Executing agent",
            extra={
                "agent_name": agent_name,
                "task_length": len(sanitized_task),
                "model": model,
                "workflow_name": workflow_name,
                "workflow_position": workflow_position,
                "cache_enabled": self.enable_cache,
            },
        )

        try:
            # Load agent definition
            agent_definition = await self.load_agent_definition(agent_name)

            # Build prompt with optional memory context
            prompt_parts = [agent_definition, ""]

            # ✅ Inject memory context if available
            # Use original task (not sanitized) for memory lookup to preserve full context
            if use_memory and self.memory:
                try:
                    # Run synchronous memory call in thread pool (Python 3.8 compatible)
                    context = await _run_in_thread(
                        self.memory.get_context_for_task, task, agent_name
                    )
                    if context:
                        prompt_parts.extend([context, ""])
                except Exception as e:
                    # If memory retrieval fails, continue without it
                    logger.debug(f"Memory retrieval failed: {e}")

            prompt_parts.extend(["# Task", sanitized_task])
            prompt = "\n".join(prompt_parts)

            # Call API with retry and timeout
            response = await self._call_api_with_retry(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract result
            output = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output += block.text

            execution_time_ms = (time.time() - start_time) * 1000

            # ✅ Async performance tracking
            if self.enable_tracking:
                await self._track_performance_async(
                    agent_name=agent_name,
                    task=task,
                    success=True,
                    execution_time_ms=execution_time_ms,
                    model=model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    workflow_name=workflow_name,
                    workflow_position=workflow_position,
                )

            # ✅ P2 FIX: Calculate estimated cost using model-specific pricing
            # Find pricing for this specific model
            pricing = None
            for model_pattern, prices in PRICING.items():
                if model_pattern in model:
                    pricing = prices
                    break

            if not pricing:
                # Default to Sonnet pricing if model not found
                pricing = PRICING.get(
                    "claude-3-5-sonnet-20241022", {"input": 0.003, "output": 0.015}
                )
                logger.debug(
                    f"Model pricing not found, using Sonnet default",
                    extra={"model": model},
                )

            input_cost = (response.usage.input_tokens / 1_000_000) * pricing["input"]
            output_cost = (response.usage.output_tokens / 1_000_000) * pricing["output"]
            estimated_cost = input_cost + output_cost

            # ✅ Store in cache
            if self.cache:
                try:
                    self.cache.set(
                        agent_name=agent_name,
                        task=sanitized_task,
                        model=model,
                        response=output,
                        input_tokens=response.usage.input_tokens,
                        output_tokens=response.usage.output_tokens,
                        estimated_cost=estimated_cost,
                    )
                    logger.debug(
                        "Response cached", extra={"agent_name": agent_name, "model": model}
                    )
                except Exception as cache_error:
                    # Don't fail execution if caching fails
                    logger.warning("Failed to cache response", extra={"error": str(cache_error)})

            # ✅ Store in memory (only if use_memory=True)
            # Use original task (not sanitized) for memory storage to preserve full context
            if use_memory and self.memory:
                try:
                    await _run_in_thread(
                        self.memory.store_session,
                        agent_name=agent_name,
                        task=task,
                        output=output,
                        success=True,
                        execution_time_ms=execution_time_ms,
                        model=model,
                        input_tokens=response.usage.input_tokens,
                        output_tokens=response.usage.output_tokens,
                        metadata={
                            "workflow_name": workflow_name,
                            "workflow_position": workflow_position,
                        },
                    )
                except Exception as memory_error:
                    # Don't fail execution if memory storage fails
                    logger.debug(f"Failed to store in memory: {memory_error}")

            logger.info(
                "Agent execution completed",
                extra={
                    "agent_name": agent_name,
                    "execution_time_ms": execution_time_ms,
                    "success": True,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cached": False,
                },
            )

            return AsyncAgentResult(
                agent_name=agent_name,
                success=True,
                output=output,
                metadata={
                    "model": model,
                    "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "execution_time_ms": execution_time_ms,
                    "workflow_name": workflow_name,
                    "workflow_position": workflow_position,
                    "cached": False,
                    "estimated_cost": estimated_cost,
                },
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_type = type(e).__name__

            logger.error(
                "Agent execution failed",
                extra={
                    "agent_name": agent_name,
                    "error": str(e),
                    "error_type": error_type,
                    "execution_time_ms": execution_time_ms,
                },
                exc_info=True,
            )

            # Track failed execution
            if self.enable_tracking:
                await self._track_performance_async(
                    agent_name=agent_name,
                    task=task,
                    success=False,
                    execution_time_ms=execution_time_ms,
                    model=model,
                    input_tokens=0,
                    output_tokens=0,
                    error_type=error_type,
                    workflow_name=workflow_name,
                    workflow_position=workflow_position,
                )

            # ✅ Store failed execution in memory (only if use_memory=True)
            # Use original task (not sanitized) for memory storage to preserve full context
            if use_memory and self.memory:
                try:
                    await _run_in_thread(
                        self.memory.store_session,
                        agent_name=agent_name,
                        task=task,
                        output=str(e),
                        success=False,
                        execution_time_ms=execution_time_ms,
                        model=model,
                        input_tokens=0,
                        output_tokens=0,
                        metadata={
                            "error_type": error_type,
                            "workflow_name": workflow_name,
                            "workflow_position": workflow_position,
                        },
                    )
                except Exception as memory_error:
                    # Don't fail execution if memory storage fails
                    logger.debug(f"Failed to store failed execution in memory: {memory_error}")

            return AsyncAgentResult(
                agent_name=agent_name,
                success=False,
                output="",
                metadata={"execution_time_ms": execution_time_ms},
                errors=[str(e)],
            )

    async def execute_with_semaphore(
        self, agent_name: str, task: str, **kwargs
    ) -> AsyncAgentResult:
        """
        Execute agent with semaphore for concurrency control.

        ✅ Implements concurrency limiting
        ✅ FIXED: Uses thread-safe semaphore getter
        """
        semaphore = await self._get_semaphore()
        async with semaphore:
            return await self.execute_agent(agent_name, task, **kwargs)

    async def execute_multiple(
        self, tasks: List[Tuple[str, str]], **kwargs
    ) -> List[AsyncAgentResult]:
        """
        Execute multiple agents concurrently with rate limiting.

        ✅ Uses semaphore to limit concurrency
        ✅ Python 3.8 compatible type hints

        Args:
            tasks: List of (agent_name, task) tuples
            **kwargs: Additional arguments passed to execute_agent

        Returns:
            List of AsyncAgentResult objects
        """
        logger.info(
            "Executing multiple agents",
            extra={"num_agents": len(tasks), "max_concurrent": self.max_concurrent},
        )

        results = await asyncio.gather(
            *[self.execute_with_semaphore(agent_name, task, **kwargs) for agent_name, task in tasks]
        )

        success_count = sum(1 for r in results if r.success)
        logger.info(
            "Multiple agent execution completed",
            extra={
                "total": len(results),
                "successful": success_count,
                "failed": len(results) - success_count,
            },
        )

        return results

    async def _track_performance_async(self, **kwargs):
        """
        Track performance metrics asynchronously.

        ✅ Uses thread pool executor to avoid blocking event loop (Python 3.8 compatible)
        """
        if not self.enable_tracking:
            return

        if self._performance_tracker is None:
            self._performance_tracker = PerformanceTracker()

        # Run in executor to avoid blocking event loop (Python 3.8 compatible)
        await _run_in_thread(self._performance_tracker.record_execution, **kwargs)

    async def close(self):
        """Close async client and cleanup resources."""
        if self._async_client is not None:
            await self._async_client.close()
            self._async_client = None

        logger.info("Async orchestrator closed")
