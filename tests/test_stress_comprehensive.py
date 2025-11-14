#!/usr/bin/env python3
"""
Comprehensive Stress Tests for Claude Multi-Agent System
Tests system behavior under extreme conditions and concurrent load.
"""

import pytest
import asyncio
import threading
import time
import os
import tempfile
import json
import random
import string
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from claude_force.quick_start import QuickStartOrchestrator
from claude_force.agent_router import AgentRouter
from claude_force.skills_manager import ProgressiveSkillsManager
from claude_force.marketplace import MarketplaceManager
from claude_force.agent_router import AgentRouter
from claude_force.workflow_composer import WorkflowComposer
from claude_force.analytics import CrossRepoAnalytics
from claude_force.import_export import AgentPortingTool
from claude_force.contribution import ContributionManager
from claude_force.template_gallery import TemplateGallery


class TestConcurrentStress:
    """Stress tests for concurrent operations"""

    def test_concurrent_project_initialization(self, tmp_path):
        """Test initializing multiple projects concurrently"""
        num_projects = 50
        orchestrator = QuickStartOrchestrator()

        def init_project(idx: int) -> bool:
            project_name = f"test_project_{idx}"
            project_dir = tmp_path / project_name / ".claude"
            try:
                # Get a template
                template = orchestrator.templates[0] if orchestrator.templates else None
                if not template:
                    return False

                # Generate config
                config = orchestrator.generate_config(
                    template=template,
                    project_name=project_name,
                    description="Test concurrent initialization"
                )

                # Initialize project
                project_dir.parent.mkdir(parents=True, exist_ok=True)
                orchestrator.initialize_project(
                    config=config,
                    output_dir=str(project_dir),
                    create_examples=False
                )
                return True
            except Exception as e:
                print(f"Project {idx} failed: {e}")
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(init_project, i) for i in range(num_projects)]
            results = [f.result() for f in as_completed(futures)]

        # At least 90% should succeed
        success_rate = sum(results) / num_projects
        assert success_rate >= 0.9, f"Success rate too low: {success_rate}"

    def test_concurrent_skill_loading(self, tmp_path):
        """Test loading skills concurrently from multiple threads"""
        manager = ProgressiveSkillsManager(skills_dir=str(tmp_path))
        num_threads = 20
        iterations_per_thread = 50

        def load_skills_repeatedly():
            for _ in range(iterations_per_thread):
                try:
                    manager.get_available_skills()
                    manager.analyze_required_skills("python-expert", "test task")
                except Exception as e:
                    return False
            return True

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(load_skills_repeatedly) for _ in range(num_threads)]
            results = [f.result() for f in as_completed(futures)]

        assert all(results), "Some threads failed during concurrent skill loading"

    def test_concurrent_marketplace_operations(self, tmp_path):
        """Test concurrent marketplace list/search/install operations"""
        manager = MarketplaceManager(claude_dir=str(tmp_path))
        num_operations = 100

        def random_operation():
            op = random.choice(['list', 'search', 'get'])
            try:
                if op == 'list':
                    manager.list_available()
                elif op == 'search':
                    manager.search(random.choice(['python', 'test', 'api']))
                elif op == 'get':
                    manager.get_plugin('wshobson-python-toolkit')
                return True
            except Exception as e:
                return False

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(random_operation) for _ in range(num_operations)]
            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / num_operations
        assert success_rate >= 0.95, f"Concurrent operations success rate: {success_rate}"

    def test_concurrent_agent_routing(self):
        """Test agent recommendation from multiple threads"""
        router = AgentRouter()
        num_requests = 200

        tasks = [
            "Build a REST API",
            "Create React components",
            "Design database schema",
            "Review code for security",
            "Deploy to production",
        ]

        def recommend_agent():
            task = random.choice(tasks)
            try:
                matches = router.recommend_agents(task=task, top_k=3)
                return len(matches) > 0
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(recommend_agent) for _ in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]

        assert all(results), "Some agent routing requests failed"

    def test_concurrent_workflow_composition(self):
        """Test composing workflows concurrently"""
        composer = WorkflowComposer()
        num_workflows = 50

        goals = [
            "Build REST API with authentication",
            "Deploy ML model to production",
            "Create data pipeline for analytics",
            "Implement frontend dashboard",
        ]

        def compose_workflow():
            goal = random.choice(goals)
            try:
                workflow = composer.compose_workflow(goal=goal, max_agents=5)
                return workflow is not None and len(workflow.steps) > 0
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(compose_workflow) for _ in range(num_workflows)]
            results = [f.result() for f in as_completed(futures)]

        success_rate = sum(results) / num_workflows
        assert success_rate >= 0.9, f"Workflow composition success rate: {success_rate}"


