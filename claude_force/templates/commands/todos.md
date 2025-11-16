---
description: Manage quick task captures and ideas
usage: /todos [--add TEXT | --complete ID | --list | --archive]
---

# Todos Command

Quick capture for ideas, tasks, and reminders without leaving your workflow.

## When to Use

**Use `/todos` for:**
- Quick ideas during work (mid-workflow capture)
- Reminders for later
- Exploratory notes
- Task backlog management

**Use `/new-task` for:**
- Formal task definition with structured requirements
- Agent orchestration and workflow execution
- Production work with validation

**Pro tip**: Use `/todos` to capture, then convert to `/new-task` when ready to execute.

---

## Quick Add

Capture an idea instantly:

```
/todos --add "Fix performance issue in ProductList component"
```

**What happens:**
1. Creates `.claude/TO-DOS.md` if it doesn't exist
2. Generates unique todo ID
3. Prompts for additional context (or accepts minimal input)
4. Suggests relevant agents/workflows automatically
5. Checks for similar existing todos

**Output:**
```
✅ Added todo: todo-20251116-143022-a3f4b2

Similar todos found:
  1. Optimize ProductList rendering (added 2 days ago)

Continue with new todo? (y/n): y

💡 Suggested agents: frontend-developer, performance-expert
💡 Suggested workflow: performance-optimization

Todo saved to .claude/TO-DOS.md
```

---

## View All Todos

List and select todos interactively:

```
/todos
```

or

```
/todos --list
```

**Output:**
```markdown
# Active Todos (5)

## 🔄 In Progress (1)

**1** 🔴 Refactor authentication module
  **Why**: Improve security and maintainability
  **Files**: src/auth/auth.ts:45-120
  **Added**: 2 hours ago
  **Suggested**: backend-architect, security-specialist

## 🔴 High Priority (2)

**2** Fix performance issue in ProductList component
  **Why**: Page load takes 3+ seconds with 100 items
  **Files**: src/components/ProductList.tsx:67-89
  **Added**: 1 hour ago
  **Suggested**: frontend-developer, performance-expert

**3** Add comprehensive error handling
  **Why**: Users see generic errors, hard to debug
  **Files**: src/api/client.ts
  **Added**: 3 hours ago
  **Suggested**: backend-architect

## 🟡 Medium Priority (2)

**4** Update API documentation
  **Why**: Endpoints changed but docs outdated
  **Added**: 1 day ago
  **Suggested**: document-writer-expert

**5** Investigate caching strategy
  **Why**: Explore Redis vs in-memory for session data
  **Added**: 2 days ago
  **Suggested**: backend-architect

---

Select todo (1-5), or:
  [a] Add new todo
  [c] Archive completed
  [0] Cancel

Your choice:
```

**After selecting a todo (e.g., 2):**

```
📋 Todo #2: Fix performance issue in ProductList component

**Why This Matters:**
Page load takes 3+ seconds with 100 items. Users experiencing slow interface.

**Success Criteria:**
- [ ] Page loads in < 1 second with 100 items
- [ ] No layout shifts during render
- [ ] Maintains smooth scrolling

**Problem:**
ProductList component re-renders entire list on every state change. No virtualization.

**Current State:**
- Files: src/components/ProductList.tsx:67-89
- Current Behavior: Renders all items at once, slow with large datasets
- Desired Behavior: Virtualized rendering, fast performance

**Required Capabilities:**
- React performance optimization
- Virtual scrolling implementation
- Profiling and benchmarking

**Suggested Resources:**
- Agents: frontend-developer, performance-expert
- Workflows: performance-optimization

**Dependencies:**
- None

What would you like to do?
  [1] Convert to task (creates formal task.md)
  [2] Start workflow (runs suggested workflow)
  [3] Mark complete
  [4] Edit
  [5] Delete
  [0] Back to list

Your choice:
```

---

## Complete a Todo

Mark a todo as completed:

```
/todos --complete 2
```

**Output:**
```
✅ Marked complete: Fix performance issue in ProductList component
📦 Completed todo moved to "Recently Completed" section
💡 Run `/todos --archive` to archive all completed todos
```

---

## Archive Completed Todos

Move completed todos to archive:

```
/todos --archive
```

**Output:**
```
📦 Archiving completed todos...

Archived 3 todos to .claude/archives/todos/todos-2025-11-16.md:
  ✅ Fix performance issue in ProductList component
  ✅ Update API documentation
  ✅ Add error handling to login flow

Active todos remaining: 2
```

---

## Todo Format

