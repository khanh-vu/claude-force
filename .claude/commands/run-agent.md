---
description: Run a specific agent with full governance
usage: /run-agent <agent-name>
---

# Run Agent Command

Execute the specified agent with complete pre-run and post-run validation.

## Instructions

1. Load all governance hooks from `.claude/hooks/`
2. Read `.claude/task.md` to understand requirements
3. Load the agent definition from `.claude/agents/{agent-name}.md`
4. Load the agent contract from `.claude/contracts/{agent-name}.contract`
5. Read context from `.claude/tasks/context_session_1.md`
6. Load scorecard from `.claude/scorecard.md`
7. Execute the agent following its specification
8. Write output to `.claude/work.md`
9. Update Write Zone in `context_session_1.md`
10. Validate output against all validators
11. Provide summary of completion status

## Available Agents

- frontend-architect
- backend-architect
- python-expert
- database-architect
- ui-components-expert
- deployment-integration-expert
- devops-architect
- google-cloud-expert
- qc-automation-expert
- document-writer-expert
- api-documenter
- frontend-developer

## Example

```
/run-agent frontend-architect
```

This will execute the frontend-architect agent with full governance.