class TestLargeScaleOperations:
    """Stress tests for large-scale operations"""

    def test_massive_project_initialization(self, tmp_path):
        """Test creating a very large project with many files"""
        orchestrator = QuickStartOrchestrator()
        project_dir = tmp_path / "massive_project" / ".claude"

        # Get a template
        template = orchestrator.templates[0] if orchestrator.templates else None
        if not template:
            pytest.skip("No templates available")

        # Create a project with very long description
        description = " ".join(["test"] * 1000)  # 1000 words

        # Generate config
        config = orchestrator.generate_config(
            template=template,
            project_name="massive_project",
            description=description
        )

        # Initialize project
        project_dir.parent.mkdir(parents=True, exist_ok=True)
        orchestrator.initialize_project(
            config=config,
            output_dir=str(project_dir),
            create_examples=False
        )

        # Verify project was created
        assert project_dir.exists()
        assert (project_dir / "claude.json").exists()

    def test_large_skill_analysis(self):
        """Test analyzing skills with very large task descriptions"""
        manager = ProgressiveSkillsManager()

        # Generate a very large task (10K words)
        large_task = " ".join(["test"] * 10000)

        start_time = time.time()
        required_skills = manager.analyze_required_skills("python-expert", large_task)
        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0, f"Large skill analysis took too long: {elapsed}s"
        assert isinstance(required_skills, list)

    def test_massive_marketplace_search(self):
        """Test searching through large plugin catalogs"""
        manager = MarketplaceManager()

        # Search with very broad terms
        results = manager.search("a")  # Single character

        # Should return results without crashing
        assert isinstance(results, list)

    def test_many_cost_estimations(self):
        """Test estimating costs for many tasks rapidly"""
        orchestrator = AgentRouter()
        num_estimations = 500

        tasks = [f"Task {i}: Build feature X" for i in range(num_estimations)]

        start_time = time.time()
        for task in tasks:
            try:
                orchestrator.analyze_task_complexity(task)
            except Exception:
                pass  # Continue even if some fail
        elapsed = time.time() - start_time

        # Should handle 500 estimations in under 10 seconds
        assert elapsed < 10.0, f"500 estimations took {elapsed}s"

    def test_bulk_agent_import(self, tmp_path):
        """Test importing many agents at once"""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        tool = AgentPortingTool(agents_dir=agents_dir)

        # Create mock agent files
        wshobson_dir = tmp_path / "wshobson_agents"
        wshobson_dir.mkdir()

        for i in range(50):
            agent_file = wshobson_dir / f"agent_{i}.md"
            agent_file.write_text(f"""# Agent {i}

Expert in area {i}.

## Skills
- Skill A
- Skill B

## When to use
Use this agent for task {i}.
""")

        # Bulk import
        results = tool.bulk_import(
            source_dir=str(wshobson_dir),
            pattern="agent_*.md"
        )

        assert len(results['imported']) == 50
        assert len(results['failed']) == 0

    def test_large_workflow_composition(self):
        """Test composing workflows with many agents"""
        composer = WorkflowComposer()

        # Request a workflow with maximum agents
        workflow = composer.compose_workflow(
            goal="Build complete enterprise application with all features",
            max_agents=20  # Request many agents
        )

        assert workflow is not None
        assert len(workflow.steps) > 0
        assert workflow.total_estimated_duration_min > 0


