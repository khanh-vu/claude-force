# Test Suite Implementation Plan

**Goal**: Achieve production-ready test coverage (95%+) with 100% pass rate

**Timeline**: 2-3 weeks
**Current Status**: 73 tests, 89% pass rate, ~70% coverage

---

## 🎯 Phase 1: Fix Existing Failures (Week 1, Days 1-2)

### Objective
Get all 73 existing tests to 100% pass rate

### Tasks

#### Task 1.1: Fix Skills Manager Empty File Handling
**Priority**: HIGH
**Time**: 2 hours
**Files**: `claude_force/skills_manager.py`

**Issue**: Empty skill files return `None` instead of empty string

**Fix**:
```python
# In _load_skill_file method
if skill_file.exists():
    try:
        content = skill_file.read_text()
        # Return content even if empty - this is valid!
        return content if content is not None else ""
    except Exception as e:
        logger.error(f"Failed to load skill {skill_id}: {e}")
        return None
```

**Tests Fixed**: 3 (test_empty_skill_file, test_skill_file_with_only_comments, test_very_large_skill_file)

#### Task 1.2: Improve Template Validation Error Messages
**Priority**: MEDIUM
**Time**: 1 hour
**Files**: `claude_force/quick_start.py`

**Issue**: Error messages don't mention "required" fields

**Fix**:
```python
class TemplateValidationError(ValueError):
    """Raised when template is missing required fields."""
    pass

# In template loading:
required_fields = ['id', 'name', 'description', 'agents', 'workflows', 'skills', 'keywords']
for field in required_fields:
    if field not in template:
        raise TemplateValidationError(
            f"Template missing required field: '{field}'. "
            f"Found fields: {list(template.keys())}"
        )
```

**Tests Fixed**: 1 (test_template_with_missing_required_fields)

#### Task 1.3: Update Test Expectations
**Priority**: LOW
**Time**: 30 minutes
**Files**: `tests/test_error_handling.py`

**Issue**: Some tests have incorrect expectations

**Fix**: Update tests to match actual (correct) behavior

**Tests Fixed**: 2 (permission tests - OS-dependent)

**Verification**:
```bash
python -m unittest tests.test_error_handling -v
# Expected: 22/22 passing
```

---

## 🚀 Phase 2: CLI Integration Tests (Week 1, Days 3-5)

### Objective
Test all CLI commands and argument combinations

### Tasks

#### Task 2.1: Create CLI Test Infrastructure
**Priority**: HIGH
**Time**: 3 hours
**Files**: `tests/test_cli_integration.py` (new)

**Features**:
- Subprocess testing for actual CLI invocation
- Capture stdout/stderr
- Test exit codes
- Test help messages

**Implementation**:
```python
import subprocess
import sys

class CLITestCase(unittest.TestCase):
    """Base class for CLI tests."""

    def run_cli(self, *args, input_text=None):
        """Run claude-force CLI command."""
        cmd = [sys.executable, "-m", "claude_force.cli"] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=input_text,
            timeout=30
        )
        return result

    def assertExitCode(self, result, expected_code):
        """Assert CLI exit code."""
        self.assertEqual(
            result.returncode,
            expected_code,
            f"Expected exit code {expected_code}, got {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
```

#### Task 2.2: Test `claude-force init` Command
**Priority**: HIGH
**Time**: 4 hours
**Files**: `tests/test_cli_integration.py`

**Tests to Add**:
1. ✅ `test_init_help` - Test --help flag
2. ✅ `test_init_non_interactive_success` - Test with --description
3. ✅ `test_init_interactive_mode` - Test with --interactive
4. ✅ `test_init_with_template` - Test --template flag
5. ✅ `test_init_force_overwrite` - Test --force flag
6. ✅ `test_init_no_examples` - Test --no-examples
7. ✅ `test_init_missing_description` - Test error when description missing
8. ✅ `test_init_invalid_template` - Test error with invalid template ID
9. ✅ `test_init_existing_directory` - Test error when .claude exists
10. ✅ `test_init_verbose_errors` - Test --verbose flag

**Sample Test**:
```python
def test_init_non_interactive_success(self):
    """Test claude-force init with non-interactive mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = self.run_cli(
            "init",
            tmpdir,
            "--description", "Test LLM application",
            "--name", "test-project"
        )

        self.assertExitCode(result, 0)
        self.assertIn("✅ Project initialized successfully", result.stdout)
        self.assertTrue((Path(tmpdir) / ".claude" / "claude.json").exists())
```

#### Task 2.3: Test `claude-force run agent` Command
**Priority**: HIGH
**Time**: 4 hours
**Files**: `tests/test_cli_integration.py`

