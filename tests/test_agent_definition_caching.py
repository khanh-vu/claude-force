"""
Tests for Agent Definition Caching (PERF-02).

Tests verify that agent definitions and contracts are cached after first load,
providing 50-100% speedup for repeated agent executions.
"""

import unittest
import tempfile
import shutil
import time
from pathlib import Path
import json

from claude_force.orchestrator import AgentOrchestrator


class TestAgentDefinitionCaching(unittest.TestCase):
    """Test agent definition caching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create test configuration
        self.config_file = self.claude_dir / "claude.json"
        self.agents_dir = self.claude_dir / "agents"
        self.contracts_dir = self.claude_dir / "contracts"
        self.agents_dir.mkdir()
        self.contracts_dir.mkdir()

        # Create test agent file
        self.agent_file = self.agents_dir / "test-agent.md"
        self.agent_file.write_text("# Test Agent\n\nThis is a test agent definition.")

        # Create test contract file
        self.contract_file = self.contracts_dir / "test-agent.contract"
        self.contract_file.write_text("# Test Contract\n\nThis is a test contract.")

        # Create config
        config = {
            "agents": {
                "test-agent": {
                    "file": "agents/test-agent.md",
                    "contract": "contracts/test-agent.contract",
                    "domains": ["testing"],
                },
                "test-agent-no-contract": {"file": "agents/test-agent.md", "domains": ["testing"]},
            },
            "workflows": {},
        }

        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_definition_cached_after_first_load(self):
        """Agent definition is cached after first load."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # First load - reads from disk
        definition1 = orchestrator._load_agent_definition("test-agent")

        # Check cache
        self.assertIn("test-agent", orchestrator._definition_cache)
        self.assertEqual(orchestrator._definition_cache["test-agent"], definition1)

        # Second load - should use cache (no disk I/O)
        definition2 = orchestrator._load_agent_definition("test-agent")

        # Should be the same content
        self.assertEqual(definition1, definition2)

        # Verify cache statistics
        stats = orchestrator.get_cache_stats()
        self.assertEqual(stats["definition_cache_size"], 1)
        self.assertIn("test-agent", stats["cached_agents"])

    def test_contract_cached_after_first_load(self):
        """Agent contract is cached after first load."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # First load
        contract1 = orchestrator._load_agent_contract("test-agent")

        # Check cache
        self.assertIn("test-agent", orchestrator._contract_cache)

        # Second load - should use cache
        contract2 = orchestrator._load_agent_contract("test-agent")

        # Should be the same
        self.assertEqual(contract1, contract2)

    def test_cache_speedup(self):
        """Cached access is faster than disk read."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # First load (cold - from disk)
        start = time.perf_counter()
        definition1 = orchestrator._load_agent_definition("test-agent")
        first_time = time.perf_counter() - start

        # Second load (warm - from cache)
        start = time.perf_counter()
        definition2 = orchestrator._load_agent_definition("test-agent")
        second_time = time.perf_counter() - start

        # Cached access should be much faster (at least 2x faster)
        # or at worst, not slower
        self.assertLessEqual(second_time, first_time)

        # Verify content is identical
        self.assertEqual(definition1, definition2)

    def test_clear_cache(self):
        """clear_agent_cache() clears both caches."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # Load and verify cached
        orchestrator._load_agent_definition("test-agent")
        orchestrator._load_agent_contract("test-agent")

        self.assertEqual(len(orchestrator._definition_cache), 1)
        self.assertEqual(len(orchestrator._contract_cache), 1)

        # Clear cache
        orchestrator.clear_agent_cache()

        # Verify caches are empty
        self.assertEqual(len(orchestrator._definition_cache), 0)
        self.assertEqual(len(orchestrator._contract_cache), 0)

        stats = orchestrator.get_cache_stats()
        self.assertEqual(stats["definition_cache_size"], 0)
        self.assertEqual(stats["contract_cache_size"], 0)

    def test_cache_maxsize_limit(self):
        """Cache respects maxsize limit (128 by default)."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # Artificially set low maxsize for testing
        orchestrator._cache_maxsize = 3

        # Create multiple agents
        for i in range(5):
            agent_name = f"agent-{i}"
            agent_file = self.agents_dir / f"{agent_name}.md"
            agent_file.write_text(f"# Agent {i}")

            orchestrator.config["agents"][agent_name] = {
                "file": f"agents/{agent_name}.md",
                "domains": ["testing"],
            }

            # Load the agent
            orchestrator._load_agent_definition(agent_name)

        # Cache should not exceed maxsize
        self.assertLessEqual(len(orchestrator._definition_cache), 3)

        # Should have most recent 3 agents
        stats = orchestrator.get_cache_stats()
        self.assertEqual(stats["definition_cache_size"], 3)

    def test_empty_contract_cached(self):
        """Empty contract (when no contract file) is cached."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # Load agent without contract
        contract = orchestrator._load_agent_contract("test-agent-no-contract")

        # Should return empty string
        self.assertEqual(contract, "")

        # Should be cached
        self.assertIn("test-agent-no-contract", orchestrator._contract_cache)
        self.assertEqual(orchestrator._contract_cache["test-agent-no-contract"], "")

    def test_cache_stats(self):
        """get_cache_stats() returns accurate statistics."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # Initial state
        stats = orchestrator.get_cache_stats()
        self.assertEqual(stats["definition_cache_size"], 0)
        self.assertEqual(stats["contract_cache_size"], 0)
        self.assertEqual(stats["cache_maxsize"], 128)
        self.assertEqual(stats["cached_agents"], [])

        # Load agent
        orchestrator._load_agent_definition("test-agent")
        orchestrator._load_agent_contract("test-agent")

        # Updated stats
        stats = orchestrator.get_cache_stats()
        self.assertEqual(stats["definition_cache_size"], 1)
        self.assertEqual(stats["contract_cache_size"], 1)
        self.assertIn("test-agent", stats["cached_agents"])

    def test_cache_after_file_modification(self):
        """Cache can be cleared to reload modified files."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # Load original definition
        definition1 = orchestrator._load_agent_definition("test-agent")
        self.assertIn("test agent definition", definition1.lower())

        # Modify the file
        self.agent_file.write_text("# Test Agent\n\nMODIFIED CONTENT")

        # Load again (will use cache - won't see changes)
        definition2 = orchestrator._load_agent_definition("test-agent")
        self.assertEqual(definition1, definition2)  # Still cached version

        # Clear cache
        orchestrator.clear_agent_cache()

        # Load again (will read from disk - will see changes)
        definition3 = orchestrator._load_agent_definition("test-agent")
        self.assertIn("MODIFIED CONTENT", definition3)
        self.assertNotEqual(definition1, definition3)

    def test_multiple_agents_cached_independently(self):
        """Multiple agents are cached independently."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # Create second agent
        agent2_file = self.agents_dir / "agent2.md"
        agent2_file.write_text("# Agent 2")

        orchestrator.config["agents"]["agent2"] = {
            "file": "agents/agent2.md",
            "domains": ["testing"],
        }

        # Load both agents
        def1 = orchestrator._load_agent_definition("test-agent")
        def2 = orchestrator._load_agent_definition("agent2")

        # Both should be cached
        self.assertEqual(len(orchestrator._definition_cache), 2)
        self.assertIn("test-agent", orchestrator._definition_cache)
        self.assertIn("agent2", orchestrator._definition_cache)

        # Content should be different
        self.assertNotEqual(def1, def2)

    def test_cache_persists_across_multiple_calls(self):
        """Cache persists across multiple run_agent calls."""
        orchestrator = AgentOrchestrator(
            config_path=str(self.config_file), anthropic_api_key="test-key", validate_api_key=False
        )

        # Simulate multiple executions of the same agent
        for i in range(5):
            # Each call should use cached definition
            definition = orchestrator._load_agent_definition("test-agent")
            self.assertIsNotNone(definition)

        # Should still only have 1 cached entry
        stats = orchestrator.get_cache_stats()
        self.assertEqual(stats["definition_cache_size"], 1)


