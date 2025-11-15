"""
Tests for abstract base classes and protocols.

Verifies that:
- BaseOrchestrator interface is properly defined
- CacheProtocol is satisfied by ResponseCache
- TrackerProtocol is satisfied by PerformanceTracker
- Dataclasses work correctly
- Custom implementations can extend base classes
"""

import unittest
from typing import Dict, List, Any, Optional
from claude_force.base import (
    BaseOrchestrator,
    AgentResult,
    WorkflowResult,
    CacheProtocol,
    TrackerProtocol,
)
from claude_force.response_cache import ResponseCache
from claude_force.performance_tracker import PerformanceTracker
import tempfile
from pathlib import Path


class TestAgentResult(unittest.TestCase):
    """Test AgentResult dataclass."""

    def test_agent_result_creation(self):
        """Test creating AgentResult instance."""
        result = AgentResult(
            success=True,
            output="Test output",
            errors=[],
            metadata={"tokens": 100},
            agent_name="test-agent",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.output, "Test output")
        self.assertEqual(result.errors, [])
        self.assertEqual(result.metadata, {"tokens": 100})
        self.assertEqual(result.agent_name, "test-agent")

    def test_agent_result_to_dict(self):
        """Test converting AgentResult to dictionary."""
        result = AgentResult(
            success=True,
            output="Test output",
            errors=[],
            metadata={"tokens": 100},
            agent_name="test-agent",
        )

        result_dict = result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["success"], True)
        self.assertEqual(result_dict["output"], "Test output")
        self.assertEqual(result_dict["errors"], [])
        self.assertEqual(result_dict["metadata"], {"tokens": 100})
        self.assertEqual(result_dict["agent_name"], "test-agent")

    def test_agent_result_with_errors(self):
        """Test AgentResult with errors."""
        result = AgentResult(
            success=False,
            output="",
            errors=["Error 1", "Error 2"],
            metadata={},
            agent_name="test-agent",
        )

        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 2)
        self.assertIn("Error 1", result.errors)


class TestWorkflowResult(unittest.TestCase):
    """Test WorkflowResult dataclass."""

    def test_workflow_result_creation(self):
        """Test creating WorkflowResult instance."""
        agent_result1 = AgentResult(
            success=True, output="Output 1", errors=[], metadata={}, agent_name="agent1"
        )
        agent_result2 = AgentResult(
            success=True, output="Output 2", errors=[], metadata={}, agent_name="agent2"
        )

        workflow_result = WorkflowResult(
            success=True,
            agent_results=[agent_result1, agent_result2],
            metadata={"total_tokens": 200},
            workflow_name="test-workflow",
        )

        self.assertTrue(workflow_result.success)
        self.assertEqual(len(workflow_result.agent_results), 2)
        self.assertEqual(workflow_result.workflow_name, "test-workflow")

    def test_workflow_result_to_dict(self):
        """Test converting WorkflowResult to dictionary."""
        agent_result = AgentResult(
            success=True, output="Output", errors=[], metadata={}, agent_name="agent1"
        )

        workflow_result = WorkflowResult(
            success=True,
            agent_results=[agent_result],
            metadata={"total_tokens": 100},
            workflow_name="test-workflow",
        )

        result_dict = workflow_result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["success"], True)
        self.assertIsInstance(result_dict["agent_results"], list)
        self.assertEqual(len(result_dict["agent_results"]), 1)
        self.assertEqual(result_dict["workflow_name"], "test-workflow")


