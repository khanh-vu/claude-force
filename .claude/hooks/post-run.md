# Post-Run Validation Hook

**Purpose**: Validate output quality and governance compliance after agent completes execution.

**Execution**: **REQUIRED** after agent finishes work.

**Failure Mode**: **BLOCKING** - Output is rejected if post-run validation fails.

---

## Validation Sequence

All validators run in sequence. **ALL must pass** for output to be accepted.

---

## 1. Scorecard Validator

**File**: `validators/scorecard-validator.md`

**Check**: Output includes complete scorecard with PASS/FAIL markings.

**Pass Criteria**:
- [x] Scorecard present in work.md
- [x] All items marked [x] PASS or [ ] FAIL
- [x] FAIL items have justification
- [x] Overall status declared

**On Failure**:
- Agent must add scorecard to output
- All items must be evaluated
- Re-run validation

**Severity**: **HIGH** - Cannot proceed without scorecard

---

## 2. Write Zone Guard

**File**: `validators/write-zone-guard.md`

**Check**: Write permissions were respected.

**Pass Criteria**:
- [x] Only work.md and Write Zone modified
- [x] task.md untouched (read-only)
- [x] Write Zone updated correctly (3-8 lines)
- [x] No other agents' zones modified
- [x] Write Zone update includes date, artifacts, status, next steps

**On Failure**:
- Identify unauthorized modifications
- Revert changes to protected files
- Update Write Zone correctly
- Re-run validation

**Severity**: **HIGH** - Governance violation

---

## 3. Secret Scan

**File**: `validators/secret-scan.md`

**Check**: No secrets, credentials, or PII in output.

**Pass Criteria**:
- [x] No API keys or tokens
- [x] No passwords or private keys
- [x] No PII (emails, phone numbers, addresses)
- [x] No hardcoded credentials
- [x] Environment variables or placeholders used

**On Failure**:
- **CRITICAL** - Remove ALL secrets immediately
- Replace with placeholders
- Create .env.example if needed
- Re-run validation

**Severity**: **CRITICAL** - Security risk

---

## 4. Diff Discipline

**File**: `validators/diff-discipline.md`

**Check**: Changes are minimal and scoped to task.

**Pass Criteria**:
- [x] Changes directly related to task requirements
- [x] No wide rewrites unless justified
- [x] No commented-out code
- [x] No unrelated modifications
- [x] Large changes documented with rationale

**On Failure**:
- Justify wide changes in scorecard
- Remove unrelated modifications
- Document necessity for large diffs
- Re-run validation

**Severity**: **MEDIUM** - Can override with justification

---

## 5. Format Lint

**File**: `validators/format-lint.md`

**Check**: Output format matches agent specification.

**Pass Criteria**:
- [x] All required sections present
- [x] Markdown syntax valid
- [x] Code blocks properly formatted
- [x] Tables properly structured
- [x] Links valid
- [x] Consistent formatting throughout

**On Failure**:
- Add missing sections
- Fix markdown syntax errors
- Format code blocks correctly
- Re-run validation

**Severity**: **LOW** - Can proceed with warnings

---

## 6. Hierarchy Governance

**File**: `validators/hierarchy-governance.md`

**Check**: Agent stayed within authority boundaries.

**Pass Criteria**:
- [x] Agent worked within contract scope
- [x] Architecture decisions by architects
- [x] Implementation by developers
- [x] Overlap requests filed if needed
- [x] No authority overreach

**On Failure**:
- Identify scope violations
- File overlap request if needed
- Get approval from controlling agent
- Re-run validation

**Severity**: **MEDIUM** - Requires overlap approval

---

## Post-Run Checklist

Agent must confirm all validations pass:

```markdown
## Post-Run Validation Summary

**Agent**: [Name]  
**Date**: [YYYY-MM-DD HH:MM]  
**Task**: [Reference]

### Validator Results

1. Scorecard Validator: [PASS/FAIL]
2. Write Zone Guard: [PASS/FAIL]
3. Secret Scan: [PASS/FAIL]
4. Diff Discipline: [PASS/FAIL]
5. Format Lint: [PASS/FAIL]
6. Hierarchy Governance: [PASS/FAIL]

**Overall**: [PASS/FAIL]

**Issues**: [List any failures]

**Actions Required**: [Remediation steps if FAIL]
```

---

## Pass/Fail Decision Tree

```
All Validators PASS?
├─ YES → Accept output, mark agent complete
└─ NO → Check severity
    ├─ CRITICAL (Secret Scan) → Reject immediately, require fix
    ├─ HIGH (Scorecard, Write Zone) → Reject, require fix
    ├─ MEDIUM (Diff, Hierarchy) → Review justification
    │   ├─ Justified → Conditional accept with review
    │   └─ Not justified → Reject, require fix
    └─ LOW (Format) → Accept with warnings, recommend fix
```