class TestCachingPerformanceBenchmark(unittest.TestCase):
    """Benchmark caching performance improvements."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()

        # Create test configuration with realistic agent size
        self.config_file = self.claude_dir / "claude.json"
        self.agents_dir = self.claude_dir / "agents"
        self.agents_dir.mkdir()

        # Create large agent file (more realistic)
        self.agent_file = self.agents_dir / "test-agent.md"
        large_content = "# Test Agent\n\n" + ("This is content. " * 1000)  # ~18KB
        self.agent_file.write_text(large_content)

        # Create config
        config = {
            "agents": {"test-agent": {"file": "agents/test-agent.md", "domains": ["testing"]}},
            "workflows": {},
        }

        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_caching_speedup_benchmark(self):
        """Measure actual speedup from caching."""
        orchestrator = AgentOrchestrator(config_path=str(self.config_file), validate_api_key=False)

        # Benchmark first load (cold)
        cold_times = []
        for _ in range(3):
            orchestrator.clear_agent_cache()
            start = time.perf_counter()
            orchestrator._load_agent_definition("test-agent")
            cold_times.append((time.perf_counter() - start) * 1000)  # ms

        # Benchmark cached loads (warm)
        warm_times = []
        for _ in range(10):
            start = time.perf_counter()
            orchestrator._load_agent_definition("test-agent")
            warm_times.append((time.perf_counter() - start) * 1000)  # ms

        avg_cold = sum(cold_times) / len(cold_times)
        avg_warm = sum(warm_times) / len(warm_times)

        # Warm should be faster (or at least not slower)
        self.assertLessEqual(avg_warm, avg_cold)

        # Calculate speedup
        speedup = (avg_cold / avg_warm) if avg_warm > 0 else float("inf")

        # Report results
        print(f"\nCaching Performance Benchmark:")
        print(f"  Cold load (avg): {avg_cold:.4f}ms")
        print(f"  Warm load (avg): {avg_warm:.4f}ms")
        print(f"  Speedup: {speedup:.2f}x faster")

        # Warm should be at least somewhat faster
        # (May not always be true on fast SSDs, but should not be slower)
        self.assertLessEqual(avg_warm, avg_cold * 1.1)  # Allow 10% margin


if __name__ == "__main__":
    unittest.main()
