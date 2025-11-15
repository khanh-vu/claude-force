# Release Metrics

This directory contains historical snapshots of release automation metrics.

## 📊 What's Here

### Current Metrics

The latest metrics are always available in the root directory:
- [`../../RELEASE_METRICS.md`](../../RELEASE_METRICS.md) - Current metrics report

### Historical Snapshots

This directory stores timestamped snapshots:
- `metrics_YYYYMMDD_HHMMSS.md` - Point-in-time metrics reports

### Purpose

**Trend Analysis**: Compare metrics over time to identify improvements or regressions

**Performance Tracking**: Monitor automation system health and effectiveness

**Reporting**: Historical data for team reviews and retrospectives

## 🔄 How It Updates

Metrics are automatically collected and stored:

1. **Automatic**: After each release workflow completes
2. **Manual**: Run "Release Metrics" workflow anytime
3. **Scheduled**: Can be configured for periodic reports

## 📈 Using the Data

### View Current Status
```bash
cat ../../RELEASE_METRICS.md
```

### Compare Metrics Over Time
```bash
# List all historical reports
ls -lt metrics_*.md

# View specific historical report
cat metrics_20250115_120000.md
```

### Generate Fresh Report
Go to Actions → "Release Metrics" → "Run workflow"

## 🎯 Key Metrics Tracked

- **Success Rates**: Workflow success/failure percentages
- **Performance**: Average workflow durations
- **Release Velocity**: Number of releases per period
- **Quality**: Pre-release vs production release ratios

## 📊 Success Criteria

The automation system is healthy when:
- Success rate > 95%
- Average release time < 10 minutes
- Regular use of pre-release testing
- Consistent release cadence

---

*Metrics are automatically maintained by the release automation system*
