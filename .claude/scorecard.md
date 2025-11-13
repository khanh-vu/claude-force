# Quality Scorecard

**Purpose**: Universal quality gates that every agent must satisfy before declaring work complete.

Copy this scorecard to the end of your output in `.claude/work.md` and mark each item with PASS/FAIL.

---

## Core Requirements

### 1. File Integrity
- [ ] `.claude/task.md` remains unmodified (read-only)
- [ ] No edits to agent definition files
- [ ] No edits to contract files
- [ ] No edits to other agents' Write Zones

**If FAIL**: Explain what was modified and why it was absolutely necessary, with human approval.

---

### 2. Write Zone Compliance
- [ ] Write Zone updated in `context_session_1.md`
- [ ] Update is 3-8 lines (not too brief, not verbose)
- [ ] Update includes date, artifacts, status, next steps
- [ ] No overlap with other agents' zones

**If FAIL**: Explain why Write Zone couldn't be updated.

---

### 3. Secrets & Security
- [ ] No API keys, tokens, or passwords in output
- [ ] No PII (names, emails, phone numbers, addresses)
- [ ] No private keys or certificates
- [ ] All sensitive values use placeholders or env vars
- [ ] `.env.example` provided if configuration needed

**If FAIL**: This is CRITICAL. Regenerate output with secrets removed.

---

### 4. Code Quality
- [ ] Minimal diffs (no wide rewrites unless justified)
- [ ] Code follows language/framework conventions
- [ ] No commented-out code blocks
- [ ] No debug logging or console.log in production code
- [ ] Error handling present for network/IO operations

**If FAIL**: Explain why wide changes were necessary.

---

### 5. Output Format Compliance
- [ ] Output matches agent's specified format exactly
- [ ] All required sections present
- [ ] Code blocks properly formatted with language tags
- [ ] Markdown structure valid (no broken tables/lists)
- [ ] Links and references valid

**If FAIL**: Identify which sections are missing or incorrectly formatted.

---

### 6. Acceptance Criteria
- [ ] Acceptance Checklist included in output
- [ ] All criteria from task.md addressed
- [ ] Each criterion marked PASS or FAIL
- [ ] FAIL items have clear reasons and mitigation plans

**If FAIL**: Add the Acceptance Checklist section.

---

### 7. Documentation
- [ ] Code includes inline comments for complex logic
- [ ] Public APIs have JSDoc/docstring comments
- [ ] README or usage examples provided where appropriate
- [ ] Breaking changes clearly documented
- [ ] Dependencies listed

**If FAIL**: Explain what documentation is missing and why.

---

### 8. Testing & Quality
- [ ] Unit tests provided for critical logic (if applicable)
- [ ] Edge cases considered and handled
- [ ] Error messages are helpful and actionable
- [ ] No TODO comments without issue tracking reference
- [ ] Performance considerations documented for hot paths

**If FAIL**: Explain testing gaps and mitigation plan.

---

### 9. Accessibility & Observability

**For Frontend/UI Work**:
- [ ] ARIA attributes for interactive elements
- [ ] Keyboard navigation supported
- [ ] Color contrast meets WCAG standards
- [ ] Focus states visible

**For Backend/API Work**:
- [ ] Structured logging present
- [ ] Metrics/observability hooks noted
- [ ] Trace/span propagation considered
- [ ] Health check endpoints defined

**If FAIL**: Document which items are missing and impact.

---

### 10. Dependencies & Boundaries
- [ ] All dependencies on other agents identified
- [ ] Cross-agent contracts respected
- [ ] No overlap requests pending approval
- [ ] Handoff requirements documented
- [ ] Next agent in workflow can proceed without blockers

**If FAIL**: List blockers preventing next agent's work.

---

## Agent-Specific Requirements

### Architecture Agents (Frontend/Backend/Database)
- [ ] Decisions documented with rationale
- [ ] Trade-offs explicitly stated
- [ ] Alternative approaches considered
- [ ] Constraints and assumptions listed
- [ ] Contract boundaries clear

### Implementation Agents (Developers/Experts)
- [ ] Code is production-ready
- [ ] Types/schemas complete and validated
- [ ] Linting rules would pass
- [ ] Build/compile would succeed
- [ ] Runtime errors handled gracefully

### Infrastructure/Deployment Agents
- [ ] Configurations use environment variables
- [ ] Secrets management strategy clear
- [ ] Rollback procedure documented
- [ ] Monitoring/alerting noted
- [ ] Cost implications identified

### Testing/QA Agents
- [ ] Test coverage meets requirements
- [ ] Both happy path and edge cases covered
- [ ] Tests are deterministic (no flaky tests)
- [ ] Test data strategy documented
- [ ] CI/CD integration clear

### Documentation Agents
- [ ] Audience clearly defined
- [ ] Examples runnable and tested
- [ ] Links and references valid
- [ ] Version/deprecation info included
- [ ] Contribution guidelines (if open source)

---

## Pass/Fail Summary

**Total Items**: Count applicable items  
**PASS**: [N]  
**FAIL**: [N]  

**Overall Status**: [PASS / CONDITIONAL PASS / FAIL]

**Conditional Pass**: When minor FAILs exist with clear mitigation plans that don't block progress.

**Full Fail**: Critical failures (secrets exposed, missing core deliverables, unable to proceed).

---

## Justification for FAILs

For each FAIL item, provide:

1. **Item**: Which scorecard item failed
2. **Reason**: Why it failed (technical constraint, time constraint, etc.)
3. **Impact**: What is the risk or consequence
4. **Mitigation**: What is the plan to address it
5. **Approval**: Does this require human review/approval

**Example**:
```markdown
### FAIL: Minimal Diffs

**Reason**: Complete refactor of authentication system required to fix security vulnerability.

**Impact**: 500+ lines changed across 10 files. May require careful review.

**Mitigation**: 
- Changes isolated to auth module
- Unit tests updated and passing
- Integration tests cover all flows
- Rollback plan documented

**Approval**: Recommend human review before merge.
```

---

## Usage Instructions

1. **Copy this scorecard** to the end of your output in `.claude/work.md`
2. **Check each box** with `[x]` for PASS or `[ ]` for FAIL
3. **Remove N/A items** (e.g., accessibility checks for backend-only work)
4. **Document FAILs** with justification in the section below
5. **Calculate summary** showing pass/fail counts
6. **Declare overall status**

---

**Version**: 1.0.0  
**Last Updated**: November 2025