**Tests to Add**:
1. ✅ `test_run_agent_help` - Test --help
2. ✅ `test_run_agent_with_auto_select` - Test --auto-select-model
3. ✅ `test_run_agent_with_estimate` - Test --estimate-cost
4. ✅ `test_run_agent_with_threshold` - Test --cost-threshold
5. ✅ `test_run_agent_yes_flag` - Test --yes flag
6. ✅ `test_run_agent_missing_task` - Test error when no task
7. ✅ `test_run_agent_task_file` - Test --task-file
8. ✅ `test_run_agent_output_file` - Test --output flag
9. ✅ `test_run_agent_json_output` - Test --json flag
10. ✅ `test_run_agent_invalid_agent` - Test error with unknown agent

**Verification**:
```bash
python -m unittest tests.test_cli_integration -v
# Expected: 20/20 passing (10 init + 10 run agent)
```

---

## 🔗 Phase 3: Integration Tests (Week 2, Days 1-3)

### Objective
Test feature interactions and end-to-end workflows

### Tasks

#### Task 3.1: Quick Start + Hybrid Integration
**Priority**: HIGH
**Time**: 3 hours
**Files**: `tests/test_feature_integration.py` (new)

**Tests to Add**:
1. ✅ `test_init_then_run_with_hybrid` - Full workflow
2. ✅ `test_init_then_cost_estimate` - Init → estimate
3. ✅ `test_template_to_execution` - Template selection → agent run

#### Task 3.2: Hybrid + Skills Integration
**Priority**: HIGH
**Time**: 3 hours
**Files**: `tests/test_feature_integration.py`

**Tests to Add**:
1. ✅ `test_hybrid_with_progressive_skills` - Combined optimizations
2. ✅ `test_cost_savings_measurement` - Measure actual savings
3. ✅ `test_token_reduction_measurement` - Measure token reduction

#### Task 3.3: Full Pipeline Integration
**Priority**: MEDIUM
**Time**: 4 hours
**Files**: `tests/test_feature_integration.py`

**Tests to Add**:
1. ✅ `test_complete_project_lifecycle` - Init → recommend → run → validate
2. ✅ `test_multi_agent_workflow` - Run multiple agents in sequence
3. ✅ `test_error_recovery` - Test graceful degradation
4. ✅ `test_configuration_persistence` - Verify configs persist correctly

**Verification**:
```bash
python -m unittest tests.test_feature_integration -v
# Expected: 10/10 passing
```

---

## ⚡ Phase 4: Performance & Validation (Week 2, Days 4-5)

### Objective
Ensure performance targets and data integrity

### Tasks

#### Task 4.1: Performance Benchmarks
**Priority**: MEDIUM
**Time**: 4 hours
**Files**: `tests/test_performance.py` (new)

**Tests to Add**:
1. ✅ `test_template_matching_performance` - < 50ms for 100 templates
2. ✅ `test_skill_loading_performance` - < 20ms for 11 skills (cached)
3. ✅ `test_cost_estimation_performance` - < 5ms
4. ✅ `test_project_init_performance` - < 500ms
5. ✅ `test_cache_effectiveness` - Cache hit rate > 80%
6. ✅ `test_memory_usage` - Memory < 100MB
7. ✅ `test_concurrent_operations` - 10 concurrent runs
8. ✅ `test_large_scale_operations` - 1000 templates

**Implementation**:
```python
import time
import tracemalloc

class TestPerformance(unittest.TestCase):

    def test_template_matching_performance(self):
        """Template matching should be < 50ms for 100 templates."""
        orchestrator = get_quick_start_orchestrator(use_semantic=False)

        # Warm up
        orchestrator.match_templates("test", top_k=3)

        # Benchmark
        start = time.perf_counter()
        result = orchestrator.match_templates("Build a web app", top_k=3)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        self.assertLess(elapsed, 50, f"Template matching took {elapsed:.2f}ms")
```

#### Task 4.2: Validation Tests
**Priority**: MEDIUM
**Time**: 3 hours
**Files**: `tests/test_validation.py` (new)

**Tests to Add**:
1. ✅ `test_claude_json_is_valid_json` - Parse check
2. ✅ `test_task_md_is_valid_markdown` - Markdown validation
3. ✅ `test_readme_md_is_valid_markdown` - Markdown validation
4. ✅ `test_scorecard_md_is_valid_markdown` - Markdown validation
5. ✅ `test_file_permissions_correct` - 644 for files, 755 for dirs
6. ✅ `test_directory_structure_complete` - All dirs created
7. ✅ `test_no_data_loss` - Data integrity check
8. ✅ `test_atomic_operations` - Rollback on error
9. ✅ `test_generated_files_parseable` - All files can be read back
10. ✅ `test_cross_references_valid` - Agent/workflow refs are valid

**Verification**:
```bash
python -m unittest tests.test_performance -v
python -m unittest tests.test_validation -v
# Expected: 18/18 passing (8 perf + 10 validation)
```

---

## 🌐 Phase 5: Cross-Platform Tests (Week 3, Optional)

### Objective
Ensure compatibility across Windows, macOS, Linux

### Tasks

#### Task 5.1: Cross-Platform Compatibility
**Priority**: LOW
**Time**: 6 hours
**Files**: `tests/test_cross_platform.py` (new)

