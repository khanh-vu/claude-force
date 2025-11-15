#!/usr/bin/env python3
"""
Performance profiling script for claude-force.

Measures startup time, config loading, agent selection, and execution overhead.
"""

import time
import sys
import os
import cProfile
import pstats
from io import StringIO
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def measure_startup_time():
    """Measure time to import claude_force."""
    start = time.perf_counter()
    import claude_force

    end = time.perf_counter()
    return (end - start) * 1000  # Convert to ms


def measure_config_load_time(config_path: str):
    """Measure time to load configuration."""
    from claude_force.orchestrator import AgentOrchestrator

    # Set dummy API key
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-dummy"

    start = time.perf_counter()
    try:
        orchestrator = AgentOrchestrator(config_path=config_path, enable_tracking=False)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None
    end = time.perf_counter()

    return (end - start) * 1000  # Convert to ms


def measure_agent_selection_time(config_path: str, iterations: int = 10):
    """Measure time for semantic agent selection."""
    try:
        from claude_force.semantic_selector import SemanticAgentSelector
    except ImportError:
        print("semantic_selector not available, skipping agent selection test")
        return None

    try:
        selector = SemanticAgentSelector(config_path=config_path)

        # Warm up
        selector.select_agents("Review code for security issues", top_k=3)

        # Measure
        start = time.perf_counter()
        for _ in range(iterations):
            selector.select_agents("Review code for security issues", top_k=3)
        end = time.perf_counter()

        avg_time = ((end - start) / iterations) * 1000  # Convert to ms
        return avg_time

    except ImportError:
        print("sentence-transformers not installed, skipping")
        return None


def measure_embedding_generation(config_path: str):
    """Measure time to generate embeddings."""
    try:
        from claude_force.semantic_selector import SemanticAgentSelector
    except ImportError:
        return None

    try:
        start = time.perf_counter()
        selector = SemanticAgentSelector(config_path=config_path)
        # Force embedding generation
        selector._ensure_initialized()
        end = time.perf_counter()

        return (end - start) * 1000  # Convert to ms
    except ImportError:
        return None


def profile_orchestrator_creation(config_path: str):
    """Profile orchestrator creation with cProfile."""
    from claude_force.orchestrator import AgentOrchestrator

    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-dummy"

    profiler = cProfile.Profile()
    profiler.enable()

    # Create orchestrator
    orchestrator = AgentOrchestrator(config_path=config_path, enable_tracking=False)

    profiler.disable()

    # Get stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)  # Top 20 functions

    return s.getvalue()


def find_config_file():
    """Find a valid config file for testing."""
    # Try common locations
    locations = [
        ".claude/claude.json",
        "../.claude/claude.json",
        "../../.claude/claude.json",
    ]

    for loc in locations:
        if Path(loc).exists():
            return str(Path(loc).resolve())

    return None


def main():
    """Run performance profiling."""
    print("=" * 80)
    print("claude-force Performance Profile")
    print("=" * 80)
    print()

    # Find config
    config_path = find_config_file()
    if not config_path:
        print("❌ No config file found. Create .claude/claude.json first.")
        print("   Try: claude-force init")
        return 1

    print(f"Using config: {config_path}")
    print()

    # 1. Startup time
    print("📊 Measuring startup time...")
    startup_time = measure_startup_time()
    print(f"   Startup time: {startup_time:.2f}ms")
    print()

    # 2. Config loading
    print("📊 Measuring config load time...")
    config_time = measure_config_load_time(config_path)
    if config_time:
        print(f"   Config load time: {config_time:.2f}ms")
    else:
        print("   ❌ Config load failed")
    print()

    # 3. Embedding generation
    print("📊 Measuring embedding generation...")
    embed_time = measure_embedding_generation(config_path)
    if embed_time:
        print(f"   Embedding generation: {embed_time:.2f}ms")
    else:
        print("   ⏭️  Skipped (semantic selector not available)")
    print()

    # 4. Agent selection
    print("📊 Measuring agent selection time (avg of 10)...")
    selection_time = measure_agent_selection_time(config_path)
    if selection_time:
        print(f"   Agent selection: {selection_time:.2f}ms")
    else:
        print("   ⏭️  Skipped (semantic selector not available)")
    print()

    # 5. Profile details
    print("📊 Detailed profiling of orchestrator creation...")
    print("-" * 80)
    profile_output = profile_orchestrator_creation(config_path)
    print(profile_output)
    print("-" * 80)
    print()

    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Startup time:        {startup_time:.2f}ms")
    if config_time:
        print(f"Config load:         {config_time:.2f}ms")
    if embed_time:
        print(f"Embedding gen:       {embed_time:.2f}ms")
    if selection_time:
        print(f"Agent selection:     {selection_time:.2f}ms")

    # Target metrics (from P2.13 acceptance criteria)
    print()
    print("Target Metrics:")
    print("  Startup time:      < 500ms")
    if selection_time:
        print("  Agent selection:   < 200ms (with cached embeddings)")
    print()

    # Recommendations
    print("Recommendations:")
    if startup_time > 500:
        print("  ⚠️  Startup time exceeds target - consider lazy imports")
    if config_time and config_time > 100:
        print("  ⚠️  Config load is slow - consider lazy loading")
    if embed_time and embed_time > 1000:
        print("  ⚠️  Embedding generation is slow - implement caching")
    if selection_time and selection_time > 200:
        print("  ⚠️  Agent selection is slow - cache embeddings")

    if startup_time < 500 and (not selection_time or selection_time < 200):
        print("  ✅ Performance is within target metrics!")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
