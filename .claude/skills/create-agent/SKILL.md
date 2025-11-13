# Create Agent Skill

## Overview
Comprehensive guide and templates for creating new Claude Code agents following best practices and patterns. This skill provides step-by-step instructions, templates, and examples for agent creation.

## Capabilities
- Agent definition template generation
- Contract creation following standard format
- Domain and responsibility definition
- Integration with claude.json
- Quality validation checklist

---

## Agent Creation Process

### Step 1: Define Agent Purpose

Before creating an agent, clearly define:
1. **Role**: What is this agent's primary role?
2. **Domain**: What specific domain expertise does it have?
3. **Responsibilities**: What specific tasks will it perform?
4. **Boundaries**: What will it NOT do?
5. **Dependencies**: Which other agents does it depend on?

### Step 2: Agent Definition Template

```markdown
# [Agent Name] Agent

## Role
[Clear, one-sentence role definition]

## Domain Expertise
- [Domain area 1]
- [Domain area 2]
- [Domain area 3]

## Skills & Specializations

### [Category 1]
- **[Skill/Tool 1]**: [Description, key features, use cases]
- **[Skill/Tool 2]**: [Description, key features, use cases]

### [Category 2]
- **[Skill/Tool 3]**: [Description, key features, use cases]

## Implementation Patterns

### Pattern 1: [Pattern Name]
```language
# Code example demonstrating common usage pattern
```
[Explanation of when and how to use this pattern]

### Pattern 2: [Pattern Name]
```language
# Another common pattern
```
[Explanation]

## Responsibilities

1. **[Responsibility Area 1]**
   - [Specific task 1]
   - [Specific task 2]

2. **[Responsibility Area 2]**
   - [Specific task 1]
   - [Specific task 2]

## Boundaries (What This Agent Does NOT Do)

- Does not [limitation 1] (delegate to [other-agent])
- Does not [limitation 2] (delegate to [other-agent])
- Focuses on [primary focus] only

## Dependencies

- **[Agent 1]**: For [reason]
- **[Agent 2]**: For [reason]

## Quality Standards

### Code Quality
- [Standard 1]
- [Standard 2]

### [Domain] Quality
- [Standard 1]
- [Standard 2]

## Output Format

### Work Output Structure
```markdown
# [Agent Name] Implementation Summary

## Objective
[What was requested]

## [Section 1]
[Content]

## [Section 2]
[Content]

## Next Steps
[Recommendations]
```

## Tools & Technologies

### Required
- [Tool 1]
- [Tool 2]

### Commonly Used
- [Tool 3]
- [Tool 4]

## Best Practices

1. **[Practice 1]**: [Description]
2. **[Practice 2]**: [Description]
3. **[Practice 3]**: [Description]

## Success Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

**Version**: 1.0.0
**Last Updated**: [Date]
**Maintained By**: [Team]
```

### Step 3: Agent Contract Template

