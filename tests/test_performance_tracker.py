"""
Tests for PerformanceTracker with ring buffer.

Tests verify that the ring buffer implementation prevents OOM and
maintains bounded memory usage even with millions of executions.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import time

from claude_force.performance_tracker import PerformanceTracker, ExecutionMetrics


class TestPerformanceTrackerBounds(unittest.TestCase):
    """Test ring buffer behavior and memory bounds."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.metrics_dir = str(Path(self.temp_dir) / ".claude" / "metrics")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_respects_max_entries(self):
        """Tracker respects max_entries limit."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100
        )

        # Add 200 metrics
        for i in range(200):
            tracker.record_execution(
                agent_name='test-agent',
                task=f'Task {i}',
                success=True,
                execution_time_ms=100.0,
                model='claude-3-5-sonnet-20241022',
                input_tokens=1000,
                output_tokens=500
            )

        # Should only have 100 (most recent)
        summary = tracker.get_summary()
        self.assertEqual(summary['in_memory_count'], 100)
        self.assertEqual(summary['total_executions'], 100)
        self.assertEqual(summary['max_entries'], 100)

    def test_ring_buffer_evicts_oldest(self):
        """Oldest metrics are evicted first."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=3
        )

        # Add metrics with different task hashes
        tracker.record_execution('agent', 'Task 1', True, 100, 'claude-3-5-sonnet-20241022', 1000, 500)
        time.sleep(0.01)  # Small delay to ensure different timestamps
        tracker.record_execution('agent', 'Task 2', True, 100, 'claude-3-5-sonnet-20241022', 1000, 500)
        time.sleep(0.01)
        tracker.record_execution('agent', 'Task 3', True, 100, 'claude-3-5-sonnet-20241022', 1000, 500)
        time.sleep(0.01)
        tracker.record_execution('agent', 'Task 4', True, 100, 'claude-3-5-sonnet-20241022', 1000, 500)

        # Get all metrics
        metrics = list(tracker._cache)
        task_hashes = [m.task_hash for m in metrics]

        # Should have 3 metrics (Task 2, 3, 4 - Task 1 was evicted)
        self.assertEqual(len(metrics), 3)

        # Verify Task 1 is not in cache
        task1_hash = tracker._task_hash('Task 1')
        self.assertNotIn(task1_hash, task_hashes)

    def test_memory_usage_estimate(self):
        """Memory usage estimation is reasonable."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=10000
        )

        # Add 1000 metrics
        for i in range(1000):
            tracker.record_execution(
                'agent',
                f'Task {i}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

        summary = tracker.get_summary()

        # ~1KB per entry = ~1MB for 1000 entries
        self.assertLess(summary['memory_usage_mb'], 2.0)
        self.assertGreater(summary['memory_usage_mb'], 0.5)

    def test_summary_caching(self):
        """Summary is cached when metrics don't change."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100
        )
        tracker.record_execution('agent', 'Task', True, 100, 'claude-3-5-sonnet-20241022', 1000, 500)

        # First call
        summary1 = tracker.get_summary()

        # Second call (should use cache)
        summary2 = tracker.get_summary()

        # Should be the same object (cached)
        self.assertIs(summary1, summary2)

        # Add new metric
        tracker.record_execution('agent', 'Task 2', True, 100, 'claude-3-5-sonnet-20241022', 1000, 500)

        # Third call (should recompute)
        summary3 = tracker.get_summary()

        # Should be a different object (recomputed)
        self.assertIsNot(summary3, summary2)
        self.assertNotEqual(summary3['total_executions'], summary2['total_executions'])

    def test_clear_method(self):
        """Clear method works correctly."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100
        )

        # Add some metrics
        for i in range(10):
            tracker.record_execution(
                'agent',
                f'Task {i}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

        # Verify metrics exist
        self.assertEqual(len(tracker._cache), 10)

        # Clear
        tracker.clear()

        # Verify cache is empty
        self.assertEqual(len(tracker._cache), 0)
        self.assertIsNone(tracker._summary_cache)
        self.assertTrue(tracker._cache_dirty)

        # Summary should return empty results
        summary = tracker.get_summary()
        self.assertEqual(summary['total_executions'], 0)

    def test_long_running_process_simulation(self):
        """Simulate long-running process with many executions."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=1000
        )

        # Simulate 100K executions
        for i in range(100_000):
            tracker.record_execution(
                'agent',
                f'Task {i % 100}',  # Reuse task descriptions
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

            # Check memory doesn't grow unbounded
            if i % 10000 == 0:
                summary = tracker.get_summary()
                self.assertLessEqual(summary['in_memory_count'], 1000)
                self.assertLess(summary['memory_usage_mb'], 2.0)

        # Final check
        final_summary = tracker.get_summary()
        self.assertEqual(final_summary['in_memory_count'], 1000)
        self.assertLess(final_summary['memory_usage_mb'], 2.0)

    def test_disable_persistence(self):
        """Can disable persistence for in-memory only mode."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100,
            enable_persistence=False
        )

        # Add metrics
        for i in range(10):
            tracker.record_execution(
                'agent',
                f'Task {i}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

        # Verify metrics in memory
        self.assertEqual(len(tracker._cache), 10)

        # Verify file was not created
        self.assertFalse(tracker.metrics_file.exists())

    def test_persistence_still_works(self):
        """Persistence to disk still works with ring buffer."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100,
            enable_persistence=True
        )

        # Add metrics
        for i in range(10):
            tracker.record_execution(
                'agent',
                f'Task {i}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

        # Verify file was created
        self.assertTrue(tracker.metrics_file.exists())

        # Verify file has correct number of lines
        with open(tracker.metrics_file, 'r') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 10)

    def test_clear_old_metrics(self):
        """clear_old_metrics works with ring buffer."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100
        )

        # Add some metrics
        for i in range(10):
            tracker.record_execution(
                'agent',
                f'Task {i}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

        # All metrics should be recent (< 1 day old)
        tracker.clear_old_metrics(days=1)

        # Should still have all metrics
        self.assertEqual(len(tracker._cache), 10)

        # Clear metrics older than 0 days (clears all)
        tracker.clear_old_metrics(days=0)

        # Should have no metrics
        self.assertEqual(len(tracker._cache), 0)

    def test_clear_old_metrics_preserves_disk_data(self):
        """clear_old_metrics reads from disk, not just ring buffer."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=5,  # Small ring buffer
            enable_persistence=True
        )

        # Add 20 metrics (more than ring buffer capacity)
        for i in range(20):
            tracker.record_execution(
                'agent',
                f'Task {i}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

        # Verify ring buffer only has 5 (most recent)
        self.assertEqual(len(tracker._cache), 5)

        # Verify disk file has all 20
        with open(tracker.metrics_file, 'r') as f:
            disk_lines = f.readlines()
        self.assertEqual(len(disk_lines), 20)

        # Clear old metrics (keep all since they're recent)
        tracker.clear_old_metrics(days=1)

        # Ring buffer should still have 5 (most recent)
        self.assertEqual(len(tracker._cache), 5)

        # Disk file should STILL have all 20 (no data loss)
        with open(tracker.metrics_file, 'r') as f:
            disk_lines = f.readlines()
        self.assertEqual(len(disk_lines), 20, "Disk data should not be lost")

        # Now clear very old metrics (older than 0 days = all)
        tracker.clear_old_metrics(days=0)

        # Both should be empty now
        self.assertEqual(len(tracker._cache), 0)
        with open(tracker.metrics_file, 'r') as f:
            disk_lines = f.readlines()
        self.assertEqual(len(disk_lines), 0)

    def test_configuration_options(self):
        """Configuration options work correctly."""
        # Test with different max_entries values
        tracker1 = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=50
        )
        self.assertEqual(tracker1.max_entries, 50)

        tracker2 = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=10000
        )
        self.assertEqual(tracker2.max_entries, 10000)

        # Test enable_persistence
        tracker3 = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100,
            enable_persistence=False
        )
        self.assertFalse(tracker3.enable_persistence)

    def test_time_filtered_summary_not_cached(self):
        """Time-filtered summary should not use cache."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=100
        )

        # Add metrics
        for i in range(10):
            tracker.record_execution(
                'agent',
                f'Task {i}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

        # Get summary with time filter (should not cache)
        summary1 = tracker.get_summary(hours=24)
        summary2 = tracker.get_summary(hours=24)

        # Should be different objects (not cached)
        self.assertIsNot(summary1, summary2)

        # But should have same values
        self.assertEqual(summary1['total_executions'], summary2['total_executions'])

    def test_backward_compatibility(self):
        """Tracker is backward compatible with old API."""
        # Can create with just metrics_dir
        tracker = PerformanceTracker(metrics_dir=self.metrics_dir)
        self.assertEqual(tracker.max_entries, 10000)  # Default value
        self.assertTrue(tracker.enable_persistence)  # Default value

        # Old methods still work
        metrics = tracker.record_execution(
            'agent',
            'Task',
            True,
            100,
            'claude-3-5-sonnet-20241022',
            1000,
            500
        )
        self.assertIsInstance(metrics, ExecutionMetrics)

        summary = tracker.get_summary()
        self.assertIn('total_executions', summary)

    def test_factory_function(self):
        """Factory function supports max_entries parameter."""
        from claude_force.performance_tracker import get_tracker

        tracker = get_tracker(
            metrics_dir=self.metrics_dir,
            max_entries=500
        )

        self.assertEqual(tracker.max_entries, 500)


class TestPerformanceTrackerStress(unittest.TestCase):
    """Stress tests for performance tracker."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.metrics_dir = str(Path(self.temp_dir) / ".claude" / "metrics")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_one_million_executions(self):
        """Handle 1 million executions without OOM."""
        tracker = PerformanceTracker(
            metrics_dir=self.metrics_dir,
            max_entries=10000,
            enable_persistence=False  # Disable for speed
        )

        # Add 1 million executions
        for i in range(1_000_000):
            tracker.record_execution(
                f'agent-{i % 10}',
                f'Task {i % 100}',
                True,
                100,
                'claude-3-5-sonnet-20241022',
                1000,
                500
            )

            # Periodic checks
            if i % 100000 == 0:
                summary = tracker.get_summary()
                # Memory should stay bounded
                self.assertLessEqual(summary['in_memory_count'], 10000)
                self.assertLess(summary['memory_usage_mb'], 15.0)

        # Final verification
        final_summary = tracker.get_summary()
        self.assertEqual(final_summary['in_memory_count'], 10000)
        self.assertLess(final_summary['memory_usage_mb'], 15.0)


if __name__ == "__main__":
    unittest.main()
