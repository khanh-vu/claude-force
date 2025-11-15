# PyPI Package Upload Guide

A comprehensive guide for uploading Python packages to PyPI (Python Package Index).

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Package Preparation](#package-preparation)
- [Building the Package](#building-the-package)
- [Testing on TestPyPI](#testing-on-testpypi)
- [Publishing to PyPI](#publishing-to-pypi)
- [Automated Publishing with GitHub Actions](#automated-publishing-with-github-actions)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

PyPI (Python Package Index) is the official repository for Python packages. This guide covers the complete process of uploading packages to PyPI, from preparation to publication.

### What You'll Learn

- How to prepare your package for distribution
- How to build distribution files (wheel and source)
- How to test your package on TestPyPI
- How to publish to production PyPI
- How to automate releases with CI/CD

## Prerequisites

### Required Tools

```bash
# Install build tools
pip install --upgrade pip
pip install build twine

# Verify installations
python -m build --version
twine --version
```

### Required Accounts

1. **PyPI Account**: Register at https://pypi.org/account/register/
2. **TestPyPI Account**: Register at https://test.pypi.org/account/register/

### API Tokens (Recommended)

Using API tokens is more secure than passwords.

#### Creating PyPI API Token

1. Log in to https://pypi.org
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Name: `claude-force-upload` (or your project name)
5. Scope: Select "Entire account" or specific project
6. Click "Create token"
7. **Copy the token immediately** (you can't view it again)

#### Creating TestPyPI Token

1. Log in to https://test.pypi.org
2. Follow same steps as above
3. Save token separately

#### Configuring Tokens

Create/edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...YOUR_TOKEN_HERE
```

**Security Note**: Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

## Package Preparation

### 1. Project Structure

Ensure your project follows this structure:

```
your-package/
├── src/your_package/          # or just your_package/
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
├── tests/
│   └── test_*.py
├── README.md
├── LICENSE
├── pyproject.toml             # Modern way (recommended)
├── setup.py                   # Legacy way (optional)
└── MANIFEST.in               # For including non-Python files
```

### 2. Configure pyproject.toml

This is the modern, recommended way to configure Python packages:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package-name"
version = "1.0.0"
description = "A short description of your package"
readme = "README.md"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
license = {text = "MIT"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
keywords = ["keyword1", "keyword2", "keyword3"]
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
]
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "mypy>=0.950",
]

[project.urls]
Homepage = "https://github.com/username/your-package"
Documentation = "https://your-package.readthedocs.io"
Repository = "https://github.com/username/your-package"
Issues = "https://github.com/username/your-package/issues"

[project.scripts]
your-cli = "your_package.cli:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["your_package*"]
exclude = ["tests*"]
```

### 3. Essential Files

#### README.md

Include:
- Project description
- Installation instructions
- Usage examples
- Contributing guidelines
- License information

#### LICENSE

Choose an appropriate license:
- MIT (permissive)
- Apache 2.0 (permissive with patent grant)
- GPL (copyleft)

Get license text from: https://choosealicense.com/

#### __init__.py

Include version information:

```python
"""Your Package - Brief description."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .module1 import MainClass
from .module2 import helper_function

__all__ = ["MainClass", "helper_function"]
```

### 4. Version Numbering

Follow [Semantic Versioning (SemVer)](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Pre-release versions**:
- `1.0.0-alpha.1` - Alpha release
- `1.0.0-beta.2` - Beta release
- `1.0.0-rc.1` - Release candidate

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info

# Or use a clean script
find . -type d -name "*.egg-info" -exec rm -rf {} +
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name "build" -exec rm -rf {} +
find . -type d -name "dist" -exec rm -rf {} +
```

### 2. Build Distribution Files

```bash
# Build both wheel and source distribution
python -m build

# This creates:
# dist/your_package-1.0.0-py3-none-any.whl  (wheel)
# dist/your_package-1.0.0.tar.gz            (source)
```

**Build output explanation**:
- `.whl` (wheel): Binary distribution (faster to install)
- `.tar.gz` (sdist): Source distribution (builds during install)

### 3. Verify Build

```bash
# Check package integrity
twine check dist/*

# Expected output:
# Checking dist/your_package-1.0.0-py3-none-any.whl: PASSED
# Checking dist/your_package-1.0.0.tar.gz: PASSED
```

**Common issues twine checks**:
- README rendering on PyPI
- Metadata completeness
- File structure
- Long description format

### 4. Inspect the Package

```bash
# List contents of wheel
unzip -l dist/your_package-1.0.0-py3-none-any.whl

# Extract and inspect
tar -tzf dist/your_package-1.0.0.tar.gz
```

## Testing on TestPyPI

**Always test on TestPyPI first** to catch issues before publishing to production PyPI.

### 1. Upload to TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Or specify explicitly
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### 2. Verify Upload

Visit: https://test.pypi.org/project/your-package/

Check:
- ✓ Version number is correct
- ✓ README renders properly
- ✓ Links work
- ✓ Metadata is complete
- ✓ Files are present

### 3. Test Installation

```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  your-package

# The --extra-index-url allows dependencies from real PyPI
```

### 4. Test Functionality

```bash
# Verify installation
pip show your-package

# Test CLI (if applicable)
your-cli --help
your-cli --version

# Test in Python
python -c "import your_package; print(your_package.__version__)"

# Run actual tests
pytest tests/
```

### 5. Fix Issues and Re-upload

If you find issues:

```bash
# 1. Fix the code
# 2. Bump version (TestPyPI doesn't allow same version re-upload)
# 3. Rebuild
python -m build
# 4. Re-upload
twine upload --repository testpypi dist/*
```

**Note**: TestPyPI versions are separate from production PyPI.

## Publishing to PyPI

Once TestPyPI testing is successful, publish to production PyPI.

### 1. Final Pre-publish Checklist

- [ ] All tests pass
- [ ] TestPyPI version tested successfully
- [ ] Version number is correct and follows SemVer
- [ ] CHANGELOG updated
- [ ] README is complete and renders correctly
- [ ] License file included
- [ ] No sensitive data in package
- [ ] Dependencies are correct
- [ ] Package name is available on PyPI

### 2. Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# You'll be prompted for credentials (or uses ~/.pypirc)
```

**Expected output**:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading your_package-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.0/50.0 kB • 00:01
Uploading your_package-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45.0/45.0 kB • 00:01

View at:
https://pypi.org/project/your-package/1.0.0/
```

### 3. Verify Publication

```bash
# Wait 1-2 minutes for CDN propagation

# Check PyPI page
# Visit: https://pypi.org/project/your-package/

# Test installation
pip install your-package

# Verify version
pip show your-package
your-package --version  # if CLI
```

### 4. Create Git Tag

```bash
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0

Major changes:
- Feature 1
- Feature 2
- Bug fix 1
"

# Push tag
git push origin v1.0.0
```

### 5. Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Select tag: `v1.0.0`
4. Title: `Version 1.0.0`
5. Description: Copy from CHANGELOG
6. Attach dist files (optional)
7. Click "Publish release"

## Automated Publishing with GitHub Actions

Automate the release process with GitHub Actions.

### 1. Store API Token in GitHub Secrets

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI API token
5. Click "Add secret"

Repeat for `TEST_PYPI_API_TOKEN`.

### 2. Create Release Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*.*.*'  # Triggers on version tags like v1.0.0

jobs:
  build-and-publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Check package
      run: twine check dist/*

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*

    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*
        generate_release_notes: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Test Release Workflow

Create `.github/workflows/test-publish.yml` for TestPyPI:

```yaml
name: Test Publish to TestPyPI

on:
  push:
    tags:
      - 'v*.*.*-rc.*'  # Triggers on RC tags like v1.0.0-rc.1

jobs:
  test-publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Check package
      run: twine check dist/*

    - name: Publish to TestPyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
      run: twine upload --repository testpypi dist/*
```

### 4. Triggering Automated Release

```bash
# For test release
git tag v1.0.0-rc.1
git push origin v1.0.0-rc.1

# For production release
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically build and publish.

## Troubleshooting

### Common Errors and Solutions

#### "File already exists"

**Error**:
```
HTTPError: 400 Bad Request
File already exists
```

**Solution**:
- PyPI doesn't allow re-uploading same version
- Bump version number in `pyproject.toml` and `__init__.py`
- Rebuild and re-upload

```bash
# Bump version (e.g., 1.0.0 → 1.0.1)
# Edit pyproject.toml and __init__.py
python -m build
twine upload dist/*
```

#### "Invalid credentials"

**Error**:
```
HTTPError: 403 Forbidden
Invalid or non-existent authentication information
```

**Solutions**:
1. Check `~/.pypirc` file has correct token
2. Ensure token starts with `pypi-`
3. Username should be `__token__` (not your username)
4. Regenerate token if expired

#### "README rendering issues"

**Error**:
```
The description failed to render in the default format of reStructuredText
```

**Solutions**:
1. Ensure `readme = "README.md"` in `pyproject.toml`
2. Use valid Markdown (no custom HTML)
3. Test locally: `twine check dist/*`
4. Use markdown validator

#### "Package name already taken"

**Error**:
```
The name 'package-name' is already in use
```

**Solutions**:
1. Choose a different name
2. Check if name is available: https://pypi.org/project/your-name/
3. Add prefix/suffix (e.g., `py-yourname`, `yourname-sdk`)
4. Use organization name (e.g., `acme-yourname`)

#### "Missing dependencies"

**Error**:
```
ModuleNotFoundError: No module named 'some_package'
```

**Solutions**:
1. Add missing dependencies to `pyproject.toml`
2. Test in clean virtual environment
3. Check `dependencies` and `optional-dependencies`

#### "Build fails"

**Error**:
```
ERROR: Could not build wheels for package
```

**Solutions**:
1. Check `build-system` in `pyproject.toml`
2. Update build tools: `pip install --upgrade build setuptools wheel`
3. Check for syntax errors
4. Ensure all files are included (check `MANIFEST.in`)

#### "Upload timeout"

**Error**:
```
ReadTimeoutError: Read timed out
```

**Solutions**:
1. Check internet connection
2. Retry upload: `twine upload dist/*`
3. Upload individual files if large:
   ```bash
   twine upload dist/package-1.0.0-py3-none-any.whl
   twine upload dist/package-1.0.0.tar.gz
   ```

### Debugging Tips

#### Check package metadata

```bash
# View metadata
python -m setuptools.config check pyproject.toml

# Or inspect built package
tar -xzf dist/package-1.0.0.tar.gz
cat package-1.0.0/PKG-INFO
```

#### Test in isolated environment

```bash
# Use Docker for truly clean environment
docker run -it --rm python:3.11 bash
pip install your-package
python -c "import your_package"
```

#### Verbose output

```bash
# Build with verbose output
python -m build --verbose

# Upload with verbose output
twine upload --verbose dist/*
```

## Best Practices

### Version Management

1. **Use semantic versioning** (MAJOR.MINOR.PATCH)
2. **Single source of truth** for version:
   ```python
   # In __init__.py
   __version__ = "1.0.0"

   # In pyproject.toml
   dynamic = ["version"]

   # Or use setuptools_scm for git-based versioning
   ```

3. **Tag releases in git**:
   ```bash
   git tag -a v1.0.0 -m "Release 1.0.0"
   git push origin v1.0.0
   ```

### Security

1. **Use API tokens**, not passwords
2. **Set proper file permissions**: `chmod 600 ~/.pypirc`
3. **Never commit** `.pypirc` or tokens to git
4. **Add to .gitignore**:
   ```
   .pypirc
   dist/
   build/
   *.egg-info/
   ```
5. **Enable 2FA** on PyPI account
6. **Use scoped tokens** (project-specific when possible)
7. **Rotate tokens** regularly
8. **Review package** before upload (no secrets, credentials, or API keys)

### Package Quality

1. **Include comprehensive tests**
2. **Add type hints** for better IDE support
3. **Write detailed docstrings**
4. **Include examples** in README
5. **Add badges** (build status, coverage, version)
6. **Maintain CHANGELOG**
7. **Use code formatters** (black, isort)
8. **Run linters** (pylint, flake8, mypy)

### Documentation

1. **Write clear README** with:
   - Installation instructions
   - Quick start example
   - API overview
   - Links to full documentation
2. **Host docs** on Read the Docs or GitHub Pages
3. **Include docstrings** for all public APIs
4. **Add usage examples**
5. **Document breaking changes**

### Testing Before Release

```bash
# Full pre-release checklist
python -m pytest tests/ -v           # Run all tests
python -m black --check .            # Check formatting
python -m pylint your_package/       # Lint code
python -m mypy your_package/         # Type check
python -m build                      # Build package
twine check dist/*                   # Validate package
```

### Continuous Integration

1. **Run tests on multiple Python versions**
2. **Test on different OS** (Linux, macOS, Windows)
3. **Automate releases** with GitHub Actions
4. **Use TestPyPI** for pre-releases
5. **Require code review** before merging

### Maintenance

1. **Respond to issues** promptly
2. **Keep dependencies updated**
3. **Security patches** as priority
4. **Deprecate features** gracefully
5. **Maintain backward compatibility** when possible
6. **Document migration paths** for breaking changes

### Versioning Strategy Example

```bash
# Development
1.0.0-alpha.1
1.0.0-alpha.2

# Testing
1.0.0-beta.1
1.0.0-rc.1

# Production
1.0.0

# Bug fixes
1.0.1
1.0.2

# New features
1.1.0
1.2.0

# Breaking changes
2.0.0
```

## Additional Resources

### Official Documentation

- PyPI: https://pypi.org/
- Packaging Guide: https://packaging.python.org/
- Twine: https://twine.readthedocs.io/
- Build: https://pypa-build.readthedocs.io/

### Tools

- **build**: Modern build tool
- **twine**: Secure package upload
- **bump2version**: Version management
- **check-manifest**: Verify MANIFEST.in
- **pyroma**: Rate package quality

### Helpful Links

- Choosing a license: https://choosealicense.com/
- Semantic Versioning: https://semver.org/
- Python Packaging Authority: https://www.pypa.io/
- Classifiers list: https://pypi.org/classifiers/

### Example Projects

Well-packaged projects to learn from:
- requests: https://github.com/psf/requests
- click: https://github.com/pallets/click
- pytest: https://github.com/pytest-dev/pytest

## Quick Reference

### Essential Commands

```bash
# Install tools
pip install build twine

# Clean build
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Create tag
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

### File Checklist

- [ ] `pyproject.toml` - Package configuration
- [ ] `README.md` - Project documentation
- [ ] `LICENSE` - License file
- [ ] `CHANGELOG.md` - Version history
- [ ] `__init__.py` - Package initialization with `__version__`
- [ ] `.gitignore` - Ignore build artifacts
- [ ] `tests/` - Test suite

### Pre-upload Checklist

- [ ] Tests pass
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] README complete
- [ ] License included
- [ ] Build successful
- [ ] Package validated (twine check)
- [ ] TestPyPI tested
- [ ] No secrets in code
- [ ] Git tag created

---

**Need Help?**
- PyPI Support: https://pypi.org/help/
- Packaging Discussions: https://discuss.python.org/c/packaging/
- Stack Overflow: Tag `python-packaging`
