# Format Lint Validator

## Purpose
Ensures agent output follows the specified format

## Validation Rules

1. Output matches agent's Output Format section
2. All required sections are present
3. Code blocks have proper language tags
4. Section headers are clear
5. Examples are provided where required
6. Documentation is complete

## Pass Criteria
✅ **PASS if**: Output format matches specification exactly

## Fail Criteria
❌ **FAIL if**: Missing sections, wrong format, or incomplete documentation

## How to Check

### Automated Check
```bash
# Check for format-lint violations
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
**Priority**: Medium  
**Enforcement**: Post-run (blocking)  
**Type**: Quality Gate

---

**Last Updated**: 2024-11-13  
**Version**: 1.0.0