Todos are stored in `.claude/TO-DOS.md` with this structure:

```markdown
### Fix performance issue in ProductList component

**Why This Matters:** Page load takes 3+ seconds with 100 items

**Success Criteria:**
- [ ] Page loads in < 1 second with 100 items
- [ ] No layout shifts during render

**Problem:** ProductList component re-renders entire list on every state change

**Current State:**
- **Files:** src/components/ProductList.tsx:67-89
- **Current Behavior:** Renders all items, slow with large datasets
- **Desired Behavior:** Virtualized rendering, fast performance

**Required Capabilities:**
- React performance optimization
- Virtual scrolling implementation

**Suggested Resources:**
- **Agents:** frontend-developer, performance-expert
- **Workflows:** performance-optimization

**Dependencies:**
- Depends on: none
- Blocks: none

**Metadata:**
- **ID:** `todo-20251116-143022-a3f4b2`
- **Priority:** high
- **Complexity:** moderate
- **Status:** active
- **Estimated Cost:** $0.15
- **Added:** 2025-11-16T14:30:22
- **Tags:** #performance, #frontend
```

---

## Advanced Usage

### Filter by Priority

```
/todos --priority high
```

### Filter by Tags

```
/todos --tags performance,frontend
```

### Show Completed

```
/todos --show-completed
```

### Export

```
/todos --export todos-backup.md
```

---

## Integration with Other Commands

### Todo → Task Workflow

```
1. /todos --add "Implement user authentication"
2. /todos (select todo #1)
3. Choose option [1] Convert to task
4. /new-task (auto-populated from todo)
5. /run-workflow full-stack-feature
```

### During Workflow

When running a workflow, capture ideas without interrupting:

```
# While /run-workflow is running
/todos --add "Refactor this pattern later"
# Continues workflow without interruption
```

---

## Examples

### Example 1: Quick Capture During Code Review

```
# During code review, notice an issue
/todos --add "Fix SQL injection vulnerability in search endpoint"

# Gets AI suggestions
💡 Suggested: security-specialist, backend-architect
💡 Priority: HIGH (detected from keywords)
✅ Saved
```

### Example 2: Managing Backlog

```
/todos

# Shows list, select #3
# Choose [1] Convert to task
# /new-task auto-opens with todo context
# Review and run workflow
```

### Example 3: End-of-Day Review

```
/todos --archive    # Clean up completed
/todos --list       # Review what's left
# Note top priorities for tomorrow
```

---

## Tips & Best Practices

**Capture Immediately**
- Don't interrupt your flow
- Minimal info to start (can refine later)
- AI suggests agents/workflows automatically

**Success Criteria**
- Make them specific and measurable
- Think "How will I know this is done?"
- AI uses these to validate completion

**Use Tags**
- Organize by theme (#performance, #security, #refactor)
- Filter and group related todos
- Track cross-cutting concerns

**Dependencies**
- Link related todos
- Understand task order
- Plan complex workflows

**Regular Review**
- Start sessions with `/todos`
- Archive completed weekly
- Convert high-priority to tasks

---

## Troubleshooting

**Issue**: "Duplicate todo detected"
**Solution**: Review similar todos, choose to skip, replace, or add anyway

**Issue**: "TO-DOS.md not found"
**Solution**: Will be created automatically on first `/todos --add`

**Issue**: "Invalid todo format"
**Solution**: Check TO-DOS.md follows template format. See "Todo Format" section above.

**Issue**: "Agent suggestions not working"
**Solution**: Ensure SemanticSelector is enabled. Fallback: manual agent selection works.

---

## Files

- **Active**: `.claude/TO-DOS.md` - Current todos
- **Archive**: `.claude/archives/todos/todos-YYYY-MM-DD.md` - Completed todos
- **Config**: `.claude/claude.json` - Todo settings (optional)

---

## Options Summary

| Option | Description | Example |
|--------|-------------|---------|
| `--add TEXT` | Quick add new todo | `/todos --add "Fix bug"` |
| `--list` | List all todos (default) | `/todos --list` |
| `--complete ID` | Mark todo complete | `/todos --complete 3` |
| `--archive` | Archive completed todos | `/todos --archive` |
| `--priority LEVEL` | Filter by priority | `/todos --priority high` |
| `--tags TAG1,TAG2` | Filter by tags | `/todos --tags performance` |
| `--show-completed` | Include completed todos | `/todos --show-completed` |
| `--export PATH` | Export to file | `/todos --export backup.md` |

---

**Last Updated**: 2025-11-16
