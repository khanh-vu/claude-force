---
description: Execute a complete multi-agent workflow
usage: /run-workflow <workflow-name>
---

# Run Workflow Command

Execute a predefined workflow with multiple agents in sequence.

## Available Workflows

### 1. full-stack-feature
Complete feature from architecture to deployment.

**Agents** (8):
1. frontend-architect
2. database-architect
3. backend-architect
4. python-expert
5. ui-components-expert
6. frontend-developer
7. qc-automation-expert
8. deployment-integration-expert

**Use for**: New features requiring both frontend and backend work.

### 2. frontend-only
Frontend-focused development workflow.

**Agents** (4):
1. frontend-architect
2. ui-components-expert
3. frontend-developer
4. qc-automation-expert

**Use for**: UI features, component libraries, client-side functionality.

### 3. backend-only
Backend API development workflow.

**Agents** (4):
1. backend-architect
2. database-architect
3. python-expert
4. qc-automation-expert

**Use for**: API endpoints, services, data processing.

### 4. documentation
Documentation generation workflow.

**Agents** (2):
1. document-writer-expert
2. api-documenter

**Use for**: Technical docs, API documentation, user guides.

## Workflow Execution

For each agent in the workflow:
1. Execute agent with full governance
2. Validate output
3. Confirm success before proceeding
4. If failure, stop workflow and report
5. Update progress in context file
6. Proceed to next agent

## Progress Tracking

The command will:
- Show current agent and progress (e.g., "Agent 3 of 8")
- Pause between agents for review (optional)
- Report completion status
- Provide summary of all artifacts

## Example

```
/run-workflow full-stack-feature
```

This will execute all 8 agents in the full-stack workflow.

## Options

```
/run-workflow full-stack-feature --no-pause
```
Run without pausing between agents.

```
/run-workflow frontend-only --start-from ui-components-expert
```
Resume workflow from specific agent.

## Notes

- Requires `.claude/task.md` to be properly filled out
- Each agent must pass validation before next one starts
- Can interrupt and resume later from same point
- Progress logged in `context_session_1.md`
