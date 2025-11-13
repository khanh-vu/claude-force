# Examples Directory

This directory contains sample tasks and expected agent outputs to help you understand how to use the Claude Multi-Agent System effectively.

---

## Directory Structure

```
examples/
├── README.md                    # This file
├── task-examples/               # Sample task.md files
│   ├── frontend-feature-task.md
│   ├── backend-api-task.md
│   └── database-schema-task.md
└── output-examples/             # Sample work.md outputs
    ├── frontend-architect-output.md
    ├── backend-architect-output.md
    └── database-architect-output.md
```

---

## How to Use Examples

### 1. Study Task Examples

Review `task-examples/` to see how to write effective task specifications:

- **frontend-feature-task.md** - Complete example of a UI feature task
- **backend-api-task.md** - Example of an API development task

Each example demonstrates:
- Clear objective and requirements
- Acceptance criteria
- Context and constraints
- Expected deliverables
- Success metrics

### 2. Review Output Examples

Study `output-examples/` to see what agents should produce:

- **frontend-architect-output.md** - Complete architecture document

Each output example shows:
- Proper formatting and structure
- Complete deliverables
- Acceptance checklist (all items PASS)
- Scorecard validation
- Next steps and handoffs

---

## Using Examples as Templates

### Copy a Task Example

```bash
# Copy example to your task.md
cp .claude/examples/task-examples/frontend-feature-task.md .claude/task.md

# Edit for your specific needs
nano .claude/task.md
```

### Compare Your Output

```bash
# After running an agent, compare your work.md to expected output
diff .claude/work.md .claude/examples/output-examples/frontend-architect-output.md
```

---

## Example Workflows

### Example 1: Frontend Feature

**Task**: `frontend-feature-task.md`

**Workflow**:
1. Copy task to `.claude/task.md`
2. Run `frontend-architect` → produces architecture
3. Run `ui-components-expert` → produces components
4. Run `frontend-developer` → implements feature
5. Run `qc-automation-expert` → adds tests

### Example 2: Backend API

**Task**: `backend-api-task.md`

**Workflow**:
1. Copy task to `.claude/task.md`
2. Run `backend-architect` → API design
3. Run `database-architect` → schema design
4. Run `python-expert` → implementation
5. Run `qc-automation-expert` → tests

---

## Creating Your Own Examples

### Adding a Task Example

1. Create a real task you want to accomplish
2. Fill in ALL sections of the task template
3. Save to `task-examples/your-task.md`
4. Run the agents and validate
5. Clean up and document

### Adding an Output Example

1. Run an agent on a real task
2. Ensure all quality gates pass
3. Copy the output to `output-examples/`
4. Annotate with explanatory comments
5. Verify it serves as a good reference

---

## Quality Checklist for Examples

When creating examples, ensure:

- [ ] Task has clear objective
- [ ] All acceptance criteria are specific and measurable
- [ ] Context provides sufficient background
- [ ] Deliverables are well-defined
- [ ] Output follows agent template exactly
- [ ] Scorecard shows all PASS
- [ ] Acceptance checklist is complete
- [ ] No secrets or sensitive data
- [ ] Example is realistic and useful

---

## Available Examples

### Task Examples

| File | Type | Agent | Complexity |
|------|------|-------|------------|
| `frontend-feature-task.md` | Frontend | frontend-architect, ui-components-expert, frontend-developer | High |
| `backend-api-task.md` | Backend | backend-architect, database-architect, python-expert | High |

### Output Examples

| File | Agent | Shows |
|------|-------|-------|
| `frontend-architect-output.md` | frontend-architect | Complete architecture with diagrams, types, contracts |

---

## Learning Path

### Beginner

1. Read `frontend-feature-task.md` - understand task structure
2. Review `frontend-architect-output.md` - see expected output
3. Try modifying the frontend task for a simpler feature
4. Run the frontend-architect agent
5. Compare your output to the example

### Intermediate

1. Study multiple task examples
2. Create your own task from scratch
3. Run a complete workflow
4. Validate against quality gates
5. Document lessons learned

### Advanced

1. Create custom workflows
2. Add your own task and output examples
3. Develop new agents
4. Share examples with community

---

## Common Patterns

### Pattern 1: Feature Development

```
Task: Specific feature request
└─> frontend-architect (architecture)
    └─> ui-components-expert (components)
        └─> frontend-developer (implementation)
            └─> qc-automation-expert (tests)
```

### Pattern 2: API Development

```
Task: API endpoint request
└─> backend-architect (design)
    └─> database-architect (schema)
        └─> python-expert (implementation)
            └─> api-documenter (docs)
```

### Pattern 3: Full Stack

```
Task: Complete feature with frontend and backend
└─> frontend-architect + backend-architect (parallel)
    └─> database-architect
        └─> python-expert + ui-components-expert (parallel)
            └─> frontend-developer
                └─> qc-automation-expert
                    └─> deployment-integration-expert
```

---

## Tips for Writing Good Tasks

### Do's ✅

- Be specific about requirements
- Include concrete acceptance criteria
- Provide context and constraints
- Define success metrics
- List dependencies clearly
- Specify technical requirements

### Don'ts ❌

- Vague objectives ("make it better")
- Missing acceptance criteria
- Unclear scope
- No context or background
- Unrealistic constraints
- Missing technical details

---

## Tips for Validating Outputs

### Check for Quality

1. **Completeness**: All deliverables present?
2. **Format**: Matches agent template?
3. **Scorecard**: All items PASS?
4. **Acceptance**: Criteria addressed?
5. **Documentation**: Clear and thorough?
6. **Handoff**: Next steps defined?

### Common Issues

| Issue | Solution |
|-------|----------|
| Missing sections | Review agent definition for required sections |
| Scorecard failures | Address each FAIL item before proceeding |
| Unclear next steps | Specify which agent should run next |
| Missing types/contracts | Add comprehensive type definitions |
| Poor documentation | Add comments and usage examples |

---

## Contributing Examples

Have a great example to share?

1. Ensure it follows quality standards
2. Remove any sensitive/proprietary information
3. Add it to the appropriate directory
4. Update this README
5. Consider submitting a PR (if open source)

---

## Questions?

- Check the main README: `../README.md`
- Review agent definitions: `../agents/`
- Read governance docs: `../hooks/README.md`
- Consult commands reference: `../commands.md`

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0
**Status**: Living document - add examples as you create them
