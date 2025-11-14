"""
MCP (Model Context Protocol) Server for Claude-Force

Exposes claude-force agents as an MCP server for integration with Claude Code
and other MCP-compatible clients.

The Model Context Protocol is a standard for AI agent communication that allows
clients to discover and interact with agent capabilities programmatically.

Usage:
    # Start MCP server
    python -m claude_force.mcp_server --port 8080

    # Or programmatically:
    from claude_force.mcp_server import MCPServer
    server = MCPServer()
    server.start(port=8080)
"""

import json
import logging
import os
import secrets
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from collections import defaultdict, deque

from .orchestrator import AgentOrchestrator, AgentResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API requests

    Limits requests per IP address using a sliding window approach.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds (default: 1 hour)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)  # IP -> deque of timestamps
        self._lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed for this IP

        Args:
            client_ip: Client IP address

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        with self._lock:
            current_time = time.time()
            client_requests = self.requests[client_ip]

            # Remove old requests outside the window
            while client_requests and client_requests[0] < current_time - self.window_seconds:
                client_requests.popleft()

            # Check if limit exceeded
            if len(client_requests) >= self.max_requests:
                # Calculate when the oldest request will expire
                retry_after = int(client_requests[0] + self.window_seconds - current_time) + 1
                return False, retry_after

            # Allow request and record timestamp
            client_requests.append(current_time)
            return True, None

    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for this IP"""
        with self._lock:
            current_time = time.time()
            client_requests = self.requests[client_ip]

            # Remove old requests
            while client_requests and client_requests[0] < current_time - self.window_seconds:
                client_requests.popleft()

            return max(0, self.max_requests - len(client_requests))


@dataclass
class MCPCapability:
    """MCP capability definition"""

    name: str
    type: str  # "agent", "workflow", "skill"
    description: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class MCPRequest:
    """MCP request structure"""

    capability: str
    action: str
    parameters: Dict[str, Any]
    request_id: Optional[str] = None


@dataclass
class MCPResponse:
    """MCP response structure"""

    success: bool
    request_id: Optional[str]
    data: Optional[Any]
    error: Optional[str]
    metadata: Dict[str, Any]


class MCPServer:
    """
    MCP Server for Claude-Force

    Exposes agents, workflows, and capabilities via the Model Context Protocol.
    """

    def __init__(
        self,
        orchestrator: Optional[AgentOrchestrator] = None,
        config_path: str = ".claude/claude.json",
        anthropic_api_key: Optional[str] = None,
        mcp_api_key: Optional[str] = None,
        allowed_origins: Optional[List[str]] = None,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 3600,
    ):
        """
        Initialize MCP server

        Args:
            orchestrator: Existing AgentOrchestrator instance (optional)
            config_path: Path to claude.json configuration
            anthropic_api_key: Anthropic API key (optional)
            mcp_api_key: MCP server API key for authentication (optional, generated if not provided)
            allowed_origins: List of allowed CORS origins (default: localhost only)
            rate_limit_requests: Maximum requests per window (default: 100)
            rate_limit_window: Rate limit window in seconds (default: 3600 = 1 hour)
        """
        self.orchestrator = orchestrator or AgentOrchestrator(
            config_path=config_path, anthropic_api_key=anthropic_api_key
        )
        # Generate or use provided MCP API key
        self.mcp_api_key = mcp_api_key or os.getenv("MCP_API_KEY") or self._generate_api_key()
        if not mcp_api_key and not os.getenv("MCP_API_KEY"):
            # Only log first 8 chars of key to prevent secret exposure in logs
            masked_key = f"{self.mcp_api_key[:8]}...{self.mcp_api_key[-4:]}"
            logger.warning(
                f"MCP API key auto-generated (key starts with: {masked_key})\n"
                "Set MCP_API_KEY environment variable or pass mcp_api_key parameter for production use.\n"
                "IMPORTANT: Save this key securely - it will not be shown again."
            )
        # Configure CORS origins
        self.allowed_origins = allowed_origins or ["http://localhost:3000", "http://localhost:8080"]
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=rate_limit_requests, window_seconds=rate_limit_window
        )
        self.server_instance = None
        self.server_thread = None

    def _generate_api_key(self) -> str:
        """Generate a secure random API key"""
        return secrets.token_urlsafe(32)

    def _verify_api_key(self, provided_key: str) -> bool:
        """
        Verify API key using constant-time comparison

        Args:
            provided_key: API key from request

        Returns:
            True if valid, False otherwise
        """
        if not provided_key or not self.mcp_api_key:
            return False
        return secrets.compare_digest(provided_key, self.mcp_api_key)

    def _get_allowed_origin(self, origin: Optional[str]) -> str:
        """
        Get allowed origin for CORS or None

        Args:
            origin: Origin header from request

        Returns:
            Allowed origin or first allowed origin if none match
        """
        if not origin:
            return self.allowed_origins[0] if self.allowed_origins else "http://localhost:3000"

        # Check if origin is in allowed list
        if origin in self.allowed_origins:
            return origin

        # Default to first allowed origin
        return self.allowed_origins[0] if self.allowed_origins else "http://localhost:3000"

    def get_capabilities(self) -> List[MCPCapability]:
        """
        List all available MCP capabilities

        Returns:
            List of MCPCapability objects
        """
        capabilities = []

        # Add agents as capabilities
        for agent_name in self.orchestrator.list_agents():
            agent_info = self.orchestrator.get_agent_info(agent_name)
            capabilities.append(
                MCPCapability(
                    name=agent_name,
                    type="agent",
                    description=agent_info.get("description", f"Agent: {agent_name}"),
                    parameters={
                        "task": {
                            "type": "string",
                            "required": True,
                            "description": "Task description for the agent",
                        },
                        "model": {
                            "type": "string",
                            "required": False,
                            "default": "claude-3-5-sonnet-20241022",
                            "description": "Claude model to use",
                        },
                        "max_tokens": {
                            "type": "integer",
                            "required": False,
                            "default": 4096,
                            "description": "Maximum tokens in response",
                        },
                    },
                    metadata={
                        "domains": agent_info.get("domains", []),
                        "priority": agent_info.get("priority", 5),
                    },
                )
            )

        # Add workflows as capabilities
        for workflow_name in self.orchestrator.list_workflows():
            capabilities.append(
                MCPCapability(
                    name=workflow_name,
                    type="workflow",
                    description=f"Multi-agent workflow: {workflow_name}",
                    parameters={
                        "task": {
                            "type": "string",
                            "required": True,
                            "description": "Initial task for the workflow",
                        },
                        "model": {
                            "type": "string",
                            "required": False,
                            "default": "claude-3-5-sonnet-20241022",
                        },
                    },
                    metadata={
                        "agents": self.orchestrator.config.get("workflows", {}).get(
                            workflow_name, []
                        )
                    },
                )
            )

        # Add special capabilities
        capabilities.append(
            MCPCapability(
                name="recommend-agents",
                type="skill",
                description="Recommend agents using semantic similarity",
                parameters={
                    "task": {
                        "type": "string",
                        "required": True,
                        "description": "Task description for recommendation",
                    },
                    "top_k": {
                        "type": "integer",
                        "required": False,
                        "default": 3,
                        "description": "Number of recommendations",
                    },
                    "min_confidence": {
                        "type": "number",
                        "required": False,
                        "default": 0.3,
                        "description": "Minimum confidence threshold",
                    },
                },
                metadata={"requires": "semantic-selection"},
            )
        )

        capabilities.append(
            MCPCapability(
                name="performance-summary",
                type="skill",
                description="Get performance metrics summary",
                parameters={
                    "hours": {
                        "type": "integer",
                        "required": False,
                        "description": "Filter metrics from last N hours",
                    }
                },
                metadata={"requires": "performance-tracking"},
            )
        )

        return capabilities

    def execute_capability(self, request: MCPRequest) -> MCPResponse:
        """
        Execute an MCP capability

        Args:
            request: MCPRequest object

        Returns:
            MCPResponse object
        """
        try:
            capability_name = request.capability
            action = request.action
            params = request.parameters

            # Handle agent execution
            if action == "execute_agent":
                result = self.orchestrator.run_agent(
                    agent_name=capability_name,
                    task=params.get("task", ""),
                    model=params.get("model", "claude-3-5-sonnet-20241022"),
                    max_tokens=params.get("max_tokens", 4096),
                    temperature=params.get("temperature", 1.0),
                )

                return MCPResponse(
                    success=result.success,
                    request_id=request.request_id,
                    data={"output": result.output, "metadata": result.metadata},
                    error=result.errors[0] if result.errors else None,
                    metadata={
                        "agent": capability_name,
                        "execution_time": result.metadata.get("execution_time_ms", 0),
                    },
                )

            # Handle workflow execution
            elif action == "execute_workflow":
                result = self.orchestrator.run_workflow(
                    workflow_name=capability_name,
                    initial_task=params.get("task", ""),
                    model=params.get("model", "claude-3-5-sonnet-20241022"),
                )

                return MCPResponse(
                    success=result.success,
                    request_id=request.request_id,
                    data={"output": result.output, "metadata": result.metadata},
                    error=result.errors[0] if result.errors else None,
                    metadata={
                        "workflow": capability_name,
                        "agents_executed": len(result.metadata.get("workflow_steps", [])),
                    },
                )

            # Handle agent recommendation
            elif action == "recommend_agents" or capability_name == "recommend-agents":
                recommendations = self.orchestrator.recommend_agents(
                    task=params.get("task", ""),
                    top_k=params.get("top_k", 3),
                    min_confidence=params.get("min_confidence", 0.3),
                )

                return MCPResponse(
                    success=True,
                    request_id=request.request_id,
                    data={"recommendations": recommendations},
                    error=None,
                    metadata={"count": len(recommendations)},
                )

            # Handle performance summary
            elif action == "get_performance" or capability_name == "performance-summary":
                summary = self.orchestrator.get_performance_summary(hours=params.get("hours"))

                return MCPResponse(
                    success=True,
                    request_id=request.request_id,
                    data=summary,
                    error=None,
                    metadata={"type": "performance-summary"},
                )

            else:
                return MCPResponse(
                    success=False,
                    request_id=request.request_id,
                    data=None,
                    error=f"Unknown action: {action}",
                    metadata={},
                )

        except Exception as e:
            logger.error(f"Error executing capability: {e}")
            return MCPResponse(
                success=False, request_id=request.request_id, data=None, error=str(e), metadata={}
            )

    def start(self, host: str = "0.0.0.0", port: int = 8080, blocking: bool = True):
        """
        Start the MCP server

        Args:
            host: Host to bind to
            port: Port to listen on
            blocking: Whether to block (True) or run in background thread (False)
        """
        handler = self._create_request_handler()
        self.server_instance = HTTPServer((host, port), handler)

        logger.info(f"MCP Server starting on {host}:{port}")
        logger.info(f"Available capabilities: {len(self.get_capabilities())}")

        if blocking:
            try:
                self.server_instance.serve_forever()
            except KeyboardInterrupt:
                logger.info("MCP Server shutting down...")
                self.server_instance.shutdown()
        else:
            self.server_thread = threading.Thread(target=self.server_instance.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            logger.info("MCP Server running in background thread")

    def stop(self):
        """Stop the MCP server"""
        if self.server_instance:
            logger.info("Stopping MCP Server...")
            self.server_instance.shutdown()
            if self.server_thread:
                self.server_thread.join()
            logger.info("MCP Server stopped")

    def _create_request_handler(self):
        """Create HTTP request handler class"""
        mcp_server = self

        class MCPRequestHandler(BaseHTTPRequestHandler):
            """HTTP request handler for MCP protocol"""

            def log_message(self, format, *args):
                """Override to use logger instead of stderr"""
                logger.info(f"{self.address_string()} - {format % args}")

            def _send_json_response(self, data: dict, status_code: int = 200):
                """Send JSON response with security headers"""
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")

                # CORS - use configured allowed origins
                origin = self.headers.get("Origin")
                allowed_origin = mcp_server._get_allowed_origin(origin)
                self.send_header("Access-Control-Allow-Origin", allowed_origin)
                self.send_header("Access-Control-Allow-Credentials", "true")

                # Security headers
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("X-Frame-Options", "DENY")
                self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'none'")
                self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

            def _verify_authentication(self) -> bool:
                """
                Verify API key authentication from Authorization header

                Returns:
                    True if authenticated, False otherwise
                """
                auth_header = self.headers.get("Authorization", "")
                if not auth_header.startswith("Bearer "):
                    return False

                api_key = auth_header[7:]  # Remove 'Bearer ' prefix
                return mcp_server._verify_api_key(api_key)

            def do_GET(self):
                """Handle GET requests"""
                parsed_path = urlparse(self.path)

                # List capabilities
                if parsed_path.path == "/capabilities":
                    capabilities = mcp_server.get_capabilities()
                    self._send_json_response(
                        {
                            "capabilities": [asdict(cap) for cap in capabilities],
                            "count": len(capabilities),
                            "server": "claude-force-mcp",
                            "version": "2.1.0-p1",
                        }
                    )

                # Health check
                elif parsed_path.path == "/health":
                    self._send_json_response(
                        {
                            "status": "healthy",
                            "server": "claude-force-mcp",
                            "version": "2.1.0-p1",
                            "capabilities": len(mcp_server.get_capabilities()),
                        }
                    )

                # Root info
                elif parsed_path.path == "/":
                    self._send_json_response(
                        {
                            "server": "claude-force-mcp",
                            "version": "2.1.0-p1",
                            "protocol": "MCP (Model Context Protocol)",
                            "endpoints": {
                                "GET /capabilities": "List all capabilities",
                                "POST /execute": "Execute a capability",
                                "GET /health": "Health check",
                            },
                            "documentation": "https://github.com/anthropics/claude-force",
                        }
                    )

                else:
                    self._send_json_response({"error": "Not found"}, status_code=404)

            def do_POST(self):
                """Handle POST requests"""
                parsed_path = urlparse(self.path)

                if parsed_path.path == "/execute":
                    # Check rate limit
                    client_ip = self.client_address[0]
                    allowed, retry_after = mcp_server.rate_limiter.is_allowed(client_ip)

                    if not allowed:
                        self._send_json_response(
                            {
                                "success": False,
                                "error": f"Rate limit exceeded. Please retry after {retry_after} seconds.",
                                "retry_after": retry_after,
                            },
                            status_code=429,
                        )
                        return

                    # Verify authentication for execute endpoint
                    if not self._verify_authentication():
                        self._send_json_response(
                            {
                                "success": False,
                                "error": "Unauthorized. Please provide valid API key in Authorization header (Bearer <key>)",
                            },
                            status_code=401,
                        )
                        return

                    # Read request body
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length).decode("utf-8")

                    try:
                        request_data = json.loads(body)

                        # Create MCP request
                        mcp_request = MCPRequest(
                            capability=request_data.get("capability", ""),
                            action=request_data.get("action", ""),
                            parameters=request_data.get("parameters", {}),
                            request_id=request_data.get("request_id"),
                        )

                        # Execute capability
                        response = mcp_server.execute_capability(mcp_request)

                        # Send response
                        self._send_json_response(asdict(response))

                    except json.JSONDecodeError:
                        self._send_json_response(
                            {"error": "Invalid JSON in request body"}, status_code=400
                        )
                    except Exception as e:
                        logger.error(f"Error processing request: {e}")
                        self._send_json_response({"error": str(e)}, status_code=500)
                else:
                    self._send_json_response({"error": "Not found"}, status_code=404)

            def do_OPTIONS(self):
                """Handle CORS preflight"""
                self.send_response(200)
                # Use configured allowed origins
                origin = self.headers.get("Origin")
                allowed_origin = mcp_server._get_allowed_origin(origin)
                self.send_header("Access-Control-Allow-Origin", allowed_origin)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                self.send_header("Access-Control-Allow-Credentials", "true")
                self.end_headers()

        return MCPRequestHandler


def main():
    """CLI entry point for MCP server"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Claude-Force MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--config", default=".claude/claude.json", help="Path to claude.json")
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY)")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        print("Set via environment variable or --api-key argument")
        return 1

    # Create and start server
    server = MCPServer(config_path=args.config, anthropic_api_key=api_key)

    try:
        server.start(host=args.host, port=args.port, blocking=True)
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
        server.stop()

    return 0


if __name__ == "__main__":
    exit(main())
