# Installation Guide - Claude-Force

Complete step-by-step guide to install and set up the Claude Multi-Agent System.

## 📋 Prerequisites

- **Python 3.8 or higher** (3.10+ recommended)
- **Anthropic API Key** - Get one from [console.anthropic.com](https://console.anthropic.com/)
- **Git** (for cloning the repository)

### Check Your Python Version

```bash
python3 --version
# Should show: Python 3.8.0 or higher
```

---

## 🚀 Installation Methods

### Method 1: Install from PyPI (Recommended)

**Easiest and fastest way to get started:**

```bash
# Install the latest stable version
pip install claude-force

# Verify installation
claude-force --help

# Expected output: Multi-Agent Orchestration System for Claude
```

**Upgrade to latest version:**
```bash
pip install --upgrade claude-force
```

### Method 2: Install from Source (For Development)

**For contributors and developers who want to modify the code:**

```bash
# 1. Clone the repository
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force

# 2. Create a virtual environment (recommended)
python3 -m venv venv

# 3. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install the package in development mode
pip install -e .

# 5. Verify installation
claude-force --help
```

### Method 3: Install from GitHub

**Install directly from GitHub (latest development version):**

```bash
pip install git+https://github.com/khanh-vu/claude-force.git
```

---

## 🔑 Set Up Your API Key

### Option 1: Environment Variable (Recommended)

```bash
# On macOS/Linux:
export ANTHROPIC_API_KEY='your-api-key-here'

# Add to your shell profile for persistence:
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
# or for zsh:
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
```

```powershell
# On Windows (PowerShell):
$env:ANTHROPIC_API_KEY = "your-api-key-here"

# For persistence:
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-api-key-here', 'User')
```

### Option 2: Pass on Command Line

```bash
claude-force --api-key your-api-key-here run agent code-reviewer --task "..."
```

---

## ✅ Verify Installation

### 1. Check Command-Line Tool

```bash
claude-force --help
```

Expected output:
```
usage: claude-force [-h] [--config CONFIG] [--api-key API_KEY]
                    {list,info,run,init} ...

Multi-Agent Orchestration System for Claude
...
```

### 2. List Available Agents

```bash
claude-force list agents
```

Expected output:
```
📋 Available Agents

Name                           Priority   Domains
--------------------------------------------------------------------------------
code-reviewer                  Critical   code-quality, security, performance
security-specialist            Critical   security, compliance, threat-modeling
...

Total: 15 agents
```

### 3. Run a Test Agent

```bash
claude-force run agent code-reviewer --task "Review this code: def add(a, b): return a + b"
```

If this works, you're all set! ✅

---

## 🐛 Troubleshooting

### Issue: `command not found: claude-force`

**Solution 1**: Ensure virtual environment is activated
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Solution 2**: Reinstall the package
```bash
pip install -e .
```

**Solution 3**: Check pip installation path
```bash
which claude-force  # Should show a path
pip show claude-force  # Should show package info
```

### Issue: `ModuleNotFoundError: No module named 'anthropic'`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: `ValueError: Anthropic API key required`

**Solutions**:
1. Set environment variable: `export ANTHROPIC_API_KEY='your-key'`
2. Pass on command line: `--api-key your-key`
3. Check key is valid at [console.anthropic.com](https://console.anthropic.com/)

### Issue: `FileNotFoundError: Configuration file not found: .claude/claude.json`

**Solution 1**: Initialize a new project
```bash
# In a new or existing project directory
claude-force init --description "My project description"
```

**Solution 2**: Navigate to an existing claude-force project
```bash
cd path/to/claude-force  # Navigate to repo root
claude-force run agent ...
```

**Solution 3**: Specify config location
```bash
claude-force --config /path/to/.claude/claude.json run agent ...
```

**Note**: If you have an existing `.claude` directory (e.g., from Claude Code), `claude-force init` will automatically preserve your existing files while adding the required configuration.

### Issue: Tests fail on Windows (Path issues)

**Solution**: Windows uses different path separators
```python
# Update test_claude_system.py if needed
# Use Path objects instead of string concatenation
from pathlib import Path
```

### Issue: `pytest: command not found`

**Solution**: Install dev dependencies
```bash
pip install -e ".[dev]"
# or
pip install pytest pytest-cov
```

---

## 🔧 Development Setup

For contributors and developers:

### 1. Clone and Install

```bash
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

### 3. Run Tests

```bash
# Run all tests
pytest test_claude_system.py -v

# Run with coverage
pytest test_claude_system.py --cov=claude_force --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 4. Run Benchmarks

```bash
python3 benchmarks/scripts/run_all.py
python3 benchmarks/scripts/generate_visual_report.py
python3 benchmarks/scripts/generate_dashboard.py
```

### 5. Code Quality Checks

```bash
# Format code
black claude_force/ tests/

# Lint code
pylint claude_force/

# Type checking
mypy claude_force/
```

---

## 🌐 Platform-Specific Notes

### macOS

- Use Homebrew to install Python: `brew install python@3.11`
- Virtual environments work seamlessly
- Recommended terminal: iTerm2 or default Terminal.app

### Linux (Ubuntu/Debian)

```bash
# Install Python and venv
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install claude-force
pip install -e .
```

### Windows

- Install Python from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation
- Use PowerShell or Windows Terminal
- Virtual environment command: `venv\Scripts\activate`

---

## 📦 Package Management

### Using pip

```bash
# Install
pip install claude-force

# Upgrade
pip install --upgrade claude-force

# Uninstall
pip uninstall claude-force
```

### Using Poetry (Alternative)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install claude-force from PyPI
poetry add claude-force

# Or install from source
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force
poetry install
```

### Using Conda

```bash
# Create conda environment
conda create -n claude-force python=3.11
conda activate claude-force

# Install from PyPI
pip install claude-force

# Or install from source
git clone https://github.com/khanh-vu/claude-force.git
cd claude-force
pip install -e .
```

---

## 🐳 Docker Installation (Coming Soon)

```bash
# Pull image
docker pull claude-force:latest

# Run
docker run -it \
  -e ANTHROPIC_API_KEY="your-key" \
  -v $(pwd):/workspace \
  claude-force:latest \
  claude-force list agents
```

---

## 🆘 Getting Help

If you encounter issues:

1. **Check this guide** - Most common issues are covered above
2. **Run tests** - `pytest test_claude_system.py -v` to verify installation
3. **Check Python version** - Must be 3.8+
4. **Verify API key** - Make sure it's set and valid
5. **Check GitHub Issues** - Search for similar problems
6. **Open an issue** - Provide error message, Python version, OS

---

## ✅ Post-Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] claude-force installed (`pip install -e .`)
- [ ] API key configured (environment variable)
- [ ] `claude-force --help` works
- [ ] `claude-force list agents` shows 15 agents
- [ ] Test agent runs successfully
- [ ] (Optional) Tests pass: `pytest test_claude_system.py -v`
- [ ] (Optional) Benchmarks run: `python3 benchmarks/scripts/run_all.py`

---

## 🎓 Next Steps

Once installed, try:

1. **List all agents**: `claude-force list agents`
2. **Get agent info**: `claude-force info code-reviewer`
3. **Run simple agent**: `claude-force run agent code-reviewer --task "Review code"`
4. **Run workflow**: `claude-force run workflow bug-fix --task "Fix login error"`
5. **Read documentation**: [README.md](README.md), [QUICK_START.md](QUICK_START.md)

---

**Installation Complete!** 🎉

You now have a fully functional Claude Multi-Agent Orchestration System.

For usage examples, see [QUICK_START.md](QUICK_START.md)

For full documentation, see [README.md](README.md)
