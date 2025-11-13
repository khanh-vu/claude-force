---
description: Create a new task from template
usage: /new-task
---

# New Task Command

Initialize a new task in `.claude/task.md` using the standard template.

## Process

1. Read the task template from `.claude/task.md`
2. If task.md already has content, archive it
3. Create new task.md with template structure
4. Prompt for key information:
   - Task title
   - Objective
   - Priority (High/Medium/Low)
   - Type (Feature/Bug Fix/Refactor/Documentation)
5. Fill in template with provided information
6. Leave other sections for user to complete

## Template Structure

The generated task will include:

- **Objective**: Clear goal statement
- **Requirements**: Functional, non-functional, technical
- **Context**: Background, assumptions, constraints
- **Acceptance Criteria**: Specific, measurable criteria
- **Scope**: What's in and out of scope
- **Resources**: Links to designs, docs, data
- **Deliverables**: Expected outputs
- **Success Metrics**: How to measure success
- **Workflow**: Suggested agent sequence
- **Risk Assessment**: Potential risks and mitigations
- **Timeline**: Estimated phases and duration

## Interactive Mode

```
/new-task

> Task title: Build Product Catalog UI
> Priority: High
> Type: Feature
> Brief objective: Create responsive product catalog with filters

✅ Created new task in .claude/task.md
📝 Please complete remaining sections before running agents
```

## Quick Mode

```
/new-task --quick --title "Add search feature" --type Feature
```

## Archive Previous Task

If `.claude/task.md` exists:
```
📦 Archived previous task to .claude/archives/task-2025-11-13.md
✅ Created new task.md
```

## Next Steps After Creation

1. Complete all task sections
2. Review acceptance criteria
3. Select appropriate workflow
4. Run first agent: `/run-agent <agent-name>`

## Example Generated Task

```markdown
# Task: Build Product Catalog UI

**Created**: 2025-11-13
**Owner**: [Your Name]
**Priority**: High
**Type**: Feature

## Objective

Create responsive product catalog with filters

[... rest of template ...]
```

## Options

- `--quick`: Skip interactive prompts
- `--title <title>`: Set task title
- `--type <type>`: Set task type
- `--priority <level>`: Set priority
- `--example <name>`: Use example task as starting point
