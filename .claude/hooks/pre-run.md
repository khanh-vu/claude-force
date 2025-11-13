# Pre-Run Governance Hook

**Purpose**: Validate prerequisites and initialize agent context before execution begins.

**Execution**: **REQUIRED** before any agent work starts.

**Failure Mode**: **BLOCKING** - Agent must not proceed if pre-run checks fail.

---

## Checks Performed

### 1. Hooks System Loading

**Requirement**: Agent must load ALL hook files before beginning work.

**Files to Load**:
- [ ] `.claude/hooks/pre-run.md` (this file)
- [ ] `.claude/hooks/post-run.md`
- [ ] `.claude/hooks/validators/scorecard-validator.md`
- [ ] `.claude/hooks/validators/write-zone-guard.md`
- [ ] `.claude/hooks/validators/secret-scan.md`
- [ ] `.claude/hooks/validators/diff-discipline.md`
- [ ] `.claude/hooks/validators/format-lint.md`
- [ ] `.claude/hooks/validators/hierarchy-governance.md`

**Verification**: Agent must confirm hooks loaded in thinking or output.

**On Failure**: **STOP** - Request agent to load all hooks before proceeding.

---

### 2. Task Definition Exists

**Requirement**: `.claude/task.md` must exist and be readable.

**Check**:
```
File exists: .claude/task.md
File readable: Yes
File not empty: Yes
Contains objective: Yes
```

**On Failure**: 
- **STOP** immediately
- Inform human: "task.md is missing or invalid. Please create it with task requirements."
- Do not attempt to proceed

---

### 3. Agent Definition Loaded

**Requirement**: Agent must read its own definition file.

**Check**:
```
Agent file: .claude/agents/[agent-name].md
File exists: Yes
File loaded: Yes
Role understood: Yes
Tools identified: Yes
Output format known: Yes
```

**On Failure**:
- **STOP** immediately
- Inform human: "Agent definition not found: [agent-name].md"
- Cannot proceed without knowing role and capabilities

---

### 4. Contract Loaded

**Requirement**: Agent must read its contract file.

**Check**:
```
Contract file: .claude/contracts/[agent-name].contract
File exists: Yes
File loaded: Yes
Scope understood: Yes
Authority clear: Yes
Write permissions known: Yes
```

**On Failure**:
- **STOP** immediately
- Inform human: "Contract not found: [agent-name].contract"
- Cannot proceed without understanding authority boundaries

---

### 5. Context Loaded

**Requirement**: Agent must read session context.

**Check**:
```
Context file: .claude/tasks/context_session_1.md
File exists: Yes
File loaded: Yes
Write Zone identified: Yes
Previous work reviewed: Yes
Dependencies checked: Yes
```

**On Failure**:
- **STOP** immediately
- Inform human: "Context file not found or unreadable"
- Cannot proceed without understanding prior work and dependencies

---

### 6. Scorecard Loaded

**Requirement**: Agent must read quality checklist.

**Check**:
```
Scorecard file: .claude/scorecard.md
File exists: Yes
File loaded: Yes
Quality gates understood: Yes
```

**On Failure**:
- **STOP** immediately
- Inform human: "Scorecard not found"
- Cannot proceed without knowing quality standards

---

### 7. Tool Scope Validation

**Requirement**: Agent must acknowledge tool restrictions.

**Check**:
Agent understands it may ONLY use tools listed in its agent definition.

**Prohibited Actions**:
- Using tools not in agent definition
- Accessing files outside write permissions
- Network calls unless authorized
- System commands unless authorized
- Installing packages unless authorized

**On Violation**: **BLOCK** - Agent must work within tool scope or request expansion.

---

### 8. Write Permission Validation

**Requirement**: Agent must acknowledge write restrictions.

**Check**:
Agent understands it may ONLY write to:
- `.claude/work.md` (artifacts)
- Its designated Write Zone in `context_session_1.md`

**Prohibited Writes**:
- `.claude/task.md` (read-only)
- Agent definition files
- Contract files
- Other agents' Write Zones
- Hook files
- Files outside authorized paths

**On Violation**: **BLOCK** - Any unauthorized write must be prevented.

---

### 9. Dependencies Check

