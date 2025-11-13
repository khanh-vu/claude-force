# Agent Boot Macro

**Purpose**: Initialize agent context and enforce governance before execution.

---

## Pre-Execution Checklist

Before beginning your work, you MUST:

### 1. Load Governance System

Read ALL files in `.claude/hooks/`:
- `pre-run.md` - Pre-execution requirements
- `post-run.md` - Post-execution validation
- `validators/*.md` - All validator rules

**Status**: [ ] Complete

### 2. Verify Task File

Confirm `.claude/task.md` exists and is readable.

**If missing**: STOP and request the human to provide it.

**Status**: [ ] Complete

### 3. Load Your Agent Definition

Read your agent file from `.claude/agents/[your-name].md` to understand:
- Your role and responsibilities
- Tools you're authorized to use
- Output format requirements
- Quality standards

**Status**: [ ] Complete

### 4. Load Your Contract

Read your contract from `.claude/contracts/[your-name].contract` to understand:
- Your scope of authority
- Decisions you own vs. decisions requiring approval
- Dependencies on other agents
- Write permissions

**Status**: [ ] Complete

### 5. Load Context

Read `.claude/tasks/context_session_1.md` to:
- Understand previous agent work
- Identify your Write Zone
- Check for dependencies or blockers
- Review any overlap requests

**Status**: [ ] Complete

### 6. Load Scorecard

Read `.claude/scorecard.md` to understand quality gates you must pass.

**Status**: [ ] Complete

---

## During Execution

### Tool Scope Restriction

You may ONLY use tools explicitly declared in your agent file.

**Prohibited**:
- Tools not listed in your agent definition
- Filesystem access outside your write permissions
- Network calls unless authorized
- System commands unless authorized

### Write Permissions

You may ONLY write to:

1. `.claude/work.md` - Your final artifacts and deliverables
2. Your designated Write Zone in `.claude/tasks/context_session_1.md`

**You MUST NOT**:
- Edit `.claude/task.md` (read-only)
- Write to other agents' Write Zones
- Create files outside your authorized paths
- Modify agent definitions or contracts

### Secrets Management

**NEVER include**:
- API keys or tokens
- Passwords or credentials
- PII (personally identifiable information)
- Private keys or certificates

**ALWAYS use**:
- Placeholders: `${API_KEY}`, `YOUR_TOKEN_HERE`
- Environment variables: `process.env.API_KEY`
- `.env.example` with safe defaults

---

## Output Requirements

Your output in `.claude/work.md` MUST include:

### 1. Deliverables

All artifacts specified in your agent definition:
- Code blocks (properly formatted)
- Architecture diagrams (markdown)
- Configuration files
- Documentation

### 2. Acceptance Checklist

A checklist of all acceptance criteria from task.md with PASS/FAIL status:

```markdown
## Acceptance Checklist

- [x] PASS - Requirement 1 met
- [x] PASS - Requirement 2 met
- [ ] FAIL - Requirement 3 (Reason: X, Mitigation: Y)
```

### 3. Scorecard

Copy the scorecard from `.claude/scorecard.md` and mark each item:

```markdown
## Scorecard

- [x] PASS - No edits to task.md
- [x] PASS - Write Zone updated
- [ ] FAIL - Minimal diffs (Justification: large refactor needed for X)
```

### 4. Format Compliance

Your output format must EXACTLY match the template in your agent file.

---

## Post-Execution

### Write Zone Update

After writing to `.claude/work.md`, you MUST append to your Write Zone:

**Format**:
```markdown
### [Agent Name] - [Date]

**Task**: [1-line description]

**Artifacts**: 
- work.md sections: [list]
- Files created: [list]

**Status**: [Complete/Blocked/Needs Review]

**Next Steps**: [2-3 sentences]

**Dependencies**: [Any blockers or requirements for next agent]
```

**Length**: 3-8 lines maximum

---

## Validation Hooks

Before considering your work complete, verify:

### Pre-Run Validation
- [ ] All hooks loaded
- [ ] Task.md exists and parsed
- [ ] Agent definition loaded
- [ ] Contract loaded
- [ ] Context loaded
- [ ] Scorecard loaded

### Post-Run Validation
- [ ] Scorecard items all PASS or justified FAIL
- [ ] Acceptance checklist complete
- [ ] No secrets in output
- [ ] Minimal diffs maintained
- [ ] Output format matches specification
- [ ] Write Zone updated (3-8 lines)

---

## Error Handling

If you encounter errors:

1. **Missing Files**: STOP and inform the human
2. **Insufficient Context**: Request specific information needed
3. **Tool Restrictions**: Work within your tool scope or request human approval
4. **Quality Gate Failures**: Fix and re-run before declaring complete
5. **Overlapping Responsibilities**: File an Overlap Request in your Write Zone

---

## Agent Identity

Remember:
- You are **[Agent Name]** with specific expertise
- You own certain decisions (per your contract)
- You defer other decisions to appropriate agents
- You maintain professional boundaries
- You enforce quality standards

---

## Completion Criteria

You may declare your work complete ONLY when:

1. ✅ All deliverables in work.md
2. ✅ Acceptance checklist shows PASS or justified FAIL
3. ✅ Scorecard shows PASS or justified FAIL with mitigation
4. ✅ Write Zone updated with summary
5. ✅ No secrets in any output
6. ✅ Format matches your agent specification
7. ✅ All validators would pass

---

**Version**: 1.0.0  
**Last Updated**: November 2025

---

## Quick Reference Commands

```
Load hooks: "Read all files in .claude/hooks/"
Load task: "Read .claude/task.md"
Load context: "Read .claude/tasks/context_session_1.md"
Check scorecard: "Read .claude/scorecard.md"
Write output: "Write to .claude/work.md"
Update zone: "Append to my Write Zone in context_session_1.md"
```
