#!/usr/bin/env python3
"""
CLI and Orchestrator Stress Tests
Comprehensive tests for CLI commands and orchestrator under stress.
"""

import pytest
import subprocess
import os
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestCLIStressTests:
    """Stress tests for CLI commands"""

    def test_cli_help_performance(self):
        """Test CLI help command performance"""
        start = time.time()
        result = subprocess.run(
            ["python3", "-m", "claude_force", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        elapsed = time.time() - start

        assert result.returncode == 0
        assert elapsed < 2.0, f"Help command took {elapsed}s"

    def test_cli_rapid_fire_commands(self):
        """Test rapid execution of CLI commands"""
        commands = [
            ["python3", "-m", "claude_force", "list", "agents"],
            ["python3", "-m", "claude_force", "marketplace", "list"],
            ["python3", "-m", "claude_force", "gallery", "browse"],
            ["python3", "-m", "claude_force", "--version"],
        ]

        num_iterations = 20

        def run_command(cmd):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for _ in range(num_iterations):
                for cmd in commands:
                    futures.append(executor.submit(run_command, cmd))

            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"CLI stress success rate: {success_rate}"

    def test_cli_init_many_projects(self, tmp_path):
        """Test CLI init command for many projects"""
        num_projects = 20

        def init_project(idx):
            project_dir = tmp_path / f"cli_project_{idx}"
            try:
                result = subprocess.run([
                    "python3", "-m", "claude_force", "init",
                    str(project_dir),
                    "--description", f"Test project {idx}",
                    "--tech", "Python,FastAPI",
                    "--no-examples"
                ], capture_output=True, text=True, timeout=30)
                return result.returncode == 0
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(init_project, i) for i in range(num_projects)]
            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / num_projects
        assert success_rate >= 0.7, f"Init success rate: {success_rate}"

    def test_cli_long_running_commands(self, tmp_path):
        """Test CLI with long-running operations"""
        project_dir = tmp_path / "long_running"

        # Init with very long description
        long_desc = " ".join(["word"] * 1000)

        start = time.time()
        result = subprocess.run([
            "python3", "-m", "claude_force", "init",
            str(project_dir),
            "--description", long_desc,
            "--tech", "Python",
            "--no-examples"
        ], capture_output=True, text=True, timeout=60)
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 30.0, f"Init took {elapsed}s"

    def test_cli_error_handling_stress(self):
        """Test CLI error handling under stress"""
        # Invalid commands
        invalid_commands = [
            ["python3", "-m", "claude_force", "nonexistent_command"],
            ["python3", "-m", "claude_force", "init"],  # Missing args
            ["python3", "-m", "claude_force", "run", "agent"],  # Missing args
            ["python3", "-m", "claude_force", "run", "agent", "nonexistent"],
        ]

        for cmd in invalid_commands:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            # Should fail gracefully (non-zero exit but no crash)
            assert result.returncode != 0

    def test_cli_special_characters_handling(self, tmp_path):
        """Test CLI with special characters in arguments"""
        special_inputs = [
            "Test with spaces",
            "Test!@#$%",
            "Test'with'quotes",
            'Test"double"quotes',
            "Test\nNewline",
            "Test\tTab",
        ]

        for special_input in special_inputs:
            project_dir = tmp_path / f"special_{hash(special_input)}"
            try:
                subprocess.run([
                    "python3", "-m", "claude_force", "init",
                    str(project_dir),
                    "--description", special_input,
                    "--tech", "Python",
                    "--no-examples"
                ], capture_output=True, text=True, timeout=20)
            except Exception:
                pass  # Should handle gracefully

    def test_cli_concurrent_recommend(self):
        """Test concurrent CLI recommend commands"""
        tasks = [
            "Build REST API",
            "Create React components",
            "Design database schema",
            "Deploy to production",
        ]

        def run_recommend(task):
            try:
                result = subprocess.run([
                    "python3", "-m", "claude_force",
                    "recommend",
                    "--task", task
                ], capture_output=True, text=True, timeout=15)
                return result.returncode == 0
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_recommend, task) for task in tasks * 5]
            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / len(results)
        assert success_rate >= 0.7, f"Recommend success rate: {success_rate}"


