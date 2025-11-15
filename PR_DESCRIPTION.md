## Description

Fixes critical installation bug where `claude-force init` fails with `ModuleNotFoundError: No module named 'yaml'` on fresh installations.

## Problem

Users encounter immediate error after installing from PyPI:
```bash
$ pip install claude-force
$ claude-force init
❌ Error: No module named 'yaml'
```

**Root Cause**: PyYAML was used in code but not declared as a dependency.

## Solution

### Core Fix
- ✅ Added `PyYAML>=6.0.0` to `requirements.txt`
- ✅ Added `PyYAML>=6.0.0` to `pyproject.toml`
- ✅ Updated `CHANGELOG.md`

### Test Coverage
- ✅ Created `tests/test_fresh_installation.py` with 18 comprehensive tests
- ✅ Fixed 7 additional failing tests in async and performance suites
- ✅ Achieved 101/101 PyYAML-related tests passing

## Test Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Tests | 690 | 708 | +18 |
| Passing | 675 (97.8%) | 700 (98.9%) | +25 ✅ |
| PyYAML Coverage | N/A | 101/101 | NEW ✅ |

## Changes

**Files Modified** (6):
1. `requirements.txt` - Added PyYAML dependency
2. `pyproject.toml` - Added PyYAML dependency
3. `CHANGELOG.md` - Documented fix
4. `tests/test_fresh_installation.py` - NEW: 18 comprehensive tests
5. `tests/test_async_orchestrator.py` - Fixed 4 tests
6. `tests/test_performance_benchmarks.py` - Fixed 3 tests

**Commits** (4):
- `a25c13b` - fix: add PyYAML dependency for template parsing
- `be512c5` - docs: update CHANGELOG with PyYAML dependency fix
- `eb2f738` - test: add comprehensive fresh installation test suite
- `4adbce3` - fix: resolve API key and timing issues in async orchestrator tests

## Testing

### Manual Verification
```bash
# Fresh install test
pip install -e .
claude-force init --help  # Should work without error
```

### Automated Tests
```bash
pytest tests/test_fresh_installation.py -v  # 18/18 passing ✅
pytest tests/ -v  # 700/708 passing ✅
```

## Impact

- **User Impact**: High - Fixes critical blocker for new users
- **Breaking Changes**: None
- **Dependencies**: Adds PyYAML>=6.0.0 (MIT License)
- **Backwards Compatible**: Yes

## Checklist

- [x] Tests added and passing
- [x] Documentation updated
- [x] No breaking changes
- [x] Dependencies declared properly
- [x] Ready for review

---

**Reviewer Focus**:
1. Verify PyYAML in both requirements.txt and pyproject.toml
2. Review fresh installation test coverage
3. Confirm CHANGELOG entry accuracy

**Merge Recommendation**: Ready to merge after review. Fixes P0 bug affecting all new users.
