"""
Example: Creating a Custom Orchestrator

This example demonstrates how to create a custom orchestrator by extending
BaseOrchestrator. Custom orchestrators can implement specialized logic for:

- Custom routing strategies
- Integration with external systems
- Specialized caching/tracking
- Custom execution pipelines

This example shows:
1. How to extend BaseOrchestrator
2. How to implement required abstract methods
3. How to add custom functionality
4. How to use the custom orchestrator
"""

from typing import Dict, List, Any, Optional
from claude_force.base import BaseOrchestrator, AgentResult
import anthropic
import os


class LoggingOrchestrator(BaseOrchestrator):
    """
    Custom orchestrator that logs all agent executions to a file.

    This example demonstrates:
    - Extending BaseOrchestrator
    - Adding custom initialization
    - Wrapping agent execution with custom logic
    - Implementing all required abstract methods
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        log_file: str = "agent_executions.log",
    ):
        """
        Initialize logging orchestrator.

        Args:
            api_key: Anthropic API key
            log_file: Path to log file
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.log_file = log_file

        # Simple agent registry
        self.agents = {
            "code-reviewer": {
                "name": "code-reviewer",
                "priority": 1,
                "domains": ["code", "review"],
                "prompt": "You are an expert code reviewer. Review the following code and provide feedback.",
            },
            "python-expert": {
                "name": "python-expert",
                "priority": 1,
                "domains": ["python", "code"],
                "prompt": "You are a Python expert. Help with the following Python task.",
            },
        }

        self._log("Logging orchestrator initialized")

    def _log(self, message: str):
        """Write message to log file."""
        with open(self.log_file, "a") as f:
            from datetime import datetime

            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] {message}\n")

    def run_agent(
        self, agent_name: str, task: str, **kwargs
    ) -> AgentResult:
        """
        Execute agent with logging.

        Args:
            agent_name: Name of agent to run
            task: Task description
            **kwargs: Additional parameters (model, max_tokens, etc.)

        Returns:
            AgentResult with execution outcome
        """
        self._log(f"Starting agent: {agent_name}")
        self._log(f"Task: {task[:100]}...")

        try:
            # Get agent config
            if agent_name not in self.agents:
                error_msg = f"Agent '{agent_name}' not found"
                self._log(f"ERROR: {error_msg}")
                return AgentResult(
                    success=False,
                    output="",
                    errors=[error_msg],
                    metadata={},
                    agent_name=agent_name,
                )

            agent_config = self.agents[agent_name]

            # Prepare prompt
            system_prompt = agent_config["prompt"]
            model = kwargs.get("model", "claude-3-haiku-20240307")
            max_tokens = kwargs.get("max_tokens", 4096)

            self._log(f"Using model: {model}")

            # Call Claude API
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": task}],
            )

            # Extract output
            output = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output += block.text

            # Log success
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            self._log(f"SUCCESS: {agent_name} completed (tokens: {tokens_used})")

            return AgentResult(
                success=True,
                output=output,
                errors=[],
                metadata={
                    "model": model,
                    "tokens_used": tokens_used,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                agent_name=agent_name,
            )

        except Exception as e:
            error_msg = str(e)
            self._log(f"ERROR: {agent_name} failed - {error_msg}")

            return AgentResult(
                success=False,
                output="",
                errors=[error_msg],
                metadata={},
                agent_name=agent_name,
            )

    def run_workflow(
        self, workflow_name: str, task: str, **kwargs
    ) -> List[AgentResult]:
        """
        Execute workflow with logging.

        Args:
            workflow_name: Name of workflow
            task: Task description
            **kwargs: Additional parameters

        Returns:
            List of AgentResult objects
        """
        self._log(f"Starting workflow: {workflow_name}")

        # Define workflows
        workflows = {
            "code-review": ["code-reviewer"],
            "python-dev": ["python-expert", "code-reviewer"],
        }

        if workflow_name not in workflows:
            self._log(f"ERROR: Workflow '{workflow_name}' not found")
            return []

        agent_names = workflows[workflow_name]
        results = []

        for agent_name in agent_names:
            result = self.run_agent(agent_name, task, **kwargs)
            results.append(result)

            # Stop on failure
            if not result.success:
                self._log(f"Workflow stopped due to failure in {agent_name}")
                break

        self._log(f"Workflow completed: {workflow_name}")
        return results

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all available agents.

        Returns:
            List of agent dictionaries
        """
        return list(self.agents.values())

    def list_workflows(self) -> Dict[str, List[str]]:
        """
        List all available workflows.

        Returns:
            Dictionary mapping workflow names to agent lists
        """
        return {
            "code-review": ["code-reviewer"],
            "python-dev": ["python-expert", "code-reviewer"],
        }


class RetryOrchestrator(BaseOrchestrator):
    """
    Custom orchestrator with automatic retry logic.

    This example demonstrates:
    - Adding retry functionality
    - Wrapping another orchestrator
    - Custom error handling
    """

    def __init__(
        self,
        base_orchestrator: BaseOrchestrator,
        max_retries: int = 3,
    ):
        """
        Initialize retry orchestrator.

        Args:
            base_orchestrator: Underlying orchestrator to wrap
            max_retries: Maximum number of retry attempts
        """
        self.base = base_orchestrator
        self.max_retries = max_retries

    def run_agent(
        self, agent_name: str, task: str, **kwargs
    ) -> AgentResult:
        """
        Execute agent with automatic retry on failure.

        Args:
            agent_name: Agent name
            task: Task description
            **kwargs: Additional parameters

        Returns:
            AgentResult
        """
        last_result = None

        for attempt in range(self.max_retries):
            result = self.base.run_agent(agent_name, task, **kwargs)

            if result.success:
                # Success on first try or after retries
                if attempt > 0:
                    result.metadata["retry_count"] = attempt
                return result

            last_result = result
            print(f"Attempt {attempt + 1}/{self.max_retries} failed, retrying...")

        # All retries exhausted
        if last_result:
            last_result.metadata["retry_count"] = self.max_retries
            last_result.errors.append(
                f"Failed after {self.max_retries} retry attempts"
            )

        return last_result

    def run_workflow(
        self, workflow_name: str, task: str, **kwargs
    ) -> List[AgentResult]:
        """Execute workflow (delegates to base)."""
        return self.base.run_workflow(workflow_name, task, **kwargs)

    def list_agents(self) -> List[Dict[str, Any]]:
        """List agents (delegates to base)."""
        return self.base.list_agents()

    def list_workflows(self) -> Dict[str, List[str]]:
        """List workflows (delegates to base)."""
        return self.base.list_workflows()


# Example usage
if __name__ == "__main__":
    print("=== Custom Orchestrator Examples ===\n")

    # Example 1: LoggingOrchestrator
    print("1. Using LoggingOrchestrator:")
    print("-" * 50)

    logger_orch = LoggingOrchestrator(log_file="example_executions.log")

    # List agents
    agents = logger_orch.list_agents()
    print(f"\nAvailable agents: {len(agents)}")
    for agent in agents:
        print(f"  - {agent['name']}: {agent['domains']}")

    # Run an agent
    result = logger_orch.run_agent(
        "python-expert",
        "Write a function to calculate fibonacci numbers",
        model="claude-3-haiku-20240307",
    )

    if result.success:
        print(f"\n✓ Success!")
        print(f"Output: {result.output[:200]}...")
        print(f"Tokens used: {result.metadata['tokens_used']}")
    else:
        print(f"\n✗ Failed: {result.errors}")

    print("\nCheck 'example_executions.log' for detailed logs")

    # Example 2: RetryOrchestrator
    print("\n2. Using RetryOrchestrator:")
    print("-" * 50)

    # Wrap the logging orchestrator with retry logic
    retry_orch = RetryOrchestrator(
        base_orchestrator=logger_orch,
        max_retries=3,
    )

    # This will use the retry logic
    result = retry_orch.run_agent(
        "code-reviewer",
        "Review this Python code: def add(a, b): return a + b",
    )

    if result.success:
        print(f"\n✓ Success!")
        if "retry_count" in result.metadata:
            print(f"Succeeded after {result.metadata['retry_count']} retries")
    else:
        print(f"\n✗ Failed: {result.errors}")

    # Example 3: Run workflow
    print("\n3. Running workflow:")
    print("-" * 50)

    results = logger_orch.run_workflow(
        "python-dev",
        "Create a function to validate email addresses",
    )

    print(f"\nWorkflow completed: {len(results)} agents executed")
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        print(f"  {status} Agent {i} ({result.agent_name}): {result.success}")

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nKey takeaways:")
    print("1. Extend BaseOrchestrator for custom orchestrators")
    print("2. Implement all 4 abstract methods")
    print("3. Add your custom logic in run_agent/run_workflow")
    print("4. Wrap orchestrators for composition (e.g., RetryOrchestrator)")