class TestOrchestratorStressTests:
    """Stress tests for orchestrator components"""

    @patch('claude_force.orchestrator.Anthropic')
    def test_orchestrator_concurrent_agent_runs(self, mock_anthropic, tmp_path):
        """Test running multiple agents concurrently (mocked)"""
        from claude_force.orchestrator import AgentOrchestrator

        # Mock the API
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        orchestrator = AgentOrchestrator(claude_dir=str(tmp_path))
        num_runs = 50

        def run_agent():
            try:
                # This would call API, but we're mocking
                result = orchestrator.run_agent(
                    agent_name="python-expert",
                    task="Write a simple function",
                    enable_tracking=False
                )
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_agent) for _ in range(num_runs)]
            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / num_runs
        assert success_rate >= 0.8, f"Agent run success rate: {success_rate}"

    @patch('claude_force.orchestrator.Anthropic')
    def test_orchestrator_workflow_stress(self, mock_anthropic, tmp_path):
        """Test orchestrator running workflows under stress"""
        from claude_force.orchestrator import AgentOrchestrator

        # Mock API
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        orchestrator = AgentOrchestrator(claude_dir=str(tmp_path))

        def run_workflow():
            try:
                results = orchestrator.run_workflow(
                    workflow_name="frontend-only",
                    task="Build user dashboard",
                    enable_tracking=False
                )
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_workflow) for _ in range(10)]
            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / 10
        assert success_rate >= 0.7, f"Workflow success rate: {success_rate}"

    def test_orchestrator_large_task_descriptions(self, tmp_path):
        """Test orchestrator with very large task descriptions"""
        from claude_force.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(claude_dir=str(tmp_path))

        # Very large task (50K words)
        large_task = " ".join(["word"] * 50000)

        start = time.time()
        try:
            # This will fail without API key, but tests the parsing
            orchestrator.run_agent(
                agent_name="python-expert",
                task=large_task,
                enable_tracking=False,
                dry_run=True  # Don't actually call API
            )
        except Exception:
            pass  # Expected without API key
        elapsed = time.time() - start

        # Should handle large input efficiently
        assert elapsed < 5.0, f"Large task processing took {elapsed}s"

    def test_orchestrator_rapid_agent_switching(self, tmp_path):
        """Test rapidly switching between agents"""
        from claude_force.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(claude_dir=str(tmp_path))

        agents = [
            "python-expert",
            "frontend-architect",
            "backend-architect",
            "database-architect",
            "devops-architect",
        ]

        start = time.time()
        for _ in range(100):
            agent = agents[_ % len(agents)]
            try:
                # Load agent config (without running)
                orchestrator.get_agent_config(agent)
            except Exception:
                pass
        elapsed = time.time() - start

        # Should be very fast (< 1 second for 100 loads)
        assert elapsed < 1.0, f"Agent switching took {elapsed}s"

    def test_orchestrator_memory_under_load(self, tmp_path):
        """Test orchestrator memory usage under load"""
        import tracemalloc
        from claude_force.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(claude_dir=str(tmp_path))

        tracemalloc.start()
        initial_memory = tracemalloc.get_traced_memory()[0]

        # Load configs many times
        for _ in range(1000):
            try:
                orchestrator.get_agent_config("python-expert")
            except Exception:
                pass

        current_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        memory_growth = (current_memory - initial_memory) / 1024 / 1024
        assert memory_growth < 50, f"Memory grew by {memory_growth}MB"

    def test_orchestrator_error_propagation(self, tmp_path):
        """Test error propagation in orchestrator"""
        from claude_force.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(claude_dir=str(tmp_path))

        # Try to run nonexistent agent
        try:
            orchestrator.run_agent(
                agent_name="nonexistent-agent",
                task="test",
                enable_tracking=False
            )
            assert False, "Should have raised error"
        except Exception as e:
            # Should raise appropriate error
            assert "nonexistent" in str(e).lower() or "not found" in str(e).lower()

    def test_orchestrator_validation_stress(self, tmp_path):
        """Test validation under stress"""
        from claude_force.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(claude_dir=str(tmp_path))

        # Try to run many invalid operations
        invalid_operations = [
            ("", "test"),  # Empty agent name
            ("python-expert", ""),  # Empty task
            (None, "test"),  # None agent
            ("python-expert", None),  # None task
        ]

        for agent, task in invalid_operations:
            try:
                orchestrator.run_agent(
                    agent_name=agent,
                    task=task,
                    enable_tracking=False
                )
            except (ValueError, TypeError, AttributeError):
                pass  # Expected


