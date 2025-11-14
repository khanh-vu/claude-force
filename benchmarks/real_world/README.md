# Real-World Benchmarks for Claude-Force

Comprehensive benchmarking system that measures agent effectiveness in real-world scenarios by tracking actual code quality, security, and test coverage improvements.

## Overview

This benchmark system measures:
- **Code Quality**: Pylint scores and violation counts
- **Security**: Bandit findings by severity level
- **Test Coverage**: Percentage of code covered by tests
- **Performance**: Agent execution time and success rates

## Quick Start

### Prerequisites

Install quality measurement tools:
```bash
pip install pylint bandit coverage
```

### Running Benchmarks

**Demo Mode** (no API key required):
```bash
python benchmark_runner.py \
  --demo \
  --scenario code_review_test \
  --agent code-reviewer \
  --baseline baselines/sample_code_with_issues.py \
  --task "Review this code for security and quality issues"
```

**Real Mode** (requires ANTHROPIC_API_KEY):
```bash
export ANTHROPIC_API_KEY="your-api-key"

python benchmark_runner.py \
  --scenario code_review_test \
  --agent code-reviewer \
  --baseline baselines/sample_code_with_issues.py \
  --task "Review this code for security and quality issues" \
  --report reports/benchmark_$(date +%Y%m%d_%H%M%S).json
```

## Directory Structure

```
benchmarks/real_world/
├── benchmark_runner.py      # Main benchmark runner
├── scenarios/               # Test scenarios (code samples)
├── baselines/               # Baseline code with known issues
├── reports/                 # Generated benchmark reports
└── README.md               # This file
```

## Benchmark Metrics

### Quality Metrics

**Pylint Score** (0-10):
- Measures code quality based on PEP 8 compliance
- Higher score = better code quality
- Tracks violation count and types

**Bandit Security Score**:
- Detects security vulnerabilities
- Categorizes by severity: HIGH, MEDIUM, LOW
- Tracks total issues found

**Test Coverage** (0-100%):
- Percentage of code covered by tests
- Measured using coverage.py
- Higher coverage = better testing

### Performance Metrics

- **Execution Time**: Time for agent to complete task
- **Success Rate**: Percentage of successful runs
- **Improvement Percentage**: Relative improvement from baseline

## Example Output

```
================================================================================
CLAUDE-FORCE REAL-WORLD BENCHMARKS
================================================================================

Timestamp: 2025-11-14T10:42:17.912306
Total Benchmarks: 1
Successful: 1
Failed: 0
Mode: DEMO (simulated)

================================================================================
RESULTS BY SCENARIO
================================================================================

Scenario: code_review_test
Agent: code-reviewer
Status: ✅ SUCCESS
Execution Time: 1156.53ms

Baseline Metrics:
  Pylint Score: 5.00/10
  Pylint Violations: 12
  Security Issues: 6 (3 HIGH, 2 MEDIUM, 1 LOW)
  Test Coverage: 0.0%

Improved Metrics:
  Pylint Score: 8.50/10
  Pylint Violations: 2
  Security Issues: 0
  Test Coverage: 85.0%

Improvements:
  pylint_score: +70.0%
  pylint_violations: -83.3%
  security_issues: -100.0%
  test_coverage: +85.0%
```

## Creating Custom Benchmarks

### 1. Create Baseline Code

Add a Python file to `baselines/` with intentional issues:

```python
# baselines/my_code.py
def process_data(user_input):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"

    # Bare except
    try:
        result = execute_query(query)
    except:
        pass

    return result
```

### 2. Run Benchmark

```bash
python benchmark_runner.py \
  --scenario my_scenario \
  --agent code-reviewer \
  --baseline baselines/my_code.py \
  --task "Review and fix security issues"
```

### 3. Analyze Results

The runner will:
1. Measure baseline metrics (Pylint, Bandit, coverage)
2. Run the specified agent
3. Measure improved metrics
4. Calculate improvement percentages
5. Generate report

## Baseline Code Samples

### sample_code_with_issues.py

Comprehensive test file with multiple issue types:
- SQL injection vulnerability
- Hardcoded credentials
- Unsafe use of eval()
- Pickle loading untrusted data
- Poor error handling
- Code style violations
- Complex nested logic

Perfect for testing code review and security agents.

## Command-Line Options

```
python benchmark_runner.py [options]

Required (choose one):
  --scenario NAME            Run single scenario
  --all                      Run all predefined scenarios

Options:
  --agent NAME               Agent to benchmark (default: code-reviewer)
  --baseline PATH            Path to baseline code file
  --task TEXT                Task description for agent
  --report PATH              Save JSON report to file
  --config PATH              Path to claude.json (default: .claude/claude.json)
  --demo                     Run in demo mode (no API key required)
```

## Interpreting Results

### Success Criteria

A successful benchmark shows:
- ✅ Execution completed without errors
- ✅ Positive improvement in quality metrics
- ✅ Reduction in security issues
- ✅ Increased test coverage

### Improvement Thresholds

- **Excellent**: >50% improvement in all metrics
- **Good**: 20-50% improvement
- **Moderate**: 5-20% improvement
- **Minimal**: <5% improvement

### Performance Targets

- **Execution Time**: <5 seconds for typical code review
- **Success Rate**: >90% across multiple runs
- **Quality Improvement**: >30% average

## Continuous Integration

Add benchmarks to CI/CD pipeline:

```yaml
# .github/workflows/benchmark.yml
name: Benchmarks

on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pylint bandit coverage

      - name: Run benchmarks
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python benchmarks/real_world/benchmark_runner.py \
            --scenario code_review_test \
            --agent code-reviewer \
            --baseline benchmarks/real_world/baselines/sample_code_with_issues.py \
            --report benchmarks/real_world/reports/ci_benchmark.json

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: benchmarks/real_world/reports/
```

## Future Enhancements

Planned improvements:
- [ ] Multiple agent comparison
- [ ] Historical trend tracking
- [ ] Automated scenario generation
- [ ] Code extraction from agent output
- [ ] Performance regression detection
- [ ] Integration with code review tools

## Troubleshooting

### Pylint/Bandit Not Found

Install quality tools:
```bash
pip install pylint bandit coverage
```

### Import Errors

Ensure claude-force is in PYTHONPATH:
```bash
export PYTHONPATH=/path/to/claude-force:$PYTHONPATH
```

### API Key Issues

For demo mode (no API calls):
```bash
python benchmark_runner.py --demo ...
```

For real mode, set environment variable:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/khanh-vu/claude-force/issues
- Documentation: https://github.com/khanh-vu/claude-force
