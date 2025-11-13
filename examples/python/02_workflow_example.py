#!/usr/bin/env python3
"""
Workflow Example

Demonstrates how to run a multi-agent workflow with the claude-force package.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from claude_force import AgentOrchestrator


def main():
    """Run a bug-fix workflow"""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    print("=" * 70)
    print("WORKFLOW EXAMPLE - Bug Fix Workflow")
    print("=" * 70 + "\n")

    # Initialize orchestrator
    try:
        orchestrator = AgentOrchestrator()
        print("✅ AgentOrchestrator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)

    # List available workflows
    print("\n📋 Available workflows:")
    workflows = orchestrator.list_workflows()
    for workflow_name, agents in workflows.items():
        print(f"  • {workflow_name}: {len(agents)} agents")

    # Define the task
    task = """
Bug Report:
- Feature: User login
- Issue: Users can't log in after password reset
- Error: "Invalid token" message appears
- Steps to reproduce:
  1. Click "Forgot Password"
  2. Enter email
  3. Receive reset link
  4. Click link
  5. Set new password
  6. Try to login
  7. Error appears

Please investigate, fix, and add tests.
"""

    print("\n📝 Task: Fix password reset bug")
    print(f"\nWorkflow: bug-fix")
    print("  Agents:")
    print("    1. bug-investigator - Root cause analysis")
    print("    2. code-reviewer - Review proposed fixes")
    print("    3. qc-automation-expert - Create tests")

    # Run the bug-fix workflow
    try:
        print("\n🔄 Running bug-fix workflow...\n")
        results = orchestrator.run_workflow(
            workflow_name='bug-fix',
            task=task,
            pass_output_to_next=True
        )

        print("\n" + "=" * 70)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 70 + "\n")

        success_count = sum(1 for r in results if r.success)
        total_count = len(results)

        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"Agent {i}/{total_count}: {result.agent_name} - {status}")

            if not result.success and result.errors:
                print(f"  Errors:")
                for error in result.errors:
                    print(f"    • {error}")

        print(f"\n📊 Overall: {success_count}/{total_count} agents succeeded")

        # Display final output
        if results and results[-1].success:
            print("\n" + "=" * 70)
            print("FINAL OUTPUT (from last agent)")
            print("=" * 70 + "\n")
            print(results[-1].output[:1000])  # Show first 1000 chars
            if len(results[-1].output) > 1000:
                print("\n... (output truncated)")

        # Exit with appropriate code
        sys.exit(0 if success_count == total_count else 1)

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