---

## Enforcement

### Strict Enforcement (Default)

**Mode**: All validators must PASS

**On Failure**: Agent must fix and re-run

**Use Cases**: Production work, critical features, security-sensitive changes

---

### Permissive Enforcement

**Mode**: CRITICAL/HIGH must PASS, MEDIUM/LOW can be justified

**On Failure**: Agent documents justification, gets approval

**Use Cases**: Prototyping, exploration, time-constrained work

**Warning**: Quality may suffer in permissive mode

---

## Remediation Process

When validation fails:

### Step 1: Identify Issues
```
Review validator output to understand specific failures.
```

### Step 2: Prioritize
```
CRITICAL → Fix immediately
HIGH → Fix before proceeding
MEDIUM → Document justification or fix
LOW → Fix or accept with warning
```

### Step 3: Fix
```
Make necessary corrections to output.
Update work.md with fixes.
```

### Step 4: Revalidate
```
Re-run post-run validation.
Confirm all issues resolved.
```

### Step 5: Document
```
Update Write Zone with resolution details.
Note any conditional acceptances.
```

---

## Audit Trail

Log post-run validation:

```markdown
### Post-Run Audit - [Agent Name] - [Date Time]

**Output Location**: .claude/work.md

**Validators Executed**:
1. scorecard-validator: PASS
2. write-zone-guard: PASS
3. secret-scan: PASS
4. diff-discipline: PASS (justified: large refactor needed)
5. format-lint: PASS
6. hierarchy-governance: PASS

**Overall Result**: CONDITIONAL PASS

**Conditions**:
- Diff discipline justified due to security refactor
- Approved by: Tech Lead
- Date: 2025-11-13

**Next Agent**: Ready to proceed

**Operator**: [Name]
```

---

## Common Failures & Resolutions

### Failure: Scorecard Missing

**Error**: "Scorecard not found in work.md"

**Resolution**:
1. Copy scorecard template from `.claude/scorecard.md`
2. Append to work.md
3. Mark all items PASS/FAIL
4. Add justifications for FAIL items
5. Re-run validation

---

### Failure: Secret Detected

**Error**: "API key detected in output: line 127"

**Resolution**:
1. Replace secret with placeholder: `${API_KEY}`
2. Create `.env.example` with safe default
3. Document in code comments
4. Re-run validation
5. Verify secret removed

---

### Failure: Write Zone Not Updated

**Error**: "Write Zone in context_session_1.md not updated"

**Resolution**:
1. Locate your Write Zone in context file
2. Append 3-8 line summary
3. Include: date, task, artifacts, status, next steps
4. Re-run validation

---

### Failure: Format Issues

**Error**: "Missing required sections: [list]"

**Resolution**:
1. Review agent definition for required format
2. Add missing sections to work.md
3. Fix markdown syntax errors
4. Format code blocks correctly
5. Re-run validation

---

## Manual Override (Emergency Only)

In **exceptional** circumstances, validation can be manually overridden:

**Requirements**:
- Human approval required
- Clear justification documented
- Risk assessment completed
- Mitigation plan in place

**Procedure**:
```markdown
### Validation Override

**Date**: [YYYY-MM-DD]
**Agent**: [Name]
**Validator Failed**: [Name]
**Reason for Override**: [Detailed justification]
**Risk**: [Assessment of what could go wrong]
**Mitigation**: [How risk is managed]
**Approved By**: [Human name/role]
**Expiration**: [When this override expires]
```

**Warning**: Overrides should be **rare** and **time-limited**.

---

## Continuous Improvement

### Validator Metrics

Track validator effectiveness:

| Validator | Failure Rate | Avg Fix Time | False Positive Rate |
|-----------|--------------|--------------|---------------------|
| scorecard-validator | 15% | 5 min | 2% |
| write-zone-guard | 8% | 3 min | 0% |
| secret-scan | 3% | 10 min | 5% |
| diff-discipline | 20% | 15 min | 10% |
| format-lint | 12% | 5 min | 15% |
| hierarchy-governance | 5% | 20 min | 3% |

### Improvement Actions

- High failure rate → Improve agent training
- High fix time → Better error messages
- High false positives → Tune validator rules

---

## Integration with CI/CD

Post-run validation can be automated:

```bash
#!/bin/bash
# post-run-validate.sh

echo "Running post-run validation..."

# Run each validator
./validators/run-all.sh

# Check results
if [ $? -eq 0 ]; then
    echo "✅ All validations passed"
    exit 0
else
    echo "❌ Validation failures detected"
    echo "Review validator output and fix issues"
    exit 1
fi
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-13 | Initial post-run hook |

---

**Status**: Active  
**Enforcement**: Strict (default)  
**Override**: Permitted with approval only