**Tests to Add**:
1. ✅ `test_windows_path_separators` - Backslash handling
2. ✅ `test_windows_line_endings` - CRLF handling
3. ✅ `test_macos_unicode_filenames` - Unicode path handling
4. ✅ `test_linux_permissions` - chmod 644/755
5. ✅ `test_symlink_handling` - Follow vs don't follow
6. ✅ `test_case_sensitivity` - Case-sensitive filesystems
7. ✅ `test_long_paths` - Windows 260 char limit
8. ✅ `test_special_characters` - OS-specific restrictions
9. ✅ `test_temp_dir_locations` - Different temp dir paths
10. ✅ `test_concurrent_file_access` - File locking behavior

**Note**: These tests should use platform detection:
```python
import platform
import sys

@unittest.skipIf(sys.platform != 'win32', "Windows-specific test")
def test_windows_path_separators(self):
    ...

@unittest.skipIf(platform.system() != 'Darwin', "macOS-specific test")
def test_macos_unicode_filenames(self):
    ...
```

---

## 📊 Progress Tracking

### Test Count Targets

| Phase | Duration | New Tests | Cumulative | Pass Rate Target |
|-------|----------|-----------|------------|------------------|
| **Current** | - | 73 | 73 | 89% |
| **Phase 1** | 2 days | +0 | 73 | 100% ✅ |
| **Phase 2** | 3 days | +20 | 93 | 100% |
| **Phase 3** | 3 days | +10 | 103 | 100% |
| **Phase 4** | 2 days | +18 | 121 | 100% |
| **Phase 5** | 3 days | +10 | 131 | 100% |

### Coverage Targets

| Module | Current | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Final |
|--------|---------|---------|---------|---------|---------|-------|
| quick_start.py | 75% | 80% | 85% | 90% | 95% | 95% |
| hybrid_orchestrator.py | 85% | 90% | 90% | 95% | 95% | 95% |
| skills_manager.py | 80% | 85% | 85% | 90% | 95% | 95% |
| cli.py | 0% | 0% | 80% | 85% | 90% | 90% |
| orchestrator.py | 0% | 0% | 0% | 70% | 80% | 80% |
| **Overall** | ~70% | ~75% | ~85% | ~90% | ~95% | **95%** |

---

## ✅ Definition of Done

### Per Phase

Each phase is complete when:
1. ✅ All new tests written and passing
2. ✅ All existing tests still passing
3. ✅ Code coverage meets phase target
4. ✅ Documentation updated
5. ✅ Code reviewed
6. ✅ Committed to version control

### Overall Project

Project is production-ready when:
1. ✅ 131+ tests, 100% passing
2. ✅ 95%+ line coverage
3. ✅ 90%+ branch coverage
4. ✅ All performance targets met
5. ✅ CI/CD pipeline green
6. ✅ Cross-platform tests passing
7. ✅ Documentation complete
8. ✅ Security review passed

---

## 🚨 Risk Mitigation

### Known Risks

1. **Platform Differences**
   - Mitigation: Use `pathlib` everywhere, test on all platforms
   - Contingency: Platform-specific code paths

2. **Performance Degradation**
   - Mitigation: Benchmark early and often
   - Contingency: Optimize hotspots, add caching

3. **Test Flakiness**
   - Mitigation: Use deterministic mocks, avoid timing dependencies
   - Contingency: Retry logic, better isolation

4. **CI/CD Failures**
   - Mitigation: Test locally first, incremental rollout
   - Contingency: Quick rollback, feature flags

---

## 📝 Daily Checklist

### Each Development Day

- [ ] Run full test suite before starting work
- [ ] Write tests first (TDD when possible)
- [ ] Ensure tests pass locally before committing
- [ ] Check coverage hasn't decreased
- [ ] Update documentation if needed
- [ ] Run linter and formatter
- [ ] Commit with descriptive message
- [ ] Push to CI/CD for validation

### Each Phase Completion

- [ ] Run full test suite
- [ ] Generate coverage report
- [ ] Review test quality
- [ ] Update progress tracking
- [ ] Document any issues or tech debt
- [ ] Plan next phase
- [ ] Celebrate progress! 🎉

---

## 📚 Resources

### Testing Tools

- **unittest**: Standard library (currently using)
- **pytest**: Consider migrating for better features
- **coverage.py**: Code coverage measurement
- **tox**: Multi-environment testing
- **hypothesis**: Property-based testing

### CI/CD

- **GitHub Actions**: Recommended for open source
- **pre-commit**: Git hooks for quality checks
- **codecov.io**: Coverage reporting and tracking

### Best Practices

- **Arrange-Act-Assert**: Clear test structure
- **FIRST Principles**: Fast, Isolated, Repeatable, Self-validating, Timely
- **Test Pyramid**: Many unit tests, fewer integration, fewest E2E
- **DRY**: Don't repeat test code, use fixtures and helpers

---

**Last Updated**: 2025-11-14
**Status**: Ready for implementation
**Next Review**: After Phase 1 completion
