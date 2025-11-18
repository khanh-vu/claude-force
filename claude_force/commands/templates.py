"""
Claude Folder Templates

Templates for .claude folder structure files.
Extracted from restructure.py for better code organization.
"""

import json

# README.md template
README_TEMPLATE = """# Claude Multi-Agent System

A professional multi-agent orchestration system for Claude.

## 🎯 Purpose

This system enables you to:
- Break complex tasks into specialized agent workflows
- Maintain clear separation of concerns
- Enforce quality gates and governance
- Track progress across multi-step projects

## 📁 Directory Structure

```
.claude/
├── README.md           # This file
├── claude.json         # Configuration
├── task.md             # Current task
├── work.md             # Agent outputs
├── scorecard.md        # Quality checklist
├── agents/             # Agent definitions
├── contracts/          # Agent contracts
├── hooks/              # Governance hooks
├── macros/             # Reusable instructions
└── tasks/              # Task context
```

## 🚀 Quick Start

1. Edit `task.md` with your objective
2. Run appropriate agent
3. Review output in `work.md`
4. Validate against scorecard

---

Created by claude-force /restructure command
"""

# claude.json configuration template
CLAUDE_JSON_CONFIG = {
    "version": "1.0.0",
    "name": "Claude Multi-Agent System",
    "description": "Orchestration system for specialized development agents",
    "agents": {},
    "workflows": {},
    "governance": {
        "hooks_enabled": True,
        "pre_run_required": False,
        "post_run_validation": False,
        "validators": [],
    },
    "paths": {
        "task": "task.md",
        "work": "work.md",
        "scorecard": "scorecard.md",
        "agents": "agents/",
        "contracts": "contracts/",
        "hooks": "hooks/",
        "macros": "macros/",
        "skills": "skills/",
    },
    "rules": {
        "task_md_readonly": True,
        "require_write_zone_update": False,
        "no_secrets_in_output": True,
        "minimal_diffs_only": False,
        "scorecard_must_pass": False,
    },
}

# task.md template
TASK_TEMPLATE = """# Task: [Task Title]

## Objective
[Describe what needs to be accomplished]

## Requirements
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Acceptance Criteria
- [ ] [Criteria 1]
- [ ] [Criteria 2]
- [ ] [Criteria 3]

## Context
[Any additional context or constraints]

---

Created by claude-force /restructure command
"""

# scorecard.md template
SCORECARD_TEMPLATE = """# Quality Scorecard

## Requirements Met
- [ ] All requirements from task.md addressed
- [ ] Acceptance criteria fulfilled
- [ ] Edge cases considered

## Code Quality
- [ ] Clean, readable code
- [ ] Proper error handling
- [ ] Security best practices followed

## Documentation
- [ ] Code commented where necessary
- [ ] README updated (if applicable)
- [ ] API documented (if applicable)

## Testing
- [ ] Unit tests included (if applicable)
- [ ] Integration tests considered
- [ ] Test coverage adequate

## Performance
- [ ] No obvious performance issues
- [ ] Scalability considered
- [ ] Resource usage reasonable

---

Created by claude-force /restructure command
"""

# work.md template
WORK_TEMPLATE = """# Work Output

## Agent: [Agent Name]
**Date**: [Date]

### Deliverables

[Agent outputs go here]

### Write Zone
[Context and summary for next agents]

---

Created by claude-force /restructure command
"""

# commands.md template
COMMANDS_TEMPLATE = """# Common Commands

## Running Agents

```bash
# Run a single agent
claude-force run agent <agent-name> --task "description"

# Run a workflow
claude-force run workflow <workflow-name> --task-file task.md
```

## Validation

```bash
# Validate current output
claude-force validate

# Review project structure
claude-force review
```

---

Created by claude-force /restructure command
"""

# workflows.md template
WORKFLOWS_TEMPLATE = """# Multi-Agent Workflows

## Available Workflows

### Full-Stack Feature
```
1. frontend-architect
2. backend-architect
3. database-architect
4. implementation agents
5. qc-automation-expert
6. code-reviewer
```

### Bug Fix
```
1. bug-investigator
2. code-reviewer
3. qc-automation-expert
```

### Documentation
```
1. document-writer-expert
2. api-documenter
```

---

Created by claude-force /restructure command
"""


def get_claude_json_template() -> str:
    """Get claude.json template as JSON string"""
    return json.dumps(CLAUDE_JSON_CONFIG, indent=2)
