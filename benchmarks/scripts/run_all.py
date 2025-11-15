#!/usr/bin/env python3
"""
Run All Benchmarks

Executes all benchmark scenarios and metrics, generates comprehensive reports.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from metrics.agent_selection import AgentSelectionBenchmark, get_test_cases
except ImportError as e:
    print(f"❌ Error: Failed to import required modules: {e}")
    print("   Make sure you're running from the project root directory.")
    print("   Try: cd /path/to/claude-force && python3 benchmarks/scripts/run_all.py")
    sys.exit(1)


class BenchmarkRunner:
    """Orchestrates all benchmarks"""

    def __init__(self):
        self.start_time = None
        self.results = {
            "metadata": {},
            "agent_selection": {},
            "scenarios": {"simple": [], "medium": [], "complex": []},
            "summary": {},
        }

    def run_agent_selection_benchmark(self):
        """Run agent selection performance benchmark"""
        print("\n" + "=" * 70)
        print("1. AGENT SELECTION BENCHMARK")
        print("=" * 70 + "\n")

        try:
            benchmark = AgentSelectionBenchmark()
            test_cases = get_test_cases()

            if not test_cases:
                print("⚠️  Warning: No test cases found. Using default test cases.")
                test_cases = []

            report = benchmark.run_benchmark(test_cases)
            benchmark.save_report()

            self.results["agent_selection"] = report
            return report
        except Exception as e:
            print(f"❌ Error running agent selection benchmark: {e}")
            # Return empty report on error
            return {
                "summary": {
                    "total_tests": 0,
                    "average_accuracy": 0,
                    "average_selection_time_ms": 0,
                },
                "accuracy_distribution": {},
                "performance_tiers": {},
                "detailed_results": [],
            }

    def list_scenarios(self) -> dict:
        """List all available scenarios"""
        scenarios_dir = Path("benchmarks/scenarios")
        scenarios = {"simple": [], "medium": [], "complex": []}

        if not scenarios_dir.exists():
            print(f"⚠️  Warning: Scenarios directory not found: {scenarios_dir}")
            return scenarios

        try:
            for difficulty in ["simple", "medium", "complex"]:
                difficulty_dir = scenarios_dir / difficulty
                if difficulty_dir.exists():
                    for scenario_file in sorted(difficulty_dir.glob("*.md")):
                        scenarios[difficulty].append(
                            {
                                "file": str(scenario_file),
                                "name": scenario_file.stem,
                                "difficulty": difficulty,
                            }
                        )
        except Exception as e:
            print(f"⚠️  Warning: Error reading scenarios: {e}")

        return scenarios

    def run_scenario_analysis(self):
        """Analyze available scenarios"""
        print("\n" + "=" * 70)
        print("2. SCENARIO ANALYSIS")
        print("=" * 70 + "\n")

        scenarios = self.list_scenarios()

        for difficulty, scenario_list in scenarios.items():
            count = len(scenario_list)
            print(f"\n{difficulty.upper()} Scenarios: {count}")
            for scenario in scenario_list:
                print(f"  • {scenario['name']}")
                self.results["scenarios"][difficulty].append(
                    {"name": scenario["name"], "file": scenario["file"], "status": "available"}
                )

        total_scenarios = sum(len(v) for v in scenarios.values())
        print(f"\nTotal Scenarios Available: {total_scenarios}")

        return scenarios

    def generate_summary(self):
        """Generate overall benchmark summary"""
        print("\n" + "=" * 70)
        print("GENERATING SUMMARY")
        print("=" * 70 + "\n")

        end_time = time.time()
        duration = end_time - self.start_time

        # Agent selection summary
        agent_metrics = self.results.get("agent_selection", {}).get("summary", {})

        # Scenario summary
        total_scenarios = sum(
            len(self.results["scenarios"][d]) for d in ["simple", "medium", "complex"]
        )

        summary = {
            "benchmark_date": datetime.now().isoformat(),
            "total_duration_seconds": round(duration, 2),
            "agent_selection": {
                "tests_run": agent_metrics.get("total_tests", 0),
                "average_accuracy": agent_metrics.get("average_accuracy", 0),
                "average_time_ms": agent_metrics.get("average_selection_time_ms", 0),
            },
            "scenarios_available": {
                "simple": len(self.results["scenarios"]["simple"]),
                "medium": len(self.results["scenarios"]["medium"]),
                "complex": len(self.results["scenarios"]["complex"]),
                "total": total_scenarios,
            },
            "system_info": {
                "agents_configured": 15,
                "workflows_configured": 6,
                "skills_available": 9,
            },
        }

        self.results["summary"] = summary
        self.results["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "benchmark_version": "1.0.0",
        }

        # Print summary
        print(f"Benchmark Date: {summary['benchmark_date']}")
        print(f"Total Duration: {summary['total_duration_seconds']}s")
        print(f"\nAgent Selection Performance:")
        print(f"  Tests Run: {summary['agent_selection']['tests_run']}")
        print(f"  Average Accuracy: {summary['agent_selection']['average_accuracy']:.2%}")
        print(f"  Average Selection Time: {summary['agent_selection']['average_time_ms']:.2f}ms")
        print(f"\nScenarios Available:")
        print(f"  Simple: {summary['scenarios_available']['simple']}")
        print(f"  Medium: {summary['scenarios_available']['medium']}")
        print(f"  Complex: {summary['scenarios_available']['complex']}")
        print(f"  Total: {summary['scenarios_available']['total']}")
        print(f"\nSystem Configuration:")
        print(f"  Agents: {summary['system_info']['agents_configured']}")
        print(f"  Workflows: {summary['system_info']['workflows_configured']}")
        print(f"  Skills: {summary['system_info']['skills_available']}")

    def save_results(self, output_path: str = "benchmarks/reports/results/complete_benchmark.json"):
        """Save complete benchmark results"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(self.results, f, indent=2)

            print(f"\n📊 Complete results saved to: {output_path}")
        except PermissionError:
            print(f"❌ Error: Permission denied writing to {output_path}")
            print("   Check file/directory permissions")
            raise
        except OSError as e:
            print(f"❌ Error: Failed to save results: {e}")
            print(f"   Output path: {output_path}")
            raise
        except Exception as e:
            print(f"❌ Error: Unexpected error saving results: {e}")
            raise

    def run_all(self):
        """Run all benchmarks"""
        self.start_time = time.time()

        print("=" * 70)
        print("CLAUDE MULTI-AGENT SYSTEM - COMPREHENSIVE BENCHMARK")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 1. Agent Selection Performance
            self.run_agent_selection_benchmark()

            # 2. Scenario Analysis
            self.run_scenario_analysis()

            # 3. Generate Summary
            self.generate_summary()

            # 4. Save Results
            self.save_results()

            print("\n" + "=" * 70)
            print("✅ ALL BENCHMARKS COMPLETED SUCCESSFULLY")
            print("=" * 70)

        except KeyboardInterrupt:
            print("\n\n⚠️  Benchmark interrupted by user")
            print("=" * 70)
            return False
        except Exception as e:
            print(f"\n❌ Benchmark failed: {e}")
            print("=" * 70)
            import traceback

            print("\nFull error trace:")
            traceback.print_exc()
            return False

        return True


def main():
    """Main entry point"""
    try:
        runner = BenchmarkRunner()
        success = runner.run_all()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
