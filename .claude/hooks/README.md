# Hooks System

**Purpose**: Enforce governance, quality gates, and operational discipline across all agent executions.

---

## Overview

The hooks system provides **automated governance** that runs before and after agent execution to ensure:

- ✅ Agents operate within their authorized scope
- ✅ Quality standards are maintained
- ✅ Security practices are followed
- ✅ Cross-agent coordination is managed
- ✅ Outputs are consistent and complete

---

## Hook Types

### 1. Pre-Run Hooks (`pre-run.md`)

Execute **before** an agent begins work.

**Purpose**:
- Validate prerequisites
- Load required context
- Enforce scope restrictions
- Initialize agent properly

**Failure Mode**: **BLOCKING** - Agent cannot proceed if pre-run fails.

---

### 2. Post-Run Hooks (`post-run.md`)

Execute **after** an agent completes work.

**Purpose**:
- Validate output quality
- Check governance compliance
- Verify completeness
- Enforce handoff requirements

**Failure Mode**: **BLOCKING** - Output is rejected if post-run fails.

---

### 3. Validators (`validators/`)

Atomic, reusable validation rules.

**Purpose**:
- Single-responsibility checks
- Composable rules
- Detailed pass/fail reporting
- Clear remediation guidance

**Validators**:
- `scorecard-validator.md` - Quality checklist validation
- `write-zone-guard.md` - Write permission enforcement
- `secret-scan.md` - Secrets detection
- `diff-discipline.md` - Change scope validation
- `format-lint.md` - Output format validation
- `hierarchy-governance.md` - Agent authority validation

---

## Execution Flow

```
┌─────────────────────────────────────────┐
│ 1. Human defines task in task.md       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 2. Agent selected for execution         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 3. PRE-RUN HOOKS                        │
│    ├─ Load hooks/pre-run.md             │
│    ├─ Verify task.md exists             │
│    ├─ Load agent definition             │
│    ├─ Load contract                     │
│    ├─ Load context                      │
│    └─ Enforce tool/file scope           │
└────────────────┬────────────────────────┘
                 │
                 │ [PASS] ─────┐
                 │             │
                 │ [FAIL] ─────┼──> BLOCK & REPORT ERROR
                 │             │
                 ▼             │
┌─────────────────────────────────────────┐
│ 4. AGENT EXECUTION                      │
│    ├─ Read task.md and context          │
│    ├─ Generate artifacts                │
│    ├─ Write to work.md                  │
│    └─ Update Write Zone                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 5. POST-RUN HOOKS                       │
│    ├─ Load hooks/post-run.md            │
│    ├─ Run all validators                │
│    ├─ Check scorecard                   │
│    ├─ Verify Write Zone update          │
│    ├─ Scan for secrets                  │
│    └─ Validate format                   │
└────────────────┬────────────────────────┘
                 │
                 │ [PASS] ─────┐
                 │             │
                 │ [FAIL] ─────┼──> REJECT & REQUEST FIX
                 │             │
                 ▼             │
┌─────────────────────────────────────────┐
│ 6. OUTPUT ACCEPTED                      │
│    ├─ work.md contains valid artifacts  │
│    ├─ Context updated                   │
│    └─ Ready for next agent              │
└─────────────────────────────────────────┘
```

---

## Hook Configuration

Hooks are enabled by default. Configuration in `claude.json`:

```json
{
  "governance": {
    "hooks_enabled": true,
    "pre_run_required": true,
    "post_run_validation": true,
    "validators": [
      "scorecard-validator",
      "write-zone-guard",
      "secret-scan",
      "diff-discipline",
      "format-lint",
      "hierarchy-governance"
    ]
  }
}
```

---

## Validator Details

### Scorecard Validator
**File**: `validators/scorecard-validator.md`  
**Purpose**: Ensures all scorecard items are addressed  
**Checks**:
- Scorecard present in output
- All items marked PASS/FAIL
- FAIL items have justification
- Overall status declared

---

### Write Zone Guard
**File**: `validators/write-zone-guard.md`  
**Purpose**: Enforces write permission boundaries  
**Checks**:
- Only authorized files modified
- Write Zone updated correctly
- No cross-zone violations
- task.md untouched

---

### Secret Scan
**File**: `validators/secret-scan.md`  
**Purpose**: Detects exposed secrets/credentials  
**Checks**:
- No API keys in output
- No passwords or tokens
- No PII (emails, phone numbers)
- Placeholders used correctly

---

### Diff Discipline
**File**: `validators/diff-discipline.md`  
**Purpose**: Ensures minimal, focused changes  
**Checks**:
- Changes scoped to task requirements
- No wide rewrites without justification
- No unrelated modifications
- Diff comments for large changes

---

### Format Lint
**File**: `validators/format-lint.md`  
**Purpose**: Validates output structure  
**Checks**:
- Markdown syntax valid
- Code blocks properly formatted
- Required sections present
- Consistent formatting

