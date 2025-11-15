# UX-02: Add Interactive Setup Wizard

**Priority**: P0 - Critical  
**Estimated Effort**: 4-6 hours  
**Impact**: HIGH - Reduces onboarding from 15min to 5min  
**Category**: User Experience

## Problem

Multi-step manual setup (4+ steps):
- Confusing for new users  
- 15-minute time to first success  
- Easy to miss configuration steps  
- No validation of setup

## Solution

Create `claude-force setup --interactive` wizard.

## Implementation

```python
@click.command()
@click.option('--interactive', is_flag=True, help='Interactive wizard')
def setup(interactive):
    """One-command setup wizard."""
    if not interactive:
        click.echo("Run with --interactive for guided setup")
        return
        
    click.echo("🚀 Claude Force Setup Wizard\n")
    
    # Step 1: Check Python version
    click.echo("[1/5] Checking Python version...")
    check_python_version()
    click.echo("✓ Python 3.8+ detected\n")
    
    # Step 2: Install dependencies
    click.echo("[2/5] Installing dependencies...")
    subprocess.run(['pip', 'install', '-e', '.'], check=True)
    click.echo("✓ Dependencies installed\n")
    
    # Step 3: Configure API key
    click.echo("[3/5] Configuring API key...")
    api_key = click.prompt("Enter your Anthropic API key", hide_input=True)
    with open('.env', 'w') as f:
        f.write(f"ANTHROPIC_API_KEY={api_key}\n")
    click.echo("✓ API key saved\n")
    
    # Step 4: Initialize project
    click.echo("[4/5] Initializing project...")
    subprocess.run(['claude-force', 'init', 'test-project'], check=True)
    click.echo("✓ Project initialized\n")
    
    # Step 5: Test with simple agent
    click.echo("[5/5] Running test agent...")
    result = orchestrator.run_agent('document-writer-expert', 
                                    task='Write a hello world message')
    if result.success:
        click.echo("✓ Setup complete!\n")
        click.echo("🎉 You're ready to use Claude Force!")
        click.echo("\nTry: claude-force run agent code-reviewer --task 'Review code'")
    else:
        click.echo("✗ Setup failed. Check your API key.")
```

## Acceptance Criteria

- [ ] Interactive wizard implemented  
- [ ] All 5 setup steps automated  
- [ ] Validation at each step  
- [ ] Clear success/failure messages  
- [ ] Time to first success < 5 minutes  
- [ ] Documentation updated

**Status**: Not Started  
**Due Date**: Week 1-2
