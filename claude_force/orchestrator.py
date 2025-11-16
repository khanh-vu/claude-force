"""
Agent Orchestrator - Core orchestration engine for Claude multi-agent system
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from claude_force.base import BaseOrchestrator, AgentResult
from claude_force.error_helpers import (
    format_agent_not_found_error,
    format_workflow_not_found_error,
    format_api_key_error,
    format_config_not_found_error,
    format_tracking_not_enabled_error,
    format_missing_dependency_error,
)

# ARCH-03: Structured logging
logger = logging.getLogger(__name__)


class AgentOrchestrator(BaseOrchestrator):
    """
    Standard orchestrator implementation.

    Inherits from BaseOrchestrator and provides concrete implementation
    for all abstract methods. This is the main orchestrator used by
    the CLI and most users.

    Usage:
        orchestrator = AgentOrchestrator(config_path=".claude/claude.json")
        result = orchestrator.run_agent("code-reviewer", task="Review this code")
        results = orchestrator.run_workflow("full-stack-feature", task="Build auth")
    """

    def __init__(
        self,
        config_path: str = ".claude/claude.json",
        anthropic_api_key: Optional[str] = None,
        enable_tracking: bool = True,
        enable_memory: bool = True,
        validate_api_key: bool = False,
    ):
        """
        Initialize orchestrator with configuration.

        Args:
            config_path: Path to claude.json configuration file
            anthropic_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            enable_tracking: Enable performance tracking (default: True)
            enable_memory: Enable agent memory system (default: True)
            validate_api_key: Validate API key immediately (default: False, validated lazily)
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        # Optionally validate API key upfront for better error messages
        # This is useful for testing error handling but not needed for read-only operations
        if validate_api_key and not self.api_key:
            raise ValueError(format_api_key_error())

        # Lazy initialization of anthropic client (only create when needed)
        self._client = None
        self.enable_tracking = enable_tracking
        self.enable_memory = enable_memory

        # Lazy initialization of performance tracker
        self._tracker = None

        # Lazy initialization of agent memory
        self._memory = None

        # Agent definition and contract caches (LRU-style with maxsize)
        self._definition_cache: Dict[str, str] = {}
        self._contract_cache: Dict[str, str] = {}
        self._cache_maxsize = 128  # Maximum cached definitions

    @property
    def client(self):
        """Lazy load anthropic client."""
        if self._client is None:
            # Validate API key when client is first needed
            if not self.api_key:
                raise ValueError(format_api_key_error())

            try:
                import anthropic

                self._client = anthropic.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    format_missing_dependency_error("anthropic", "pip install anthropic")
                )
        return self._client

    @property
    def tracker(self):
        """Lazy load performance tracker."""
        if self._tracker is None and self.enable_tracking:
            try:
                from claude_force.performance_tracker import PerformanceTracker

                self._tracker = PerformanceTracker()
            except Exception as e:
                logger.warning(f"Performance tracking disabled: {e}")
        return self._tracker

    @property
    def memory(self):
        """Lazy load agent memory."""
        if self._memory is None and self.enable_memory:
            try:
                from claude_force.agent_memory import AgentMemory

                memory_path = self.config_path.parent / "sessions.db"
                self._memory = AgentMemory(db_path=str(memory_path))
            except Exception as e:
                logger.warning(f"Agent memory disabled: {e}")
        return self._memory

    def _load_config(self) -> Dict:
        """Load claude.json configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(format_config_not_found_error(str(self.config_path)))

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.config_path}: {e}")

    def _load_agent_definition(self, agent_name: str) -> str:
        """
        Load agent definition from markdown file with caching.

        Uses in-memory cache to avoid repeated disk I/O for the same agent.
        Provides 50-100% speedup for repeated agent executions.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent definition markdown content

        Raises:
            ValueError: If agent not found in config
            FileNotFoundError: If agent file doesn't exist
        """
        # Check cache first
        if agent_name in self._definition_cache:
            return self._definition_cache[agent_name]

        # Validate agent exists in config
        agent_config = self.config["agents"].get(agent_name)
        if not agent_config:
            all_agents = list(self.config["agents"].keys())
            raise ValueError(format_agent_not_found_error(agent_name, all_agents))

        # Load from disk
        agent_file = self.config_path.parent / agent_config["file"]
        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

        with open(agent_file, "r") as f:
            definition = f.read()

        # Cache the definition (with simple size limit)
        if len(self._definition_cache) >= self._cache_maxsize:
            # Simple eviction: remove first (oldest) entry
            self._definition_cache.pop(next(iter(self._definition_cache)))

        self._definition_cache[agent_name] = definition
        return definition

    def _load_agent_contract(self, agent_name: str) -> str:
        """
        Load agent contract with caching.

        Uses in-memory cache to avoid repeated disk I/O.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent contract content (empty string if no contract)
        """
        # Check cache first
        if agent_name in self._contract_cache:
            return self._contract_cache[agent_name]

        # Get contract from config
        agent_config = self.config["agents"].get(agent_name)
        if not agent_config or "contract" not in agent_config:
            self._contract_cache[agent_name] = ""
            return ""

        contract_file = self.config_path.parent / agent_config["contract"]
        if not contract_file.exists():
            self._contract_cache[agent_name] = ""
            return ""

        # Load from disk
        with open(contract_file, "r") as f:
            contract = f.read()

        # Cache the contract (with simple size limit)
        if len(self._contract_cache) >= self._cache_maxsize:
            # Simple eviction: remove first (oldest) entry
            self._contract_cache.pop(next(iter(self._contract_cache)))

        self._contract_cache[agent_name] = contract
        return contract

    def clear_agent_cache(self):
        """
        Clear cached agent definitions and contracts.

        Useful for testing or when agent files have been modified and need to be reloaded.
        """
        self._definition_cache.clear()
        self._contract_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache size and hit rate information
        """
        return {
            "definition_cache_size": len(self._definition_cache),
            "contract_cache_size": len(self._contract_cache),
            "cache_maxsize": self._cache_maxsize,
            "cached_agents": list(self._definition_cache.keys()),
        }

    def _build_prompt(
        self,
        agent_definition: str,
        agent_contract: str,
        task: str,
        agent_name: str,
        use_memory: bool = True,
    ) -> str:
        """Build complete prompt for agent with optional memory context"""
        prompt_parts = [
            "# Agent Definition",
            agent_definition,
            "",
        ]

        if agent_contract:
            prompt_parts.extend(
                [
                    "# Agent Contract",
                    agent_contract,
                    "",
                ]
            )

        # Inject memory context if available
        if use_memory and self.memory:
            try:
                context = self.memory.get_context_for_task(task, agent_name)
                if context:
                    prompt_parts.extend([context, ""])
            except Exception as e:
                # If memory retrieval fails, continue without it
                logger.debug(f"Memory retrieval failed for agent '{agent_name}': {e}")

        prompt_parts.extend(
            [
                "# Task",
                task,
                "",
                "Please execute this task following your agent definition and contract.",
            ]
        )

        return "\n".join(prompt_parts)

    def run_agent(
        self,
        agent_name: str,
        task: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        workflow_name: Optional[str] = None,
        workflow_position: Optional[int] = None,
    ) -> AgentResult:
        """
        Run a single agent on a task.

        Args:
            agent_name: Name of agent to run (e.g., "code-reviewer")
            task: Task description or content to process
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation (0.0-1.0)
            workflow_name: Name of workflow (internal use)
            workflow_position: Position in workflow (internal use)

        Returns:
            AgentResult with output and metadata

        Example:
            result = orchestrator.run_agent(
                "code-reviewer",
                task="Review this code: def foo(): pass"
            )
            print(result.output)
        """
        import time

        start_time = time.time()
        error_type = None

        try:
            # Load agent definition and contract
            agent_definition = self._load_agent_definition(agent_name)
            agent_contract = self._load_agent_contract(agent_name)

            # Build prompt (with memory context if enabled)
            prompt = self._build_prompt(agent_definition, agent_contract, task, agent_name)

            # Call Claude API
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response
            output = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output += block.text

            execution_time_ms = (time.time() - start_time) * 1000

            # Record metrics
            if self.tracker:
                self.tracker.record_execution(
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

            # Store in memory
            if self.memory:
                try:
                    self.memory.store_session(
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
                except Exception as e:
                    # Memory storage failures shouldn't break execution
                    logger.debug(f"Failed to store execution in memory for '{agent_name}': {e}")

            return AgentResult(
                agent_name=agent_name,
                success=True,
                output=output,
                metadata={
                    "model": model,
                    "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "execution_time_ms": execution_time_ms,
                },
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_type = type(e).__name__

            # Record failed execution
            if self.tracker:
                self.tracker.record_execution(
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

            # Store failed session in memory
            if self.memory:
                try:
                    self.memory.store_session(
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
                except Exception as e:
                    # Memory storage failures shouldn't break execution
                    logger.debug(
                        f"Failed to store failed execution in memory for '{agent_name}': {e}"
                    )

            return AgentResult(
                agent_name=agent_name,
                success=False,
                output="",
                metadata={"execution_time_ms": execution_time_ms},
                errors=[str(e)],
            )

    def run_workflow(
        self, workflow_name: str, task: str, pass_output_to_next: bool = True
    ) -> List[AgentResult]:
        """
        Run a multi-agent workflow.

        Args:
            workflow_name: Name of workflow (e.g., "full-stack-feature")
            task: Initial task description
            pass_output_to_next: Whether to pass each agent's output to the next

        Returns:
            List of AgentResult objects, one per agent

        Example:
            results = orchestrator.run_workflow(
                "bug-fix",
                task="Investigate 500 error in /api/users endpoint"
            )
            for result in results:
                print(f"{result.agent_name}: {result.success}")
        """
        workflow = self.config["workflows"].get(workflow_name)
        if workflow is None:
            all_workflows = list(self.config["workflows"].keys())
            raise ValueError(format_workflow_not_found_error(workflow_name, all_workflows))

        results = []
        current_task = task

        for i, agent_name in enumerate(workflow):
            print(f"Running agent {i + 1}/{len(workflow)}: {agent_name}...")

            result = self.run_agent(
                agent_name,
                current_task,
                workflow_name=workflow_name,
                workflow_position=i + 1,
            )
            results.append(result)

            if not result.success:
                print(f"❌ Agent {agent_name} failed: {result.errors}")
                break

            print(f"✓ Agent {agent_name} completed")

            # Pass output to next agent
            if pass_output_to_next and result.success:
                current_task = f"""
# Previous Agent Output

Agent: {agent_name}

Output:
{result.output}

# Your Task

Continue from the previous agent's output. Original task: {task}
"""

        return results

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        agents = []
        for name, config in self.config["agents"].items():
            agents.append(
                {
                    "name": name,
                    "file": config.get("file", ""),
                    "domains": config.get("domains", []),
                    "priority": config.get("priority", 3),
                }
            )
        return sorted(agents, key=lambda x: x["priority"])

    def list_workflows(self) -> Dict[str, List[str]]:
        """List all available workflows"""
        return self.config.get("workflows", {})

    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed information about an agent"""
        if agent_name not in self.config["agents"]:
            all_agents = list(self.config["agents"].keys())
            raise ValueError(format_agent_not_found_error(agent_name, all_agents))

        agent_config = self.config["agents"][agent_name]

        # Try to load agent definition to extract role
        try:
            definition = self._load_agent_definition(agent_name)
            # Extract first few lines as description
            lines = definition.split("\n")[:10]
            description = "\n".join(lines)
        except Exception as e:
            logger.warning(f"Could not load description for agent '{agent_name}': {e}")
            description = "No description available"

        return {
            "name": agent_name,
            "file": agent_config.get("file", ""),
            "contract": agent_config.get("contract", ""),
            "domains": agent_config.get("domains", []),
            "priority": agent_config.get("priority", 3),
            "description": description,
        }

    def recommend_agents(
        self, task: str, top_k: int = 3, min_confidence: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Recommend agents for a task using semantic similarity.

        Uses embeddings-based matching for intelligent agent selection with
        confidence scores. Requires sentence-transformers package.

        Args:
            task: Task description
            top_k: Number of agents to recommend (default: 3)
            min_confidence: Minimum confidence threshold 0-1 (default: 0.3)

        Returns:
            List of agent recommendations with confidence scores

        Example:
            recommendations = orchestrator.recommend_agents(
                "Review authentication code for security issues",
                top_k=3
            )
            for rec in recommendations:
                print(f"{rec['agent']}: {rec['confidence']:.2f} - {rec['reasoning']}")

        Raises:
            ImportError: If sentence-transformers not installed
        """
        try:
            from claude_force.semantic_selector import SemanticAgentSelector
        except ImportError:
            raise ImportError(
                format_missing_dependency_error(
                    "sentence-transformers", "pip install sentence-transformers"
                )
            )

        selector = SemanticAgentSelector(config_path=str(self.config_path))
        matches = selector.select_agents(task, top_k=top_k, min_confidence=min_confidence)

        return [
            {
                "agent": match.agent_name,
                "confidence": round(match.confidence, 3),
                "reasoning": match.reasoning,
                "domains": match.domains,
                "priority": match.priority,
            }
            for match in matches
        ]

    def explain_agent_selection(self, task: str, agent_name: str) -> Dict[str, Any]:
        """
        Explain why a specific agent was or wasn't recommended for a task.

        Args:
            task: Task description
            agent_name: Agent to explain

        Returns:
            Dictionary with explanation details

        Example:
            explanation = orchestrator.explain_agent_selection(
                "Fix bug in login endpoint",
                "bug-investigator"
            )
            print(f"Selected: {explanation['selected']}")
            print(f"Rank: {explanation['rank']}")
            print(f"Confidence: {explanation['confidence']}")

        Raises:
            ImportError: If sentence-transformers not installed
        """
        try:
            from claude_force.semantic_selector import SemanticAgentSelector
        except ImportError:
            raise ImportError(
                format_missing_dependency_error(
                    "sentence-transformers", "pip install sentence-transformers"
                )
            )

        selector = SemanticAgentSelector(config_path=str(self.config_path))
        return selector.explain_selection(task, agent_name)

    def get_performance_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get performance summary statistics.

        Args:
            hours: Only include last N hours (None for all time)

        Returns:
            Dictionary with summary statistics

        Example:
            summary = orchestrator.get_performance_summary(hours=24)
            print(f"Success rate: {summary['success_rate']:.2%}")
            print(f"Total cost: ${summary['total_cost']:.4f}")
        """
        if not self.tracker:
            raise RuntimeError(format_tracking_not_enabled_error())

        return self.tracker.get_summary(hours)

    def get_agent_performance(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics by agent.

        Args:
            agent_name: Specific agent (None for all agents)

        Returns:
            Dictionary with per-agent statistics

        Example:
            stats = orchestrator.get_agent_performance("code-reviewer")
            print(f"Executions: {stats['code-reviewer']['executions']}")
            print(f"Success rate: {stats['code-reviewer']['success_rate']:.2%}")
        """
        if not self.tracker:
            raise RuntimeError(format_tracking_not_enabled_error())

        return self.tracker.get_agent_stats(agent_name)

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """
        Get cost breakdown by agent and model.

        Returns:
            Dictionary with cost breakdown

        Example:
            costs = orchestrator.get_cost_breakdown()
            print(f"Total cost: ${costs['total']:.4f}")
            for agent, cost in costs['by_agent'].items():
                print(f"  {agent}: ${cost:.4f}")
        """
        if not self.tracker:
            raise RuntimeError(format_tracking_not_enabled_error())

        return self.tracker.get_cost_breakdown()

    def export_performance_metrics(self, output_path: str, format: str = "json"):
        """
        Export performance metrics to file.

        Args:
            output_path: Path to output file
            format: Export format ("json" or "csv")

        Example:
            orchestrator.export_performance_metrics("metrics.json", "json")
            orchestrator.export_performance_metrics("metrics.csv", "csv")
        """
        if not self.tracker:
            raise RuntimeError(format_tracking_not_enabled_error())

        if format == "json":
            self.tracker.export_json(output_path)
        elif format == "csv":
            self.tracker.export_csv(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    # TÂCHES Integration - Workflow Management Services

    @property
    def todos(self):
        """
        Lazy load TodoManager service.

        Provides todo management with AI-optimized task capture.

        Example:
            todo = TodoItem(action="Fix bug", problem="Login fails", ...)
            orchestrator.todos.add_todo(todo)
            todos = orchestrator.todos.get_todos()
        """
        if not hasattr(self, "_todo_manager"):
            self._todo_manager = None

        if self._todo_manager is None:
            try:
                from claude_force.services.todo_manager import TodoManager
                from claude_force.response_cache import ResponseCache

                # Get semantic selector if available
                semantic_selector = None
                try:
                    from claude_force.semantic_selector import SemanticAgentSelector

                    semantic_selector = SemanticAgentSelector()
                except Exception as e:
                    logger.debug(f"SemanticAgentSelector unavailable: {e}")

                self._todo_manager = TodoManager(
                    cache=ResponseCache(), semantic_selector=semantic_selector
                )
            except Exception as e:
                logger.warning(f"TodoManager initialization failed: {e}")

        return self._todo_manager

    @property
    def handoffs(self):
        """
        Lazy load HandoffGenerator service.

        Provides session handoff generation for continuity.

        Example:
            handoff = orchestrator.handoffs.generate_handoff()
            path = orchestrator.handoffs.save_handoff(handoff)
        """
        if not hasattr(self, "_handoff_generator"):
            self._handoff_generator = None

        if self._handoff_generator is None:
            try:
                from claude_force.services.handoff_generator import HandoffGenerator

                self._handoff_generator = HandoffGenerator(self)
            except Exception as e:
                logger.warning(f"HandoffGenerator initialization failed: {e}")

        return self._handoff_generator

    @property
    def meta_prompt(self):
        """
        Lazy load MetaPrompter service.

        Provides meta-prompting with governance validation.

        Example:
            request = MetaPromptRequest(objective="Build auth system")
            response = orchestrator.meta_prompt.generate_workflow(request)
        """
        if not hasattr(self, "_meta_prompter"):
            self._meta_prompter = None

        if self._meta_prompter is None:
            try:
                from claude_force.services.meta_prompter import MetaPrompter

                self._meta_prompter = MetaPrompter(self)
            except Exception as e:
                logger.warning(f"MetaPrompter initialization failed: {e}")

        return self._meta_prompter

    # Helper methods for TÂCHES services

    def get_available_skills(self) -> List[str]:
        """
        Get list of available skills.

        Returns:
            List of skill names

        Example:
            skills = orchestrator.get_available_skills()
            print(f"Available: {', '.join(skills)}")
        """
        skills = []

        # Check .claude/skills directory
        skills_dir = self.config_path.parent / "skills"
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    skills.append(skill_dir.name)

        return skills
