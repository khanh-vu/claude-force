# Diff Discipline Validator

## Purpose
Ensures agents make minimal, focused changes

## Validation Rules

1. Changes are scoped to the task
2. No wide file rewrites without justification
3. No refactoring unless requested
4. No reformatting existing code
5. Changes are clearly bounded
6. Justification provided for large changes

## Pass Criteria
✅ **PASS if**: Changes are minimal and focused on task requirements

## Fail Criteria
❌ **FAIL if**: Wide rewrites, unnecessary refactoring, or scope creep

## How to Check

### Automated Check
```bash
# Check for diff-discipline violations
# (Specific check logic for this validator)
```

### Manual Check
1. Review agent output in `.claude/work.md`
2. Verify against rules above
3. Check for violations
4. Document any failures

## Agent Instructions if FAIL

If this validator fails:

1. Review the specific rule that failed
2. Correct the violation in `.claude/work.md`
3. Re-run your self-checks
4. Verify compliance with all rules
5. Update output and try again

## Examples

### Example - PASS
```markdown
[Example of compliant output that passes this validator]
```

### Example - FAIL
```markdown
[Example of non-compliant output that fails this validator]
```

❌ This FAILS because: [specific reason]

## Common Violations

1. **[Common Violation 1]**
   - Description of what agents often do wrong
   - How to fix it

2. **[Common Violation 2]**
   - Description of another common mistake
   - How to fix it

## Remediation Steps

To fix violations:

1. Identify the specific rule violated
2. Review your output for instances
3. Correct each instance
4. Verify no other violations remain
5. Re-run validation

## Integration

This validator is enforced by:
- `.claude/hooks/post-run.md` (post-execution)
- Part of quality gate before completion
- Blocks run if violations found

## Priority
**Priority**: High  
**Enforcement**: Post-run (blocking)  
**Type**: Quality Gate

---

**Last Updated**: 2024-11-13  
**Version**: 1.0.0