**Requirement**: Agent must verify dependencies are met.

**Check**:
- [ ] Required previous agents completed?
- [ ] Required artifacts available?
- [ ] Blockers resolved?
- [ ] Overlap requests approved (if any)?

**On Failure**:
- **PAUSE** execution
- Inform human: "Dependencies not met: [list]"
- Wait for prerequisites to be satisfied

---

### 10. Boot Macro Execution

**Requirement**: Agent should ideally execute via boot macro.

**Check**:
Boot macro (`.claude/macros/boot.md`) provides structured initialization.

**Recommendation**: 
```
Execute [agent-name] using the boot macro for proper initialization.
```

**Note**: Not strictly required, but best practice.

---

## Pre-Run Checklist

Before proceeding, agent must confirm:

```markdown
## Pre-Run Checklist Confirmation

- [x] All hooks loaded from .claude/hooks/
- [x] task.md exists and parsed
- [x] Agent definition loaded and understood
- [x] Contract loaded and acknowledged
- [x] Context loaded and Write Zone identified
- [x] Scorecard loaded and quality gates known
- [x] Tool scope restrictions acknowledged
- [x] Write permissions understood and will be respected
- [x] Dependencies verified (or none required)
- [x] Ready to proceed with execution

**Agent**: [Name]  
**Date**: [YYYY-MM-DD HH:MM]  
**Status**: READY
```

---

## Enforcement

### For Agents

**You MUST**:
1. Execute all checks in order
2. Confirm each check passes
3. Stop immediately on any failure
4. Report failures clearly to human
5. Wait for issues to be resolved before proceeding

**You MUST NOT**:
1. Skip or bypass pre-run checks
2. Proceed if any check fails
3. Assume files exist without verification
4. Operate outside tool/write scope
5. Ignore dependency blockers

---

### For Operators

**You SHOULD**:
1. Ensure all required files exist before running agent
2. Initialize context file if new session
3. Review agent's pre-run confirmation
4. Address any reported failures promptly
5. Verify agent loaded hooks properly

---

## Common Failures & Resolutions

### Failure: task.md Missing

**Error**: "task.md not found"

**Resolution**:
1. Create `.claude/task.md`
2. Define objective, requirements, acceptance criteria
3. Re-run agent

---

### Failure: Context File Missing

**Error**: "context_session_1.md not found"

**Resolution**:
1. Create `.claude/tasks/context_session_1.md`
2. Initialize Write Zones for all agents
3. Re-run agent

---

### Failure: Agent Definition Not Found

**Error**: "Agent definition missing: [name].md"

**Resolution**:
1. Verify agent name is correct
2. Check `.claude/agents/` directory
3. Create agent definition if missing
4. Re-run agent

---

### Failure: Dependencies Not Met

**Error**: "Required artifact from [previous-agent] not available"

**Resolution**:
1. Run prerequisite agent first
2. Verify output in work.md
3. Check Write Zone for handoff
4. Re-run current agent

---

## Emergency Bypass (NOT RECOMMENDED)

In exceptional circumstances, if you must bypass pre-run:

**Conditions**:
- System-level emergency
- Human explicitly authorizes bypass
- Full understanding of risks

**Procedure**:
1. Document why bypass is necessary
2. Get explicit human approval
3. Document which checks were skipped
4. Proceed with extreme caution
5. Run post-run validation carefully

**Warning**: Bypassing pre-run checks can lead to:
- Security vulnerabilities
- Data corruption
- Quality failures
- Wasted work due to missing context

---

## Audit Trail

Log pre-run execution:

```markdown
### Pre-Run Audit - [Agent Name] - [Date Time]

**Status**: [PASS/FAIL]

**Checks**:
- Hooks loaded: PASS
- task.md exists: PASS
- Agent definition: PASS
- Contract loaded: PASS
- Context loaded: PASS
- Scorecard loaded: PASS
- Tool scope: PASS
- Write permissions: PASS
- Dependencies: PASS

**Issues**: None

**Ready for Execution**: Yes

**Operator**: [Name]
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-13 | Initial pre-run hook |

---

**Status**: Active  
**Enforcement**: Strict  
**Override**: Not permitted without human authorization