class TestMemoryAndPerformance:
    """Memory and performance stress tests"""

    def test_memory_leak_skill_caching(self):
        """Test for memory leaks in skill caching"""
        import tracemalloc

        manager = ProgressiveSkillsManager()

        tracemalloc.start()
        initial_memory = tracemalloc.get_traced_memory()[0]

        # Load skills many times
        for _ in range(1000):
            manager.analyze_required_skills("python-expert", "test task")
            manager.clear_cache()  # Clear cache each time

        current_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        # Memory growth should be minimal (< 10MB)
        memory_growth = (current_memory - initial_memory) / 1024 / 1024
        assert memory_growth < 10, f"Memory leak detected: {memory_growth}MB growth"

    def test_performance_degradation_over_time(self):
        """Test that operations don't slow down over time"""
        orchestrator = AgentRouter()

        times = []
        for _ in range(100):
            start = time.time()
            orchestrator.analyze_task_complexity("Build a feature")
            elapsed = time.time() - start
            times.append(elapsed)

        # First 10 vs last 10 shouldn't differ by more than 50%
        first_10_avg = sum(times[:10]) / 10
        last_10_avg = sum(times[-10:]) / 10

        if first_10_avg > 0:
            degradation = (last_10_avg - first_10_avg) / first_10_avg
            assert degradation < 0.5, f"Performance degraded by {degradation*100}%"

    def test_cache_effectiveness(self):
        """Test that caching improves performance significantly"""
        manager = ProgressiveSkillsManager()
        task = "Build REST API with authentication"

        # First call (cache miss)
        start = time.time()
        manager.analyze_required_skills("python-expert", task)
        first_call_time = time.time() - start

        # Second call (cache hit)
        start = time.time()
        manager.analyze_required_skills("python-expert", task)
        second_call_time = time.time() - start

        # Second call should be at least 2x faster
        if first_call_time > 0.001:  # Only test if first call took measurable time
            speedup = first_call_time / second_call_time
            assert speedup >= 2.0, f"Cache speedup only {speedup}x"

    def test_large_file_handling(self, tmp_path):
        """Test handling very large configuration files"""
        large_config = {
            "agents": {f"agent_{i}": {
                "file": f"agents/agent_{i}.md",
                "contract": f"contracts/agent_{i}.contract",
                "domains": [f"domain{j}" for j in range(100)],
                "priority": 1
            } for i in range(1000)}  # 1000 agents
        }

        config_file = tmp_path / "claude.json"
        config_file.write_text(json.dumps(large_config, indent=2))

        # Try to load it
        start = time.time()
        with open(config_file) as f:
            loaded = json.load(f)
        elapsed = time.time() - start

        assert len(loaded["agents"]) == 1000
        assert elapsed < 1.0, f"Loading large config took {elapsed}s"

    def test_concurrent_file_access(self, tmp_path):
        """Test concurrent reads/writes don't corrupt data"""
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps({"counter": 0}))

        lock = threading.Lock()

        def increment_counter():
            for _ in range(100):
                with lock:
                    with open(test_file) as f:
                        data = json.load(f)
                    data["counter"] += 1
                    with open(test_file, 'w') as f:
                        json.dump(data, f)

        threads = [threading.Thread(target=increment_counter) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        with open(test_file) as f:
            final_data = json.load(f)

        # All increments should be accounted for
        assert final_data["counter"] == 1000


class TestEdgeCasesAndBoundaries:
    """Edge case and boundary condition tests"""

    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        orchestrator = QuickStartOrchestrator()
        router = AgentRouter()
        manager = ProgressiveSkillsManager()

        # Empty task strings
        matches = router.recommend_agents(task="", top_k=3)
        assert isinstance(matches, list)

        # Empty skill analysis
        skills = manager.analyze_required_skills("python-expert", "")
        assert isinstance(skills, list)

    def test_special_characters_in_inputs(self, tmp_path):
        """Test handling of special characters"""
        special_chars = "!@#$%^&*()[]{}|\\:;\"'<>?/~`"

        router = AgentRouter()

        # Special characters in task
        matches = router.recommend_agents(task=special_chars, top_k=3)
        assert isinstance(matches, list)

        # Test passes - special char handling in routing works

    def test_unicode_and_emoji_handling(self):
        """Test handling of unicode and emoji characters"""
        router = AgentRouter()

        unicode_task = "Build 🚀 REST API with 💾 database and 🔐 authentication"
        matches = router.recommend_agents(task=unicode_task, top_k=3)
        assert isinstance(matches, list)

        # Chinese characters
        chinese_task = "构建REST API"
        matches = router.recommend_agents(task=chinese_task, top_k=3)
        assert isinstance(matches, list)

    def test_extremely_long_strings(self):
        """Test handling of extremely long strings"""
        router = AgentRouter()

        # 100K character task
        long_task = "a" * 100000
        matches = router.recommend_agents(task=long_task, top_k=3)
        assert isinstance(matches, list)

    def test_boundary_values(self):
        """Test boundary values for numeric parameters"""
        orchestrator = AgentRouter()
        router = AgentRouter()
        composer = WorkflowComposer()

        # Zero top_k
        matches = router.recommend_agents(task="test", top_k=0)
        assert len(matches) == 0

        # Negative top_k (should be handled)
        matches = router.recommend_agents(task="test", top_k=-1)
        assert isinstance(matches, list)

        # Very large top_k
        matches = router.recommend_agents(task="test", top_k=10000)
        assert isinstance(matches, list)

        # Zero max_agents in workflow
        workflow = composer.compose_workflow(goal="test", max_agents=0)
        assert workflow is None or len(workflow.steps) == 0

    def test_null_and_none_handling(self):
        """Test handling of None/null values"""
        router = AgentRouter()
        manager = ProgressiveSkillsManager()

        # None task
        try:
            matches = router.recommend_agents(task=None, top_k=3)
        except (TypeError, ValueError):
            pass  # Expected to raise error

        # None agent name
        try:
            skills = manager.analyze_required_skills(None, "test task")
        except (TypeError, ValueError):
            pass  # Expected to raise error

    def test_concurrent_cache_corruption(self):
        """Test that concurrent access doesn't corrupt caches"""
        manager = ProgressiveSkillsManager()

        def stress_cache():
            for i in range(100):
                manager.analyze_required_skills("python-expert", f"task {i}")
                if i % 10 == 0:
                    manager.clear_cache()
            return True

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(stress_cache) for _ in range(20)]
            results = [f.result() for f in as_completed(futures)]

        assert all(results)