```markdown
# [Agent Name] - Agent Contract

## Agent Identity
- **Name**: [agent-name-kebab-case]
- **Type**: [Agent Type/Role]
- **Version**: 1.0.0

## Scope of Authority

This agent has FINAL authority over:
- [Authority area 1]
- [Authority area 2]
- [Authority area 3]

## Core Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]

## Deliverables

This agent MUST deliver:
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

## Boundaries (What This Agent Does NOT Do)
- Focuses on [primary focus] only
- Does not [limitation 1]
- Does not [limitation 2]

## Dependencies
- [Agent 1] for [reason]
- [Agent 2] for [reason]

## Input Requirements

### Required Inputs
- `.claude/task.md` with clear objective and acceptance criteria
- Context from previous agents (if part of workflow) in `tasks/context_session_1.md`

### Optional Inputs
- [Optional input 1]
- [Optional input 2]

## Output Requirements

### MUST Include
1. Complete deliverables as specified above
2. [Specific output requirement 1]
3. [Specific output requirement 2]
4. Acceptance Checklist (all items marked PASS/FAIL)
5. Scorecard appended with PASS/FAIL ticks
6. Write Zone update (3-8 lines) in `tasks/context_session_1.md`

### Output Location
- Primary: `.claude/work.md`
- Context: Own Write Zone in `tasks/context_session_1.md`

### Output Format
- Follow the format specified in the agent's definition file
- [Format requirement 1]
- [Format requirement 2]

## Quality Gates

### Pre-execution Checks
- [ ] `.claude/task.md` exists and is readable
- [ ] Required dependencies (if any) are satisfied
- [ ] All hooks loaded (`.claude/hooks/*`)
- [ ] Tool scope understood and respected
- [ ] [Domain-specific check]

### Post-execution Validation
- [ ] All deliverables present
- [ ] [Domain-specific validation 1]
- [ ] [Domain-specific validation 2]
- [ ] Acceptance Checklist complete (all PASS)
- [ ] Scorecard appended with PASS marks
- [ ] Write Zone updated with summary
- [ ] No secrets or API keys in output
- [ ] Minimal diff discipline maintained
- [ ] Format matches specification

## Collaboration Protocol

### Before Starting
1. Read `.claude/task.md` fully
2. Check `tasks/context_session_1.md` for context from previous agents
3. Review contracts from dependency agents (if applicable)
4. Load all hooks from `.claude/hooks/`
5. [Domain-specific preparation step]

### During Execution
1. Work within defined scope only
2. [Domain-specific execution guideline]
3. Respect boundaries - don't overlap with other agents
4. Follow quality gates and guardrails

### After Completion
1. Write complete output to `.claude/work.md`
2. Append summary to own Write Zone
3. [Domain-specific completion step]
4. Mark completion in context

## Governance & Compliance

### Must Follow
- All rules in `.claude/hooks/pre-run.md`
- All validators in `.claude/hooks/validators/`
- All rules in `.claude/hooks/post-run.md`
- Agent-specific quality gates
- [Domain-specific best practices]

### Must NOT Do
- Edit `.claude/task.md`
- Write outside of `.claude/work.md` and own Write Zone
- Include secrets, API keys, or sensitive data
- Make wide, unfocused changes
- Overlap with other agents' scope
- [Domain-specific prohibition]

## Escalation & Overlap

### If Scope Is Unclear
1. Document the ambiguity
2. Propose options with trade-offs
3. Pick a reasonable default
4. Note the assumption in output

### If Overlap with Another Agent
1. File an **Overlap Request** to that agent
2. Wait for approval (logged in Write Zone)
3. Proceed after approval received
4. Document the collaboration

## Success Criteria

This agent's output is considered successful when:
- [ ] [Success criterion 1]
- [ ] [Success criterion 2]
- [ ] Quality gates pass
- [ ] Acceptance Checklist shows all PASS
- [ ] Scorecard shows all PASS
- [ ] Write Zone updated
- [ ] No governance violations

## [Domain]-Specific Requirements

### For [Specific Task Type]
- [ ] [Requirement 1]
- [ ] [Requirement 2]
- [ ] [Requirement 3]

## Change Management

Changes to this contract require:
1. Human approval
2. Version increment
3. Dated note in Progress Log of `context_session_1.md`
4. Notification to dependent agents

---

**Contract Effective Date**: [Date]
**Last Updated**: [Date]
**Approved By**: System Architect
```

### Step 4: Register in claude.json

Add the agent to `.claude/claude.json`:

```json
{
  "agents": {
    "agent-name": {
      "file": "agents/agent-name.md",
      "contract": "contracts/agent-name.contract",
      "domains": ["domain1", "domain2", "domain3"],
      "priority": 2
    }
  }
}
```

**Priority Guidelines**:
- **Priority 1**: Core architects (frontend, backend, database)
- **Priority 2**: Specialized experts (python, security, AI/ML)
- **Priority 3**: Support roles (deployment, documentation)

### Step 5: Validation Checklist

Before finalizing the agent:

**Agent Definition:**
- [ ] Role is clearly defined in one sentence
- [ ] Domain expertise is comprehensive
- [ ] Skills are organized in logical categories
- [ ] Implementation patterns are provided with code examples
- [ ] Responsibilities are specific and actionable
- [ ] Boundaries are explicit
- [ ] Dependencies are identified
- [ ] Output format is well-defined
- [ ] Tools and technologies are listed
- [ ] Best practices are documented
- [ ] Success criteria are measurable

**Agent Contract:**
- [ ] Agent identity section is complete
- [ ] Scope of authority is clearly defined
- [ ] Core responsibilities align with agent definition
- [ ] Deliverables are specific and measurable
- [ ] Boundaries match agent definition
- [ ] Dependencies are listed
- [ ] Input/output requirements are clear
- [ ] Quality gates are comprehensive
- [ ] Collaboration protocol is defined
- [ ] Governance rules are specified
- [ ] Success criteria are measurable
- [ ] Domain-specific requirements included

**Integration:**
- [ ] Agent is registered in claude.json
- [ ] Domains are accurately specified
- [ ] Priority is appropriate
- [ ] File paths are correct
- [ ] No conflicts with existing agents

## Agent Design Best Practices

### 1. Single Responsibility Principle
Each agent should have ONE primary responsibility:
- ✅ Good: "Frontend Architect - designs React component architecture"
- ❌ Bad: "Full Stack Developer - does frontend, backend, database, and deployment"

### 2. Clear Boundaries
Explicitly state what the agent does NOT do:
- Prevents scope creep
- Clarifies dependencies
- Reduces agent overlap
- Improves orchestration

### 3. Concrete Deliverables
Specify exactly what the agent must produce:
- ✅ Good: "React component files, TypeScript types, unit tests, Storybook stories"
- ❌ Bad: "Frontend code"

### 4. Domain Expertise Depth
Provide comprehensive domain knowledge:
- List specific tools, frameworks, libraries
- Include version information when relevant
- Provide patterns and best practices
- Include code examples

### 5. Workflow Integration
Consider how the agent fits into workflows:
- What agents come before this one?
- What agents depend on this one's output?
- What context does it need?
- What context does it provide?

## Common Agent Patterns

### Pattern 1: Architect Agent
**Characteristics**:
- High-level design authority
- Creates blueprints and specifications
- Defines architecture and patterns
- Priority 1
- Few dependencies

**Examples**: frontend-architect, backend-architect, database-architect

### Pattern 2: Implementation Expert
**Characteristics**:
- Implements specific technology stack
- Produces working code
- Priority 2
- Depends on architects

**Examples**: python-expert, ui-components-expert, ai-engineer

### Pattern 3: Quality Agent
**Characteristics**:
- Reviews and validates work
- Provides feedback and recommendations
- Does not modify code
- Priority 2-3
- Depends on implementation agents

**Examples**: code-reviewer, security-specialist

### Pattern 4: Support Agent
**Characteristics**:
- Provides auxiliary services
- Documentation, deployment, configuration
- Priority 3
- Depends on multiple agents

**Examples**: document-writer-expert, deployment-integration-expert

## Example: Creating a "Mobile App Expert" Agent

### Step 1: Define Purpose
- **Role**: Mobile application development expert
- **Domain**: iOS and Android development, React Native, Flutter
- **Responsibilities**: Design mobile architecture, implement mobile features
- **Boundaries**: Does not design backend APIs, does not handle deployment
- **Dependencies**: backend-architect for API contracts

### Step 2: Create Agent Definition
Create `.claude/agents/mobile-app-expert.md` with:
- Detailed skills in React Native, Flutter, native iOS/Android
- Implementation patterns for common mobile patterns
- Platform-specific best practices

### Step 3: Create Contract
Create `.claude/contracts/mobile-app-expert.contract` with:
- Authority over mobile implementations
- Deliverables: mobile app code, platform configs, tests
- Quality gates specific to mobile development

### Step 4: Register
Add to `claude.json`:
```json
"mobile-app-expert": {
  "file": "agents/mobile-app-expert.md",
  "contract": "contracts/mobile-app-expert.contract",
  "domains": ["mobile", "react-native", "flutter", "ios", "android"],
  "priority": 2
}
```

### Step 5: Create Workflows
Add mobile-focused workflows:
```json
"workflows": {
  "mobile-feature": [
    "backend-architect",
    "mobile-app-expert",
    "code-reviewer",
    "document-writer-expert"
  ]
}
```

## Troubleshooting

### Issue: Agent Scope Too Broad
**Problem**: Agent tries to do too many things
**Solution**: Split into multiple agents with specific focuses

### Issue: Overlapping Agents
**Problem**: Multiple agents have same responsibilities
**Solution**: Clarify boundaries, use dependencies, redesign agent scope

### Issue: Agent Too Narrow
**Problem**: Agent has very limited use cases
**Solution**: Combine with related agent or expand scope slightly

### Issue: Missing Dependencies
**Problem**: Agent needs info from other agents
**Solution**: Add explicit dependencies in contract

## Agent Maintenance

### When to Update an Agent
- New tools/frameworks emerge in the domain
- Best practices evolve
- Agent boundaries need clarification
- Performance issues identified
- User feedback indicates improvements needed

### Versioning
- Increment version when making changes
- Document changes in contract
- Notify dependent agents
- Update workflows if needed

## Conclusion

Creating effective Claude Code agents requires:
1. Clear role and scope definition
2. Comprehensive domain expertise
3. Well-defined boundaries
4. Formal contracts
5. Quality validation
6. Proper integration

Follow this skill's templates and best practices to create high-quality, maintainable agents that work well in multi-agent workflows.

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: Claude Code Team
