# Demo Mode

## Overview

Demo mode allows you to explore claude-force **without an API key**. It provides realistic simulated responses that demonstrate the system's capabilities without making actual API calls or incurring costs.

## Features

- ✅ **No API Key Required** - Try claude-force immediately
- ✅ **Realistic Responses** - Agent-specific mock outputs
- ✅ **Full CLI Support** - All commands work in demo mode
- ✅ **Zero Cost** - No API charges
- ✅ **Instant Feedback** - Fast simulated responses

## Usage

Simply add the `--demo` flag to any claude-force command:

```bash
# List agents (demo mode)
claude-force --demo list agents

# Run a single agent (demo mode)
claude-force --demo run agent code-reviewer --task "Review this code: def foo(): pass"

# Run a workflow (demo mode)
claude-force --demo run workflow full-review --task "Review and test this feature"

# Get agent information (demo mode)
claude-force --demo info code-reviewer
```

## Example Output

### Code Review Agent

```bash
$ claude-force --demo run agent code-reviewer --task "Review authentication logic"

🎭 DEMO MODE - Simulated responses, no API calls

🚀 Running agent: code-reviewer

✅ Agent completed successfully

# Code Review Results

## Overview
I've analyzed the code and found several areas for improvement.

## Issues Found

### 1. Error Handling
**Severity:** Medium
**Location:** Lines 15-23

The current error handling could be more robust. Consider:
- Adding specific exception types instead of bare `except`
- Logging errors for debugging
- Providing user-friendly error messages

...
```

### Test Writer Agent

```bash
$ claude-force --demo run agent test-writer --task "Write tests for user service"

🎭 DEMO MODE - Simulated responses, no API calls

🚀 Running agent: test-writer

✅ Agent completed successfully

# Test Suite Generated

## Test File: test_module.py

```python
import unittest
from unittest.mock import patch, Mock
from module import function_to_test

class TestModule(unittest.TestCase):
    """Test suite for module functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = {"key": "value"}

    def test_basic_functionality(self):
        """Test basic function behavior."""
        result = function_to_test(self.test_data)
        self.assertEqual(result, expected_value)
...
```

## When to Use Demo Mode

Demo mode is perfect for:

1. **Trying Before Buying** - Explore claude-force before getting an API key
2. **Demonstrations** - Show the system to others without API costs
3. **Testing CLI** - Verify command syntax and options
4. **Learning** - Understand agent types and their outputs
5. **Development** - Test integration without API calls

## Limitations

Demo mode has some limitations:

- ❌ Responses are generic templates, not actual AI analysis
- ❌ Cannot process real code or provide actual insights
- ❌ No performance tracking or cost metrics
- ❌ Semantic agent selection is not available
- ❌ Hybrid orchestration features are disabled

## Transitioning to Production

When you're ready to use real AI analysis:

1. **Get an API Key**
   ```bash
   # Visit: https://console.anthropic.com/account/keys
   # Create a new API key
   ```

2. **Set Environment Variable**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

3. **Remove --demo Flag**
   ```bash
   # Production use (with API key)
   claude-force run agent code-reviewer --task "Review this code"
   ```

## Demo Mode Implementation

Demo mode uses the `DemoOrchestrator` class which:

- Simulates processing time (0.5-1.5 seconds)
- Generates agent-specific responses based on domains
- Includes realistic metadata (tokens, duration)
- Follows the same interface as `AgentOrchestrator`

### Agent-Specific Responses

Each agent type generates appropriate responses:

- **Code Reviewers** → Code review reports with issues and recommendations
- **Test Writers** → Complete test suites with unittest examples
- **Documentation Writers** → API documentation with examples
- **Security Auditors** → Security analysis reports with findings
- **API Designers** → API endpoint specifications

## Code Example

You can also use demo mode programmatically:

```python
from claude_force.demo_mode import DemoOrchestrator

# Create demo orchestrator (no API key needed)
demo = DemoOrchestrator(config_path=".claude/claude.json")

# Run agent in demo mode
result = demo.run_agent(
    agent_name="code-reviewer",
    task="Review this authentication function"
)

print(result.output)
print(f"Demo mode: {result.metadata['demo_mode']}")
```

## FAQ

### Q: Do I need an API key for demo mode?
**A:** No! Demo mode works without any API key.

### Q: Are the responses real AI analysis?
**A:** No, demo mode returns simulated template responses. For real AI analysis, use production mode with an API key.

### Q: Can I use demo mode for testing?
**A:** Yes! Demo mode is perfect for:
- Testing CLI commands
- Verifying workflow configurations
- Learning agent types
- Demonstrating the system

### Q: Does demo mode work with all commands?
**A:** Yes, most commands work in demo mode:
- ✅ `list agents` / `list workflows`
- ✅ `run agent` / `run workflow`
- ✅ `info <agent>`
- ❌ `metrics` (requires real execution data)
- ❌ `recommend --explain` (requires semantic analysis)

### Q: How do I switch from demo to production?
**A:** Just remove the `--demo` flag and ensure `ANTHROPIC_API_KEY` is set:
```bash
# Demo
claude-force --demo run agent code-reviewer --task "..."

# Production
claude-force run agent code-reviewer --task "..."
```

## See Also

- [Installation Guide](installation.md)
- [Quick Start](../README.md#quick-start)
- [API Reference](api-reference/index.md)
