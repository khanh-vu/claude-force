# Contributing to Claude Force

Thank you for your interest in contributing to Claude Force! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Adding New Features](#adding-new-features)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to maintain a respectful, collaborative environment. Please be considerate and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- An Anthropic API key (for testing)
- Basic understanding of multi-agent systems

### First Contribution Ideas

Good first issues to tackle:
- Improving documentation
- Adding unit tests
- Fixing typos or formatting
- Adding examples
- Creating new agent definitions

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/claude-force.git
cd claude-force
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install in Development Mode

```bash
# Install with all optional dependencies
pip install -e ".[semantic,api,dev]"

# Or install minimal dependencies
pip install -e .
```

### 4. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Add your API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

### 5. Verify Installation

```bash
# Run tests to verify everything works
python3 -m pytest tests/ -v

# Try the CLI
claude-force --help
```

## Making Changes

### Branch Naming Convention

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description

# Or for documentation
git checkout -b docs/what-you-are-documenting
```

### Code Style Guidelines

#### Python Code Style

We follow **PEP 8** with these specifics:

```python
# Good: Use type hints
def run_agent(
    self,
    agent_name: str,
    task: str,
    model: Optional[str] = None
) -> AgentResult:
    """
    Run a single agent on a task.

    Args:
        agent_name: Name of the agent to run
        task: Task description
        model: Optional model override

    Returns:
        AgentResult with success status and output

    Raises:
        ValueError: If agent_name is invalid
    """
    pass

# Good: Use descriptive variable names
agent_result = self.execute_agent(task_description)

# Bad: Unclear abbreviations
ar = self.exec(td)

# Good: Constants in UPPER_CASE
MAX_TOKEN_LIMIT = 100000
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

# Good: Classes in PascalCase
class AgentOrchestrator:
    pass

# Good: Functions/methods in snake_case
def calculate_token_estimate(text: str) -> int:
    pass
```

#### Documentation Style

```python
# Use Google-style docstrings
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    More detailed explanation if needed. Can span
    multiple lines.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When this error occurs
        RuntimeError: When this error occurs

    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

#### Markdown Style

- Use ATX-style headers (`#` not underlines)
- One blank line before and after headers
- Use fenced code blocks with language specified
- Keep line length under 100 characters for readability
- Use relative links for internal documentation

### Commit Message Guidelines

Follow the **Conventional Commits** specification:

```bash
# Format
<type>(<scope>): <subject>

<body>

<footer>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Code style changes (formatting, no logic change)
refactor: Code refactoring (no feature change)
perf:     Performance improvements
test:     Adding or updating tests
chore:    Maintenance tasks

# Examples
feat(agents): add kubernetes-expert agent for cluster management

fix(cache): resolve HMAC verification failure on cache hits

docs(readme): add table of contents and restructure sections

test(orchestrator): add integration tests for async execution

refactor(cli): extract command handlers into separate modules
Reduces cli.py from 1989 lines to manageable size.
Improves maintainability and testability.

Closes #123
```

## Testing

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_orchestrator.py -v

# Run specific test class
python3 -m pytest tests/test_orchestrator.py::TestAgentOrchestrator -v

# Run specific test
python3 -m pytest tests/test_orchestrator.py::TestAgentOrchestrator::test_run_agent -v

# Run with coverage
python3 -m pytest tests/ --cov=claude_force --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Writing Tests

#### Test File Structure

```python
"""
Test module for <component>.

This module tests <what it tests>.
"""

import pytest
from claude_force import YourClass


class TestYourClass:
    """Tests for YourClass."""

    @pytest.fixture
    def setup_instance(self):
        """Create a test instance."""
        return YourClass()

    def test_basic_functionality(self, setup_instance):
        """Test basic functionality works as expected."""
        result = setup_instance.method()
        assert result == expected_value

    def test_error_handling(self, setup_instance):
        """Test error handling for invalid input."""
        with pytest.raises(ValueError):
            setup_instance.method(invalid_input)
```

#### Test Coverage Requirements

- **New features**: Must include tests (minimum 80% coverage)
- **Bug fixes**: Must include regression test
- **Refactoring**: Existing tests must pass
- **Critical paths**: Aim for 100% coverage

### Manual Testing

Before submitting:

```bash
# Test CLI commands
claude-force list agents
claude-force run agent code-reviewer --task "Review authentication code"
claude-force metrics summary

# Test Python API
python3 examples/python/01_simple_agent.py

# Test with different models
claude-force run agent document-writer-expert --task "..." --model haiku

# Test error handling
claude-force run agent nonexistent-agent --task "test"
```

## Submitting Changes

### Pull Request Process

1. **Ensure all tests pass**
   ```bash
   python3 -m pytest tests/ -v
   ```

2. **Update documentation**
   - Add/update docstrings
   - Update README.md if needed
   - Update CHANGELOG.md (if exists)

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(component): add new feature"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Add screenshots/examples if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for new functionality
- [ ] Updated existing tests if needed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-reviewed my own code
- [ ] Commented complex/hard-to-understand code
- [ ] Updated documentation
- [ ] Changes generate no new warnings
- [ ] Added tests with good coverage
- [ ] All tests pass

## Related Issues
Closes #issue_number
```

## Adding New Features

### Adding a New Agent

1. **Create agent definition**
   ```bash
   # Create agent file
   touch .claude/agents/my-new-agent.md
   ```

2. **Define agent capabilities**
   ```markdown
   # My New Agent

   ## Purpose
   Brief description of what this agent does.

   ## Skills
   - Skill 1
   - Skill 2

   ## When to Use
   - Use case 1
   - Use case 2

   ## When NOT to Use
   - Scenario 1
   - Scenario 2

   ## Output Format
   <detailed output format>
   ```

3. **Create contract**
   ```bash
   touch .claude/contracts/my-new-agent.contract
   ```

4. **Register in claude.json**
   ```json
   {
     "agents": {
       "my-new-agent": {
         "file": "agents/my-new-agent.md",
         "contract": "contracts/my-new-agent.contract",
         "domains": ["domain1", "domain2"],
         "priority": 2
       }
     }
   }
   ```

5. **Add tests**
   ```python
   def test_my_new_agent():
       """Test the new agent works correctly."""
       orchestrator = AgentOrchestrator()
       result = orchestrator.run_agent("my-new-agent", task="test task")
       assert result.success
   ```

6. **Update documentation**
   - Add to README.md agent list
   - Update AGENT_SKILLS_MATRIX.md
   - Add example usage

### Adding a New Python Module

1. **Create module file**
   ```bash
   touch claude_force/my_module.py
   ```

2. **Add docstring and implementation**
   ```python
   """
   My Module - Brief description.

   This module provides functionality for...
   """

   from typing import Optional, List
   import logging

   logger = logging.getLogger(__name__)


   class MyClass:
       """Brief description of MyClass."""

       def __init__(self, param: str):
           """Initialize MyClass."""
           self.param = param
   ```

3. **Export from __init__.py**
   ```python
   # In claude_force/__init__.py
   from .my_module import MyClass

   __all__ = ["MyClass", ...]
   ```

4. **Add comprehensive tests**
   ```python
   # In tests/test_my_module.py
   import pytest
   from claude_force.my_module import MyClass


   class TestMyClass:
       def test_initialization(self):
           instance = MyClass("test")
           assert instance.param == "test"
   ```

### Adding CLI Commands

1. **Add command handler** in `claude_force/cli.py`:
   ```python
   @cli.command()
   @click.argument('name')
   @click.option('--flag', help='Description')
   def my_command(name: str, flag: bool):
       """Brief description of command."""
       # Implementation
       click.echo(f"Running {name}...")
   ```

2. **Test manually**
   ```bash
   claude-force my-command test-name --flag
   ```

3. **Add integration test**

## Documentation

### Documentation Locations

- **README.md**: Project overview, quick start, features
- **IMPLEMENTATION.md**: Implementation details
- **ARCHITECTURE.md**: System architecture and design
- **API docs**: Docstrings in code
- **.claude/**: Agent definitions and contracts

### Building Documentation

```bash
# View README locally
mdcat README.md

# Generate API documentation (if sphinx is set up)
cd docs
make html
```

### Documentation Checklist

When adding features:
- [ ] Add docstrings to all public functions/classes
- [ ] Update README.md if user-facing
- [ ] Add usage examples
- [ ] Update CHANGELOG.md
- [ ] Add to appropriate guide document

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Git commit history

### Thank You!

Every contribution helps make Claude Force better. Thank you for being part of this project!

---

**Questions?** Open an issue or start a discussion on GitHub.

**Want to contribute but not sure where to start?** Look for issues labeled `good-first-issue` or `help-wanted`.
