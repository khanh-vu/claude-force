---
description: Analyze existing project for claude-force integration
usage: /review [path]
---

# Review Command

Analyze an existing project's .claude setup and provide recommendations for claude-force integration.

## Purpose

The `/review` command helps you:
- Assess existing .claude folder structure
- Detect technology stack (languages, frameworks, databases)
- Recommend appropriate agents for your project
- Identify potential issues or improvements
- Get project statistics and insights

## Usage

### Basic Review (Current Directory)
```
/review
```

### Review Specific Directory
```
/review /path/to/project
```

### With Output Format Options
```
/review --format markdown
/review --format json
/review --output report.md
```

## What Gets Analyzed

### Project Statistics
- Total files and lines of code
- File distribution by extension
- Project size (bytes)
- Test file detection
- Git repository status

### Technology Stack Detection
**Languages** (12+):
- Python, JavaScript, TypeScript, Java, Go, Rust
- C++, C, Ruby, PHP, Swift, Kotlin

**Frameworks** (9+):
- React, Vue.js, Angular, Next.js
- FastAPI, Django, Flask, Express.js, Spring Boot

**Databases** (5+):
- PostgreSQL, MySQL, MongoDB, Redis, SQLite

**Infrastructure & Tools**:
- Docker, Kubernetes, CI/CD pipelines
- Cloud providers (AWS, GCP, Azure)

### Agent Recommendations
Based on detected technologies, recommends:
- Relevant agents with confidence scores
- Agent priorities (primary, secondary, optional)
- Skill matches and capabilities

### Security Analysis
- Skips sensitive files (credentials, keys, .env)
- Validates project paths (prevents path traversal)
- Respects system boundaries

## Implementation

You should execute this command by:

1. **Import the ReviewCommand class**:
```python
from claude_force.commands.review import ReviewCommand
from pathlib import Path
```

2. **Determine the project path**:
   - If user provides a path argument, use that
   - Otherwise, use current working directory
   - Validate the path exists and is a directory

3. **Execute the review**:
```python
# Create command instance
command = ReviewCommand(Path(project_path))

# Run analysis
result = command.execute()

# Format output based on user preference
if format_preference == "markdown":
    output = command.format_markdown(result)
elif format_preference == "json":
    output = command.format_json(result)
else:
    output = command.format_markdown(result)  # default

# Display to user
print(output)
```

4. **Handle errors gracefully**:
   - ValueError: Invalid path, not a directory, or system directory
   - SecurityError: Path traversal attempt
   - Other exceptions: File permissions, I/O errors

## Output Format

### Markdown (Default)

```markdown
# Project Analysis Report

**Project**: /home/user/my-app
**Analyzed**: 2025-11-17 14:30:00

## Project Statistics

- **Total Files**: 127
- **Total Lines**: 15,234
- **Project Size**: 2.4 MB
- **Has Tests**: Yes
- **Git Repository**: Yes

### File Distribution
- Python (.py): 45 files
- JavaScript (.js): 32 files
- TypeScript (.ts): 28 files
- JSON (.json): 15 files
- Other: 7 files

## Technology Stack

### Languages
- Python
- JavaScript
- TypeScript

### Frameworks
- React
- FastAPI
- Next.js

### Databases
- PostgreSQL
- Redis

### Infrastructure
- Docker
- GitHub Actions

## Recommended Agents

### Primary Agents (High Priority)
1. **python-expert** (95% confidence)
   - Specialization: Python development
   - Skills: FastAPI, async, testing

2. **frontend-architect** (90% confidence)
   - Specialization: Frontend architecture
   - Skills: React, Next.js, TypeScript

### Secondary Agents (Medium Priority)
3. **database-architect** (85% confidence)
   - Specialization: Database design
   - Skills: PostgreSQL, Redis, caching

4. **devops-expert** (80% confidence)
   - Specialization: Infrastructure
   - Skills: Docker, CI/CD, deployment

### Optional Agents (Low Priority)
5. **qc-automation-expert** (70% confidence)
   - Specialization: Testing
   - Skills: Test automation, quality assurance

## Recommendations

Based on this analysis:
- ✅ Strong Python/FastAPI backend detected
- ✅ Modern React/Next.js frontend
- ✅ Proper database infrastructure
- ✅ Tests are present
- ⚠️ Consider adding API documentation
- 💡 Recommended workflow: **full-stack-feature**
```

