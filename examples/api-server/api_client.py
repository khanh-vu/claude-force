#!/usr/bin/env python3
"""
API Client Example for Claude-Force REST API

Demonstrates how to interact with the claude-force API server.
"""

import time
import requests
from typing import Optional, Dict, Any


class ClaudeForceClient:
    """Client for Claude-Force REST API"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "dev-key-12345"):
        """
        Initialize client

        Args:
            base_url: API server URL
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def list_agents(self) -> Dict[str, Any]:
        """List all available agents"""
        response = requests.get(f"{self.base_url}/agents", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def recommend_agents(self, task: str, top_k: int = 3, min_confidence: float = 0.3) -> list:
        """Get agent recommendations for a task"""
        response = requests.post(
            f"{self.base_url}/agents/recommend",
            headers=self.headers,
            json={"task": task, "top_k": top_k, "min_confidence": min_confidence},
        )
        response.raise_for_status()
        return response.json()

    def run_agent_sync(
        self,
        agent_name: str,
        task: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> Dict[str, Any]:
        """Run an agent synchronously (waits for completion)"""
        response = requests.post(
            f"{self.base_url}/agents/run",
            headers=self.headers,
            json={
                "agent_name": agent_name,
                "task": task,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()
        return response.json()

    def run_agent_async(
        self,
        agent_name: str,
        task: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> str:
        """
        Run an agent asynchronously (returns immediately)

        Returns:
            task_id: ID to check status later
        """
        response = requests.post(
            f"{self.base_url}/agents/run/async",
            headers=self.headers,
            json={
                "agent_name": agent_name,
                "task": task,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()
        return response.json()["task_id"]

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of an async task"""
        response = requests.get(f"{self.base_url}/tasks/{task_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def wait_for_task(
        self, task_id: str, poll_interval: float = 2.0, timeout: float = 300.0
    ) -> Dict[str, Any]:
        """
        Wait for an async task to complete

        Args:
            task_id: Task ID to wait for
            poll_interval: Seconds between status checks
            timeout: Max seconds to wait

        Returns:
            Final task result

        Raises:
            TimeoutError: If task doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            status = self.get_task_status(task_id)

            if status["status"] in ["completed", "failed"]:
                return status

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

            time.sleep(poll_interval)

    def run_workflow(
        self, workflow_name: str, task: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> Dict[str, Any]:
        """Run a multi-agent workflow"""
        response = requests.post(
            f"{self.base_url}/workflows/run",
            headers=self.headers,
            json={"workflow_name": workflow_name, "task": task, "model": model},
        )
        response.raise_for_status()
        return response.json()

    def get_metrics_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Get performance metrics summary"""
        params = {"hours": hours} if hours else {}
        response = requests.get(
            f"{self.base_url}/metrics/summary", headers=self.headers, params=params
        )
        response.raise_for_status()
        return response.json()

    def get_agent_metrics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get per-agent performance metrics"""
        params = {"agent_name": agent_name} if agent_name else {}
        response = requests.get(
            f"{self.base_url}/metrics/agents", headers=self.headers, params=params
        )
        response.raise_for_status()
        return response.json()

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get cost breakdown"""
        response = requests.get(f"{self.base_url}/metrics/costs", headers=self.headers)
        response.raise_for_status()
        return response.json()


def main():
    """Example usage"""
    print("=" * 70)
    print("CLAUDE-FORCE API CLIENT EXAMPLE")
    print("=" * 70 + "\n")

    # Initialize client
    client = ClaudeForceClient(base_url="http://localhost:8000", api_key="dev-key-12345")

    # 1. Health check
    print("1. Health Check")
    print("-" * 70)
    health = client.health_check()
    print(f"Status: {health['status']}")
    print(f"Orchestrator: {'✅' if health['orchestrator'] else '❌'}")
    print()

    # 2. List agents
    print("2. List Available Agents")
    print("-" * 70)
    agents = client.list_agents()
    print(f"Found {agents['count']} agents:")
    for agent in agents["agents"][:5]:
        print(f"  - {agent}")
    print()

    # 3. Get recommendations
    print("3. Agent Recommendations")
    print("-" * 70)
    task = "Review authentication code for security vulnerabilities"
    print(f"Task: {task}\n")

    recommendations = client.recommend_agents(task, top_k=3)
    for rec in recommendations:
        confidence = rec["confidence"] * 100
        print(f"  {rec['agent']}: {confidence:.1f}% confidence")
        print(f"    Reasoning: {rec['reasoning'][:80]}...")
    print()

    # 4. Run agent synchronously
    print("4. Synchronous Agent Execution")
    print("-" * 70)
    print("Running code-reviewer agent (this will wait for completion)...\n")

    result = client.run_agent_sync(
        agent_name="code-reviewer",
        task="Review this code:\ndef login(user, pwd): return user == 'admin'",
        model="claude-3-5-sonnet-20241022",
    )

    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time_ms']:.0f}ms")
    print(f"Output (first 200 chars): {result['output'][:200]}...")
    print()

    # 5. Run agent asynchronously
    print("5. Asynchronous Agent Execution")
    print("-" * 70)
    print("Submitting task asynchronously...\n")

    task_id = client.run_agent_async(
        agent_name="bug-investigator",
        task="Investigate: Users getting 500 errors on /api/users endpoint",
    )

    print(f"Task ID: {task_id}")
    print("Task submitted, checking status...\n")

    # Poll for completion
    print("Waiting for task to complete...")
    result = client.wait_for_task(task_id, poll_interval=2.0, timeout=60.0)

    print(f"Status: {result['status']}")
    if result["result"]:
        print(f"Success: {result['result']['success']}")
        print(f"Output: {result['result']['output'][:200]}...")
    print()

    # 6. Run workflow
    print("6. Workflow Execution")
    print("-" * 70)
    print("Running code-quality-gate workflow...\n")

    try:
        workflow_result = client.run_workflow(
            workflow_name="code-quality-gate", task="Review and test the authentication module"
        )

        print(f"Success: {workflow_result['success']}")
        print(f"Execution time: {workflow_result['execution_time_ms']:.0f}ms")
        print(f"Agents involved: {len(workflow_result['metadata'].get('workflow_steps', []))}")
    except requests.exceptions.HTTPError as e:
        print(f"Workflow not found or error: {e}")
    print()

    # 7. Get metrics
    print("7. Performance Metrics")
    print("-" * 70)

    summary = client.get_metrics_summary()
    print(f"Total Executions: {summary.get('total_executions', 0)}")
    print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
    print(f"Total Cost: ${summary.get('total_cost', 0):.4f}")
    print(f"Avg Execution Time: {summary.get('avg_execution_time_ms', 0):.0f}ms")
    print()

    # 8. Agent-specific metrics
    print("8. Agent Performance")
    print("-" * 70)

    agent_metrics = client.get_agent_metrics()
    print(f"{'Agent':<30} {'Runs':>8} {'Success':>10} {'Cost':>12}")
    print("-" * 70)

    for agent, data in list(agent_metrics.items())[:5]:
        runs = data.get("executions", 0)
        success_rate = data.get("success_rate", 0)
        cost = data.get("total_cost", 0)
        print(f"{agent:<30} {runs:>8} {success_rate:>9.1%} ${cost:>10.4f}")
    print()

    print("=" * 70)
    print("✅ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
