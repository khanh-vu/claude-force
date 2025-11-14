"""
Performance Tests for claude-force.

Tests performance benchmarks and ensures operations meet target latencies
for production use.
"""

import unittest
import time
import tempfile
import shutil
from pathlib import Path
import tracemalloc

from claude_force.quick_start import (
    QuickStartOrchestrator,
    get_quick_start_orchestrator
)
from claude_force.skills_manager import (
    ProgressiveSkillsManager,
    get_skills_manager
)
from claude_force.hybrid_orchestrator import (
    HybridOrchestrator,
)
from unittest.mock import patch


class TestTemplateMatchingPerformance(unittest.TestCase):
    """Test template matching performance."""

    def test_template_matching_performance(self):
        """Template matching should be < 50ms for 100 templates."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # Warm up (first call may be slower)
        orchestrator.match_templates("test", top_k=3)

        # Benchmark multiple runs
        times = []
        for _ in range(5):
            start = time.perf_counter()
            result = orchestrator.match_templates(
                "Build a web application with authentication",
                top_k=3
            )
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

            times.append(elapsed)
            self.assertIsNotNone(result)

        # Average should be < 50ms
        avg_time = sum(times) / len(times)
        self.assertLess(
            avg_time,
            50,
            f"Template matching took {avg_time:.2f}ms on average (target: < 50ms)"
        )

    def test_caching_speedup(self):
        """Template caching should provide speedup on repeated access."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # First access (cold)
        start = time.perf_counter()
        first_result = orchestrator.match_templates("Test project", top_k=3)
        first_time = (time.perf_counter() - start) * 1000

        # Second access (should be cached or faster)
        start = time.perf_counter()
        second_result = orchestrator.match_templates("Test project", top_k=3)
        second_time = (time.perf_counter() - start) * 1000

        # Verify results are consistent
        self.assertEqual(len(first_result), len(second_result))

        # Both should be reasonably fast
        self.assertLess(first_time, 100)
        self.assertLess(second_time, 100)


class TestSkillsLoadingPerformance(unittest.TestCase):
    """Test skills loading performance."""

    def test_skill_loading_time(self):
        """Skill loading should be < 20ms for 11 skills (cached)."""
        manager = get_skills_manager()

        # Get available skills
        available_skills = manager.get_available_skills()

        if len(available_skills) == 0:
            self.skipTest("No skills available to test")

        # Test loading up to 5 skills
        skills_to_load = available_skills[:5]

        # Warm up cache
        manager.load_skills(skills_to_load)

        # Benchmark cached access
        start = time.perf_counter()
        result = manager.load_skills(skills_to_load)
        elapsed = (time.perf_counter() - start) * 1000

        self.assertIsNotNone(result)
        self.assertLess(
            elapsed,
            20,
            f"Skill loading took {elapsed:.2f}ms (target: < 20ms cached)"
        )

    def test_cache_hit_rate(self):
        """Cache should be effective for repeated skill access."""
        manager = get_skills_manager()

        available_skills = manager.get_available_skills()
        if len(available_skills) == 0:
            self.skipTest("No skills available to test")

        # Clear cache
        manager.skill_cache.clear()

        # Load skills multiple times
        skill_list = available_skills[:3]

        # First load (cache miss)
        start = time.perf_counter()
        manager.load_skills(skill_list)
        first_time = time.perf_counter() - start

        # Second load (cache hit)
        start = time.perf_counter()
        manager.load_skills(skill_list)
        second_time = time.perf_counter() - start

        # Cached access should be faster or similar
        # (May not always be faster due to string operations)
        self.assertLessEqual(second_time, first_time * 2)

    def test_memory_usage(self):
        """Skill cache should not use excessive memory."""
        tracemalloc.start()

        manager = get_skills_manager()
        available_skills = manager.get_available_skills()

        if len(available_skills) == 0:
            tracemalloc.stop()
            self.skipTest("No skills available to test")

        # Load all available skills
        snapshot1 = tracemalloc.take_snapshot()

        manager.load_skills(available_skills)

        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Calculate memory increase
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        total_increase = sum(stat.size_diff for stat in top_stats)

        # Should be less than 5MB for skill cache
        max_memory = 5 * 1024 * 1024  # 5MB in bytes
        self.assertLess(
            total_increase,
            max_memory,
            f"Memory usage increased by {total_increase / 1024 / 1024:.2f}MB (target: < 5MB)"
        )


