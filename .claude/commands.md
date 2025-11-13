# Commands Reference

Quick reference for common operations in the Claude Multi-Agent System.

---

## Agent Execution

### Run a Single Agent

```
Run the [agent-name] agent on the current task.
```

**Example**:
```
Run the frontend-architect agent on the current task.
```

### Run with Boot Macro

```
Execute [agent-name] using the boot macro for full initialization.
```

This ensures all governance checks and context loading happens properly.

---

## Task Management

### Create New Task

```
Create a new task in .claude/task.md for [description].
```

### Update Task

```
Update .claude/task.md to add [new requirement].
```

### View Task

```
Show me the current task from .claude/task.md.
```

---

## Context & Progress

### View Context

```
Show me the context from tasks/context_session_1.md.
```

### View Agent's Write Zone

```
Show me the [agent-name] Write Zone from context_session_1.md.
```

### View Last Output

```
Show me the latest output from .claude/work.md.
```

---

## Workflow Orchestration

### Run Full Workflow

```
Execute the full-stack-feature workflow on this task:
1. frontend-architect
2. database-architect
3. backend-architect
4. python-expert
5. ui-components-expert
6. frontend-developer
7. qc-automation-expert
8. deployment-integration-expert
```

### Run Partial Workflow

```
Run agents [A, B, C] in sequence on the current task.
```

### Workflow Status

```
Review the workflow progress from context_session_1.md and summarize:
- Completed agents
- Current agent
- Remaining agents
- Any blockers
```

---

## Validation & Quality

### Run Scorecard

```
Evaluate the output in work.md against the scorecard and provide a summary.
```

### Run Specific Validator

```
Run the [validator-name] validator on the current work.md.
```

**Validators**:
- `scorecard-validator`
- `write-zone-guard`
- `secret-scan`
- `diff-discipline`
- `format-lint`
- `hierarchy-governance`

### Full Validation

```
Run all validators from hooks/validators/ on the current output.
```

---

## Agent Management

### List Agents

```
List all available agents with their domains.
```

### Show Agent Definition

```
Show me the [agent-name] agent definition.
```

### Show Agent Contract

```
Show me the contract for [agent-name].
```

### Agent Capabilities

```
What can the [agent-name] agent do? What tools does it have access to?
```

---

## Debugging & Troubleshooting

### Check Hook Violations

```
Check if the current output violates any hooks in hooks/.
```

### Diagnose Failure

```
The [agent-name] agent failed. Diagnose the issue by checking:
1. Task.md completeness
2. Write Zone status
3. Scorecard failures
4. Validator errors
```

### Review Diff

```
Show me what changed in work.md compared to the previous version.
```

---

## Skills Integration

### List Available Skills

```
List all available Claude skills in the skills/ directory.
```

### Use Skill

```
Use the [skill-name] skill to [action].
```

**Example**:
```
Use the docx skill to convert the work.md output to a professional document.
```

---

## Multi-Agent Coordination

### File Overlap Request

```
[Agent A] needs to modify [file/area] which is owned by [Agent B]. File an overlap request.
```

### Review Overlap Requests

```
Show me all pending overlap requests from context_session_1.md.
```

### Approve Overlap Request

```
[Controlling Agent] approves [Requesting Agent]'s overlap request for [scope]. Log this decision.
```

---

## Reporting

### Generate Summary

```
Summarize the work completed so far:
- Agents executed
- Artifacts created
- Quality status
- Next steps
```

### Export Artifacts

```
Package all artifacts from work.md into organized files ready for implementation.
```

### Progress Report

```
Generate a progress report showing:
- Task objective
- Completed work
- Current status
- Remaining work
- Estimated completion
```

---

## Maintenance

### Reset Work

```
Clear work.md to start fresh output. (Keep context_session_1.md intact)
```

### Archive Session

```
Archive the current session (context_session_1.md) and start a new session (context_session_2.md).
```

### Validate System

```
Validate the entire .claude/ system structure:
- All required files present
- All agents have contracts
- All validators are valid
- No orphaned references
```

---

## Advanced Operations

### Simulate Agent

```
Simulate what [agent-name] would output for this task without actually executing.
```

### Diff Agents

```
Compare the contracts of [agent-a] and [agent-b] to identify overlap areas.
```

### Optimize Workflow

```
Given the task requirements, suggest the optimal agent workflow.
```

### Create Custom Workflow

```
Create a custom workflow for [use case]:
1. [agent-1] for [purpose]
2. [agent-2] for [purpose]
3. ...
```

---

## Templates

### Task Template

```markdown
# Task: [Title]

## Objective
[Clear, measurable goal]

## Requirements
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Context
[Background information, constraints, assumptions]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Resources
- [Link 1]
- [Link 2]

## Notes
[Additional information]
```

### Write Zone Update Template

```markdown
### [Agent Name] - [YYYY-MM-DD HH:MM]

**Task**: [One-line description]

**Artifacts**: 
- work.md: [sections created]
- Files: [list if any]

**Status**: [Complete/Blocked/Needs Review]

**Next Steps**: [2-3 sentences about what should happen next]

**Dependencies**: [Any blockers or requirements]
```

---

## Keyboard Shortcuts (For Workflow)

These are conceptual shortcuts for common operation patterns:

- **Quick Execute**: Run agent on current task with standard setup
- **Validate & Continue**: Run validators, fix issues, proceed to next agent
- **Review & Commit**: Review output, check scorecard, mark task complete
- **Debug Mode**: Enable verbose logging and validation output
- **Archive & Reset**: Archive current work and start fresh session

---

## Environment Variables

Configure system behavior via `.claude/.env`:

```bash
# Validation strictness (strict, normal, permissive)
VALIDATION_MODE=normal

# Auto-run validators after each agent
AUTO_VALIDATE=true

# Require human approval for overlaps
OVERLAP_APPROVAL_REQUIRED=true

# Maximum Write Zone length (lines)
MAX_WRITE_ZONE_LENGTH=8

# Skills integration enabled
SKILLS_ENABLED=true

# Log level (debug, info, warn, error)
LOG_LEVEL=info
```

---

## Troubleshooting Common Issues

### "Task.md not found"
**Solution**: Create `.claude/task.md` with your task specification.

### "Agent not found"
**Solution**: Check agent name matches file in `.claude/agents/`.

### "Write Zone violation"
**Solution**: Agent wrote outside its designated zone. Review `context_session_1.md`.

### "Scorecard failures"
**Solution**: Review `.claude/work.md` and address each FAIL item.

### "Secret detected"
**Solution**: Remove API keys/passwords from output, use placeholders.

### "Format mismatch"
**Solution**: Ensure output matches agent's template specification.

---

## Quick Start Checklist

Before running any agent, ensure:

- [ ] `.claude/task.md` exists with clear objective
- [ ] `.claude/tasks/context_session_1.md` initialized
- [ ] Agent definition and contract reviewed
- [ ] Previous agents' work reviewed (if applicable)
- [ ] Required skills/tools available

After agent runs:

- [ ] Output in `.claude/work.md` reviewed
- [ ] Scorecard shows PASS or justified FAIL
- [ ] Write Zone updated
- [ ] Validators pass
- [ ] Next agent can proceed

---

**Version**: 1.0.0  
**Last Updated**: November 2025

---

## Getting Help

1. Check agent definition for capabilities
2. Review contract for scope
3. Examine Write Zone for context
4. Run validators for specific issues
5. Review scorecard for quality gates
6. Consult workflows.md for patterns
7. Read hooks documentation for rules

For system-level issues, review `.claude/claude.json` configuration.
