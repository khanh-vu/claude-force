# Troubleshooting Guide

This guide covers common issues and solutions for Claude Force. Issues are organized by category for easy navigation.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [API Key & Authentication](#api-key--authentication)
- [Agent Execution Issues](#agent-execution-issues)
- [Performance Issues](#performance-issues)
- [Cache Issues](#cache-issues)
- [Network & Connectivity](#network--connectivity)
- [Testing Issues](#testing-issues)
- [Configuration Issues](#configuration-issues)
- [Marketplace Issues](#marketplace-issues)
- [Advanced Troubleshooting](#advanced-troubleshooting)

## Quick Diagnostics

Before diving into specific issues, run the diagnostic tool:

```bash
# Run system diagnostics
claude-force diagnose

# Expected output:
# ✅ Python version: 3.10.0
# ✅ Claude Force version: 2.2.0
# ✅ API key configured: Yes (sk-ant-...1234)
# ✅ Cache status: Enabled (1.2 MB, 15 entries)
# ✅ Config file: Found (.claude/claude.json)
# ✅ Agents available: 19
# ✅ Skills available: 11
# ❌ Network connectivity: Failed
```

The diagnose command identifies common issues automatically.

## Installation Issues

### Issue: `pip install claude-force` fails

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement claude-force
```

**Solutions**:

1. **Check Python version**:
   ```bash
   python --version  # Must be 3.8+

   # If too old, upgrade or use python3
   python3 --version
   ```

2. **Upgrade pip**:
   ```bash
   pip install --upgrade pip
   ```

3. **Install from GitHub** (if PyPI is unavailable):
   ```bash
   pip install git+https://github.com/khanh-vu/claude-force.git
   ```

4. **Install from source**:
   ```bash
   git clone https://github.com/khanh-vu/claude-force.git
   cd claude-force
   pip install -e .
   ```

### Issue: `claude-force` command not found

**Symptoms**:
```bash
claude-force --help
# bash: claude-force: command not found
```

**Solutions**:

1. **Check if installed**:
   ```bash
   pip list | grep claude-force
   ```

2. **Reinstall with entry points**:
   ```bash
   pip install --force-reinstall claude-force
   ```

3. **Check PATH** (if installed in user directory):
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.local/bin:$PATH"
   source ~/.bashrc
   ```

4. **Use python -m syntax**:
   ```bash
   python -m claude_force.cli --help
   ```

### Issue: Import errors for optional dependencies

**Symptoms**:
```python
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solutions**:

1. **Install semantic dependencies**:
   ```bash
   pip install -e ".[semantic]"
   ```

2. **Install API dependencies**:
   ```bash
   pip install -e ".[api]"
   ```

3. **Install all dependencies**:
   ```bash
   pip install -e ".[all]"
   ```

4. **Install individual packages**:
   ```bash
   pip install sentence-transformers  # For semantic selection
   pip install fastapi uvicorn        # For API server
   pip install pytest pytest-cov      # For development
   ```

## API Key & Authentication

### Issue: "ANTHROPIC_API_KEY not found"

**Symptoms**:
```
Error: ANTHROPIC_API_KEY environment variable not set
```

**Solutions**:

1. **Set environment variable**:
   ```bash
   # Linux/macOS
   export ANTHROPIC_API_KEY='sk-ant-your-key-here'

   # Windows (PowerShell)
   $env:ANTHROPIC_API_KEY='sk-ant-your-key-here'

   # Windows (CMD)
   set ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

2. **Add to .env file**:
   ```bash
   echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
   ```

3. **Add to shell profile** (persistent):
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Pass directly in code**:
   ```python
   from claude_force import AgentOrchestrator

   orchestrator = AgentOrchestrator(api_key='sk-ant-your-key-here')
   ```

### Issue: "Invalid API key"

**Symptoms**:
```
AuthenticationError: Invalid API key provided
```

**Solutions**:

1. **Verify key format**:
   ```bash
   # Should start with 'sk-ant-'
   echo $ANTHROPIC_API_KEY
   ```

2. **Check for whitespace**:
   ```bash
   # Remove trailing whitespace
   export ANTHROPIC_API_KEY=$(echo $ANTHROPIC_API_KEY | tr -d '[:space:]')
   ```

3. **Generate new key**:
   - Visit https://console.anthropic.com/
   - Navigate to API Keys
   - Create new key

4. **Check account status**:
   - Verify account is active
   - Check billing status
   - Ensure API access is enabled

### Issue: "Rate limit exceeded"

**Symptoms**:
```
RateLimitError: Rate limit exceeded (429)
```

**Solutions**:

1. **Enable rate limiting**:
   ```python
   from claude_force import AsyncOrchestrator

   orchestrator = AsyncOrchestrator(
       max_concurrent_requests=2  # Reduce from default 3
   )
   ```

2. **Add retry logic**:
   ```python
   import time

   max_retries = 3
   for attempt in range(max_retries):
       try:
           result = orchestrator.run_agent("code-reviewer", task="...")
           break
       except RateLimitError:
           if attempt < max_retries - 1:
               time.sleep(2 ** attempt)  # Exponential backoff
           else:
               raise
   ```

3. **Use caching** (avoids API calls for repeated tasks):
   ```python
   orchestrator = AgentOrchestrator(enable_cache=True)
   ```

4. **Upgrade API tier** (contact Anthropic for higher limits)

## Agent Execution Issues

### Issue: "Agent not found"

**Symptoms**:
```
Error: Agent 'security-expert' not found
```

**Solutions**:

1. **List available agents**:
   ```bash
   claude-force list agents
   ```

2. **Check agent name spelling**:
   ```bash
   # Correct
   claude-force run agent security-specialist --task "..."

   # Incorrect (common typo)
   claude-force run agent security-expert --task "..."
   ```

3. **Use agent recommendation**:
   ```bash
   claude-force recommend --task "Your task description"
   # Shows best agents with correct names
   ```

4. **Verify claude.json**:
   ```bash
   cat .claude/claude.json | jq '.agents | keys'
   ```

### Issue: Agent returns empty or invalid output

**Symptoms**:
```
Agent completed successfully but output is empty
```

**Solutions**:

1. **Enable verbose mode**:
   ```bash
   claude-force run agent code-reviewer --task "..." --verbose
   ```

2. **Check task description**:
   ```bash
   # Too vague
   claude-force run agent code-reviewer --task "review"

   # Better (specific)
   claude-force run agent code-reviewer \
     --task "Review src/auth.py for security vulnerabilities"
   ```

3. **Increase token limit**:
   ```python
   orchestrator = AgentOrchestrator(max_tokens=100000)
   ```

4. **Check agent definition**:
   ```bash
   cat .claude/agents/code-reviewer.md
   # Verify output format section is correct
   ```

### Issue: "Task file not found"

**Symptoms**:
```
Error: Task file 'task.md' not found
```

**Solutions**:

1. **Check file path**:
   ```bash
   # Verify file exists
   ls -la .claude/task.md

   # Use absolute path
   claude-force run agent code-reviewer \
     --task-file /absolute/path/to/task.md
   ```

2. **Check permissions**:
   ```bash
   chmod 644 .claude/task.md
   ```

3. **Use stdin instead**:
   ```bash
   echo "Review this code" | claude-force run agent code-reviewer --task -
   ```

### Issue: Workflow fails midway

**Symptoms**:
```
Workflow 'full-stack-feature' failed at agent 3 of 10
```

**Solutions**:

1. **Check individual agent**:
   ```bash
   # Run the failing agent independently
   claude-force run agent database-architect --task "..." --verbose
   ```

2. **Enable checkpoint recovery**:
   ```python
   orchestrator = AgentOrchestrator(enable_checkpoints=True)
   result = orchestrator.run_workflow("full-stack-feature", task="...")
   # Automatically resumes from last successful agent
   ```

3. **Review agent dependencies**:
   ```bash
   # Check workflow definition
   cat .claude/claude.json | jq '.workflows["full-stack-feature"]'
   ```

4. **Run in debug mode**:
   ```bash
   export CLAUDE_DEBUG=1
   claude-force run workflow full-stack-feature --task "..."
   ```

## Performance Issues

### Issue: Slow response times

**Symptoms**:
```
Agent execution taking 30+ seconds
```

**Diagnosis**:
```bash
# Enable performance tracking
claude-force run agent code-reviewer --task "..." --track-performance

# View metrics
claude-force metrics summary
```

**Solutions**:

1. **Enable response caching**:
   ```python
   orchestrator = AgentOrchestrator(enable_cache=True)
   # 60-80% faster for repeated tasks
   ```

2. **Use progressive skills loading**:
   ```python
   from claude_force import ProgressiveSkillsManager

   manager = ProgressiveSkillsManager()
   # Automatically reduces tokens by 30-50%
   ```

3. **Use faster model for simple tasks**:
   ```bash
   claude-force run agent document-writer-expert \
     --task "..." \
     --model haiku  # 3-5x faster
   ```

4. **Reduce task complexity**:
   ```bash
   # Instead of
   --task "Review entire codebase for all issues"

   # Try
   --task "Review src/auth.py for SQL injection"
   ```

5. **Check network latency**:
   ```bash
   ping api.anthropic.com
   # High latency? Consider using async orchestration
   ```

### Issue: High memory usage

**Symptoms**:
```
Memory usage: 2+ GB
```

**Diagnosis**:
```bash
# Check memory usage
ps aux | grep claude-force
```

**Solutions**:

1. **Disable semantic selector** (saves 90-420MB):
   ```python
   orchestrator = AgentOrchestrator(enable_semantic=False)
   ```

2. **Unload semantic model after use**:
   ```python
   orchestrator.semantic_selector.unload_model()
   ```

3. **Limit cache size**:
   ```python
   from claude_force import ResponseCache

   cache = ResponseCache(max_entries=100)  # Default: unlimited
   ```

4. **Use async with limits**:
   ```python
   orchestrator = AsyncOrchestrator(max_concurrent_requests=2)
   # Reduces memory from parallel executions
   ```

### Issue: Cache taking too much disk space

**Symptoms**:
```bash
du -sh .claude/cache
# 5.0G .claude/cache
```

**Solutions**:

1. **Set cache size limit**:
   ```python
   cache = ResponseCache(max_size_mb=100)  # Limit to 100MB
   ```

2. **Clear old entries**:
   ```bash
   # Clear entries older than 30 days
   claude-force cache clean --older-than 30d

   # Clear all cache
   rm -rf .claude/cache/*.db
   ```

3. **Adjust TTL** (time-to-live):
   ```python
   cache = ResponseCache(ttl_days=30)  # Default: 90
   ```

## Cache Issues

### Issue: Cache not working

**Symptoms**:
```
Cache hits: 0% (expected >50%)
```

**Diagnosis**:
```bash
# Check cache status
claude-force cache status

# Expected output:
# Cache enabled: Yes
# Total entries: 42
# Hit rate: 65%
# Size: 2.3 MB
```

**Solutions**:

1. **Verify cache is enabled**:
   ```python
   orchestrator = AgentOrchestrator(enable_cache=True)
   ```

2. **Check cache secret**:
   ```bash
   # Should not use default in production
   export CLAUDE_CACHE_SECRET="your-unique-secret-here"
   ```

3. **Verify cache directory exists**:
   ```bash
   mkdir -p .claude/cache
   chmod 755 .claude/cache
   ```

4. **Check cache integrity**:
   ```bash
   # Verify cache database
   sqlite3 .claude/cache/response_cache.db "SELECT COUNT(*) FROM cache;"
   ```

### Issue: "Cache integrity verification failed"

**Symptoms**:
```
Warning: Cache entry failed HMAC verification
```

**Causes**:
- Cache secret changed
- Database file corrupted
- Manual database modification

**Solutions**:

1. **Clear corrupted cache**:
   ```bash
   rm -rf .claude/cache/*.db
   claude-force cache rebuild
   ```

2. **Use consistent cache secret**:
   ```bash
   # Add to .env (don't commit!)
   echo "CLAUDE_CACHE_SECRET=your-secret-here" >> .env
   ```

3. **Disable integrity verification** (not recommended for production):
   ```python
   cache = ResponseCache(verify_integrity=False)
   ```

## Network & Connectivity

### Issue: "Connection timeout"

**Symptoms**:
```
ConnectionError: Timeout connecting to api.anthropic.com
```

**Solutions**:

1. **Check internet connection**:
   ```bash
   ping api.anthropic.com
   curl -I https://api.anthropic.com
   ```

2. **Check firewall/proxy**:
   ```bash
   # Set proxy if needed
   export HTTPS_PROXY=http://proxy.example.com:8080
   export HTTP_PROXY=http://proxy.example.com:8080
   ```

3. **Increase timeout**:
   ```python
   orchestrator = AgentOrchestrator(timeout=60)  # Default: 30
   ```

4. **Retry with backoff**:
   ```python
   import time

   for attempt in range(3):
       try:
           result = orchestrator.run_agent("code-reviewer", task="...")
           break
       except ConnectionError:
           time.sleep(2 ** attempt)
   ```

### Issue: SSL/TLS errors

**Symptoms**:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions**:

1. **Update certifi**:
   ```bash
   pip install --upgrade certifi
   ```

2. **Update pip and setuptools**:
   ```bash
   pip install --upgrade pip setuptools
   ```

3. **Install system certificates** (macOS):
   ```bash
   /Applications/Python\ 3.10/Install\ Certificates.command
   ```

4. **Temporary workaround** (not recommended):
   ```python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

## Testing Issues

### Issue: Tests failing

**Symptoms**:
```
FAILED tests/test_orchestrator.py::test_run_agent - AssertionError
```

**Solutions**:

1. **Run tests verbosely**:
   ```bash
   python -m pytest tests/ -v --tb=short
   ```

2. **Run specific test**:
   ```bash
   python -m pytest tests/test_orchestrator.py::test_run_agent -v
   ```

3. **Check test dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Clear test cache**:
   ```bash
   python -m pytest --cache-clear
   ```

5. **Check for environment issues**:
   ```bash
   # Tests may need API key
   export ANTHROPIC_API_KEY='your-test-key'

   # Or use mock mode
   export CLAUDE_TEST_MODE=mock
   python -m pytest tests/
   ```

### Issue: Coverage too low

**Symptoms**:
```
Coverage: 75% (target: 80%)
```

**Solutions**:

1. **Generate coverage report**:
   ```bash
   python -m pytest tests/ --cov=claude_force --cov-report=html
   open htmlcov/index.html
   ```

2. **Find uncovered lines**:
   ```bash
   python -m pytest tests/ --cov=claude_force --cov-report=term-missing
   ```

3. **Add missing tests** for uncovered code

## Configuration Issues

### Issue: "Config file not found"

**Symptoms**:
```
Error: Configuration file .claude/claude.json not found
```

**Solutions**:

1. **Initialize project**:
   ```bash
   claude-force init my-project
   cd my-project
   ```

2. **Create minimal config**:
   ```bash
   mkdir -p .claude
   cat > .claude/claude.json <<EOF
   {
     "agents": {},
     "workflows": {}
   }
   EOF
   ```

3. **Use custom config path**:
   ```bash
   claude-force --config /path/to/claude.json run agent code-reviewer --task "..."
   ```

4. **Check directory structure**:
   ```bash
   ls -la .claude/
   # Should contain claude.json
   ```

### Issue: "Invalid JSON in config"

**Symptoms**:
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**Solutions**:

1. **Validate JSON**:
   ```bash
   python -m json.tool .claude/claude.json
   ```

2. **Common JSON errors**:
   ```json
   // Bad: Trailing comma
   {
     "agents": {
       "code-reviewer": {...},
     }
   }

   // Good: No trailing comma
   {
     "agents": {
       "code-reviewer": {...}
     }
   }
   ```

3. **Use JSON linter**:
   ```bash
   jq . .claude/claude.json
   ```

4. **Restore from backup**:
   ```bash
   cp .claude/claude.json.backup .claude/claude.json
   ```

## Marketplace Issues

### Issue: "Plugin not found in marketplace"

**Symptoms**:
```
Error: Plugin 'nonexistent-plugin' not found
```

**Solutions**:

1. **Search marketplace**:
   ```bash
   claude-force marketplace search kubernetes
   ```

2. **List all plugins**:
   ```bash
   claude-force marketplace list
   ```

3. **Check plugin name spelling**

4. **Refresh marketplace index**:
   ```bash
   claude-force marketplace refresh
   ```

### Issue: "Plugin installation failed"

**Symptoms**:
```
Error installing plugin: Permission denied
```

**Solutions**:

1. **Check permissions**:
   ```bash
   chmod -R 755 .claude/plugins/
   ```

2. **Install to user directory**:
   ```bash
   claude-force marketplace install plugin-name --user
   ```

3. **Manual installation**:
   ```bash
   # Download plugin
   wget https://example.com/plugin.zip

   # Extract to plugins directory
   unzip plugin.zip -d .claude/plugins/
   ```

## Advanced Troubleshooting

### Enable Debug Mode

```bash
# Set debug environment variable
export CLAUDE_DEBUG=1

# Run with debug logging
claude-force --debug run agent code-reviewer --task "..."

# Python API
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check System Information

```bash
# Python environment
python --version
pip list | grep claude

# System info
uname -a
echo $PATH

# Claude Force version
claude-force --version

# Configuration
claude-force config show
```

### Enable Detailed Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claude-force.log'),
        logging.StreamHandler()
    ]
)

# Run with logging
from claude_force import AgentOrchestrator
orchestrator = AgentOrchestrator()
result = orchestrator.run_agent("code-reviewer", task="...")
```

### Profile Performance

```python
import cProfile
import pstats
from claude_force import AgentOrchestrator

# Profile execution
orchestrator = AgentOrchestrator()

cProfile.run(
    'orchestrator.run_agent("code-reviewer", task="Review code")',
    'profile_output.prof'
)

# Analyze results
stats = pstats.Stats('profile_output.prof')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Generate Debug Report

```bash
# Generate comprehensive debug report
claude-force debug-report > debug_report.txt

# Expected content:
# - System information
# - Configuration
# - Recent logs
# - Cache status
# - Performance metrics
# - Installed dependencies
```

### Common Debug Commands

```bash
# Test API connectivity
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages

# Verify installation
python -c "import claude_force; print(claude_force.__version__)"

# Check dependencies
pip check

# List installed agents
python -c "from claude_force import AgentOrchestrator; \
  o = AgentOrchestrator(); \
  print(list(o.config['agents'].keys()))"
```

## Still Having Issues?

If none of these solutions work:

1. **Search existing issues**:
   https://github.com/khanh-vu/claude-force/issues

2. **Create new issue** with:
   - Output from `claude-force diagnose`
   - Full error message and stack trace
   - Steps to reproduce
   - Expected vs actual behavior
   - System information

3. **Include debug information**:
   ```bash
   claude-force debug-report > debug.txt
   # Attach debug.txt to issue
   ```

4. **Check documentation**:
   - [README.md](README.md)
   - [FAQ.md](FAQ.md)
   - [INSTALLATION.md](INSTALLATION.md)
   - [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Need immediate help?** Open an issue on GitHub with the `help-wanted` label.
