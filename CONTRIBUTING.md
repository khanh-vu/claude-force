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

## Release Process

### Overview

The project uses automated release workflows with semantic versioning. Releases are triggered by git tags and managed through GitHub Actions.

### Versioning Strategy

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, major architectural changes
- **MINOR** (0.X.0): New features, backward-compatible improvements
- **PATCH** (0.0.X): Bug fixes, documentation updates

**Pre-release versions**:
- `X.Y.Z-alpha.N` - Early development, unstable
- `X.Y.Z-beta.N` - Feature complete, testing phase
- `X.Y.Z-rc.N` - Release candidate, production-ready testing

### Commit Message Format (Important!)

We use **Conventional Commits** for automated changelog generation and version bumping:

```bash
# Format: <type>(<scope>): <subject>

# Types that trigger version bumps:
feat:     New feature (→ MINOR version bump)
fix:      Bug fix (→ PATCH version bump)
BREAKING CHANGE: Breaking change (→ MAJOR version bump)

# Other types (no version bump):
docs:     Documentation changes
style:    Code style (formatting, no logic change)
refactor: Code refactoring
perf:     Performance improvements
test:     Adding/updating tests
chore:    Maintenance tasks
ci:       CI/CD changes
build:    Build system changes

# Examples:
feat(agents): add kubernetes-engineer agent
fix(orchestrator): resolve race condition in workflow execution
docs(readme): update installation instructions
BREAKING CHANGE: remove deprecated HybridOrchestrator.run() method
```

### Pre-release Checklist

Before creating a release, maintainers run:

```bash
# Run automated pre-release checks
python3 scripts/pre_release_checklist.py

# This checks:
# ✓ Version consistency across all files
# ✓ All tests pass
# ✓ No security vulnerabilities
# ✓ Code is properly formatted
# ✓ Package builds successfully
```

### Release Process (For Maintainers)

#### Standard Release

```bash
# 1. Ensure main branch is clean
git checkout main
git pull origin main

# 2. Run pre-release checklist
python3 scripts/pre_release_checklist.py

# 3. Bump version (creates commit and tag automatically)
pip install bump2version
bump2version patch  # or: minor, major

# 4. Push to trigger release workflow
git push origin main --tags

# 5. GitHub Actions automatically:
#    - Runs all tests
#    - Builds package
#    - Publishes to PyPI
#    - Generates changelog
#    - Creates GitHub Release
```

#### Release Candidate

For testing new features before official release:

```bash
# 1. Go to GitHub Actions
# 2. Select "Release Candidate" workflow
# 3. Click "Run workflow"
# 4. Enter:
#    - version_type: rc, beta, or alpha
#    - base_version: e.g., 1.0.0

# This will:
# - Create version tag (e.g., v1.0.0-rc.1)
# - Publish to TestPyPI
# - Create pre-release on GitHub

# 5. Test the RC:
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  claude-force==1.0.0-rc.1

# 6. If tests pass, promote to release:
git tag v1.0.0
git push origin v1.0.0
```

#### Hotfix Release

For urgent bug fixes:

```bash
# 1. Create hotfix branch from tag
git checkout -b hotfix/v1.0.1 v1.0.0

# 2. Fix the bug
git commit -m "fix: critical security vulnerability in agent loader"

# 3. Bump patch version
bump2version patch

# 4. Merge to main and push tags
git checkout main
git merge hotfix/v1.0.1
git push origin main --tags
```

### Version Consistency

All version numbers must be consistent across:
- `pyproject.toml`
- `setup.py`
- `claude_force/__init__.py`
- `README.md`

Run this to check:
```bash
python3 scripts/check_version_consistency.py
```

The `bump2version` tool updates all these files automatically.

### Changelog

Changelogs are generated automatically from commit messages using `git-cliff`:

```bash
# Generate changelog for latest release
git-cliff --latest --output CHANGELOG.md

# Preview changelog without writing
git-cliff --latest --strip header
```

**Important**: Use conventional commit messages so changes are properly categorized in the changelog!

### Release Checklist (For Maintainers)

Before creating a release:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Version is consistent across all files
- [ ] CHANGELOG.md is updated (auto-generated)
- [ ] Documentation is current
- [ ] No security vulnerabilities (`bandit -r claude_force/`)
- [ ] Code is formatted (`black --check claude_force/`)
- [ ] Package builds successfully (`python -m build`)
- [ ] All PRs are merged
- [ ] Release notes are prepared

### Post-release

After a release is published:

1. **Verify PyPI**: Check https://pypi.org/project/claude-force/
2. **Test installation**: `pip install claude-force==X.Y.Z`
3. **Update documentation**: If using GitHub Pages or external docs
4. **Announce**: Create announcement issue, notify community
5. **Monitor**: Watch for installation issues or bug reports

### Troubleshooting Releases

**Release failed?**

```bash
# Check GitHub Actions logs
# Fix the issue
# Delete the tag locally and remotely:
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# Re-run the release process
```

**Version conflict on PyPI?**

```bash
# PyPI doesn't allow re-uploading same version
# Bump to next patch version:
bump2version patch
git push origin main --tags
```

**Need to rollback?**

```bash
# Use the emergency rollback workflow
# Go to GitHub Actions → Emergency Rollback
# Enter the version to rollback to
```

For more details, see [RELEASE_AUTOMATION_PLAN.md](RELEASE_AUTOMATION_PLAN.md).

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
