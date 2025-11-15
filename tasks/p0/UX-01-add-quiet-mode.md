# UX-01: Add Quiet Mode for CI/CD

**Priority**: P0 - Critical  
**Estimated Effort**: 3-4 hours  
**Impact**: HIGH - Enables CI/CD integration  
**Category**: User Experience

## Problem

No quiet mode for scripting:
- Verbose output breaks CI/CD pipelines
- Hard to parse results programmatically  
- No JSON output format  
- CI/CD can't use exit codes reliably

## Solution

Add `--quiet` and `--format json` flags to all commands.

## Implementation

```python
@click.command('run')
@click.argument('agent_name')
@click.option('--task', help='Task description')
@click.option('--quiet', is_flag=True, help='Minimal output (CI/CD mode)')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def run_agent(agent_name, task, quiet, format):
    """Run agent with optional quiet mode."""
    result = orchestrator.run_agent(agent_name, task)
    
    if format == 'json':
        import json
        output = {
            'success': result.success,
            'agent': agent_name,
            'output': result.output,
            'errors': result.errors
        }
        click.echo(json.dumps(output))
    elif not quiet:
        if result.success:
            click.echo(f"✓ {result.output}")
        else:
            click.echo(f"✗ Error: {result.errors}", err=True)
    
    # Exit code for CI/CD
    sys.exit(0 if result.success else 1)
```

## CI/CD Usage Example

```bash
# In GitHub Actions
- name: Review Code
  run: |
    claude-force run agent code-reviewer \
      --task "Review PR changes" \
      --quiet \
      --format json > result.json
    
    if [ $? -ne 0 ]; then
      echo "Code review failed"
      exit 1
    fi
```

## Acceptance Criteria

- [ ] `--quiet` flag on all commands  
- [ ] `--format json` option  
- [ ] Proper exit codes (0=success, 1=failure)  
- [ ] CI/CD example in docs  
- [ ] Tests for both modes  
- [ ] No output to stdout in quiet mode (except JSON)

**Status**: Not Started  
**Due Date**: Week 1
