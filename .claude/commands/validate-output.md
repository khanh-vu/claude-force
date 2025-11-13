---
description: Validate work.md against all quality gates
usage: /validate-output
---

# Validate Output Command

Run all validators on the current `.claude/work.md` to ensure it meets quality standards.

## Validators to Run

1. **Scorecard Validator** - Check all scorecard items marked PASS/FAIL
2. **Write Zone Guard** - Verify Write Zone updated correctly
3. **Secret Scan** - Ensure no secrets in output
4. **Diff Discipline** - Verify minimal, focused changes
5. **Format Lint** - Validate output structure and formatting
6. **Hierarchy Governance** - Ensure agent stayed within scope

## Process

1. Read `.claude/work.md`
2. Read all validators from `.claude/hooks/validators/`
3. Run each validator in sequence
4. Report PASS/FAIL for each
5. Provide summary of issues
6. Suggest remediation steps for failures

## Output Format

```markdown
## Validation Results

### Scorecard Validator: ✅ PASS
- All items marked PASS or justified FAIL

### Write Zone Guard: ✅ PASS
- Write Zone updated with 5 lines
- Last updated: 2025-11-13 10:30

### Secret Scan: ❌ FAIL
- Found API key on line 245
- Remediation: Replace with placeholder

### Diff Discipline: ✅ PASS
- Changes focused and minimal

### Format Lint: ✅ PASS
- All sections present
- Markdown valid

### Hierarchy Governance: ✅ PASS
- Agent stayed within contract scope

## Summary
- **Total**: 6 validators
- **Passed**: 5
- **Failed**: 1
- **Status**: ❌ VALIDATION FAILED

## Next Steps
1. Fix secret leak on line 245
2. Re-run validation
3. Proceed when all validators pass
```

## Example

```
/validate-output
```
