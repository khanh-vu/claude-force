# Release Automation Plan for claude-force v1.0

> **Status**: Draft for Review
> **Target Release**: v1.0.0
> **Current Version**: 2.2.0 (pre-1.0 development versions)
> **Date**: 2025-11-15

## Executive Summary

This document outlines a comprehensive automation strategy for the Python package release process for `claude-force`. The plan builds upon the existing GitHub Actions workflows and introduces modern best practices for semantic versioning, changelog generation, and automated quality gates.

**Current State**:
- ✅ Comprehensive CI pipeline (testing, linting, security, benchmarks)
- ✅ Manual release workflow via git tags
- ✅ TestPyPI testing capability
- ⚠️  Manual version bumping in multiple files
- ⚠️  Manual changelog maintenance
- ⚠️  No automated pre-release validation

**Target State**:
- ✅ Fully automated version management
- ✅ Automated changelog generation
- ✅ Pre-release quality gates
- ✅ Release candidate workflow
- ✅ Automated documentation updates
- ✅ Post-release automation

---

## 1. Version Management Strategy

### 1.1 Semantic Versioning

Adopt strict [Semantic Versioning 2.0.0](https://semver.org/) with the following conventions:

- **MAJOR** (X.0.0): Breaking API changes, major architectural changes
- **MINOR** (0.X.0): New features, agent additions, backward-compatible improvements
- **PATCH** (0.0.X): Bug fixes, documentation updates, minor improvements

**Pre-release versions**:
- `X.Y.Z-alpha.N` - Early development, unstable
- `X.Y.Z-beta.N` - Feature complete, testing phase
- `X.Y.Z-rc.N` - Release candidate, production-ready testing

### 1.2 Automated Version Bumping

**Tool**: [bump2version](https://github.com/c4urself/bump2version) or [semantic-release](https://github.com/semantic-release/semantic-release)

**Files to update automatically**:
- `pyproject.toml` (version field)
- `setup.py` (version variable)
- `README.md` (badge versions)
- `claude_force/__init__.py` (`__version__` attribute)
- `CHANGELOG.md` (version headers)

**Configuration** (`.bumpversion.cfg`):
```ini
[bumpversion]
current_version = 2.2.0
commit = True
tag = True
tag_name = v{new_version}
message = chore: bump version to {new_version}

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file:setup.py]
search = version="{current_version}"
replace = version="{new_version}"

[bumpversion:file:claude_force/__init__.py]
search = __version__ = "{current_version}"
replace = __version__ = "{new_version}"

[bumpversion:file:README.md]
search = **Version**: {current_version}
replace = **Version**: {new_version}
```

**Alternative: Python Semantic Release**

For more advanced automation, use [python-semantic-release](https://python-semantic-release.readthedocs.io/):
- Analyzes commit messages (Conventional Commits)
- Automatically determines version bump type
- Generates changelogs
- Creates releases

```bash
pip install python-semantic-release
semantic-release version
semantic-release publish
```

---

## 2. Changelog Automation

### 2.1 Conventional Commits

Adopt [Conventional Commits](https://www.conventionalcommits.org/) specification:

**Format**: `<type>(<scope>): <subject>`

**Types**:
- `feat:` - New feature (MINOR version bump)
- `fix:` - Bug fix (PATCH version bump)
- `docs:` - Documentation only
- `style:` - Formatting, no code change
- `refactor:` - Code restructuring
- `perf:` - Performance improvement
- `test:` - Adding tests
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes
- `build:` - Build system changes
- `BREAKING CHANGE:` - Breaking changes (MAJOR version bump)

**Examples**:
```
feat(agents): add kubernetes-engineer agent
fix(orchestrator): resolve race condition in workflow execution
docs(readme): update installation instructions
perf(cache): implement agent definition caching
BREAKING CHANGE: remove deprecated HybridOrchestrator API
```

### 2.2 Automated Changelog Generation

**Tool**: [git-cliff](https://git-cliff.org/) or [conventional-changelog](https://github.com/conventional-changelog/conventional-changelog)

**Configuration** (`cliff.toml`):
```toml
[changelog]
header = """
# Changelog

All notable changes to claude-force will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
"""
body = """
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper_first }}
    {% for commit in commits %}
        - {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
    {%- endfor %}
{% endfor %}
"""

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
    { message = "^feat", group = "Features" },
    { message = "^fix", group = "Bug Fixes" },
    { message = "^doc", group = "Documentation" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Refactoring" },
    { message = "^test", group = "Testing" },
    { message = "^chore", group = "Miscellaneous" },
]
```

**GitHub Action** (`.github/workflows/changelog.yml`):
```yaml
name: Update Changelog

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog
        uses: orhun/git-cliff-action@v2
        with:
          config: cliff.toml
          args: --latest --output CHANGELOG.md

      - name: Commit changelog
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add CHANGELOG.md
          git commit -m "docs: update changelog for ${GITHUB_REF_NAME}"
          git push
```

---

## 3. Release Workflow Automation

### 3.1 Enhanced Release Workflow

**File**: `.github/workflows/release.yml`

**Improvements**:
1. Pre-release quality gates
2. Automated changelog generation
3. Documentation deployment
4. GitHub Release creation with rich notes
5. PyPI publication with trusted publishing
6. Post-release notifications

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write
  id-token: write
  pull-requests: write

jobs:
  # Step 1: Pre-release validation
  validate:
    name: Pre-release Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run full test suite
        run: |
          pytest test_claude_system.py -v --cov=claude_force
          pytest tests/ -v

      - name: Run security checks
        run: |
          pip install bandit safety
          bandit -r claude_force/ -ll
          safety check

      - name: Lint code
        run: |
          pip install black pylint mypy
          black --check claude_force/
          pylint claude_force/ --fail-under=8.0

      - name: Verify version consistency
        run: |
          python scripts/check_version_consistency.py

      - name: Check documentation
        run: |
          python scripts/verify_docs.py

  # Step 2: Build package
  build:
    name: Build Package
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: |
          pip install build twine

      - name: Build package
        run: |
          python -m build

      - name: Check package
        run: |
          twine check --strict dist/*

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: python-package
          path: dist/
          retention-days: 7

  # Step 3: Publish to PyPI
  publish-pypi:
    name: Publish to PyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/claude-force
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          skip-existing: false
          verify-metadata: true

  # Step 4: Generate changelog
  changelog:
    name: Generate Changelog
    needs: publish-pypi
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog
        uses: orhun/git-cliff-action@v2
        with:
          config: cliff.toml
          args: --latest --strip header
        id: changelog

      - name: Update CHANGELOG.md
        run: |
          git-cliff --tag ${GITHUB_REF_NAME} --output CHANGELOG.md

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add CHANGELOG.md
          git commit -m "docs: update changelog for ${GITHUB_REF_NAME}" || true
          git push origin HEAD:main || true

  # Step 5: Create GitHub Release
  github-release:
    name: Create GitHub Release
    needs: [publish-pypi, changelog]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: python-package
          path: dist/

      - name: Extract version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=${VERSION}" >> $GITHUB_OUTPUT
          echo "major=$(echo $VERSION | cut -d. -f1)" >> $GITHUB_OUTPUT
          echo "minor=$(echo $VERSION | cut -d. -f2)" >> $GITHUB_OUTPUT

      - name: Generate release notes
        uses: orhun/git-cliff-action@v2
        with:
          config: cliff.toml
          args: --latest --strip header
        id: release_notes

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          draft: false
          prerelease: ${{ contains(github.ref, 'alpha') || contains(github.ref, 'beta') || contains(github.ref, 'rc') }}
          name: Release v${{ steps.version.outputs.version }}
          body: |
            # 🚀 claude-force v${{ steps.version.outputs.version }}

            ## Installation

            ```bash
            pip install claude-force==${{ steps.version.outputs.version }}
            ```

            ## What's Changed

            ${{ steps.release_notes.outputs.content }}

            ## Documentation

            - 📚 [Installation Guide](https://github.com/${{ github.repository }}/blob/main/INSTALLATION.md)
            - 🚀 [Quick Start](https://github.com/${{ github.repository }}/blob/main/QUICK_START.md)
            - 📖 [Full Documentation](https://github.com/${{ github.repository }}/blob/main/README.md)

            ## Upgrade Guide

            ```bash
            pip install --upgrade claude-force
            ```

            ---

            **Full Changelog**: https://github.com/${{ github.repository }}/blob/main/CHANGELOG.md
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # Step 6: Post-release tasks
  post-release:
    name: Post-release Tasks
    needs: github-release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create announcement issue
        uses: actions/github-script@v7
        with:
          script: |
            const version = context.ref.replace('refs/tags/v', '');
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `📢 Released v${version}`,
              body: `🎉 **claude-force v${version}** has been released!\n\n` +
                    `- 📦 [PyPI Package](https://pypi.org/project/claude-force/${version}/)\n` +
                    `- 📝 [Release Notes](${context.payload.release.html_url})\n` +
                    `- 📚 [Documentation](https://github.com/${context.repo.owner}/${context.repo.repo})\n\n` +
                    `Install now:\n\`\`\`bash\npip install claude-force==${version}\n\`\`\``,
              labels: ['release', 'announcement']
            });

      - name: Notify on Slack (optional)
        if: false  # Enable if Slack integration configured
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🚀 New release: claude-force v${{ steps.version.outputs.version }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 3.2 Release Candidate Workflow

**File**: `.github/workflows/release-candidate.yml`

```yaml
name: Release Candidate

on:
  workflow_dispatch:
    inputs:
      version_type:
        description: 'Version bump type'
        required: true
        type: choice
        options:
          - rc
          - beta
          - alpha
      base_version:
        description: 'Base version (e.g., 1.0.0)'
        required: true
        type: string

jobs:
  create-rc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: |
          pip install bump2version

      - name: Determine RC version
        id: rc_version
        run: |
          BASE_VERSION="${{ github.event.inputs.base_version }}"
          TYPE="${{ github.event.inputs.version_type }}"

          # Get latest RC number for this version
          LATEST_RC=$(git tag -l "v${BASE_VERSION}-${TYPE}.*" | sort -V | tail -1)

          if [ -z "$LATEST_RC" ]; then
            RC_NUM=1
          else
            RC_NUM=$(echo $LATEST_RC | grep -oP "${TYPE}\.\K\d+" | awk '{print $1+1}')
          fi

          RC_VERSION="${BASE_VERSION}-${TYPE}.${RC_NUM}"
          echo "version=${RC_VERSION}" >> $GITHUB_OUTPUT

      - name: Update version files
        run: |
          # Update all version references
          sed -i 's/version = ".*"/version = "${{ steps.rc_version.outputs.version }}"/' pyproject.toml
          sed -i 's/version=".*"/version="${{ steps.rc_version.outputs.version }}"/' setup.py

      - name: Commit and tag
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add pyproject.toml setup.py
          git commit -m "chore: bump version to ${{ steps.rc_version.outputs.version }}"
          git tag "v${{ steps.rc_version.outputs.version }}"
          git push origin "v${{ steps.rc_version.outputs.version }}"

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
          password: ${{ secrets.TEST_PYPI_API_TOKEN }}

      - name: Create pre-release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: v${{ steps.rc_version.outputs.version }}
          prerelease: true
          draft: false
          name: Release Candidate v${{ steps.rc_version.outputs.version }}
          body: |
            # 🧪 Release Candidate v${{ steps.rc_version.outputs.version }}

            This is a pre-release version for testing purposes.

            ## Installation

            ```bash
            pip install --index-url https://test.pypi.org/simple/ \
              --extra-index-url https://pypi.org/simple \
              claude-force==${{ steps.rc_version.outputs.version }}
            ```

            ## Testing

            Please test this release and report any issues before the final release.
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 4. Automated Documentation Updates

### 4.1 Documentation Deployment

**Tool**: [MkDocs](https://www.mkdocs.org/) or [Sphinx](https://www.sphinx-doc.org/)

**GitHub Pages deployment** (`.github/workflows/docs.yml`):
```yaml
name: Documentation

on:
  push:
    branches: [main]
    tags:
      - 'v*.*.*'
  pull_request:
    branches: [main]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocstrings

      - name: Build documentation
        run: |
          mkdocs build

      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v'))
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

### 4.2 API Documentation Generation

**Auto-generate API docs from docstrings**:
```yaml
- name: Generate API documentation
  run: |
    pip install pdoc3
    pdoc --html --output-dir docs/api claude_force
```

---

## 5. Quality Gates & Validation

### 5.1 Pre-release Checklist

Create automated checks before allowing releases:

**Script**: `scripts/check_version_consistency.py`
```python
#!/usr/bin/env python3
"""Verify version consistency across all files"""

import sys
from pathlib import Path
import re
import toml

def get_version_from_pyproject():
    pyproject = toml.load("pyproject.toml")
    return pyproject["project"]["version"]

def get_version_from_setup():
    setup_content = Path("setup.py").read_text()
    match = re.search(r'version="([^"]+)"', setup_content)
    return match.group(1) if match else None

def get_version_from_init():
    init_content = Path("claude_force/__init__.py").read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    return match.group(1) if match else None

def main():
    versions = {
        "pyproject.toml": get_version_from_pyproject(),
        "setup.py": get_version_from_setup(),
        "__init__.py": get_version_from_init(),
    }

    print("Version consistency check:")
    for source, version in versions.items():
        print(f"  {source}: {version}")

    if len(set(versions.values())) != 1:
        print("\n❌ Version mismatch detected!")
        sys.exit(1)

    print("\n✅ All versions are consistent")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 5.2 Release Checklist Automation

**Script**: `scripts/pre_release_checklist.py`
```python
#!/usr/bin/env python3
"""Automated pre-release checklist"""

import subprocess
import sys
from pathlib import Path

CHECKS = [
    {
        "name": "All tests pass",
        "command": ["pytest", "test_claude_system.py", "-v"],
    },
    {
        "name": "No security vulnerabilities",
        "command": ["bandit", "-r", "claude_force/", "-ll"],
    },
    {
        "name": "Code is formatted",
        "command": ["black", "--check", "claude_force/"],
    },
    {
        "name": "No linting errors",
        "command": ["pylint", "claude_force/", "--fail-under=8.0"],
    },
    {
        "name": "Changelog is updated",
        "command": ["python", "scripts/check_changelog.py"],
    },
    {
        "name": "Version is consistent",
        "command": ["python", "scripts/check_version_consistency.py"],
    },
    {
        "name": "README is up to date",
        "command": ["python", "scripts/verify_readme.py"],
    },
]

def run_check(check):
    print(f"\n{'='*60}")
    print(f"Running: {check['name']}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            check["command"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print(f"✅ {check['name']}: PASSED")
            return True
        else:
            print(f"❌ {check['name']}: FAILED")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {check['name']}: ERROR - {e}")
        return False

def main():
    print("🚀 Pre-release Checklist")
    print("="*60)

    results = []
    for check in CHECKS:
        results.append(run_check(check))

    print("\n" + "="*60)
    print("Summary:")
    print("="*60)

    for check, passed in zip(CHECKS, results):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check['name']}")

    if all(results):
        print("\n✅ All checks passed! Ready for release.")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix before releasing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1)
**Priority**: HIGH
**Effort**: 2-3 days

- [ ] Set up version consistency script
- [ ] Configure `.bumpversion.cfg`
- [ ] Create pre-release checklist script
- [ ] Test manual version bumping workflow
- [ ] Document new versioning process

**Deliverables**:
- `scripts/check_version_consistency.py`
- `scripts/pre_release_checklist.py`
- `.bumpversion.cfg`
- Updated `CONTRIBUTING.md` with release process

### Phase 2: Changelog Automation (Week 1-2)
**Priority**: HIGH
**Effort**: 2-3 days

- [ ] Adopt Conventional Commits specification
- [ ] Configure `git-cliff` or `conventional-changelog`
- [ ] Create changelog generation workflow
- [ ] Update existing CHANGELOG.md format
- [ ] Train team on commit message format

**Deliverables**:
- `cliff.toml` or `changelog.config.js`
- `.github/workflows/changelog.yml`
- Updated `CHANGELOG.md`
- Commit message guidelines

### Phase 3: Enhanced Release Workflow (Week 2)
**Priority**: HIGH
**Effort**: 3-4 days

- [ ] Enhance `.github/workflows/release.yml` with quality gates
- [ ] Add automated version bumping
- [ ] Integrate changelog generation
- [ ] Add post-release notifications
- [ ] Test end-to-end release process

**Deliverables**:
- Updated `.github/workflows/release.yml`
- Release process documentation
- Successful test release

### Phase 4: Release Candidate Workflow (Week 2-3)
**Priority**: MEDIUM
**Effort**: 2 days

- [ ] Create `.github/workflows/release-candidate.yml`
- [ ] Configure TestPyPI publication
- [ ] Add RC version naming logic
- [ ] Test RC creation and promotion

**Deliverables**:
- `.github/workflows/release-candidate.yml`
- RC process documentation
- Successful test RC

### Phase 5: Documentation Automation (Week 3)
**Priority**: MEDIUM
**Effort**: 2-3 days

- [ ] Set up MkDocs or Sphinx
- [ ] Configure GitHub Pages deployment
- [ ] Add API documentation generation
- [ ] Create documentation workflow
- [ ] Test documentation builds

**Deliverables**:
- `mkdocs.yml` or `conf.py`
- `.github/workflows/docs.yml`
- Deployed documentation site

### Phase 6: Monitoring & Refinement (Week 4)
**Priority**: LOW
**Effort**: 1-2 days

- [ ] Add release metrics tracking
- [ ] Set up post-release monitoring
- [ ] Create release dashboard
- [ ] Gather team feedback
- [ ] Refine workflows based on usage

**Deliverables**:
- Release metrics dashboard
- Updated workflows based on feedback
- Final documentation

---

## 7. Tools & Dependencies

### 7.1 Required Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **bump2version** | Version management | `pip install bump2version` |
| **git-cliff** | Changelog generation | GitHub Action or binary |
| **twine** | PyPI package validation | `pip install twine` |
| **pytest** | Testing | Already installed |
| **black** | Code formatting | Already installed |
| **pylint** | Linting | Already installed |

### 7.2 Optional Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **semantic-release** | Automated releases | `pip install python-semantic-release` |
| **mkdocs** | Documentation | `pip install mkdocs mkdocs-material` |
| **pdoc3** | API docs | `pip install pdoc3` |
| **commitizen** | Commit message helper | `pip install commitizen` |

### 7.3 GitHub Secrets Configuration

Required secrets in GitHub repository settings:

- `PYPI_API_TOKEN` - PyPI API token for publishing (✅ already configured)
- `TEST_PYPI_API_TOKEN` - TestPyPI token for RC testing (✅ already configured)
- `SLACK_WEBHOOK_URL` - (Optional) Slack notifications
- `DISCORD_WEBHOOK_URL` - (Optional) Discord notifications

---

## 8. Release Process Documentation

### 8.1 Standard Release Process

**For maintainers**:

```bash
# 1. Ensure main branch is clean
git checkout main
git pull origin main

# 2. Run pre-release checklist
python scripts/pre_release_checklist.py

# 3. Bump version (automatic commit and tag)
bump2version patch  # or minor, major

# 4. Push tags to trigger release
git push origin main --tags

# 5. GitHub Actions will:
#    - Run all tests
#    - Build package
#    - Publish to PyPI
#    - Generate changelog
#    - Create GitHub Release
#    - Send notifications
```

### 8.2 Release Candidate Process

**For testing new features**:

```bash
# 1. Trigger RC workflow via GitHub UI
#    Go to Actions → Release Candidate → Run workflow
#    Select: version_type=rc, base_version=1.0.0

# 2. Test RC installation
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  claude-force==1.0.0-rc.1

# 3. Run integration tests
pytest tests/integration/

# 4. If tests pass, promote to release
git tag v1.0.0
git push origin v1.0.0
```

### 8.3 Hotfix Process

**For urgent bug fixes**:

```bash
# 1. Create hotfix branch from tag
git checkout -b hotfix/v1.0.1 v1.0.0

# 2. Fix the bug and commit
git commit -m "fix: critical security vulnerability"

# 3. Bump patch version
bump2version patch

# 4. Merge to main and push tags
git checkout main
git merge hotfix/v1.0.1
git push origin main --tags
```

---

## 9. Success Metrics

### 9.1 Key Performance Indicators

**Before Automation**:
- ⏱️  Release time: ~2-4 hours (manual)
- 🐛 Human errors per release: 2-3
- 📝 Changelog update time: 30-60 minutes
- 🧪 Pre-release validation: Inconsistent

**After Automation**:
- ⏱️  Release time: ~15-30 minutes (automated)
- 🐛 Human errors per release: 0-1
- 📝 Changelog update time: < 5 minutes (automated)
- 🧪 Pre-release validation: 100% consistent

### 9.2 Quality Metrics

- **Test coverage**: Maintain 100% (currently achieved)
- **Release success rate**: > 95%
- **Rollback rate**: < 5%
- **Time to fix failed release**: < 30 minutes

### 9.3 Team Productivity

- **Time saved per release**: ~2-3 hours
- **Developer focus time**: Increased (less manual work)
- **Release frequency**: Can increase to weekly/bi-weekly
- **Confidence in releases**: Higher due to automated checks

---

## 10. Risk Mitigation

### 10.1 Identified Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| PyPI publish failure | HIGH | LOW | Retry logic, manual fallback |
| Version conflict | MEDIUM | MEDIUM | Automated consistency checks |
| Broken changelog | LOW | LOW | Template validation |
| Failed quality gates | MEDIUM | LOW | Clear error messages, documentation |
| GitHub Actions quota | LOW | VERY LOW | Optimize workflow triggers |

### 10.2 Rollback Plan

**If release fails**:

1. **Immediately**: Trigger manual rollback workflow
2. **Within 15 minutes**: Publish previous stable version to PyPI
3. **Within 30 minutes**: Create hotfix if needed
4. **Within 1 hour**: Post-mortem and fix automation

**Rollback workflow** (`.github/workflows/rollback.yml`):
```yaml
name: Emergency Rollback

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to'
        required: true
        type: string

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: v${{ github.event.inputs.version }}

      - name: Re-publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          skip-existing: true

      - name: Notify team
        run: |
          echo "⚠️  Rolled back to v${{ github.event.inputs.version }}"
```

---

## 11. Future Enhancements

### 11.1 Advanced Features (Post v1.0)

- **Automated security scanning**: Integrate Snyk or Dependabot
- **Performance regression testing**: Track performance metrics across releases
- **Multi-platform testing**: Add Windows and macOS CI runners
- **Docker image releases**: Publish Docker images to GHCR/Docker Hub
- **Release analytics**: Track download stats, usage metrics
- **Automated upgrade guides**: Generate migration guides for breaking changes

### 11.2 Integration Opportunities

- **IDE integration**: VS Code extension for release management
- **Slack bot**: Interactive release commands
- **Release dashboard**: Web UI for release status
- **Automated blog posts**: Generate release announcements

---

## 12. Conclusion

This release automation plan provides a comprehensive roadmap for modernizing the `claude-force` package release process. By implementing these improvements incrementally over 3-4 weeks, we can achieve:

✅ **Faster releases** - From hours to minutes
✅ **Higher quality** - Automated validation and testing
✅ **Better documentation** - Auto-generated changelogs and release notes
✅ **Increased confidence** - Consistent, repeatable process
✅ **Team productivity** - More time for development, less for releases

### Next Steps

1. **Review this plan** with the team
2. **Prioritize phases** based on immediate needs
3. **Assign ownership** for each phase
4. **Set timeline** for implementation
5. **Begin Phase 1** - Foundation setup

---

## Appendix

### A. Commit Message Examples

**Good examples**:
```
feat(agents): add kubernetes-engineer agent with Helm support
fix(orchestrator): resolve race condition in parallel workflow execution
docs(readme): update installation instructions for Python 3.12
perf(cache): implement LRU cache for agent definitions (30% speedup)
BREAKING CHANGE: remove deprecated HybridOrchestrator.run() method
```

**Bad examples**:
```
update code          # Too vague
fixed bug           # No context
WIP                # Work in progress (shouldn't be in main)
asdf               # Meaningless
```

### B. Version Bump Decision Tree

```
Is this a breaking change?
├─ YES → MAJOR version (X.0.0)
└─ NO → Is this a new feature?
    ├─ YES → MINOR version (0.X.0)
    └─ NO → Is this a bug fix?
        ├─ YES → PATCH version (0.0.X)
        └─ NO → PATCH version (docs, chore, etc.)
```

### C. Resources

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Python Packaging Guide](https://packaging.python.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Author**: Claude Code
**Status**: Draft for Review
