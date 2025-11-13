# GitHub Actions Integration Examples

This directory contains example GitHub Actions workflows demonstrating how to integrate claude-force into your CI/CD pipeline for automated code review, security scanning, and documentation generation.

## 📋 Available Workflows

### 1. Code Review (`code-review.yml`)

Automatically reviews all code changes in pull requests using Claude's code-reviewer agent.

**Triggers:**
- Pull request opened, updated, or reopened
- Only for code files (`.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`)

**Features:**
- Reviews each changed file individually
- Checks code quality, potential bugs, and performance issues
- Posts review summary as PR comment
- Uploads detailed reviews as artifacts
- Tracks performance metrics

**Setup:**
```yaml
# Add to: .github/workflows/code-review.yml
```

### 2. Security Scan (`security-scan.yml`)

Performs comprehensive security analysis using Claude's security-specialist agent.

**Triggers:**
- Push to main/develop/staging branches
- Pull requests
- Weekly scheduled scan (Mondays at 2am)

**Features:**
- Scans for OWASP Top 10 vulnerabilities
- Detects SQL injection, XSS, authentication issues
- Identifies hardcoded secrets and weak cryptography
- Creates severity-based reports (CRITICAL/HIGH/MEDIUM/LOW)
- Fails build on critical/high vulnerabilities
- Auto-creates GitHub issues for critical findings

**Setup:**
```yaml
# Add to: .github/workflows/security-scan.yml
```

### 3. Documentation Generation (`docs-generation.yml`)

Automatically generates and updates documentation when code changes.

**Triggers:**
- Push to main branch (code changes in `src/`, `lib/`)
- Manual workflow dispatch

**Features:**
- Generates API documentation for changed files
- Creates changelog entries automatically
- Updates README.md when needed
- Commits documentation back to repository
- Supports markdown format

**Setup:**
```yaml
# Add to: .github/workflows/docs-generation.yml
```

## 🚀 Getting Started

### Prerequisites