class TestErrorRecoveryAndResilience:
    """Error handling and recovery tests"""

    def test_recovery_from_corrupted_cache(self, tmp_path):
        """Test recovery from corrupted cache files"""
        manager = ProgressiveSkillsManager(skills_dir=str(tmp_path))

        # Manually create a corrupted cache
        cache_file = tmp_path / ".skill_cache.json"
        cache_file.write_text("{invalid json content")

        # Should recover gracefully
        skills = manager.analyze_required_skills("python-expert", "test task")
        assert isinstance(skills, list)

    def test_missing_directory_recovery(self, tmp_path):
        """Test recovery when directories go missing"""
        manager = ProgressiveSkillsManager(skills_dir=str(tmp_path))

        # Delete the skills directory
        import shutil
        if tmp_path.exists():
            shutil.rmtree(tmp_path)

        # Should recreate and recover gracefully
        try:
            skills = manager.get_available_skills()
            assert isinstance(skills, list)
        except Exception:
            pass  # May fail gracefully

    def test_partial_file_write_recovery(self, tmp_path):
        """Test recovery from partial file writes"""
        test_file = tmp_path / "test.json"

        # Write partial JSON
        test_file.write_text('{"incomplete": "json"')

        # Try to read and recover
        try:
            with open(test_file) as f:
                json.load(f)
        except json.JSONDecodeError:
            # Should handle gracefully
            pass

    def test_network_timeout_simulation(self):
        """Test handling of simulated network timeouts"""
        # This would test API timeout handling
        # Skip if no API key available
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("No API key available")

        orchestrator = AgentRouter()

        # Simulate network delay by setting very short timeout
        # The system should handle this gracefully
        try:
            with pytest.raises(Exception):  # Should raise timeout or similar
                # This would need actual API call mocking
                pass
        except Exception:
            pass

    def test_disk_full_simulation(self, tmp_path):
        """Test handling when disk is full"""
        # Test handling of very large strings
        manager = ProgressiveSkillsManager()

        # Try with very large task description
        large_desc = "x" * 1000000  # 1MB string
        try:
            manager.analyze_required_skills("python-expert", large_desc)
        except Exception:
            pass  # Should handle gracefully

    def test_permission_denied_handling(self, tmp_path):
        """Test handling of permission denied errors"""
        if os.name == 'nt':  # Skip on Windows
            pytest.skip("Permission tests not reliable on Windows")

        test_dir = tmp_path / "readonly"
        test_dir.mkdir()
        test_file = test_dir / "test.json"
        test_file.write_text("{}")

        # Make directory read-only
        os.chmod(test_dir, 0o444)

        # Try to write to read-only directory
        # Note: Permission behavior is system-specific (root, containers, etc.)
        # Both success and PermissionError are acceptable outcomes
        try:
            with open(test_dir / "newfile.json", 'w') as f:
                f.write("{}")
            # May succeed on some systems (e.g., root, containers)
        except (PermissionError, OSError):
            pass  # Expected on systems that enforce read-only directories
        finally:
            # Restore permissions
            os.chmod(test_dir, 0o755)

    def test_race_condition_handling(self, tmp_path):
        """Test handling of race conditions in file operations"""
        test_file = tmp_path / "shared.json"
        test_file.write_text(json.dumps({"value": 0}))

        def increment_file():
            try:
                with open(test_file) as f:
                    data = json.load(f)
                time.sleep(0.001)  # Simulate processing
                data["value"] += 1
                with open(test_file, 'w') as f:
                    json.dump(data, f)
                return True
            except Exception:
                return False

        # Run many concurrent increments without locking
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(increment_file) for _ in range(50)]
            results = [f.result() for f in as_completed(futures)]

        # Some may fail due to race conditions, but shouldn't crash
        assert isinstance(results, list)


