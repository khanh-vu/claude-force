#!/usr/bin/env python3
"""
Batch Processing Example

Demonstrates how to process multiple files/tasks with the claude-force package.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from claude_force import AgentOrchestrator


def main():
    """Process multiple code files for security review"""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    print("=" * 70)
    print("BATCH PROCESSING EXAMPLE - Security Review")
    print("=" * 70 + "\n")

    # Initialize orchestrator
    try:
        orchestrator = AgentOrchestrator()
        print("✅ AgentOrchestrator initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)

    # Define sample code files to review
    code_samples = [
        {
            "filename": "auth.py",
            "code": """
def authenticate_user(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = database.execute(query)
    return result.fetchone()
""",
        },
        {
            "filename": "api.py",
            "code": """
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(os.path.join('/uploads', file.filename))
    return "File uploaded"
""",
        },
        {
            "filename": "config.py",
            "code": """
# Database configuration
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "admin123"  # TODO: Move to env
SECRET_KEY = "hardcoded-secret-key-12345"
""",
        },
    ]

    print(f"📁 Files to review: {len(code_samples)}\n")

    # Process each file
    results = []
    start_time = datetime.now()

    for i, sample in enumerate(code_samples, 1):
        filename = sample["filename"]
        code = sample["code"]

        print(f"[{i}/{len(code_samples)}] Reviewing {filename}...")

        task = f"""
Review this code file for security vulnerabilities:

File: {filename}

```python
{code}
```

Provide:
1. Security issues found (OWASP classification if applicable)
2. Severity (Critical/High/Medium/Low)
3. Recommended fixes
4. Secure code example
"""

        try:
            result = orchestrator.run_agent(
                agent_name="security-specialist",
                task=task,
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                temperature=0.2,
            )

            results.append({"filename": filename, "success": result.success, "result": result})

            status = "✅" if result.success else "❌"
            print(f"  {status} {filename} - {'Success' if result.success else 'Failed'}")

        except Exception as e:
            print(f"  ❌ {filename} - Error: {e}")
            results.append({"filename": filename, "success": False, "result": None})

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 70 + "\n")

    success_count = sum(1 for r in results if r["success"])
    print(f"Total files: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print(f"Duration: {duration:.2f}s")
    print(f"Average time per file: {duration / len(results):.2f}s")

    # Detailed results
    print("\n" + "=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70 + "\n")

    for item in results:
        filename = item["filename"]
        result = item["result"]

        print(f"\n{'─' * 70}")
        print(f"File: {filename}")
        print(f"{'─' * 70}")

        if item["success"] and result:
            # Show first 500 chars of output
            output = result.output[:500]
            print(output)
            if len(result.output) > 500:
                print("\n... (output truncated)")
        else:
            print("❌ Review failed")
            if result and result.errors:
                for error in result.errors:
                    print(f"  • {error}")

    # Save results to file
    output_dir = Path("examples/python/output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"security_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    try:
        with open(output_file, "w") as f:
            f.write("SECURITY REVIEW RESULTS\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Files reviewed: {len(results)}\n")
            f.write(f"Successful: {success_count}\n\n")

            for item in results:
                f.write(f"\n{'=' * 70}\n")
                f.write(f"File: {item['filename']}\n")
                f.write(f"{'=' * 70}\n\n")

                if item["success"] and item["result"]:
                    f.write(item["result"].output)
                else:
                    f.write("❌ Review failed\n")

        print(f"\n\n📄 Full results saved to: {output_file}")

    except Exception as e:
        print(f"\n⚠️  Warning: Could not save results to file: {e}")

    print("\n" + "=" * 70)
    sys.exit(0 if success_count == len(results) else 1)


if __name__ == "__main__":
    main()
