#!/usr/bin/env python3
"""
Agent Selection Performance Metrics

Measures the speed and accuracy of agent selection based on task descriptions.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class AgentSelectionMetric:
    """Metrics for a single agent selection"""

    task_description: str
    expected_agents: List[str]
    selected_agents: List[str]
    selection_time_ms: float
    accuracy: float
    timestamp: str


class AgentSelectionBenchmark:
    """Benchmark agent selection performance"""

    def __init__(self, claude_config_path: str = ".claude/claude.json"):
        """Initialize benchmark with Claude configuration"""
        self.config_path = Path(claude_config_path)
        self.agents = self._load_agents()
        self.results: List[AgentSelectionMetric] = []

    def _load_agents(self) -> Dict:
        """Load agent configuration"""
        with open(self.config_path) as f:
            config = json.load(f)
        return config.get("agents", {})

    def select_agents(self, task_description: str, task_category: str) -> Tuple[List[str], float]:
        """
        Simulate agent selection based on task description.

        In real implementation, this would use the actual agent selection logic.
        For benchmark purposes, we use keyword matching and domain analysis.
        """
        start_time = time.perf_counter()
        selected = []

        # Simple keyword-based selection (would be more sophisticated in reality)
        keywords_map = {
            "api": ["backend-architect", "api-documenter"],
            "endpoint": ["backend-architect"],
            "database": ["database-architect"],
            "schema": ["database-architect"],
            "frontend": ["frontend-architect", "ui-components-expert"],
            "react": ["frontend-architect", "ui-components-expert", "frontend-developer"],
            "component": ["ui-components-expert"],
            "test": ["qc-automation-expert"],
            "bug": ["bug-investigator", "code-reviewer"],
            "security": ["security-specialist"],
            "auth": ["backend-architect", "security-specialist"],
            "deploy": ["deployment-integration-expert"],
            "docker": ["devops-architect"],
            "documentation": ["document-writer-expert", "api-documenter"],
            "review": ["code-reviewer"],
        }

        task_lower = task_description.lower()

        # Find matching agents based on keywords
        for keyword, agents in keywords_map.items():
            if keyword in task_lower:
                for agent in agents:
                    if agent not in selected and agent in self.agents:
                        selected.append(agent)

        # If no agents selected, default to general agents
        if not selected:
            selected = ["backend-architect"]  # Safe default

        # Remove duplicates while preserving order
        selected = list(dict.fromkeys(selected))

        end_time = time.perf_counter()
        selection_time = (end_time - start_time) * 1000  # Convert to ms

        return selected, selection_time

    def calculate_accuracy(self, expected: List[str], selected: List[str]) -> float:
        """
        Calculate selection accuracy.

        Accuracy = (True Positives + True Negatives) / Total
        For simplicity: Accuracy = len(intersection) / len(union)
        """
        if not expected and not selected:
            return 1.0

        expected_set = set(expected)
        selected_set = set(selected)

        if not expected_set and selected_set:
            return 0.0

        intersection = expected_set.intersection(selected_set)
        union = expected_set.union(selected_set)

        return len(intersection) / len(union) if union else 0.0

    def run_benchmark(self, test_cases: List[Dict]) -> Dict:
        """
        Run benchmark on test cases.

        Args:
            test_cases: List of dicts with 'description', 'category', 'expected_agents'

        Returns:
            Aggregate metrics
        """
        print("Running Agent Selection Benchmark...\n")

        for i, test_case in enumerate(test_cases, 1):
            description = test_case["description"]
            category = test_case["category"]
            expected = test_case["expected_agents"]

            print(f"Test {i}/{len(test_cases)}: {description[:50]}...")

            selected, selection_time = self.select_agents(description, category)
            accuracy = self.calculate_accuracy(expected, selected)

            metric = AgentSelectionMetric(
                task_description=description,
                expected_agents=expected,
                selected_agents=selected,
                selection_time_ms=selection_time,
                accuracy=accuracy,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            )

            self.results.append(metric)

            status = "✅" if accuracy >= 0.8 else "⚠️" if accuracy >= 0.5 else "❌"
            print(f"  {status} Accuracy: {accuracy:.2%} | Time: {selection_time:.2f}ms")
            print(f"     Expected: {expected}")
            print(f"     Selected: {selected}\n")

        return self.generate_report()

    def generate_report(self) -> Dict:
        """Generate aggregate metrics report"""
        if not self.results:
            return {}

        total_tests = len(self.results)
        total_time = sum(r.selection_time_ms for r in self.results)
        avg_time = total_time / total_tests
        avg_accuracy = sum(r.accuracy for r in self.results) / total_tests

        high_accuracy = sum(1 for r in self.results if r.accuracy >= 0.8)
        medium_accuracy = sum(1 for r in self.results if 0.5 <= r.accuracy < 0.8)
        low_accuracy = sum(1 for r in self.results if r.accuracy < 0.5)

        report = {
            "summary": {
                "total_tests": total_tests,
                "average_accuracy": round(avg_accuracy, 4),
                "average_selection_time_ms": round(avg_time, 2),
                "total_time_ms": round(total_time, 2),
            },
            "accuracy_distribution": {
                "high (>= 80%)": high_accuracy,
                "medium (50-79%)": medium_accuracy,
                "low (< 50%)": low_accuracy,
            },
            "performance_tiers": {
                "fast (< 1ms)": sum(1 for r in self.results if r.selection_time_ms < 1),
                "normal (1-10ms)": sum(1 for r in self.results if 1 <= r.selection_time_ms < 10),
                "slow (>= 10ms)": sum(1 for r in self.results if r.selection_time_ms >= 10),
            },
            "detailed_results": [asdict(r) for r in self.results],
        }

        return report

    def save_report(self, output_path: str = "benchmarks/reports/results/agent_selection.json"):
        """Save report to file"""
        report = self.generate_report()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Report saved to: {output_path}")
        return report


def get_test_cases() -> List[Dict]:
    """Define test cases for benchmarking"""
    return [
        # Simple tasks
        {
            "description": "Add a health check endpoint to the API",
            "category": "backend",
            "expected_agents": ["backend-architect"],
        },
        {
            "description": "Fix bug in email validation that rejects valid emails with plus signs",
            "category": "bug-fix",
            "expected_agents": ["bug-investigator", "code-reviewer"],
        },
        {
            "description": "Update API documentation for new /health endpoint",
            "category": "documentation",
            "expected_agents": ["api-documenter", "document-writer-expert"],
        },
        # Medium tasks
        {
            "description": "Implement JWT-based user authentication with registration and login",
            "category": "backend",
            "expected_agents": ["backend-architect", "database-architect", "security-specialist"],
        },
        {
            "description": "Create a React component for user profile with form validation",
            "category": "frontend",
            "expected_agents": ["frontend-architect", "ui-components-expert", "frontend-developer"],
        },
        {
            "description": "Add database schema for orders with relationships to users and products",
            "category": "database",
            "expected_agents": ["database-architect"],
        },
        # Complex tasks
        {
            "description": "Build a complete user authentication system with frontend, backend, database, and security review",
            "category": "full-stack",
            "expected_agents": [
                "frontend-architect",
                "backend-architect",
                "database-architect",
                "security-specialist",
            ],
        },
        {
            "description": "Create Dockerfile for production deployment with multi-stage build and security hardening",
            "category": "devops",
            "expected_agents": ["devops-architect", "security-specialist"],
        },
        {
            "description": "Review pull request for security vulnerabilities, code quality, and test coverage",
            "category": "code-review",
            "expected_agents": ["code-reviewer", "security-specialist"],
        },
        {
            "description": "Investigate production bug causing intermittent 500 errors in payment processing",
            "category": "bug-fix",
            "expected_agents": ["bug-investigator", "backend-architect", "code-reviewer"],
        },
    ]


def main():
    """Run agent selection benchmark"""
    print("=" * 70)
    print("Agent Selection Performance Benchmark")
    print("=" * 70)
    print()

    benchmark = AgentSelectionBenchmark()
    test_cases = get_test_cases()

    report = benchmark.run_benchmark(test_cases)
    benchmark.save_report()

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Average Accuracy: {report['summary']['average_accuracy']:.2%}")
    print(f"Average Selection Time: {report['summary']['average_selection_time_ms']:.2f}ms")
    print(f"\nAccuracy Distribution:")
    for tier, count in report["accuracy_distribution"].items():
        print(f"  {tier}: {count} tests")
    print(f"\nPerformance Tiers:")
    for tier, count in report["performance_tiers"].items():
        print(f"  {tier}: {count} tests")
    print("=" * 70)


if __name__ == "__main__":
    main()
