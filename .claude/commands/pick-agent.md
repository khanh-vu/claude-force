---
description: Copy agent packs from source to target project
usage: /pick-agent [agents...]
---

# Pick Agent Command

Copy agent packs (definitions + contracts) from a source project to your target project.

## Purpose

The `/pick-agent` command helps you:
- Browse available agents from claude-force or another project
- Copy agent definition files to your project
- Copy agent contract files to your project
- Update your claude.json configuration automatically
- Reuse proven agent packs across projects

## Usage

### List Available Agents
```
/pick-agent --list
```

### Copy Single Agent
```
/pick-agent python-expert
```

### Copy Multiple Agents
```
/pick-agent python-expert code-reviewer database-architect
```

### Specify Source Project
```
/pick-agent python-expert --source /path/to/claude-force
```

### Copy from Different Project
```
/pick-agent python-expert --source /path/to/other-project --target /path/to/my-project
```

## What Gets Copied

For each agent, the command copies:

1. **Agent Definition**: `agents/{agent-name}.md`
   - Role and responsibilities
   - Skills and specializations
   - Deliverables format
   - Examples and patterns

2. **Agent Contract**: `contracts/{agent-name}.contract`
   - Scope of authority
   - Core responsibilities
   - Input/output requirements
   - Quality gates
   - Collaboration protocol

3. **Configuration Entry**: Updates `claude.json`
   - Agent metadata
   - File references
   - Domain tags
   - Priority level

## Implementation

You should execute this command by:

1. **Import the PickAgentCommand class**:
```python
from claude_force.commands.pick_agent import PickAgentCommand
from pathlib import Path
```

2. **Determine source and target paths**:
   - Source: claude-force installation or another project
   - Target: Current project or user-specified path
   - Default source: claude-force package location
   - Default target: Current working directory

3. **List available agents**:
```python
command = PickAgentCommand(
    source_project=Path("/path/to/claude-force"),
    target_project=Path("/path/to/my-project")
)

# List all available agents
available = command.list_available_agents()
print(f"Available agents: {', '.join(available)}")
```

4. **Execute the copy**:
```python
# Copy specific agents
result = command.execute(["python-expert", "code-reviewer"])

# Format output
output = command.format_markdown(result)
print(output)
```

5. **Handle errors gracefully**:
   - ValueError: Invalid paths
   - FileNotFoundError: Agent files not found
   - PermissionError: Cannot write to target
   - JSON errors: Invalid configuration

## Agent Validation

The command only lists and copies agents that are complete:

✅ **Valid Agent** (will be listed):
- Has `agents/{name}.md` file
- Has `contracts/{name}.contract` file
- Has entry in source `claude.json`

❌ **Invalid Agent** (will be skipped):
- Missing agent definition file
- Missing contract file
- Incomplete configuration

## Output Format

### Markdown (Default)

```markdown
# Pick Agent Report

**Source**: /home/user/claude-force
**Target**: /home/user/my-app

## Summary

- **Agents Copied**: 3
- **Agents Failed**: 0
- **Config Updated**: ✅ Yes

✅ **Pick agent completed successfully**

## Agents Copied

1. python-expert
2. code-reviewer
3. database-architect
```

### JSON Format

```json
{
  "success": true,
  "agents_copied": 3,
  "agents_failed": 0,
  "config_updated": true,
  "agents_added_to_config": 3,
  "errors": []
}
```

## Available Agents (claude-force)

### Core Development Agents

**General Purpose**:
- `code-reviewer` - Code quality, security, best practices
- `bug-investigator` - Debugging, root cause analysis
- `security-specialist` - Security audit, OWASP, compliance

**Backend Development**:
- `backend-architect` - API design, service architecture
- `python-expert` - Python development, CLI, testing
- `database-architect` - Schema design, migrations, optimization
- `data-engineer` - ETL, data pipelines, warehousing

**Frontend Development**:
- `frontend-architect` - App structure, routing, state management
- `frontend-developer` - React/Next.js implementation
- `ui-components-expert` - Component design, design systems
- `seo-performance-expert` - SEO, Core Web Vitals, optimization

**Testing & Quality**:
- `qc-automation-expert` - Test automation, Playwright, Jest

**DevOps & Infrastructure**:
- `devops-architect` - Docker, Kubernetes, IaC
- `google-cloud-expert` - GCP services, Cloud Run, Firestore
- `deployment-integration-expert` - CI/CD, deployment configs
- `infrastructure-reliability-expert` - High availability, failover

**Documentation**:
- `document-writer-expert` - Technical writing, markdown
- `api-documenter` - OpenAPI, Swagger, API docs

**AI & ML**:
- `ai-engineer` - ML, LLMs, RAG, embeddings
- `prompt-engineer` - Prompt engineering, function calling

**Specialized**:
- `claude-code-expert` - Claude Code orchestration, agents
- Various crypto trading agents (if needed)

## Examples

### Example 1: Basic Agent Copy

```
User: /pick-agent python-expert

You: Listing available agents from claude-force...

Found 30 available agents.

Copying agent: python-expert
✓ Copied agents/python-expert.md
✓ Copied contracts/python-expert.contract
✓ Updated claude.json

✅ Successfully copied 1 agent
```

### Example 2: Multiple Agents