1. **Anthropic API Key**: Get your API key from [Anthropic Console](https://console.anthropic.com/)

2. **GitHub Secret**: Add your API key as a repository secret:
   - Go to: Repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key

### Installation Steps

#### Option 1: Same Repository (Development)

If claude-force is in the same repository as your code:

```yaml
- name: Install claude-force
  run: |
    pip install -e .
```

#### Option 2: PyPI Package (Production)

If using claude-force as a package:

```yaml
- name: Install claude-force
  run: |
    pip install claude-force
```

#### Option 3: Specific Version

```yaml
- name: Install claude-force
  run: |
    pip install claude-force==2.1.0
```

### Basic Workflow Setup

1. **Copy workflow file** to `.github/workflows/`:
   ```bash
   mkdir -p .github/workflows
   cp examples/github-actions/code-review.yml .github/workflows/
   ```

2. **Configure secrets**:
   - Add `ANTHROPIC_API_KEY` to repository secrets

3. **Adjust permissions** (in workflow file):
   ```yaml
   permissions:
     contents: read       # Read repository code
     pull-requests: write # Comment on PRs
     issues: write        # Create security issues (for security-scan)
   ```

4. **Customize file patterns** (optional):
   ```yaml
   paths:
     - '**.py'      # Python files
     - '**.js'      # JavaScript files
     - '**.ts'      # TypeScript files
     - '**.java'    # Java files
     - '**.go'      # Go files
     - '**.rs'      # Rust files
     # Add more as needed
   ```

5. **Commit and push**:
   ```bash
   git add .github/workflows/
   git commit -m "ci: add Claude-powered code review"
   git push
   ```

## 🔧 Configuration Options

### Model Selection

Change the Claude model used for analysis:

```yaml
--model claude-3-5-sonnet-20241022  # Balanced (default)
--model claude-3-opus-20240229      # Most capable
--model claude-3-haiku-20240307     # Fastest, most economical
```

### Code Review Customization

Adjust review depth and focus:

```yaml
- name: Review changed files
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    TASK="Review this code focusing on:
    1. Security vulnerabilities
    2. Performance issues
    3. Code maintainability
    4. Best practices
    5. Potential bugs

    Provide specific, actionable feedback with file:line references."

    claude-force run agent code-reviewer \
      --task "$TASK" \
      --task-file "$file" \
      --output "reviews/$(basename $file).md"
```

### Security Scan Customization

Focus on specific security concerns:

```yaml
- name: Security scan
  run: |
    TASK="Focus security analysis on:
    1. Authentication bypass vulnerabilities
    2. Data injection attacks (SQL, NoSQL, Command)
    3. Sensitive data exposure
    4. API security issues

    For each finding provide exploitation scenario and remediation."

    claude-force run agent security-specialist --task "$TASK"
```

### Artifact Retention

Control how long reports are kept:

```yaml
- name: Upload report
  uses: actions/upload-artifact@v3
  with:
    retention-days: 30  # Keep for 30 days (default: 90)
```

## 📊 Performance Metrics

All workflows automatically track performance metrics:

```yaml
- name: Performance metrics
  run: |
    claude-force metrics summary
    claude-force metrics costs
```

View metrics in workflow logs or export for analysis.

## 💡 Usage Examples

### Example 1: Review Single PR

```bash
# Workflow runs automatically when PR is created
# Review appears as PR comment
```

### Example 2: Manual Security Scan

```bash
# Trigger manually from GitHub Actions UI:
# Actions → Claude Security Scan → Run workflow
```

### Example 3: Check Review Results

```bash
# Download artifacts from workflow run:
# Actions → Workflow Run → Artifacts → code-reviews
```

## 🎯 Best Practices

### 1. **Cost Management**

- Use Haiku model for routine checks
- Reserve Sonnet/Opus for critical reviews
- Set file size limits to avoid large token usage:

```yaml
- name: Check file size
  run: |
    for file in $FILES; do
      size=$(wc -l < "$file")
      if [ "$size" -gt 1000 ]; then
        echo "⚠️ Skipping large file: $file ($size lines)"
        continue
      fi
      # ... review file
    done
```

### 2. **Review Quality**

- Provide specific instructions for each agent
- Include relevant context (related files, design docs)
- Use appropriate agents for each task type

### 3. **Security**

- Never commit API keys to repository
- Use GitHub Secrets for sensitive data
- Rotate API keys regularly
- Monitor API usage in Anthropic Console

### 4. **Performance**

- Cache dependencies (pip, npm) for faster runs
- Run workflows only on relevant file changes
- Use parallel jobs for independent tasks:

```yaml
jobs:
  code-review:
    # ... review job

  security-scan:
    # ... security job (runs in parallel)
```

### 5. **Error Handling**

- Don't fail builds on review warnings
- Use `|| true` for non-critical steps
- Provide clear error messages:

```yaml
run: |
  claude-force run agent code-reviewer ... \
    || echo "⚠️ Code review failed - check logs for details"
```

## 🔍 Troubleshooting

### Workflow Not Triggering

**Problem**: Workflow doesn't run on PR
**Solution**: Check file path filters match your files

```yaml
paths:
  - '**.py'  # Must match your file extensions
```

### API Key Issues

**Problem**: "Authentication failed" error
**Solution**: Verify secret configuration

1. Check secret name matches: `ANTHROPIC_API_KEY`
2. Verify API key is valid in Anthropic Console
3. Ensure repository has access to secret

### High Costs

**Problem**: Unexpected API costs
**Solution**: Monitor and optimize usage

```yaml
# Add cost estimates to workflow
- name: Estimate cost
  run: |
    FILE_COUNT=$(echo "$FILES" | wc -l)
    AVG_COST=0.05  # ~$0.05 per file review
    ESTIMATED=$(echo "$FILE_COUNT * $AVG_COST" | bc)
    echo "💰 Estimated cost: \$$ESTIMATED"
```

### Review Quality Issues

**Problem**: Reviews are too generic
**Solution**: Provide more specific instructions

```yaml
TASK="Review focusing on:
- Database query optimization (we use PostgreSQL)
- React hook best practices (we use functional components)
- Error handling (we use custom error middleware)

Provide specific line numbers and code examples."
```

## 📚 Additional Resources

- **Claude-Force Documentation**: [Main README](../../README.md)
- **Agent Configuration**: [Agent Guide](../../docs/agents.md)
- **CLI Reference**: [CLI Documentation](../../docs/cli.md)
- **GitHub Actions Docs**: [GitHub Actions Documentation](https://docs.github.com/actions)

## 🤝 Contributing

Have ideas for more workflow examples? Contributions welcome!

1. Create new workflow example
2. Add documentation to this README
3. Test in a real repository
4. Submit PR with your example

## 📄 License

These examples are provided under the same license as claude-force (MIT).

---

**Need Help?** Open an issue or discussion in the claude-force repository.
