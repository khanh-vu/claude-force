#!/usr/bin/env python3
"""
MCP Client Example for Claude-Force

Demonstrates how to interact with the Claude-Force MCP server using HTTP requests.

Usage:
    # Start MCP server first (in another terminal):
    python -m claude_force.mcp_server --port 8080

    # Then run this client:
    python examples/mcp/mcp_client_example.py
"""

import requests
import json
import sys
from typing import Dict, Any, Optional


class MCPClient:
    """Simple MCP client for Claude-Force"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize MCP client

        Args:
            base_url: MCP server URL
        """
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def list_capabilities(self) -> Dict[str, Any]:
        """List all available capabilities"""
        response = requests.get(f"{self.base_url}/capabilities")
        response.raise_for_status()
        return response.json()

    def execute_agent(
        self,
        agent_name: str,
        task: str,
        model: str = "claude-3-5-sonnet-20241022",
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an agent via MCP

        Args:
            agent_name: Name of the agent
            task: Task description
            model: Claude model to use
            request_id: Optional request ID for tracking

        Returns:
            MCP response dictionary
        """
        payload = {
            "capability": agent_name,
            "action": "execute_agent",
            "parameters": {"task": task, "model": model},
        }

        if request_id:
            payload["request_id"] = request_id

        response = requests.post(
            f"{self.base_url}/execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        response.raise_for_status()
        return response.json()

    def execute_workflow(
        self, workflow_name: str, task: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> Dict[str, Any]:
        """Execute a workflow via MCP"""
        payload = {
            "capability": workflow_name,
            "action": "execute_workflow",
            "parameters": {"task": task, "model": model},
        }

        response = requests.post(
            f"{self.base_url}/execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        response.raise_for_status()
        return response.json()

    def recommend_agents(
        self, task: str, top_k: int = 3, min_confidence: float = 0.3
    ) -> Dict[str, Any]:
        """Get agent recommendations via MCP"""
        payload = {
            "capability": "recommend-agents",
            "action": "recommend_agents",
            "parameters": {"task": task, "top_k": top_k, "min_confidence": min_confidence},
        }

        response = requests.post(
            f"{self.base_url}/execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        response.raise_for_status()
        return response.json()

    def get_performance_summary(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Get performance metrics via MCP"""
        payload = {
            "capability": "performance-summary",
            "action": "get_performance",
            "parameters": {},
        }

        if hours is not None:
            payload["parameters"]["hours"] = hours

        response = requests.post(
            f"{self.base_url}/execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of MCP client"""
    print("=" * 70)
    print("CLAUDE-FORCE MCP CLIENT EXAMPLE")
    print("=" * 70)
    print()

    # Initialize client
    client = MCPClient(base_url="http://localhost:8080")

    try:
        # 1. Health check
        print("1. Health Check")
        print("-" * 70)
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Server: {health['server']}")
        print(f"Version: {health['version']}")
        print(f"Capabilities: {health['capabilities']}")
        print()

        # 2. List capabilities
        print("2. List Capabilities")
        print("-" * 70)
        caps = client.list_capabilities()
        print(f"Total capabilities: {caps['count']}")
        print()

        # Show first 5 capabilities
        print("Sample capabilities:")
        for cap in caps["capabilities"][:5]:
            print(f"  - {cap['name']} ({cap['type']})")
            print(f"    {cap['description']}")
        print()

        # 3. Recommend agents
        print("3. Agent Recommendations")
        print("-" * 70)
        task = "Review authentication code for SQL injection vulnerabilities"
        print(f"Task: {task}\n")

        try:
            recommendations = client.recommend_agents(task, top_k=3)

            if recommendations["success"]:
                print("Recommendations:")
                for rec in recommendations["data"]["recommendations"]:
                    confidence = rec["confidence"] * 100
                    print(f"  • {rec['agent']}: {confidence:.1f}% confidence")
                    print(f"    Reasoning: {rec['reasoning'][:80]}...")
            else:
                print(f"Error: {recommendations['error']}")
        except Exception as e:
            print(f"Semantic selection not available: {e}")
        print()

        # 4. Execute agent
        print("4. Execute Agent (code-reviewer)")
        print("-" * 70)
        print("Executing agent with simple task...\n")

        code_task = """Review this Python code for security issues:

def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    return cursor.fetchone()
"""

        result = client.execute_agent(
            agent_name="code-reviewer", task=code_task, request_id="demo-001"
        )

        print(f"Success: {result['success']}")
        print(f"Request ID: {result['request_id']}")

        if result["success"]:
            print("\nAgent Output (first 300 chars):")
            print(result["data"]["output"][:300] + "...")
            print(f"\nExecution time: {result['metadata']['execution_time']:.0f}ms")
        else:
            print(f"Error: {result['error']}")
        print()

        # 5. Get performance metrics
        print("5. Performance Metrics")
        print("-" * 70)

        try:
            perf = client.get_performance_summary()

            if perf["success"]:
                summary = perf["data"]
                print(f"Total executions: {summary.get('total_executions', 0)}")
                print(f"Success rate: {summary.get('success_rate', 0):.1%}")
                print(f"Total cost: ${summary.get('total_cost', 0):.4f}")
                print(f"Avg execution time: {summary.get('avg_execution_time_ms', 0):.0f}ms")
        except Exception as e:
            print(f"Performance tracking not available: {e}")
        print()

        # 6. Execute workflow (optional - may take longer)
        print("6. Execute Workflow (Optional)")
        print("-" * 70)
        print("Skipping workflow execution in this demo (can be slow)")
        print("To execute a workflow:")
        print('  result = client.execute_workflow("bug-fix", "Investigate login issue")')
        print()

        print("=" * 70)
        print("✅ MCP Client example completed successfully!")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to MCP server")
        print()
        print("Please start the MCP server first:")
        print("  python -m claude_force.mcp_server --port 8080")
        print()
        print("Then run this example again:")
        print("  python examples/mcp/mcp_client_example.py")
        return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
