# Installation Guide

Complete installation guide for claude-force.

## Quick Install

### From PyPI (Recommended)

```bash
pip install claude-force
claude-force --version
```

That's it! You're ready to use claude-force.

## Detailed Installation

### Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **pip** package manager
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))

#### Check Python Version

```bash
python3 --version
# Should show: Python 3.8.0 or higher
```

### Installation Methods

#### Method 1: PyPI (Recommended)

Install the latest stable version:

```bash
# Install
pip install claude-force

# Verify installation
claude-force --help

# Upgrade to latest
pip install --upgrade claude-force
```

#### Method 2: From Source (For Development)

Install from GitHub for the latest development version:

```bash
# Clone repository
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

#### Method 3: Install from GitHub

Install directly from GitHub without cloning:

```bash
pip install git+https://github.com/khanh-vu/claude-force.git
```

### Optional Dependencies

#### Semantic Agent Selection

For AI-powered agent recommendation:

```bash
pip install sentence-transformers numpy
```

#### Development Tools

For development and testing:

```bash
pip install pytest pytest-cov black pylint mypy
```

## Configuration

### Set Up API Key

#### Option 1: Environment Variable (Recommended)

**Linux/macOS:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'

# Add to shell profile for persistence
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
# or for zsh:
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"

# For persistence:
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-api-key-here', 'User')
```

#### Option 2: Pass to CLI

```bash
claude-force --api-key your-api-key-here run agent code-reviewer --task "..."
```

#### Option 3: Python API

```python
from claude_force.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(
    anthropic_api_key="your-api-key-here"
)
```

## Verification

### Verify Installation

```bash
# Check version
claude-force --version

# List available commands
claude-force --help

# Test with a simple command
claude-force init ./test-project \
  --description "Test project" \
  --name "test"
```

### Run Tests

```bash
# Run all tests
pytest test_claude_system.py -v

# Run with coverage
pytest test_claude_system.py --cov=claude_force --cov-report=html
```

## Troubleshooting

### Command Not Found

**Problem**: `command not found: claude-force`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Or reinstall
pip install --force-reinstall claude-force
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'claude_force'`

**Solution**:
```bash
# Install package
pip install claude-force

# Or for development
pip install -e .
```

### API Key Errors

**Problem**: `ValueError: Anthropic API key required`

**Solution**:
```bash
# Set environment variable
export ANTHROPIC_API_KEY='your-key'

# Or pass to command
claude-force --api-key your-key ...
```

### Sentence Transformers Not Found

**Problem**: `ImportError: No module named 'sentence_transformers'`

**Solution**:
```bash
# Install optional dependency
pip install sentence-transformers
```

## Platform-Specific Notes

### macOS

```bash
# Install Python via Homebrew
brew install python@3.11

# Install claude-force
pip3 install claude-force
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install claude-force
pip3 install claude-force
```

### Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Check "Add Python to PATH" during installation
3. Open PowerShell and run:
   ```powershell
   pip install claude-force
   ```

## Next Steps

- **Quick Start**: See [Quick Start Guide](quickstart.md)
- **API Reference**: Explore [API Documentation](api-reference/index.md)
- **Examples**: Check out [Examples](examples/index.md)

---

**Need help?** Open an issue on [GitHub](https://github.com/khanh-vu/claude-force/issues).
