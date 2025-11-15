#!/usr/bin/env python3
"""
Simple Agent Example

Demonstrates how to run a single agent with the claude-force package.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from claude_force import AgentOrchestrator


def main():
    """Run a simple code review agent"""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    print("=" * 70)
    print("SIMPLE AGENT EXAMPLE - Code Review")
    print("=" * 70 + "\n")

    # Initialize orchestrator
    try:
        orchestrator = AgentOrchestrator()
        print("✅ AgentOrchestrator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)

    # Define the task
    task = """
Review this Python function for code quality, security, and performance:

```python
def process_user_input(user_input):
    # Execute user command
    import os
    os.system(user_input)
    return "Command executed"
```

Provide:
1. Security issues (if any)
2. Code quality issues
3. Performance considerations
4. Recommended fixes
"""

    print("Task: Review a Python function for security issues\n")

    # Run the code-reviewer agent
    try:
        print("🔄 Running code-reviewer agent...")
        result = orchestrator.run_agent(
            agent_name="code-reviewer",
            task=task,
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.3,
        )

        if result.success:
            print("\n" + "=" * 70)
            print("✅ AGENT EXECUTION SUCCESSFUL")
            print("=" * 70 + "\n")
            print(result.output)
            print("\n" + "=" * 70)
            print(f"Agent: {result.agent_name}")
            print(f"Model: {result.metadata.get('model', 'N/A')}")
            print(f"Tokens: {result.metadata.get('tokens_used', 'N/A')}")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("❌ AGENT EXECUTION FAILED")
            print("=" * 70 + "\n")
            print("Errors:")
            for error in result.errors or []:
                print(f"  • {error}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