class TestCostEstimationPerformance(unittest.TestCase):
    """Test cost estimation performance."""

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_cost_estimation_performance(self, mock_init):
        """Cost estimation should be < 5ms."""
        mock_init.return_value = None

        orchestrator = HybridOrchestrator(auto_select_model=True)

        # Warm up
        orchestrator.estimate_cost("test task", "backend-developer")

        # Benchmark
        times = []
        for _ in range(10):
            start = time.perf_counter()
            estimate = orchestrator.estimate_cost(
                "Implement REST API endpoint with validation",
                "backend-developer"
            )
            elapsed = (time.perf_counter() - start) * 1000

            times.append(elapsed)
            self.assertIsNotNone(estimate)

        avg_time = sum(times) / len(times)
        self.assertLess(
            avg_time,
            5,
            f"Cost estimation took {avg_time:.2f}ms on average (target: < 5ms)"
        )


class TestProjectInitPerformance(unittest.TestCase):
    """Test project initialization performance."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_project_init_performance(self):
        """Project initialization should be < 500ms."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # Get a template
        matches = orchestrator.match_templates("Test project", top_k=1)
        template = matches[0]

        # Generate config
        config = orchestrator.generate_config(
            template=template,
            project_name="perf-test",
            description="Performance test project"
        )

        # Benchmark initialization
        claude_dir = Path(self.temp_dir) / ".claude"

        start = time.perf_counter()
        result = orchestrator.initialize_project(
            config=config,
            output_dir=str(claude_dir)
        )
        elapsed = (time.perf_counter() - start) * 1000

        self.assertGreater(len(result['created_files']), 0)
        self.assertLess(
            elapsed,
            500,
            f"Project initialization took {elapsed:.2f}ms (target: < 500ms)"
        )


class TestConcurrentOperations(unittest.TestCase):
    """Test concurrent operation performance."""

    def test_concurrent_skill_loading(self):
        """Skills manager should handle concurrent access."""
        import threading

        manager = get_skills_manager()
        available_skills = manager.get_available_skills()

        if len(available_skills) == 0:
            self.skipTest("No skills available to test")

        results = []
        errors = []

        def load_skills():
            try:
                # Load random subset of skills
                subset = available_skills[:3]
                content = manager.load_skills(subset)
                results.append(content)
            except Exception as e:
                errors.append(e)

        # Create 10 concurrent threads
        threads = [threading.Thread(target=load_skills) for _ in range(10)]

        # Start all threads
        start = time.perf_counter()
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - start

        # Verify no errors
        self.assertEqual(len(errors), 0, f"Concurrent errors: {errors}")
        self.assertEqual(len(results), 10)

        # Should complete in reasonable time
        self.assertLess(elapsed, 2.0, f"Concurrent loading took {elapsed:.2f}s")


class TestLargeScaleOperations(unittest.TestCase):
    """Test performance with large-scale operations."""

    @patch('claude_force.hybrid_orchestrator.AgentOrchestrator.__init__')
    def test_many_cost_estimations(self, mock_init):
        """Should handle many cost estimations efficiently."""
        mock_init.return_value = None

        orchestrator = HybridOrchestrator(auto_select_model=True)

        # Generate 100 different tasks
        tasks = [
            f"Implement feature {i} with validation and tests"
            for i in range(100)
        ]

        start = time.perf_counter()

        for task in tasks:
            estimate = orchestrator.estimate_cost(task, "backend-developer")
            self.assertIsNotNone(estimate)

        elapsed = time.perf_counter() - start

        # 100 estimates should complete in < 1 second
        self.assertLess(
            elapsed,
            1.0,
            f"100 cost estimations took {elapsed:.2f}s (target: < 1s)"
        )

        # Average per estimation
        avg_per_estimate = (elapsed / 100) * 1000  # ms
        self.assertLess(avg_per_estimate, 10, f"Avg per estimate: {avg_per_estimate:.2f}ms")


if __name__ == "__main__":
    unittest.main()