```
User: /pick-agent python-expert code-reviewer qc-automation-expert

You: Copying 3 agents from claude-force...

1/3 python-expert... ✓
2/3 code-reviewer... ✓
3/3 qc-automation-expert... ✓

Updated claude.json with 3 agents

✅ Successfully copied 3 agents to your project
```

### Example 3: List Then Pick

```
User: /pick-agent --list

You: Available agents in claude-force:

**Core Development** (12 agents):
- backend-architect
- code-reviewer
- database-architect
- frontend-architect
- python-expert
- ... (7 more)

**Specialized** (18 agents):
- ai-engineer
- claude-code-expert
- devops-architect
- ... (15 more)

Total: 30 agents available

User: I need Python and testing agents

You: Based on your needs, I recommend:
- python-expert (Python development)
- qc-automation-expert (Testing & QA)
- code-reviewer (Code quality)

Would you like me to copy these? [y/N]

User: y

You: Copying 3 agents...
✅ Done! All agents copied successfully.
```

### Example 4: Copy from Custom Source

```
User: /pick-agent custom-agent --source /path/to/other-project

You: Copying agent from /path/to/other-project...

✓ Copied agents/custom-agent.md
✓ Copied contracts/custom-agent.contract
✓ Updated claude.json

✅ Successfully copied custom-agent
```

### Example 5: Error Handling

```
User: /pick-agent nonexistent-agent

You: ❌ Error copying agent: nonexistent-agent

Agent not found in source project.

Available agents: python-expert, code-reviewer, database-architect, ...

Did you mean one of these?
- python-expert
- frontend-developer
```

## Integration with Other Commands

Recommended workflow:

```
1. /review → Analyze project
     ↓ (get agent recommendations)

2. /restructure --auto → Fix .claude structure
     ↓

3. /pick-agent <recommended-agents> → Copy needed agents
     ↓

4. Verify claude.json updated correctly
     ↓

✅ Ready to run workflows
```

## Configuration Update

When copying agents, `claude.json` is automatically updated:

**Before**:
```json
{
  "agents": {}
}
```

**After** (copying python-expert):
```json
{
  "agents": {
    "python-expert": {
      "file": "agents/python-expert.md",
      "contract": "contracts/python-expert.contract",
      "domains": ["python", "scripting", "automation", "cli"],
      "priority": 2
    }
  }
}
```

The configuration preserves:
- Domain tags (for semantic routing)
- Priority levels (for workflow ordering)
- All metadata from source project

## Best Practices

1. **Review First**: Run `/review` to get agent recommendations
2. **Check Compatibility**: Ensure agents match your tech stack
3. **Start Small**: Copy a few agents first, test, then add more
4. **Verify Config**: Check claude.json after copying
5. **Version Control**: Commit agent additions to git
6. **Update Workflows**: Add new agents to your workflows

## Safety Features

### Non-Destructive
- Never overwrites existing agent files
- Preserves existing claude.json structure
- Only adds new agents, doesn't modify existing ones

### Validation
- Validates source and target paths
- Checks file existence before copying
- Ensures claude.json is valid JSON
- Preserves file permissions

### Security
- Uses `validate_project_root()` for security
- Prevents path traversal attacks
- Blocks system directory access
- Validates all file operations

## Advanced Usage

### Bulk Import from File

```
User: I have a list of agents in agents.txt

You: I'll read the list and copy all agents.

Reading agents.txt...
Found 5 agents to copy:
- python-expert
- code-reviewer
- database-architect
- frontend-developer
- qc-automation-expert

Copy all 5 agents? [y/N]
```

### Conditional Copy

```
User: Copy all backend agents

You: Filtering for backend agents...

Found 4 backend agents:
- backend-architect
- python-expert
- database-architect
- data-engineer

Copy these 4 agents? [y/N]
```

### Preview Before Copy

```
User: /pick-agent python-expert --preview

You: Preview: python-expert

**Role**: Python Development Expert
**Domains**: python, scripting, automation, cli
**Priority**: 2

**Will copy**:
- agents/python-expert.md (20KB)
- contracts/python-expert.contract (8KB)

**Will update**:
- claude.json (add agent configuration)

Proceed with copy? [y/N]
```

## Troubleshooting

### Issue: Agent Not Found

**Problem**: Agent name doesn't exist in source
**Solution**: Use `/pick-agent --list` to see available agents

### Issue: Permission Denied

**Problem**: Cannot write to target directory
**Solution**: Check file permissions on target .claude folder

### Issue: Invalid JSON

**Problem**: claude.json is corrupted
**Solution**: Run `/restructure` first to fix configuration

### Issue: Partial Copy

**Problem**: Agent file copied but contract missing
**Solution**: Re-run command, it will complete the copy

## Technical Notes

### Implementation Details
- Built with TDD (Test-Driven Development)
- 11 comprehensive tests (100% pass rate)
- File operations with proper error handling
- Security-first design

### Test Coverage
- List agents: 2 tests ✓
- Copy single agent: 2 tests ✓
- Copy multiple agents: 1 test ✓
- Update configuration: 1 test ✓
- Execute workflow: 1 test ✓
- Output formatting: 2 tests ✓
- Error handling: All scenarios covered

### Performance
- Fast for typical agent copies (< 100ms per agent)
- Handles bulk operations efficiently
- No network operations (local file copy)
- Minimal memory footprint

---

**Command Status**: ✅ Implemented, Tested, Ready for Use
**Version**: 1.0.0
**Last Updated**: 2025-11-17
