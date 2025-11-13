# Session Start Hook

**Purpose**: Initialize the Claude multi-agent system environment when a session begins.

**Trigger**: Automatically when Claude Code session starts

**Execution**: Claude Code native hook system

---

## What This Hook Does

When a Claude Code session starts, this hook:

1. ✅ Verifies system structure integrity
2. ✅ Creates missing required files
3. ✅ Initializes environment configuration
4. ✅ Displays welcome message with status
5. ✅ Provides quick start guidance

---

## Initialization Steps

### 1. Verify Directory Structure

Check that all required directories exist:

```bash
.claude/
├── agents/
├── contracts/
├── hooks/
│   └── validators/
├── macros/
├── tasks/
├── skills/
├── examples/
│   ├── task-examples/
│   └── output-examples/
└── commands/
```

**Action**: Create any missing directories.

---

### 2. Verify Required Files

Check core files exist:

```
✅ claude.json          - Agent configuration
✅ task.md              - Task template
✅ work.md              - Work output placeholder
✅ scorecard.md         - Quality checklist
✅ commands.md          - Commands reference
✅ workflows.md         - Workflow patterns
✅ README.md            - System documentation
```

**Action**: If any file is missing, create from template or warn user.

---

### 3. Initialize Context File

If no context file exists for this session:

```markdown
Create: .claude/tasks/context_session_1.md

With:
- Session metadata (started time, status)
- Write Zones for all agents
- Progress log
- Overlap requests section
- Shared context section
```

**Action**: Auto-create context file if missing.

---

### 4. Create work.md if Missing

If `.claude/work.md` doesn't exist:

```markdown
Create placeholder file with:
- Purpose description
- Expected sections
- Quality gates reference
- Status: Awaiting agent execution
```

---

### 5. Load Environment Configuration

Check for `.claude/.env`:

```bash
if [ -f .claude/.env ]; then
  echo "✅ Environment configuration loaded"
else
  echo "ℹ️  No .env file found (optional)"
  echo "   Copy .env.example to customize settings"
fi
```

---

### 6. Run System Health Check

Validate system integrity:

```bash
✅ All agents have definition files (12/12)
✅ All agents have contracts (12/12)
✅ All validators present (6/6)
✅ All workflows valid (4/4)
⚠️  work.md is empty (this is normal initially)
```

**Action**: Report any issues found.

---

### 7. Check for Existing Tasks

```bash
if task.md has content:
  echo "📋 Found existing task: [Task Title]"
  echo "   Status: [status]"
  echo "   Last updated: [date]"
  echo ""
  echo "Ready to continue work"
else:
  echo "📝 No task defined yet"
  echo "   Use: /new-task to create one"
  echo "   Or: Copy from examples/"
fi
```

---

### 8. Display Welcome Message

```markdown
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🤖 Claude Multi-Agent System                          ║
║   Version 1.0.0                                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

✅ System initialized successfully

## System Status

📊 **Agents**: 12 available
🔧 **Workflows**: 4 pre-built
✅ **Governance**: 6 validators active
📚 **Skills**: DOCX, XLSX, PPTX, PDF

## Quick Start

### New Task
```
/new-task                    # Create new task from template
```

### Run Agent
```
/run-agent frontend-architect    # Execute specific agent
/run-workflow full-stack-feature # Run complete workflow
```

### Check Status
```
/status                      # Show current progress
/validate-output             # Validate work.md
```

## Help

- 📖 Read: .claude/README.md
- 🎓 Examples: .claude/examples/
- 💡 Commands: .claude/commands.md
- ❓ Help: /help

---

**Ready to start building! 🚀**
```

---

## Implementation

### For Claude Code

This hook integrates with Claude Code's SessionStart system:

```yaml
# .claude/hooks/session-start.yaml (if supported)
name: Initialize Multi-Agent System
trigger: session_start
script: session-start.md
```

### Manual Trigger

If automatic hooks aren't supported, users can run manually:

```
Please initialize the Claude multi-agent system by:
1. Reading .claude/hooks/session-start.md
2. Following the initialization steps
3. Reporting system status
```

---

## Configuration

### Skip Initialization

If user wants to skip auto-initialization:

```bash
# In .env
SESSION_START_ENABLED=false
```

### Custom Welcome Message

```bash
# In .env
CUSTOM_WELCOME_MESSAGE="Welcome to MyCompany's Agent System"
```

### Silent Mode

```bash
# In .env
SESSION_START_SILENT=true  # Only show errors/warnings
```

---

## Troubleshooting

### Hook Not Running

**Issue**: Session starts but hook doesn't execute

**Solutions**:
1. Check if Claude Code supports SessionStart hooks
2. Manually trigger: "Run session-start initialization"
3. Check `.env` for `SESSION_START_ENABLED=false`

### Permission Errors

**Issue**: Cannot create files during initialization

**Solutions**:
1. Check directory permissions
2. Verify write access to `.claude/`
3. Run with appropriate permissions

### Missing Files

**Issue**: Some required files not found

**Solutions**:
1. Re-clone repository
2. Run: `git restore .claude/`
3. Copy missing files from examples

---

## Example Session Start Output

```bash
🔧 Initializing Claude Multi-Agent System...

✅ Directory structure verified
✅ Core files present (7/7)
✅ Created context file: context_session_1.md
✅ work.md placeholder created
✅ Environment loaded from .env
✅ System health check passed

📊 System Status:
   - Agents: 12
   - Workflows: 4
   - Validators: 6
   - Skills: 4

📋 Current Task:
   Title: Build Product Catalog UI
   Status: In Progress (3/8 agents complete)
   Next: Run ui-components-expert

💡 Quick Actions:
   /status              - Show detailed progress
   /run-agent ...       - Continue workflow
   /validate-output     - Check quality gates

⏱️  Initialization completed in 0.3s

Ready! 🚀
```

---

## Benefits of SessionStart Hook

1. **Automatic Setup** - No manual initialization needed
2. **Error Prevention** - Catches missing files early
3. **User Guidance** - Shows next steps immediately
4. **Consistency** - Same setup every session
5. **Health Monitoring** - Detects system issues
6. **Resume Support** - Picks up where you left off

---

## Future Enhancements

- [ ] Auto-detect git branch and adjust context
- [ ] Load team-specific configurations
- [ ] Integrate with project management tools
- [ ] Show recent commit messages
- [ ] Suggest relevant workflows based on task
- [ ] Auto-update agent definitions
- [ ] Check for system updates

---

**Version**: 1.0.0
**Status**: Ready for use
**Last Updated**: 2025-11-13

---

## Notes

- This hook is designed for Claude Code's SessionStart system
- If running outside Claude Code, users should manually initialize
- The hook is non-blocking - failures won't prevent work
- All actions are idempotent - safe to run multiple times
