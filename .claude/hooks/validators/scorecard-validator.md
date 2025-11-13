# Scorecard Validator

## Purpose
Ensures that every agent output includes the scorecard from `.claude/scorecard.md` with explicit PASS/FAIL ticks for all items.

## Validation Rules

1. **Scorecard Presence**: The scorecard from `.claude/scorecard.md` must be appended to `.claude/work.md`
2. **All Items Marked**: Every scorecard item must have an explicit PASS or FAIL mark
3. **FAIL Items Must Have Mitigation**: Any FAIL item must include clear explanation and mitigation plan
4. **Acceptance Checklist Present**: Agent-specific Acceptance Checklist must be included and checked

## Pass Criteria

✅ **PASS if**:
- The complete scorecard from `.claude/scorecard.md` is appended to `.claude/work.md`
- Every scorecard item has an explicit PASS [x] or FAIL [ ] mark
- Any FAIL items include:
  - Clear explanation of why it failed
  - Bounded justification (not "out of scope")
  - Concrete mitigation plan or next steps
- Agent-specific Acceptance Checklist is included and all items are checked

## Fail Criteria

❌ **FAIL if**:
- Scorecard is missing or incomplete
- Any item is unmarked or ambiguous
- FAIL items lack justification or mitigation
- Acceptance Checklist is missing or not completed

## How to Check

1. Open `.claude/work.md`
2. Scroll to the end
3. Verify scorecard is present
4. Check all items are marked [x] or [ ]
5. For any [ ] (FAIL), verify mitigation is documented

## Agent Instructions if FAIL

If this validator fails:

1. Copy the complete scorecard from `.claude/scorecard.md`
2. Append it to the end of `.claude/work.md`
3. Mark each item as PASS [x] or FAIL [ ]
4. For each FAIL:
   - Explain why it failed
   - Provide mitigation or next steps
   - Document any blockers
5. Include your Acceptance Checklist with all items marked
6. Re-run your self-checks
7. Update output and try again

## Example - PASS

```markdown
## Scorecard (from .claude/scorecard.md)

- [x] Requirements → Deliverables mapping is explicit
- [x] Types/schemas are complete and validated
- [x] Security: no secrets, safe defaults, least-privilege
- [x] Accessibility addressed (if UI) / Observability (if backend)
- [x] Performance: hot paths optimized/bounded
- [x] Tests or runnable snippets provided
- [x] Minimal diff discipline maintained
- [x] Acceptance Checklist: all PASS
- [x] Append protocol followed
- [x] Risks & follow-ups clearly listed

## Acceptance Checklist

- [x] All deliverables complete
- [x] Code follows best practices
- [x] No secrets in output
- [x] Write Zone updated
```

## Example - FAIL (Bad)

```markdown
## Scorecard

- [x] Requirements covered
- [ ] Tests provided
- Some items checked
```

❌ This FAILS because:
- Not the complete scorecard
- FAIL item has no mitigation
- Format is wrong

## Example - PASS (With Justified FAIL)

```markdown
## Scorecard

- [x] Requirements → Deliverables mapping is explicit
- [x] Types/schemas are complete and validated
- [ ] Tests or runnable snippets provided
  - **Mitigation**: Tests are blocked by missing test database
  - **Next Step**: Database Architect needs to provide test schema
  - **Timeline**: Can complete tests in next iteration after schema ready
- [x] Minimal diff discipline maintained
- [x] Acceptance Checklist: all PASS
- [x] Append protocol followed
- [x] Risks & follow-ups clearly listed
```

✅ This PASSES because:
- Complete scorecard present
- FAIL item has clear mitigation
- Next steps are actionable

## Automation Hint

To check automatically:

```bash
# Check if scorecard is present
grep -q "## Scorecard" .claude/work.md || echo "FAIL: No scorecard"

# Check for unmarked items
grep "^- \[ \]" .claude/scorecard.md | while read item; do
  grep -q "$item" .claude/work.md || echo "FAIL: Missing item"
done
```

## References
- Source scorecard: `.claude/scorecard.md`
- Output location: End of `.claude/work.md`
- Enforcement: `.claude/hooks/post-run.md`

---

**Validator Type**: Quality Gate  
**Enforcement**: Post-run (blocking)  
**Priority**: Critical