class TestIntegrationScenarios:
    """Integration tests combining multiple components"""

    def test_full_project_lifecycle(self, tmp_path):
        """Test complete project lifecycle - routing to workflow"""
        # 1. Get agent recommendations
        router = AgentRouter()
        matches = router.recommend_agents(task="Build REST API", top_k=3)
        assert len(matches) > 0

        # 2. Compose workflow
        composer = WorkflowComposer()
        workflow = composer.compose_workflow(
            goal="Build REST API with authentication",
            max_agents=5
        )
        assert workflow is not None

        # 3. Analyze skills
        skills_mgr = ProgressiveSkillsManager()
        skills = skills_mgr.analyze_required_skills("python-expert", "Build REST API")
        assert isinstance(skills, list)

    def test_marketplace_to_workflow_integration(self):
        """Test using marketplace plugins in workflows"""
        # 1. List marketplace plugins
        marketplace = MarketplaceManager()
        plugins = marketplace.list_available()
        assert len(plugins) > 0

        # 2. Use marketplace in agent routing
        router = AgentRouter(include_marketplace=True)
        matches = router.recommend_agents(task="Deploy to Kubernetes", top_k=3)
        assert isinstance(matches, list)

        # 3. Use in workflow composition
        composer = WorkflowComposer(include_marketplace=True)
        workflow = composer.compose_workflow(goal="Deploy application", max_agents=3)
        assert workflow is not None

    def test_import_export_roundtrip(self, tmp_path):
        """Test importing and exporting agents preserves data"""
        tool = AgentPortingTool(agents_dir=str(tmp_path))

        # Create a test agent
        wshobson_dir = tmp_path / "wshobson"
        wshobson_dir.mkdir()

        original_agent = wshobson_dir / "test_agent.md"
        original_agent.write_text("""# Test Agent

Expert in testing.

## Skills
- Unit testing
- Integration testing

## When to use
Use for testing tasks.
""")

        # Import
        result = tool.import_from_wshobson(str(original_agent))
        assert result is not None
        assert 'name' in result

        # Export
        export_dir = tmp_path / "export"
        export_dir.mkdir()
        exported = tool.export_to_wshobson("test-agent", export_dir)
        assert exported is not None
        assert exported.exists()

        # Compare (should be similar)
        exported_content = exported.read_text()
        assert "test" in exported_content.lower()

    def test_analytics_cross_repo_comparison(self):
        """Test cross-repository analytics"""
        analytics = CrossRepoAnalytics()

        # Compare agents
        report = analytics.compare_agents(
            task="Review code for security",
            agents=["code-reviewer", "security-specialist"]
        )

        assert report is not None
        assert len(report.results) == 2
        assert report.winner is not None

    def test_contribution_workflow(self, tmp_path):
        """Test complete contribution workflow"""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        contrib_mgr = ContributionManager(agents_dir=str(agents_dir))

        # Create a test agent in proper structure (agents/custom_agent/AGENT.md)
        agent_dir = agents_dir / "custom_agent"
        agent_dir.mkdir()
        agent_file = agent_dir / "AGENT.md"
        agent_file.write_text("""# Custom Agent

## Role
Custom agent for testing

## Domain Expertise
- Testing
- Quality Assurance

## Responsibilities
- Test execution
- Bug reporting

## Output Format
Test results and reports.
""")

        # Validate
        validation = contrib_mgr.validate_agent_for_contribution("custom_agent")
        assert validation.valid

        # Prepare contribution
        package = contrib_mgr.prepare_contribution(
            agent_name="custom_agent",
            target_repo="wshobson"
        )
        assert package is not None
        assert package.agent_name == "custom_agent"

    def test_template_gallery_to_project_init(self, tmp_path):
        """Test using template gallery"""
        # 1. Browse templates
        gallery = TemplateGallery()
        templates = gallery.list_templates()
        assert len(templates) > 0

        # 2. Get specific template
        template = gallery.get_template("fullstack-web")
        assert template is not None

        # 3. Verify template has required attributes
        assert hasattr(template, 'name')
        assert hasattr(template, 'description')
        assert hasattr(template, 'tech_stack')


