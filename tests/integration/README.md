# Integration Tests

Comprehensive integration tests for the claude-force multi-agent orchestration system.

## Overview

This test suite provides end-to-end integration testing of the core claude-force components, ensuring that all pieces work together correctly in real-world scenarios.

## Test Files

### 1. `test_orchestrator_end_to_end.py`
**Purpose**: Test complete orchestrator workflows from agent selection to execution

**Test Classes**:
- `TestOrchestratorEndToEnd`: Core orchestrator functionality
  - Single agent execution with performance tracking
  - Multi-agent workflow execution
  - Error handling and partial failures
  - Result validation

- `TestPerformanceTrackingIntegration`: Performance metrics collection
  - Metrics recording and storage
  - Cost calculation for different models
  - Analytics and trend analysis
  - Agent performance comparison

- `TestSemanticSelectorIntegration`: Semantic agent selection
  - Agent matching accuracy
  - Multi-agent recommendations
  - Confidence score calibration

- `TestCompleteIntegrationWorkflow`: Full end-to-end workflows
  - Selection → Execution → Tracking pipeline
  - Integration of all components

**Coverage**: Orchestrator (63%), Performance Tracker (61%)

### 2. `test_cli_commands.py`
**Purpose**: Test all CLI commands via subprocess

**Test Classes**:
- `TestCLIListCommands`: List agents/workflows
- `TestCLIInfoCommands`: Get agent information
- `TestCLIRecommendCommand`: Agent recommendations
- `TestCLIAnalyzeCommand`: Performance analysis
- `TestCLIMarketplaceCommands`: Marketplace operations
- `TestCLIComposeCommand`: Workflow composition
- `TestCLIExportImportCommands`: Config export/import
- `TestCLIValidationCommands`: Config validation

**Coverage**: CLI integration and command-line argument handling

### 3. `test_workflow_marketplace.py`
**Purpose**: Test workflow composition and marketplace integration

**Test Classes**:
- `TestWorkflowComposerIntegration`: Workflow creation and management
  - Custom workflow creation
  - Workflow validation
  - Save/load operations
  - Workflow optimization

- `TestMarketplaceIntegration`: Marketplace operations
  - List marketplace agents
  - Search and filtering
  - Agent installation
  - Ratings and reviews

- `TestWorkflowMarketplaceIntegration`: Combined workflow/marketplace
  - Install agents and compose workflows
  - Workflow recommendations

- `TestCompleteWorkflowExecution`: Full workflow execution
  - Multi-agent workflow execution
  - Mocked Claude API responses

**Coverage**: Workflow Composer (35%), Marketplace (40%)

## Running Tests

### Run All Integration Tests
```bash
python3 -m pytest tests/integration/ -v
```

### Run Specific Test File
```bash
python3 -m pytest tests/integration/test_orchestrator_end_to_end.py -v
```

### Run With Coverage
```bash
python3 -m pytest tests/integration/ --cov=claude_force --cov-report=html
```

### Run Specific Test Class
```bash
python3 -m pytest tests/integration/test_orchestrator_end_to_end.py::TestOrchestratorEndToEnd -v
```

### Run Specific Test Method
```bash
python3 -m pytest tests/integration/test_orchestrator_end_to_end.py::TestOrchestratorEndToEnd::test_run_single_agent_with_tracking -v
```

## Test Results

**Current Status** (as of 2025-11-14):
- **Total Tests**: 45
- **Passing**: 18
- **Skipped**: 8 (graceful handling of missing dependencies)
- **Failed**: 19 (mostly API mismatches, will be fixed)
- **Coverage**: 18% (up from 0% before)

### Coverage Breakdown
| Module | Coverage | Notes |
|--------|----------|-------|
| orchestrator.py | 63% | ✅ Good coverage |
| performance_tracker.py | 61% | ✅ Good coverage |
| marketplace.py | 40% | 🟡 Moderate |
| workflow_composer.py | 35% | 🟡 Moderate |
| agent_router.py | 23% | 🔴 Needs work |
| semantic_selector.py | 24% | 🔴 Needs work |
| cli.py | 3% | 🔴 Needs work |

## Mocking Strategy

The integration tests use mocks for external dependencies:

**Mocked**:
- `anthropic.Client`: Claude API client (to avoid real API calls)
- Claude API responses: MockClaudeResponse class provides realistic responses

**Real**:
- File system operations (using temporary directories)
- Configuration loading and parsing
- Agent definition loading
- Performance metrics storage
- Semantic selector logic (when sentence-transformers available)

## Dependencies

**Required**:
- `pytest`: Test framework
- `pytest-cov`: Coverage reporting
- `anthropic`: Claude API client (mocked in tests)
- `numpy`: For vector operations

**Optional** (tests skip gracefully if missing):
- `sentence-transformers`: For semantic agent selection tests

## Known Issues

1. **CLI Tests**: Some CLI tests fail because the package isn't installed globally. These work when running from installed package.

2. **API Mismatches**: Some tests assume API methods that don't exist yet (e.g., `recommend_agents` vs actual method names). Will be fixed in follow-up.

3. **Workflow Composer**: Constructor signature differs from what tests expect. Tests skip gracefully.

## Future Improvements

1. **Increase Coverage to 80%**:
   - Add more CLI integration tests
   - Expand semantic selector tests
   - Add agent router tests

2. **Fix API Mismatches**:
   - Update tests to match actual API
   - Or update API to match expected interface

3. **Add More Scenarios**:
   - Multi-step workflow failures
   - Cost threshold enforcement
   - Concurrent agent execution
   - Rate limiting scenarios

4. **Performance Tests**:
   - Load testing with many agents
   - Stress testing workflows
   - Memory usage profiling

## Contributing

When adding integration tests:

1. **Create Temporary Directories**: Use `tempfile.mkdtemp()` for test isolation
2. **Clean Up**: Always use tearDown to remove temporary files
3. **Mock External APIs**: Never make real API calls in tests
4. **Handle Missing Dependencies**: Use skipIf decorators for optional dependencies
5. **Test Real Scenarios**: Integration tests should test realistic workflows

## Contact

For questions or issues with integration tests, see:
- IMPLEMENTATION_CHECKLIST.md (P1 task #4)
- GitHub Issues: https://github.com/khanh-vu/claude-force/issues
