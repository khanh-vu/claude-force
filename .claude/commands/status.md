---
description: Show current session status and progress
usage: /status
---

# Status Command

Display the current state of your Claude multi-agent session.

## Information Displayed

### Task Information
- Current task title and objective
- Task status (Not Started/In Progress/Complete)
- Priority and type
- Key requirements overview

### Session Progress
- Session ID and start time
- Active workflow (if any)
- Agents completed vs total
- Current agent (if in progress)
- Estimated completion time

### Recent Activity
- Last 5 agent executions
- Timestamps and status
- Any blockers or issues

### Quality Status
- Validation status of current work.md
- Scorecard pass/fail summary
- Open issues or warnings

### Next Steps
- Recommended next agent
- Any pending dependencies
- Blockers to resolve

## Output Format

```markdown
## Session Status

**Session**: 1
**Started**: 2025-11-13 09:00
**Duration**: 2 hours 15 minutes
**Status**: 🟡 In Progress

---

## Current Task

**Title**: Build Product Catalog UI
**Priority**: 🔴 High
**Type**: Feature
**Status**: In Progress (60% complete)

**Objective**: Create responsive product catalog with filters and search

---

## Workflow Progress

**Workflow**: full-stack-feature
**Progress**: 5 of 8 agents complete (62%)

✅ frontend-architect (Complete)
✅ database-architect (Complete)
✅ backend-architect (Complete)
✅ python-expert (Complete)
✅ ui-components-expert (Complete)
🔄 frontend-developer (In Progress)
⏳ qc-automation-expert (Pending)
⏳ deployment-integration-expert (Pending)

---

## Quality Status

**Last Validation**: 2025-11-13 10:30
**Status**: ✅ All Checks Pass

- Scorecard: 12/12 PASS
- Write Zone: Updated
- Secrets: None detected
- Format: Valid

---

## Recent Activity

| Time | Agent | Status | Duration |
|------|-------|--------|----------|
| 10:30 | ui-components-expert | ✅ Complete | 25 min |
| 10:05 | python-expert | ✅ Complete | 20 min |
| 09:45 | backend-architect | ✅ Complete | 30 min |
| 09:15 | database-architect | ✅ Complete | 18 min |
| 09:00 | frontend-architect | ✅ Complete | 22 min |

---

## Blockers & Issues

⚠️ 1 issue requires attention:

- **B-001**: API key from vendor pending
  - Impact: Medium
  - Blocking: deployment-integration-expert
  - Status: Waiting for response

---

## Next Steps

1. **Immediate**: Complete frontend-developer implementation
2. **Next Agent**: qc-automation-expert
3. **After That**: deployment-integration-expert
4. **Blockers**: Resolve B-001 before final deployment

**Estimated Completion**: 1.5 hours

---

## Artifacts Produced

📄 **In work.md**:
- Frontend architecture brief
- Database schema (DDL)
- API specification (OpenAPI)
- Python ETL scripts
- React components (ProductCard, FilterBar, SearchBox)

📁 **Separate Files**:
- None yet

---

## Recommendations

💡 **Tips**:
- Run validation before proceeding to next agent
- Review Write Zones for context
- Ensure all acceptance criteria addressed
- Consider break after frontend-developer completes

---

**Last Updated**: 2025-11-13 11:00
```

## Quick Status

For a brief status:

```
/status --quick

Session 1 | full-stack-feature | 5/8 agents ✅ | frontend-developer 🔄
```

## Options

- `--quick`: Brief one-line status
- `--detailed`: Include full Write Zone contents
- `--json`: Export status as JSON
- `--save`: Save status report to file

## Use Cases

### Before Starting Work
```
/status
```
See where you left off, what's next.

### After Agent Completes
```
/status
```
Verify completion, see updated progress.

### During Long Workflows
```
/status --quick
```
Quick check without leaving your flow.

### For Reporting
```
/status --save
```
Generate report for stakeholders.

## Status in Other Contexts

### Git Integration
```bash
/status --git
```
Shows git branch, uncommitted changes, last commit.

### System Health
```bash
/status --system
```
Shows file sizes, validation health, warnings.