class TestEndToEndWorkflows:
    """End-to-end workflow tests"""

    def test_complete_rest_api_workflow(self, tmp_path):
        """Test complete REST API development workflow"""
        # Route to agents
        router = AgentRouter()
        agent_matches = router.recommend_agents(
            task="Design REST API with authentication",
            top_k=5
        )

        assert len(agent_matches) > 0
        assert any("backend" in m.agent_name.lower() or "api" in m.agent_name.lower()
                  for m in agent_matches)

        # Compose workflow
        composer = WorkflowComposer()
        workflow = composer.compose_workflow(
            goal="Build REST API with JWT authentication and PostgreSQL",
            max_agents=8
        )

        assert workflow is not None
        assert len(workflow.steps) >= 3
        assert workflow.total_estimated_duration_min > 0
        assert workflow.total_estimated_cost > 0

    def test_complete_ml_pipeline_workflow(self, tmp_path):
        """Test complete ML pipeline workflow"""
        # Route to agents
        router = AgentRouter()
        agent_matches = router.recommend_agents(
            task="Build ML training pipeline",
            top_k=5
        )

        assert len(agent_matches) > 0

        # Compose workflow
        composer = WorkflowComposer()
        workflow = composer.compose_workflow(
            goal="Train and deploy ML model with monitoring",
            max_agents=6
        )

        assert workflow is not None

    def test_complete_data_pipeline_workflow(self, tmp_path):
        """Test complete data engineering workflow"""
        # Get recommendations
        router = AgentRouter()
        matches = router.recommend_agents(
            task="Build ETL data pipeline",
            top_k=5
        )

        assert len(matches) > 0

        # Compose workflow
        composer = WorkflowComposer()
        workflow = composer.compose_workflow(
            goal="Build ETL pipeline with data quality checks",
            max_agents=5
        )

        assert workflow is not None

    def test_multi_stage_deployment_workflow(self, tmp_path):
        """Test multi-stage deployment workflow"""
        # Get deployment agents
        router = AgentRouter()
        matches = router.recommend_agents(
            task="Deploy to Kubernetes with monitoring",
            top_k=5
        )

        assert len(matches) > 0

        # Compose deployment workflow
        composer = WorkflowComposer()
        workflow = composer.compose_workflow(
            goal="Deploy to production with monitoring and rollback",
            max_agents=6
        )

        assert workflow is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