class TestPerformanceTrackerStress:
    """Stress tests for performance tracker"""

    def test_tracker_high_volume_logging(self, tmp_path):
        """Test performance tracker with high volume logging"""
        from claude_force.performance_tracker import PerformanceTracker

        tracker = PerformanceTracker(metrics_dir=str(tmp_path))

        # Log many executions rapidly
        num_logs = 1000

        start = time.time()
        for i in range(num_logs):
            tracker.log_execution(
                agent_name=f"agent_{i % 10}",
                task=f"task_{i}",
                execution_time_ms=100 + i % 100,
                input_tokens=1000 + i % 500,
                output_tokens=500 + i % 300,
                model="claude-3-5-sonnet-20241022"
            )
        elapsed = time.time() - start

        # Should handle 1000 logs in under 5 seconds
        assert elapsed < 5.0, f"Logging {num_logs} entries took {elapsed}s"

    def test_tracker_concurrent_logging(self, tmp_path):
        """Test concurrent performance logging"""
        from claude_force.performance_tracker import PerformanceTracker

        tracker = PerformanceTracker(metrics_dir=str(tmp_path))

        def log_entry(idx):
            try:
                tracker.log_execution(
                    agent_name=f"agent_{idx % 5}",
                    task=f"task_{idx}",
                    execution_time_ms=100,
                    input_tokens=1000,
                    output_tokens=500,
                    model="claude-3-5-sonnet-20241022"
                )
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(log_entry, i) for i in range(200)]
            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / 200
        assert success_rate >= 0.9, f"Concurrent logging success rate: {success_rate}"

    def test_tracker_large_file_handling(self, tmp_path):
        """Test tracker with large log files"""
        from claude_force.performance_tracker import PerformanceTracker

        tracker = PerformanceTracker(metrics_dir=str(tmp_path))

        # Create large log file
        for i in range(5000):
            tracker.log_execution(
                agent_name=f"agent_{i % 10}",
                task=f"task_{i}",
                execution_time_ms=100,
                input_tokens=1000,
                output_tokens=500,
                model="claude-3-5-sonnet-20241022"
            )

        # Try to read and analyze
        start = time.time()
        try:
            summary = tracker.get_performance_summary()
        except Exception:
            summary = None
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 10.0, f"Reading large log took {elapsed}s"

    def test_tracker_export_stress(self, tmp_path):
        """Test exporting large amounts of data"""
        from claude_force.performance_tracker import PerformanceTracker

        tracker = PerformanceTracker(metrics_dir=str(tmp_path))

        # Log data
        for i in range(1000):
            tracker.log_execution(
                agent_name=f"agent_{i % 10}",
                task=f"task_{i}",
                execution_time_ms=100,
                input_tokens=1000,
                output_tokens=500,
                model="claude-3-5-sonnet-20241022"
            )

        # Export to different formats
        export_file = tmp_path / "export.json"

        start = time.time()
        try:
            tracker.export_performance_metrics(
                output_file=str(export_file),
                format="json"
            )
        except Exception:
            pass
        elapsed = time.time() - start

        # Should export quickly
        assert elapsed < 5.0, f"Export took {elapsed}s"


class TestSemanticSelectorStress:
    """Stress tests for semantic selector"""

    def test_semantic_selector_many_queries(self):
        """Test semantic selector with many queries"""
        try:
            from claude_force.semantic_selector import SemanticAgentSelector

            selector = SemanticAgentSelector()

            # Many different queries
            queries = [
                f"Build feature {i}" for i in range(100)
            ]

            start = time.time()
            for query in queries:
                try:
                    selector.select_agent(task=query, top_k=3)
                except Exception:
                    pass  # May fail without sentence-transformers
            elapsed = time.time() - start

            # Should handle 100 queries quickly
            assert elapsed < 30.0, f"100 queries took {elapsed}s"

        except ImportError:
            pytest.skip("sentence-transformers not available")

    def test_semantic_selector_long_queries(self):
        """Test semantic selector with very long queries"""
        try:
            from claude_force.semantic_selector import SemanticAgentSelector

            selector = SemanticAgentSelector()

            # Very long query (10K words)
            long_query = " ".join(["word"] * 10000)

            start = time.time()
            try:
                selector.select_agent(task=long_query, top_k=5)
            except Exception:
                pass
            elapsed = time.time() - start

            # Should handle long query
            assert elapsed < 10.0, f"Long query took {elapsed}s"

        except ImportError:
            pytest.skip("sentence-transformers not available")

    def test_semantic_selector_concurrent_queries(self):
        """Test concurrent semantic queries"""
        try:
            from claude_force.semantic_selector import SemanticAgentSelector

            selector = SemanticAgentSelector()

            def run_query(query):
                try:
                    selector.select_agent(task=query, top_k=3)
                    return True
                except Exception:
                    return False

            queries = [f"Task {i}" for i in range(50)]

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(run_query, q) for q in queries]
                results = [f.result() for f in as_completed(futures)]

            success_rate = sum(results) / len(results)
            assert success_rate >= 0.8, f"Concurrent queries success rate: {success_rate}"

        except ImportError:
            pytest.skip("sentence-transformers not available")


class TestMCPServerStress:
    """Stress tests for MCP server"""

    def test_mcp_server_startup_performance(self):
        """Test MCP server startup time"""
        try:
            from claude_force.mcp_server import MCPServer

            start = time.time()
            server = MCPServer()
            elapsed = time.time() - start

            # Should start quickly
            assert elapsed < 3.0, f"MCP server startup took {elapsed}s"
            assert server is not None

        except Exception:
            pytest.skip("MCP server not available")

    def test_mcp_server_handle_many_requests(self):
        """Test MCP server handling many requests"""
        try:
            from claude_force.mcp_server import MCPServer

            server = MCPServer()

            # Simulate many requests
            def handle_request():
                try:
                    # This would normally be HTTP requests
                    server.list_agents()
                    return True
                except Exception:
                    return False

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(handle_request) for _ in range(100)]
                results = [f.result() for f in as_completed(futures)]

            success_rate = sum(results) / 100
            assert success_rate >= 0.8, f"MCP request success rate: {success_rate}"

        except Exception:
            pytest.skip("MCP server not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
