#!/usr/bin/env python3
"""
Get expert reviews of the GitHub Actions release workflow.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_force.orchestrator import AgentOrchestrator


def main():
    orchestrator = AgentOrchestrator()

    # Read the release workflow
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
    with open(workflow_path) as f:
        workflow_content = f.read()

    reviews = {}

    # 1. DevOps Architect Review
    print("=" * 80)
    print("Getting devops-architect review...")
    print("=" * 80)

    git_workflow_task = f"""Review this GitHub Actions release workflow for a Python package.

WORKFLOW FILE:
```yaml
{workflow_content}
```

Please provide a comprehensive review covering:

1. **Workflow Design & Best Practices**:
   - Job dependencies and execution order
   - Artifact handling between jobs
   - Use of GitHub Actions features (caching, outputs, etc.)
   - Workflow triggers and conditions
   - Concurrency and resource management

2. **Security & Permissions**:
   - Permissions configuration (contents, pull-requests)
   - Secret handling (PYPI_API_TOKEN)
   - Token usage in git operations
   - Security best practices

3. **Git Operations**:
   - Tag fetching and handling
   - Branch checkout strategies
   - Commit and push operations
   - Git configuration

4. **Release Process**:
   - Version extraction and handling
   - Changelog generation approach
   - GitHub Release creation
   - Post-release tasks

5. **Error Handling & Reliability**:
   - Job failure handling
   - Retry strategies
   - Rollback considerations
   - Skip-existing and idempotency

6. **Potential Issues**:
   - Race conditions
   - Network failures
   - Concurrent releases
   - Tag/commit mismatches

Provide:
- ✅ What's well implemented
- ⚠️ Potential issues or concerns
- 💡 Suggestions for improvements
- 🔄 Alternative approaches to consider
"""

    try:
        result1 = orchestrator.run_agent("devops-architect", git_workflow_task)
        review1 = result1.output if hasattr(result1, "output") else str(result1)
        reviews["devops-architect"] = review1
        print("\n" + review1 + "\n")
    except Exception as e:
        print(f"Error getting devops-architect review: {e}")
        reviews["devops-architect"] = f"ERROR: {e}"

    print("\n" + "=" * 80)
    print("Getting deployment-integration-expert review...")
    print("=" * 80)

    # 2. Deployment Integration Expert Review
    deployment_expert_task = f"""Review this Python package deployment workflow to PyPI.

WORKFLOW FILE:
```yaml
{workflow_content}
```

Focus on:

1. **PyPI Publishing**:
   - Authentication method (twine with API token)
   - Package building and validation
   - Artifact integrity checks
   - Upload strategy (skip-existing, non-interactive)

2. **Build Process**:
   - Python version selection
   - Dependency management
   - Build tool usage (python -m build)
   - Package validation (twine check --strict)

3. **Pre-release Validation**:
   - Version consistency checks
   - Test execution
   - Security scanning (bandit, safety)
   - Code formatting (black)

4. **Release Automation**:
   - Changelog generation (git-cliff)
   - GitHub Release creation
   - Announcement issue creation
   - Links and documentation

5. **Deployment Best Practices**:
   - Caching strategies (pip cache)
   - Artifact retention policies
   - Environment separation (pypi environment commented out)
   - TWINE_USERNAME/__token__ usage

6. **Production Readiness**:
   - Rollback capabilities
   - Version tagging strategy
   - Release validation
   - Monitoring and notifications

7. **Common Pitfalls**:
   - PyPI upload failures
   - Version conflicts
   - Metadata validation
   - Network timeouts

Provide deployment-specific feedback:
- 🚀 Deployment strengths
- ⚠️ Deployment risks
- 🔧 Configuration improvements
- 📦 Package quality checks
- 🔒 Security considerations
"""

    try:
        result2 = orchestrator.run_agent("deployment-integration-expert", deployment_expert_task)
        review2 = result2.output if hasattr(result2, "output") else str(result2)
        reviews["deployment-integration-expert"] = review2
        print("\n" + review2 + "\n")
    except Exception as e:
        print(f"Error getting deployment-integration-expert review: {e}")
        reviews["deployment-integration-expert"] = f"ERROR: {e}"

    # Save reviews to file
    output_path = Path(__file__).parent.parent / "RELEASE_WORKFLOW_REVIEW.md"

    with open(output_path, "w") as f:
        f.write("# Release Workflow - Expert Reviews\n\n")
        f.write("**Date:** 2025-11-15\n")
        f.write("**Reviewers:** devops-architect, deployment-integration-expert\n\n")
        f.write("---\n\n")

        f.write("## 1. DevOps Architect Review\n\n")
        f.write("**Focus:** GitHub Actions, Git Operations, Workflow Design, Infrastructure\n\n")
        f.write(reviews.get("devops-architect", "No review available") + "\n\n")
        f.write("---\n\n")

        f.write("## 2. Deployment Integration Expert Review\n\n")
        f.write("**Focus:** PyPI Publishing, Build Process, CI/CD, Production Readiness\n\n")
        f.write(reviews.get("deployment-integration-expert", "No review available") + "\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write(
            "Both expert reviews have been completed. See sections above for detailed feedback.\n"
        )

    print(f"\n✅ Reviews saved to: {output_path}")

    return reviews


if __name__ == "__main__":
    main()
