# CI/CD Integration Guide

This guide shows how to use Claude-Force in CI/CD pipelines with quiet mode and JSON output.

## Features for CI/CD

Claude-Force provides several features designed for CI/CD integration:

- **`--quiet` flag**: Suppresses verbose output (no emojis, minimal text)
- **`--format json` option**: Outputs machine-readable JSON
- **Proper exit codes**: Returns 0 on success, 1 on failure
- **Backward compatibility**: Existing `--json` flags still work

## Command Line Flags

### Quiet Mode

Use `--quiet` or `-q` to suppress verbose output:

```bash
claude-force run agent code-reviewer --task "Review changes" --quiet
```

### JSON Format

Use `--format json` to get machine-readable output:

```bash
claude-force run agent code-reviewer --task "Review changes" --format json
```

###Combined (Recommended for CI/CD)

```bash
claude-force run agent code-reviewer \
  --task "Review changes" \
  --quiet \
  --format json > result.json
```

## Exit Codes

Claude-Force follows standard Unix conventions:

- **Exit code 0**: Success
- **Exit code 1**: Failure (agent failed, command error, etc.)

Check exit codes in your CI/CD scripts:

```bash
if claude-force run agent test --task "Run tests" --quiet; then
  echo "Tests passed"
else
  echo "Tests failed"
  exit 1
fi
```

## JSON Output Format

### Run Agent

```json
{
  "success": true,
  "agent": "code-reviewer",
  "output": "Code review results...",
  "errors": [],
  "metadata": {
    "tokens_used": 1500,
    "model": "claude-3-5-sonnet-20241022",
    "execution_time": 2.5
  }
}
```

### Run Workflow

```json
{
  "success": true,
  "workflow": "ci-pipeline",
  "task": "Review and test PR",
  "total_tokens": 5000,
  "results": [
    {
      "agent": "code-reviewer",
      "success": true,
      "output": "Review results...",
      "errors": [],
      "metadata": {}
    },
    {
      "agent": "test-runner",
      "success": true,
      "output": "All tests passed",
      "errors": [],
      "metadata": {}
    }
  ]
}
```

### List Agents

```json
[
  {
    "name": "code-reviewer",
    "priority": 1,
    "domains": ["code", "review", "quality"]
  },
  {
    "name": "test-runner",
    "priority": 2,
    "domains": ["testing", "qa"]
  }
]
```

## GitHub Actions Example

```yaml
name: Code Review with Claude-Force

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Claude-Force
        run: pip install claude-force

      - name: Run Code Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude-force run agent code-reviewer \
            --task "Review the changes in this PR" \
            --quiet \
            --format json > review.json

      - name: Check Review Result
        run: |
          if [ $? -ne 0 ]; then
            echo "Code review failed"
            exit 1
          fi
          echo "Code review passed"

      - name: Post Review Comment
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = JSON.parse(fs.readFileSync('review.json', 'utf8'));

            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.name,
              body: `## AI Code Review\\n\\n${review.output}`
            });
```

## GitLab CI Example

```yaml
code-review:
  image: python:3.11
  stage: test
  before_script:
    - pip install claude-force
  script:
    - |
      claude-force run agent code-reviewer \
        --task "Review merge request changes" \
        --quiet \
        --format json > review.json
    - |
      if [ $? -ne 0 ]; then
        echo "Code review failed"
        cat review.json
        exit 1
      fi
  artifacts:
    paths:
      - review.json
    when: always
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

## CircleCI Example

```yaml
version: 2.1

jobs:
  code-review:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install Claude-Force
          command: pip install claude-force
      - run:
          name: Run Code Review
          command: |
            claude-force run agent code-reviewer \
              --task "Review code changes" \
              --quiet \
              --format json > review.json
      - run:
          name: Process Review
          command: |
            if [ $? -eq 0 ]; then
              echo "Review passed"
            else
              echo "Review failed"
              cat review.json
              exit 1
            fi
      - store_artifacts:
          path: review.json

workflows:
  version: 2
  review:
    jobs:
      - code-review:
          filters:
            branches:
              ignore: main
```

## Jenkins Pipeline Example

```groovy
pipeline {
    agent any

    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install claude-force'
            }
        }

        stage('Code Review') {
            steps {
                script {
                    def exitCode = sh(
                        script: """
                            claude-force run agent code-reviewer \
                                --task "Review PR changes" \
                                --quiet \
                                --format json > review.json
                        """,
                        returnStatus: true
                    )

                    if (exitCode != 0) {
                        error("Code review failed")
                    }

                    def review = readJSON file: 'review.json'
                    echo "Review output: ${review.output}"
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'review.json', fingerprint: true
        }
    }
}
```

## Best Practices

### 1. Use Environment Variables for API Keys

```bash
export ANTHROPIC_API_KEY="your-api-key"
claude-force run agent code-reviewer --task "..." --quiet --format json
```

### 2. Parse JSON Output

```bash
# Using jq to parse JSON
RESULT=$(claude-force run agent test --task "Run tests" --format json)
SUCCESS=$(echo $RESULT | jq -r '.success')

if [ "$SUCCESS" = "true" ]; then
  echo "Tests passed"
else
  echo "Tests failed"
  echo $RESULT | jq -r '.errors[]'
  exit 1
fi
```

### 3. Combine with Other Tools

```bash
# Run code review and save results
claude-force run agent code-reviewer \
  --task "Review changes" \
  --format json > review.json

# Use results in other tools
cat review.json | jq '.output' | tee code_review.txt

# Post to Slack, email, etc.
curl -X POST "https://hooks.slack.com/..." \
  -d "$(cat review.json | jq '{text: .output}')"
```

### 4. Handle Errors Gracefully

```bash
#!/bin/bash
set +e  # Don't exit on error

claude-force run agent code-reviewer \
  --task "Review code" \
  --quiet \
  --format json > review.json

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✓ Code review passed"
  jq -r '.output' review.json
else
  echo "✗ Code review failed (exit code: $EXIT_CODE)"
  jq -r '.errors[]' review.json
  exit 1
fi
```

### 5. Use Workflows for Complex Pipelines

```bash
# Run multi-agent workflow
claude-force run workflow ci-pipeline \
  --task "Review, test, and deploy" \
  --quiet \
  --format json > workflow_results.json

# Check if all agents succeeded
ALL_SUCCESS=$(jq -r '.success' workflow_results.json)

if [ "$ALL_SUCCESS" = "true" ]; then
  echo "All pipeline steps passed"
else
  echo "Pipeline failed"
  jq -r '.results[] | select(.success == false) | .agent + ": " + (.errors | join(", "))' workflow_results.json
  exit 1
fi
```

## Troubleshooting

### No Output in Quiet Mode

This is expected! Use `--format json` to get machine-readable output:

```bash
# Wrong: No output
claude-force list agents --quiet

# Right: JSON output
claude-force list agents --quiet --format json
```

### Exit Code Always 0

Make sure you're checking the exit code immediately:

```bash
# Wrong
claude-force run agent test --task "Test" --quiet
echo $?  # May show 0 even if failed

# Right
if claude-force run agent test --task "Test" --quiet; then
  echo "Success"
else
  echo "Failed"
fi
```

### Invalid JSON

Ensure you're using `--format json`:

```bash
# Wrong: Not valid JSON
claude-force run agent test --task "Test"

# Right: Valid JSON
claude-force run agent test --task "Test" --format json
```

## Supported Commands

The following commands support `--quiet` and `--format json`:

- ✅ `claude-force run agent`
- ✅ `claude-force run workflow`
- ✅ `claude-force list agents`
- ✅ `claude-force list workflows`

Other commands will be updated in future releases.
