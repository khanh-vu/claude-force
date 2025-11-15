# Release Automation Scripts

This directory contains automation scripts for the claude-force release process.

## Scripts

### check_version_consistency.py

**Purpose**: Verify version consistency across all project files.

**Usage**:
```bash
python3 scripts/check_version_consistency.py
```

**What it checks**:
- `pyproject.toml` - project version
- `setup.py` - package version
- `claude_force/__init__.py` - `__version__` attribute
- `README.md` - version badge

**Exit codes**:
- `0` - All versions are consistent
- `1` - Version mismatch detected or missing version

**Example output**:
```
======================================================================
Version Consistency Check
======================================================================

Versions found:
  ✓ pyproject.toml                 → 2.2.0
  ✓ setup.py                       → 2.2.0
  ✓ claude_force/__init__.py       → 2.2.0
  ✓ README.md                      → 2.2.0

✅ All versions are consistent: 2.2.0
======================================================================
```

---

### pre_release_checklist.py

**Purpose**: Run comprehensive pre-release validation checks.

**Usage**:
```bash
python3 scripts/pre_release_checklist.py
```

**What it checks**:
1. ✅ Version consistency across all files
2. ✅ All system tests pass
3. ✅ Unit tests pass (optional if API keys not available)
4. ✅ Code is formatted with Black
5. ✅ No security vulnerabilities (Bandit)
6. ✅ Package builds successfully

**Exit codes**:
- `0` - All required checks passed, ready for release
- `1` - Some required checks failed
- `130` - Interrupted by user (Ctrl+C)

**Requirements**:
```bash
pip install pytest black bandit build
```

**Example output**:
```
🚀 Pre-release Checklist for claude-force
======================================================================

Checking required tools...

[1/6] Running: Version consistency
----------------------------------------------------------------------
✅ Version consistency: PASSED

[2/6] Running: System tests
----------------------------------------------------------------------
✅ System tests: PASSED

...

📊 Summary
======================================================================
✅ PASS - Version consistency [REQUIRED]
✅ PASS - System tests [REQUIRED]
⚠️  SKIP - Unit tests [OPTIONAL]
✅ PASS - Code formatting (black) [REQUIRED]
✅ PASS - Security scan (bandit) [REQUIRED]
✅ PASS - Package build test [REQUIRED]

Required checks: 5/5 passed
Optional checks: 0/1 passed

======================================================================
✅ All required checks passed! Ready for release.
======================================================================
```

**Notes**:
- Automatically installs missing tools
- Color-coded output for easy scanning
- Cleans up temporary build artifacts
- Can be interrupted with Ctrl+C

---

## Integration with Release Process

These scripts are integrated into the release workflow:

### Manual Release

```bash
# 1. Run pre-release checklist
python3 scripts/pre_release_checklist.py

# 2. If all checks pass, bump version
bump2version patch  # or minor, major

# 3. Push tags to trigger release
git push origin main --tags
```

### CI/CD Integration

These scripts are used in GitHub Actions workflows:

**`.github/workflows/release.yml`**:
```yaml
- name: Verify version consistency
  run: python3 scripts/check_version_consistency.py

- name: Run pre-release checks
  run: python3 scripts/pre_release_checklist.py
```

---

## Development

### Adding New Checks

To add a new check to `pre_release_checklist.py`:

1. Add to the `CHECKS` list:
```python
CHECKS = [
    # ... existing checks ...
    {
        "name": "My new check",
        "command": ["my-command", "args"],
        "required": True,  # or False for optional
    },
]
```

2. Test the check:
```bash
python3 scripts/pre_release_checklist.py
```

### Testing Scripts

Test each script independently:

```bash
# Test version consistency checker
python3 scripts/check_version_consistency.py

# Test pre-release checklist
python3 scripts/pre_release_checklist.py

# Test in CI environment (without colors)
NO_COLOR=1 python3 scripts/pre_release_checklist.py
```

---

## Troubleshooting

### Version Mismatch Error

```bash
❌ Version mismatch detected!
   Found 2 different versions:
   • 2.1.0 in: pyproject.toml
   • 2.2.0 in: setup.py, README.md
```

**Solution**: Update all files to the same version or use `bump2version` to update automatically.

### Missing Tools

```bash
⚠️  Missing tools: pytest, black, bandit
Installing with pip...
```

**Solution**: The script auto-installs missing tools, or install manually:
```bash
pip install pytest black bandit build
```

### Tests Failing

If pre-release checks fail, review the output and fix the issues:

```bash
# Run specific checks individually
pytest test_claude_system.py -v
black --check claude_force/
bandit -r claude_force/ -ll
python -m build
```

---

## See Also

- [RELEASE_AUTOMATION_PLAN.md](../RELEASE_AUTOMATION_PLAN.md) - Complete release automation plan
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Release process for maintainers
- [.bumpversion.cfg](../.bumpversion.cfg) - Version bumping configuration
- [cliff.toml](../cliff.toml) - Changelog generation configuration