class TestBaseOrchestrator(unittest.TestCase):
    """Test BaseOrchestrator abstract class."""

    def test_cannot_instantiate_base_orchestrator(self):
        """Test that BaseOrchestrator cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseOrchestrator()

    def test_custom_orchestrator_must_implement_methods(self):
        """Test that custom orchestrator must implement all abstract methods."""

        # Missing all methods
        with self.assertRaises(TypeError):

            class IncompleteOrchestrator(BaseOrchestrator):
                pass

            IncompleteOrchestrator()

    def test_custom_orchestrator_implementation(self):
        """Test that custom orchestrator can be implemented correctly."""

        class CustomOrchestrator(BaseOrchestrator):
            def run_agent(self, agent_name: str, task: str, **kwargs) -> AgentResult:
                return AgentResult(
                    success=True,
                    output="Custom output",
                    errors=[],
                    metadata={},
                    agent_name=agent_name,
                )

            def run_workflow(
                self, workflow_name: str, task: str, **kwargs
            ) -> List[AgentResult]:
                return [
                    AgentResult(
                        success=True,
                        output="Agent 1",
                        errors=[],
                        metadata={},
                        agent_name="agent1",
                    )
                ]

            def list_agents(self) -> List[Dict[str, Any]]:
                return [{"name": "agent1", "priority": 1}]

            def list_workflows(self) -> Dict[str, List[str]]:
                return {"workflow1": ["agent1", "agent2"]}

        # Should instantiate successfully
        orchestrator = CustomOrchestrator()
        self.assertIsInstance(orchestrator, BaseOrchestrator)

        # Test methods work
        result = orchestrator.run_agent("test-agent", "test task")
        self.assertIsInstance(result, AgentResult)
        self.assertTrue(result.success)

        agents = orchestrator.list_agents()
        self.assertIsInstance(agents, list)
        self.assertEqual(len(agents), 1)


class TestCacheProtocol(unittest.TestCase):
    """Test that ResponseCache satisfies CacheProtocol."""

    def setUp(self):
        """Set up test cache."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = ResponseCache(
            cache_dir=Path(self.temp_dir), ttl_hours=1, max_size_mb=10
        )

    def tearDown(self):
        """Clean up test cache."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_implements_protocol(self):
        """Test that ResponseCache has all required protocol methods."""
        # Check that all protocol methods exist
        self.assertTrue(hasattr(self.cache, "get"))
        self.assertTrue(hasattr(self.cache, "set"))
        self.assertTrue(hasattr(self.cache, "delete"))
        self.assertTrue(hasattr(self.cache, "clear"))
        self.assertTrue(hasattr(self.cache, "size"))

        # Check methods are callable
        self.assertTrue(callable(self.cache.get))
        self.assertTrue(callable(self.cache.set))
        self.assertTrue(callable(self.cache.delete))
        self.assertTrue(callable(self.cache.clear))
        self.assertTrue(callable(self.cache.size))

    def test_cache_protocol_get(self):
        """Test cache get method."""
        # Should return None for non-existent key
        result = self.cache.get("test-agent", "test task", "claude-3-haiku-20240307")
        self.assertIsNone(result)

    def test_cache_protocol_set_and_get(self):
        """Test cache set and get methods."""
        self.cache.set(
            agent_name="test-agent",
            task="test task",
            model="claude-3-haiku-20240307",
            response="test response",
            input_tokens=100,
            output_tokens=50,
            estimated_cost=0.001,
        )

        result = self.cache.get("test-agent", "test task", "claude-3-haiku-20240307")
        self.assertIsNotNone(result)
        self.assertEqual(result["response"], "test response")

    def test_cache_protocol_delete(self):
        """Test cache delete method."""
        # Set a value
        self.cache.set(
            agent_name="test-agent",
            task="test task",
            model="claude-3-haiku-20240307",
            response="test response",
            input_tokens=100,
            output_tokens=50,
            estimated_cost=0.001,
        )

        # Get the cache key
        key = self.cache._cache_key("test-agent", "test task", "claude-3-haiku-20240307")

        # Delete should return True for existing key
        deleted = self.cache.delete(key)
        self.assertTrue(deleted)

        # Delete should return False for non-existent key
        deleted_again = self.cache.delete(key)
        self.assertFalse(deleted_again)

    def test_cache_protocol_size(self):
        """Test cache size method."""
        initial_size = self.cache.size()
        self.assertEqual(initial_size, 0)

        # Add entry
        self.cache.set(
            agent_name="test-agent",
            task="test task",
            model="claude-3-haiku-20240307",
            response="test response",
            input_tokens=100,
            output_tokens=50,
            estimated_cost=0.001,
        )

        new_size = self.cache.size()
        self.assertEqual(new_size, 1)

    def test_cache_protocol_clear(self):
        """Test cache clear method."""
        # Add entries
        self.cache.set(
            agent_name="agent1",
            task="task1",
            model="claude-3-haiku-20240307",
            response="response1",
            input_tokens=100,
            output_tokens=50,
            estimated_cost=0.001,
        )

        self.assertGreater(self.cache.size(), 0)

        # Clear cache
        self.cache.clear()
        self.assertEqual(self.cache.size(), 0)


class TestTrackerProtocol(unittest.TestCase):
    """Test that PerformanceTracker satisfies TrackerProtocol."""

    def setUp(self):
        """Set up test tracker."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = PerformanceTracker(
            metrics_dir=self.temp_dir, max_entries=100, enable_persistence=False
        )

    def tearDown(self):
        """Clean up test tracker."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tracker_implements_protocol(self):
        """Test that PerformanceTracker has all required protocol methods."""
        # Check that all protocol methods exist
        self.assertTrue(hasattr(self.tracker, "record_execution"))
        self.assertTrue(hasattr(self.tracker, "get_summary"))
        self.assertTrue(hasattr(self.tracker, "get_agent_stats"))
        self.assertTrue(hasattr(self.tracker, "export_json"))
        self.assertTrue(hasattr(self.tracker, "export_csv"))

        # Check methods are callable
        self.assertTrue(callable(self.tracker.record_execution))
        self.assertTrue(callable(self.tracker.get_summary))
        self.assertTrue(callable(self.tracker.get_agent_stats))
        self.assertTrue(callable(self.tracker.export_json))
        self.assertTrue(callable(self.tracker.export_csv))

    def test_tracker_protocol_record_execution(self):
        """Test tracker record_execution method."""
        metrics = self.tracker.record_execution(
            agent_name="test-agent",
            task="test task",
            success=True,
            duration_ms=1000.0,
            model="claude-3-haiku-20240307",
            input_tokens=100,
            output_tokens=50,
        )

        # Should return ExecutionMetrics
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.agent_name, "test-agent")
        self.assertTrue(metrics.success)

    def test_tracker_protocol_get_summary(self):
        """Test tracker get_summary method."""
        # Record some executions
        self.tracker.record_execution(
            agent_name="agent1",
            task="task1",
            success=True,
            duration_ms=1000.0,
            model="claude-3-haiku-20240307",
            input_tokens=100,
            output_tokens=50,
        )

        summary = self.tracker.get_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("total_executions", summary)
        self.assertEqual(summary["total_executions"], 1)

    def test_tracker_protocol_get_agent_stats(self):
        """Test tracker get_agent_stats method."""
        # Record some executions
        self.tracker.record_execution(
            agent_name="agent1",
            task="task1",
            success=True,
            duration_ms=1000.0,
            model="claude-3-haiku-20240307",
            input_tokens=100,
            output_tokens=50,
        )

        stats = self.tracker.get_agent_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("agent1", stats)

    def test_tracker_protocol_export_json(self):
        """Test tracker export_json method."""
        # Record execution
        self.tracker.record_execution(
            agent_name="agent1",
            task="task1",
            success=True,
            duration_ms=1000.0,
            model="claude-3-haiku-20240307",
            input_tokens=100,
            output_tokens=50,
        )

        output_path = Path(self.temp_dir) / "metrics.json"
        self.tracker.export_json(str(output_path))

        # Check file exists
        self.assertTrue(output_path.exists())

        # Check file is valid JSON
        import json

        with open(output_path) as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_tracker_protocol_export_csv(self):
        """Test tracker export_csv method."""
        # Record execution
        self.tracker.record_execution(
            agent_name="agent1",
            task="task1",
            success=True,
            duration_ms=1000.0,
            model="claude-3-haiku-20240307",
            input_tokens=100,
            output_tokens=50,
        )

        output_path = Path(self.temp_dir) / "metrics.csv"
        self.tracker.export_csv(str(output_path))

        # Check file exists
        self.assertTrue(output_path.exists())

        # Check file has content
        import csv

        with open(output_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()