### JSON Format

```json
{
  "timestamp": "2025-11-17T14:30:00",
  "project_path": "/home/user/my-app",
  "stats": {
    "total_files": 127,
    "total_lines": 15234,
    "total_size_bytes": 2515456,
    "files_by_extension": {
      ".py": 45,
      ".js": 32,
      ".ts": 28
    },
    "has_tests": true,
    "is_git_repo": true
  },
  "tech_stack": {
    "languages": ["Python", "JavaScript", "TypeScript"],
    "frameworks": ["React", "FastAPI", "Next.js"],
    "databases": ["PostgreSQL", "Redis"],
    "infrastructure": ["Docker", "GitHub Actions"]
  },
  "recommended_agents": [
    {
      "agent_name": "python-expert",
      "confidence": 0.95,
      "priority": "primary",
      "reason": "Strong Python/FastAPI presence"
    }
  ]
}
```

## Options

- `--format <markdown|json|dict>`: Output format (default: markdown)
- `--output <file>`: Save report to file instead of displaying
- `--skip-sensitive <true|false>`: Skip sensitive files (default: true)
- `--max-depth <number>`: Maximum directory depth to analyze
- `--max-files <number>`: Maximum number of files to analyze

## Examples

### Example 1: Quick Review
```
User: /review

You: Analyzing current project...
[Displays markdown report for current directory]
```

### Example 2: Review External Project
```
User: /review /home/user/other-project

You: Analyzing /home/user/other-project...
[Displays analysis results]
```

### Example 3: Export as JSON
```
User: /review --format json --output analysis.json

You: Analyzing current project...
Analysis saved to analysis.json
```

### Example 4: Review with Custom Options
```
User: /review --max-depth 5 --max-files 1000

You: Analyzing current project (max depth: 5, max files: 1000)...
[Displays filtered analysis]
```

## Error Handling

### Invalid Path
```
User: /review /nonexistent/path

You: ❌ Error: Path /nonexistent/path does not exist
Please provide a valid project directory.
```

### Security Violation
```
User: /review /etc

You: ❌ Error: Cannot analyze system directory /etc
This is prevented for security reasons.
```

### Permission Denied
```
User: /review /root/private

You: ❌ Error: Permission denied accessing /root/private
Please check directory permissions.
```

## Integration with Other Commands

After running `/review`, you might want to:

1. **Fix Issues**: Use `/restructure` to update .claude folder
2. **Add Agents**: Use `/pick-agent` to copy recommended agents
3. **Run Workflow**: Execute a workflow with recommended agents
4. **Validate Setup**: Ensure .claude structure is correct

## Best Practices

1. **Run Before Integration**: Always review before integrating claude-force
2. **Check Recommendations**: Review agent suggestions carefully
3. **Security First**: Command automatically skips sensitive files
4. **Save Reports**: Use `--output` to keep analysis records
5. **Iterative Analysis**: Re-run after making changes

## Technical Notes

### Implementation Details
- Built with TDD (Test-Driven Development)
- 9 comprehensive tests (100% pass rate)
- Security-first design (path validation, sensitive file detection)
- Performance optimized (lazy loading, caching)

### Test Coverage
- Basic functionality: Import, initialization, execution
- Input validation: Path checking, security boundaries
- Output formatting: Markdown, JSON, dictionary

### Security Features
- **Path Validation**: Prevents path traversal attacks
- **Sensitive File Detection**: 50+ patterns for credentials/keys
- **System Protection**: Blocks access to critical directories
- **Boundary Enforcement**: Keeps analysis within project scope

---

**Command Status**: ✅ Implemented, Tested, Ready for Use
**Version**: 1.0.0
**Last Updated**: 2025-11-17
