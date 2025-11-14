#!/usr/bin/env python3
"""
Get expert reviews of the performance optimization plan.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_force.orchestrator import AgentOrchestrator

def main():
    orchestrator = AgentOrchestrator()

    # Read the optimization plan
    plan_path = Path(__file__).parent.parent / "docs" / "performance-optimization-plan.md"
    with open(plan_path) as f:
        plan_content = f.read()

    # Truncate for summary (first 15000 chars to fit in context)
    plan_summary = plan_content[:15000] + "\n\n[... document continues with implementation details, testing strategy, and appendices ...]"

    reviews = {}

    # 1. Claude Code Expert Review
    print("=" * 80)
    print("Getting claude-code-expert review...")
    print("=" * 80)

    claude_expert_task = f"""Review this performance optimization implementation plan for Claude Force.

PLAN SUMMARY:
{plan_summary}

Please provide a comprehensive architectural and design review covering:

1. **System Architecture & Design**:
   - Async/await implementation approach
   - Separation of concerns (AsyncAgentOrchestrator vs AgentOrchestrator)
   - Design patterns used (lazy initialization, factory pattern, etc.)

2. **Caching Architecture**:
   - ResponseCache design (TTL, LRU eviction)
   - Cache key generation strategy
   - Memory vs disk caching approach
   - Cache invalidation strategy

3. **DAG-based Workflow Execution**:
   - WorkflowDAG design and implementation
   - Cycle detection algorithm
   - Dependency resolution approach
   - Error handling in parallel execution

4. **Backward Compatibility**:
   - Strategy for maintaining 100% compatibility
   - Migration path design
   - Feature flag approach

5. **Scalability & Performance**:
   - Potential bottlenecks
   - Resource management (memory, file handles, connections)
   - Concurrency limits and semaphores

6. **Risk Mitigation**:
   - Identified risks and mitigations
   - Rollback strategy
   - Testing approach

Provide:
- ✅ What's well designed
- ⚠️ Potential issues or concerns
- 💡 Suggestions for improvements
- 🔄 Alternative approaches to consider
"""

    try:
        result1 = orchestrator.run_agent("claude-code-expert", claude_expert_task)
        review1 = result1.output if hasattr(result1, 'output') else str(result1)
        reviews['claude-code-expert'] = review1
        print("\n" + review1 + "\n")
    except Exception as e:
        print(f"Error getting claude-code-expert review: {e}")
        reviews['claude-code-expert'] = f"ERROR: {e}"

    print("\n" + "=" * 80)
    print("Getting code-reviewer review...")
    print("=" * 80)

    # 2. Code Reviewer Review
    code_reviewer_task = f"""Review this performance optimization implementation plan from a code quality perspective.

PLAN SUMMARY:
{plan_summary}

Focus on:

1. **Code Quality & Best Practices**:
   - Code organization and structure
   - Naming conventions
   - Error handling patterns
   - Resource cleanup (context managers, file handles)

2. **Potential Bugs & Edge Cases**:
   - Race conditions in async code
   - Cache corruption scenarios
   - DAG deadlock conditions
   - Memory leaks (cache growth, unclosed connections)
   - File handle exhaustion

3. **Testing Coverage**:
   - Unit test completeness
   - Integration test scenarios
   - Performance test design
   - Missing test cases

4. **Security Considerations**:
   - Input validation (agent names, task strings)
   - Cache poisoning risks
   - File path traversal in cache
   - API key handling in async context

5. **Maintainability**:
   - Code complexity
   - Documentation needs
   - Debugging considerations
   - Monitoring and observability

6. **Python-specific Issues**:
   - GIL implications
   - AsyncIO pitfalls
   - Type hints coverage
   - Exception handling in async context

Provide specific code review feedback with:
- 🐛 Bugs and critical issues
- ⚠️ Warnings and potential problems
- 📝 Code quality improvements
- 🔒 Security considerations
"""

    try:
        result2 = orchestrator.run_agent("code-reviewer", code_reviewer_task)
        review2 = result2.output if hasattr(result2, 'output') else str(result2)
        reviews['code-reviewer'] = review2
        print("\n" + review2 + "\n")
    except Exception as e:
        print(f"Error getting code-reviewer review: {e}")
        reviews['code-reviewer'] = f"ERROR: {e}"

    print("\n" + "=" * 80)
    print("Getting python-expert review...")
    print("=" * 80)

    # 3. Python Expert Review
    python_expert_task = f"""Review this performance optimization plan from a Python language and ecosystem perspective.

PLAN SUMMARY:
{plan_summary}

Focus on:

1. **AsyncIO Implementation**:
   - Proper async/await usage
   - AsyncIO best practices
   - Event loop management
   - Mixing sync and async code
   - AsyncIO pitfalls and gotchas

2. **Concurrency & Parallelism**:
   - GIL implications for I/O-bound vs CPU-bound tasks
   - asyncio.gather() usage
   - Semaphore usage for rate limiting
   - Thread safety considerations

3. **Python Performance Optimization**:
   - Lazy initialization patterns
   - Generator vs list comprehensions
   - dataclasses usage
   - Type hints for performance

4. **File I/O & Caching**:
   - aiofiles usage
   - JSON serialization performance
   - pathlib usage
   - File locking considerations

5. **Error Handling**:
   - Exception handling in async context
   - Context managers (async with)
   - Cleanup and resource management
   - Logging in async code

6. **Dependencies & Ecosystem**:
   - anthropic async client usage
   - aiofiles compatibility
   - pytest-asyncio testing
   - Type checking with mypy

7. **Python Version Compatibility**:
   - Python 3.8+ features used
   - Compatibility considerations
   - Type hints (list[] vs List[])

Provide Python-specific feedback:
- 🐍 Pythonic improvements
- ⚡ Performance optimizations
- 🔧 Better library usage
- 📚 Missing best practices
- ⚠️ Python-specific pitfalls
"""

    try:
        result3 = orchestrator.run_agent("python-expert", python_expert_task)
        review3 = result3.output if hasattr(result3, 'output') else str(result3)
        reviews['python-expert'] = review3
        print("\n" + review3 + "\n")
    except Exception as e:
        print(f"Error getting python-expert review: {e}")
        reviews['python-expert'] = f"ERROR: {e}"

    # Save reviews to file
    output_path = Path(__file__).parent.parent / "docs" / "performance-optimization-reviews.md"

    with open(output_path, 'w') as f:
        f.write("# Performance Optimization Plan - Expert Reviews\n\n")
        f.write("**Date:** 2025-11-14\n")
        f.write("**Reviewers:** claude-code-expert, code-reviewer, python-expert\n\n")
        f.write("---\n\n")

        f.write("## 1. Claude Code Expert Review\n\n")
        f.write("**Focus:** Architecture, Design Patterns, System Design\n\n")
        f.write(reviews.get('claude-code-expert', 'No review available') + "\n\n")
        f.write("---\n\n")

        f.write("## 2. Code Reviewer Review\n\n")
        f.write("**Focus:** Code Quality, Bugs, Security, Testing\n\n")
        f.write(reviews.get('code-reviewer', 'No review available') + "\n\n")
        f.write("---\n\n")

        f.write("## 3. Python Expert Review\n\n")
        f.write("**Focus:** Python Best Practices, AsyncIO, Performance\n\n")
        f.write(reviews.get('python-expert', 'No review available') + "\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("All three expert reviews have been completed. See sections above for detailed feedback.\n")

    print(f"\n✅ Reviews saved to: {output_path}")

    return reviews

if __name__ == "__main__":
    main()
