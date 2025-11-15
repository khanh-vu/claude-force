#!/usr/bin/env python3
"""
Get expert reviews of the performance optimization implementation.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_force.orchestrator import AgentOrchestrator

def main():
    orchestrator = AgentOrchestrator()

    # Read the implementation files
    async_orch_path = Path(__file__).parent.parent / "claude_force" / "async_orchestrator.py"
    cache_path = Path(__file__).parent.parent / "claude_force" / "response_cache.py"
    summary_path = Path(__file__).parent.parent / "docs" / "performance-implementation-summary.md"

    with open(async_orch_path) as f:
        async_code = f.read()

    with open(cache_path) as f:
        cache_code = f.read()

    with open(summary_path) as f:
        summary = f.read()[:8000]  # Truncate for context

    reviews = {}

    # 1. Claude Code Expert Review
    print("=" * 80)
    print("Getting claude-code-expert review of implementation...")
    print("=" * 80)

    claude_expert_task = f"""Review the actual implementation code for the performance optimization.

IMPLEMENTATION SUMMARY:
{summary}

ASYNC ORCHESTRATOR CODE (claude_force/async_orchestrator.py):
```python
{async_code[:12000]}
```

RESPONSE CACHE CODE (claude_force/response_cache.py):
```python
{cache_code[:12000]}
```

Please provide a comprehensive review covering:

1. **Architecture Quality**:
   - Is the async implementation clean and well-structured?
   - Are the design patterns appropriately applied?
   - Is separation of concerns maintained?

2. **Implementation Completeness**:
   - Are all critical fixes properly implemented?
   - Are there any missing pieces?
   - Is error handling comprehensive?

3. **Code Quality**:
   - Are the implementations production-ready?
   - Is the code maintainable?
   - Are there any code smells?

4. **Performance Considerations**:
   - Will the async implementation deliver expected performance gains?
   - Is the cache implementation efficient?
   - Are there performance bottlenecks?

5. **Security**:
   - Are input validation checks sufficient?
   - Is HMAC implementation correct?
   - Are there security vulnerabilities?

Provide rating (1-5 stars) and recommendation: APPROVE / APPROVE WITH CHANGES / REJECT
"""

    try:
        result1 = orchestrator.run_agent("claude-code-expert", claude_expert_task)
        review1 = result1.output if hasattr(result1, 'output') else str(result1)
        reviews['claude-code-expert'] = review1
        print("\n" + review1 + "\n")
    except Exception as e:
        print(f"Error getting claude-code-expert review: {e}")
        reviews['claude-code-expert'] = f"ERROR: {e}"

    # 2. Code Reviewer Review
    print("\n" + "=" * 80)
    print("Getting code-reviewer review of implementation...")
    print("=" * 80)

    code_reviewer_task = f"""Review the actual implementation code for bugs, security issues, and code quality.

ASYNC ORCHESTRATOR (464 lines):
```python
{async_code[:15000]}
```

RESPONSE CACHE (518 lines):
```python
{cache_code[:15000]}
```

Focus your review on:

1. **Bug Detection**:
   - Are there any logical errors?
   - Race conditions in async code?
   - Cache corruption scenarios?
   - Memory leak potential?

2. **Security Analysis**:
   - Is input validation working correctly?
   - Can HMAC be bypassed?
   - Path traversal prevention effective?
   - Any injection vulnerabilities?

3. **Edge Cases**:
   - How does it handle timeouts?
   - What if API returns unexpected responses?
   - Concurrent access to cache?
   - Large file handling?

4. **Error Handling**:
   - Are exceptions properly caught?
   - Resource cleanup guaranteed?
   - Error messages informative?

5. **Testing Needs**:
   - What additional tests are needed?
   - Are edge cases covered?

Provide: BUG COUNT, SECURITY ISSUES, and recommendation: APPROVE / FIX REQUIRED / REJECT
"""

    try:
        result2 = orchestrator.run_agent("code-reviewer", code_reviewer_task)
        review2 = result2.output if hasattr(result2, 'output') else str(result2)
        reviews['code-reviewer'] = review2
        print("\n" + review2 + "\n")
    except Exception as e:
        print(f"Error getting code-reviewer review: {e}")
        reviews['code-reviewer'] = f"ERROR: {e}"

    # 3. Python Expert Review
    print("\n" + "=" * 80)
    print("Getting python-expert review of implementation...")
    print("=" * 80)

    python_expert_task = f"""Review the Python implementation quality and best practices.

CODE SAMPLE:
```python
{async_code[:10000]}

{cache_code[:10000]}
```

Analyze:

1. **AsyncIO Implementation**:
   - Is async/await used correctly?
   - Event loop handling proper?
   - asyncio.timeout() implementation correct?
   - Semaphore usage appropriate?

2. **Python Best Practices**:
   - Type hints correct and Python 3.8 compatible?
   - Dataclass usage appropriate?
   - Context managers used properly?
   - Logging structured correctly?

3. **Performance**:
   - Is asyncio.to_thread() usage correct?
   - heapq optimization implemented properly?
   - File I/O optimal?
   - Memory usage efficient?

4. **Pythonic Code**:
   - Code follows PEP 8?
   - Naming conventions good?
   - No Python anti-patterns?

5. **Dependencies**:
   - tenacity used correctly?
   - anthropic async client used properly?
   - Import statements correct?

Rate code quality (1-5 stars) and provide: PYTHONIC SCORE, recommendation: APPROVE / IMPROVE / REJECT
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
    output_path = Path(__file__).parent.parent / "docs" / "performance-implementation-reviews.md"

    with open(output_path, 'w') as f:
        f.write("# Performance Optimization Implementation - Expert Reviews\n\n")
        f.write("**Date:** 2025-11-14\n")
        f.write("**Code Reviewed:** async_orchestrator.py, response_cache.py\n")
        f.write("**Reviewers:** claude-code-expert, code-reviewer, python-expert\n\n")
        f.write("---\n\n")

        f.write("## 1. Architecture & Design Review (claude-code-expert)\n\n")
        f.write("**Focus:** Architecture quality, design patterns, implementation completeness\n\n")
        f.write(reviews.get('claude-code-expert', 'No review available') + "\n\n")
        f.write("---\n\n")

        f.write("## 2. Code Quality & Security Review (code-reviewer)\n\n")
        f.write("**Focus:** Bugs, security vulnerabilities, edge cases\n\n")
        f.write(reviews.get('code-reviewer', 'No review available') + "\n\n")
        f.write("---\n\n")

        f.write("## 3. Python Implementation Review (python-expert)\n\n")
        f.write("**Focus:** AsyncIO correctness, Python best practices, performance\n\n")
        f.write(reviews.get('python-expert', 'No review available') + "\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("All three expert reviews of the implementation have been completed. ")
        f.write("See sections above for detailed feedback.\n")

    print(f"\n✅ Implementation reviews saved to: {output_path}")

    return reviews

if __name__ == "__main__":
    main()