---

### Hierarchy Governance
**File**: `validators/hierarchy-governance.md`  
**Purpose**: Enforces agent authority boundaries  
**Checks**:
- Agent stays within contract scope
- Overlap requests filed when needed
- Architecture decisions by architects
- Implementation by developers

---

## Using Hooks

### Agent Perspective

Agents **must**:

1. **Pre-Run**: Execute boot macro which loads all hooks
2. **During**: Stay within authorized scope
3. **Post-Run**: Include scorecard and pass all validators
4. **Failure**: Fix issues and re-run

### Operator Perspective

Operators **should**:

1. **Before agent run**: Ensure hooks are loaded
2. **After agent run**: Review validator results
3. **On failure**: Provide feedback to agent
4. **On success**: Proceed to next step

---

## Customizing Hooks

### Adding a New Validator

1. Create `validators/new-validator.md`
2. Define purpose, checks, pass/fail criteria
3. Add to `claude.json` validators list
4. Update this README

**Template**:
```markdown
# New Validator

**Purpose**: [What this validates]

## Checks
- [ ] Check 1
- [ ] Check 2

## Pass Criteria
[When this validator passes]

## Fail Criteria
[When this validator fails]

## Remediation
[How to fix failures]
```

---

### Disabling a Validator

Edit `claude.json`:

```json
{
  "governance": {
    "validators": [
      "scorecard-validator",
      "write-zone-guard",
      "secret-scan"
      // Removed: "diff-discipline", "format-lint"
    ]
  }
}
```

**Warning**: Disabling validators reduces quality enforcement.

---

## Validator Severity

| Validator | Severity | Can Override? |
|-----------|----------|---------------|
| secret-scan | **CRITICAL** | Never |
| scorecard-validator | **HIGH** | With justification |
| write-zone-guard | **HIGH** | Rarely |
| hierarchy-governance | **MEDIUM** | With overlap request |
| diff-discipline | **MEDIUM** | With justification |
| format-lint | **LOW** | Yes |

**CRITICAL**: Automatic block, no override  
**HIGH**: Block unless explicit justification with approval  
**MEDIUM**: Warning, can proceed with documented reason  
**LOW**: Advisory, best practice guidance

---

## Troubleshooting

### Pre-Run Failures

**Symptom**: Agent cannot start execution

**Common Causes**:
- task.md missing or unreadable
- Agent definition not found
- Contract not found
- Context file corrupted

**Resolution**:
1. Verify all required files exist
2. Check file permissions
3. Validate JSON/Markdown syntax
4. Review error messages

---

### Post-Run Failures

**Symptom**: Agent completes but output rejected

**Common Causes**:
- Scorecard incomplete
- Secrets detected in output
- Write Zone not updated
- Format doesn't match specification

**Resolution**:
1. Review validator error messages
2. Fix identified issues
3. Re-run agent
4. Validate corrections

---

### Validator Conflicts

**Symptom**: Two validators give conflicting guidance

**Example**: diff-discipline wants minimal changes, but format-lint requires reformatting entire file

**Resolution**:
1. Identify the conflict
2. Prioritize by severity (see table above)
3. Document the trade-off
4. Get human approval if needed

---

## Best Practices

### For Agents
1. ✅ Read hooks at start of every execution
2. ✅ Run self-validation before declaring complete
3. ✅ Address all validator failures
4. ✅ Document justifications for any FAIL items

### For Operators
1. ✅ Don't disable validators without good reason
2. ✅ Review validator results after each agent
3. ✅ Provide clear feedback on failures
4. ✅ Keep hooks up to date

### For System Maintainers
1. ✅ Keep validators single-purpose
2. ✅ Write clear error messages
3. ✅ Provide actionable remediation steps
4. ✅ Test hooks on sample outputs

---

## Hook Version Control

Track hook changes:

| Version | Date | Changes | Reason |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-13 | Initial hooks system | Launch |
| 1.0.1 | TBD | Add rate limiting validator | Performance concerns |

---

## Metrics

Track hook effectiveness:

- **Pre-Run Failure Rate**: [X%]
- **Post-Run Failure Rate**: [Y%]
- **Most Common Failure**: [Validator name]
- **Average Fixes Required**: [N per agent]

---

## Future Enhancements

Planned improvements:

- [ ] Automated validator execution
- [ ] Slack/email notifications on failures
- [ ] Validator dashboard/reporting
- [ ] Custom validator plugins
- [ ] Graduated severity enforcement
- [ ] Machine learning for pattern detection

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintainer**: System Admin

---

## References

- `pre-run.md` - Pre-execution governance
- `post-run.md` - Post-execution validation
- `validators/*.md` - Individual validator documentation
- `../claude.json` - Hook configuration
- `../scorecard.md` - Quality checklist template
