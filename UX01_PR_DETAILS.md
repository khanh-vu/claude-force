# Pull Request: UX-01 - Quiet Mode for CI/CD Integration

## Title
```
feat(ux): add quiet mode and JSON format for CI/CD integration (UX-01)
```

## Base Branch
```
main
```

## Head Branch
```
claude/ux-01-quiet-mode-01TpR8JRcBoeyVJBWgSzPwrm
```

## Description

```markdown
## Summary

Implements P0 critical task **UX-01: Add Quiet Mode for CI/CD Integration**, enabling claude-force to be used in automated CI/CD pipelines with machine-readable output and proper exit codes.

## Problem Solved

Before this PR:
- ❌ Verbose output with emojis broke CI/CD pipelines
- ❌ Hard to parse results programmatically
- ❌ No JSON output format
- ❌ CI/CD couldn't reliably use exit codes

After this PR:
- ✅ `--quiet` flag suppresses verbose output
- ✅ `--format json` provides machine-readable output
- ✅ Proper exit codes (0=success, 1=failure)
- ✅ Full backward compatibility

## New Features

### 1. Quiet Mode (`--quiet` / `-q`)

Suppresses all verbose output for CI/CD environments:

```bash
# Before: Verbose output with emojis
🚀 Running agent: code-reviewer
✅ Agent completed successfully

# After: No output in quiet mode
claude-force run agent code-reviewer --task "Review" --quiet
```

### 2. JSON Output Format (`--format json`)

Machine-readable JSON output for automation:

```bash
claude-force run agent code-reviewer --task "Review" --format json
```

**Output:**
```json
{
  "success": true,
  "agent": "code-reviewer",
  "output": "Code review results...",
  "errors": [],
  "metadata": {
    "tokens_used": 1500,
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

### 3. Reliable Exit Codes

- **Exit 0**: Success
- **Exit 1**: Failure

Perfect for CI/CD pipeline decisions:

```bash
if claude-force run agent test --task "Run tests" --quiet; then
  echo "Tests passed ✓"
else
  echo "Tests failed ✗"
  exit 1
fi
```

## Supported Commands

| Command | `--quiet` | `--format json` | Exit Codes |
|---------|-----------|-----------------|------------|
| `run agent` | ✅ | ✅ | ✅ |
| `run workflow` | ✅ | ✅ | ✅ |
| `list agents` | ✅ | ✅ | ✅ |
| `list workflows` | ✅ | ✅ | ✅ |

## Implementation Details

### CLI Changes (`claude_force/cli.py`)

**Added argument flags:**
- `--quiet` / `-q`: Minimal output mode
- `--format [text|json]`: Output format selection

**Modified functions:**
- `cmd_run_agent()`: Handle quiet mode and JSON output
- `cmd_run_workflow()`: Handle quiet mode and JSON output
- `cmd_list_agents()`: Handle quiet mode and JSON output
- `cmd_list_workflows()`: Handle quiet mode and JSON output

**Backward compatibility:**
- Existing `--json` flag still works (internally uses `--format json`)
- Default behavior unchanged (text output, verbose)

### Test Coverage (`tests/test_quiet_mode.py`)

**7 passing tests:**

1. `test_list_agents_quiet_mode` - Verifies no output in quiet mode
2. `test_list_workflows_quiet_mode` - Verifies no output in quiet mode
3. `test_list_agents_json_format` - Validates JSON structure
4. `test_list_workflows_json_format` - Validates JSON structure
5. `test_json_flag_still_works` - Backward compatibility check
6. `test_successful_agent_exits_zero` - Exit code 0 on success
7. `test_failed_agent_exits_one` - Exit code 1 on failure

### Documentation (`docs/CI_CD_INTEGRATION.md`)

**Comprehensive CI/CD guide including:**

- Feature overview and usage examples
- JSON output format specifications
- Integration examples for:
  - GitHub Actions
  - GitLab CI
  - CircleCI
  - Jenkins
- Best practices for parsing JSON and error handling
- Troubleshooting guide

## Usage Examples

### GitHub Actions

```yaml
- name: Run Code Review
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    claude-force run agent code-reviewer \
      --task "Review PR changes" \
      --quiet \
      --format json > review.json

    if [ $? -ne 0 ]; then
      echo "Review failed"
      exit 1
    fi
```

### GitLab CI

```yaml
code-review:
  script:
    - |
      claude-force run agent code-reviewer \
        --task "Review MR" \
        --quiet \
        --format json > review.json
  artifacts:
    paths:
      - review.json
```

### Parse JSON with jq

```bash
# Extract specific fields
claude-force list agents --format json | jq '.[].name'

# Check success status
RESULT=$(claude-force run agent test --task "Test" --format json)
SUCCESS=$(echo $RESULT | jq -r '.success')

if [ "$SUCCESS" = "true" ]; then
  echo "Success"
else
  echo "Failed"
  exit 1
fi
```

## JSON Output Formats

### Run Agent

```json
{
  "success": true,
  "agent": "agent-name",
  "output": "execution results",
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
  "workflow": "workflow-name",
  "task": "task description",
  "total_tokens": 5000,
  "results": [
    {
      "agent": "agent1",
      "success": true,
      "output": "...",
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
  }
]
```

## Backward Compatibility

✅ **100% backward compatible**

- Default behavior unchanged (text output, verbose)
- Existing `--json` flag still works
- No breaking changes to public APIs
- Old scripts continue to work without modification

## Testing

```bash
# Run quiet mode tests
python -m unittest tests.test_quiet_mode -v

# Results: 7/7 core tests passing
# - Quiet mode verification: ✅
# - JSON format validation: ✅
# - Exit code behavior: ✅
# - Backward compatibility: ✅
```

## Impact

### Enables CI/CD Integration ✅

Claude-force can now be used in:
- GitHub Actions workflows
- GitLab CI pipelines
- CircleCI jobs
- Jenkins pipelines
- Any automated environment

### Machine-Readable Output ✅

- Parse results programmatically with `jq`, Python, etc.
- Extract specific fields from JSON
- Process results in other tools

### Reliable Automation ✅

- Proper exit codes for pipeline decisions
- No emoji/formatting issues in logs
- Consistent output format

## Addresses

- **Task**: UX-01 from P0 implementation plan
- **Priority**: P0 - Critical
- **Impact**: HIGH - Enables CI/CD integration
- **Effort**: 3-4 hours (completed)

## Related

- Part of comprehensive implementation plan (IMPLEMENTATION_PLAN.md)
- Follows expert UX review recommendations
- Addresses critical gap identified in user experience audit

---

**Ready for review!** All tests passing, comprehensive documentation included, fully backward compatible.
```

## Instructions

**Visit this URL to create the PR:**
```
https://github.com/khanh-vu/claude-force/compare/main...claude/ux-01-quiet-mode-01TpR8JRcBoeyVJBWgSzPwrm
```

**Steps:**
1. Click "Create pull request"
2. Copy title from above
3. Copy full description from above
4. Submit PR

## Files Changed

```
claude_force/cli.py                - Modified (864 lines changed)
docs/CI_CD_INTEGRATION.md         - Added (500+ lines)
tests/test_quiet_mode.py           - Added (300+ lines, 7 tests)
```

## Commit

```
cf5fcbe feat(ux): add quiet mode and JSON format for CI/CD integration (UX-01)
```
