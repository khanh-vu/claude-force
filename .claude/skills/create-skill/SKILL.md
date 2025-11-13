# Create Skill Skill

## Overview
Comprehensive guide and templates for creating new Claude Code skills. This skill provides step-by-step instructions, structure patterns, and examples for skill development.

## Capabilities
- Skill structure definition
- Pattern documentation
- Example creation
- Integration with agents
- Best practices documentation

---

## Skill Creation Process

### Step 1: Define Skill Purpose

Before creating a skill, clearly define:
1. **What**: What capability does this skill provide?
2. **Why**: Why is this skill needed?
3. **Who**: Which agents will use this skill?
4. **When**: In what scenarios is this skill used?
5. **How**: What patterns/examples will it provide?

### Step 2: Skill Directory Structure

Create a skill with this standard structure:

```
skill-name/
├── SKILL.md           # Main skill definition
├── README.md          # Overview and quick start
├── patterns/          # Reusable patterns (optional)
│   ├── pattern1.md
│   ├── pattern2.md
│   └── pattern3.md
└── examples/          # Example usage (optional)
    ├── example1.md
    └── example2.md
```

### Step 3: SKILL.md Template

```markdown
# [Skill Name] Skill

## Overview
[Clear description of what this skill provides - 2-3 sentences]

## Capabilities
- [Capability 1]
- [Capability 2]
- [Capability 3]

---

## [Section 1: Core Concept/Framework]

### [Subsection 1.1]
[Explanation of key concept or pattern]

**Example**:
```language
# Code example demonstrating the concept
```

[Explanation of the example]

### [Subsection 1.2]
[Another important concept]

**Pattern**:
```markdown
# Template or pattern for common usage
```

## [Section 2: Practical Patterns]

### Pattern 1: [Pattern Name]
**When to Use**: [Scenario description]

**Implementation**:
```language
# Complete, runnable code example
```

**Explanation**:
[Detailed explanation of how this works]

**Best Practices**:
- [Practice 1]
- [Practice 2]

### Pattern 2: [Pattern Name]
[Same structure as Pattern 1]

## [Section 3: Advanced Topics]

### [Advanced Topic 1]
[Detailed explanation with examples]

### [Advanced Topic 2]
[Detailed explanation with examples]

## Common Use Cases

### Use Case 1: [Scenario]
**Problem**: [Description of problem]

**Solution**:
```language
# Code solution
```

**Result**: [Expected outcome]

### Use Case 2: [Scenario]
[Same structure as Use Case 1]

## Best Practices

1. **[Practice 1]**: [Description and rationale]
2. **[Practice 2]**: [Description and rationale]
3. **[Practice 3]**: [Description and rationale]

## Anti-Patterns (What NOT to Do)

### Anti-Pattern 1: [Description]
**Problem**:
```language
# Example of what NOT to do
```

**Why It's Bad**: [Explanation]

**Better Approach**:
```language
# Correct way to do it
```

## Troubleshooting

### Issue 1: [Common problem]
**Symptoms**: [How to recognize this issue]
**Cause**: [Why this happens]
**Solution**: [How to fix it]

### Issue 2: [Common problem]
[Same structure as Issue 1]

## Related Skills
- [Related Skill 1]: [How it relates]
- [Related Skill 2]: [How it relates]

## References
- [External Resource 1]
- [External Resource 2]

---

**Skill Version**: 1.0.0
**Last Updated**: [Date]
**Maintained By**: [Team Name]
```

### Step 4: README.md Template

```markdown
# [Skill Name]

[One-paragraph description of what this skill does and why it's useful]

## Quick Start

[Simplest possible example to get started]

```language
# Minimal working example
```

## When to Use This Skill

This skill is most useful when:
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

## Contents

- **SKILL.md**: Complete skill documentation with patterns and examples
- **patterns/**: Reusable pattern templates
- **examples/**: Real-world usage examples

## Examples

### [Example 1 Name]
```language
# Code snippet
```
[Brief explanation]

### [Example 2 Name]
```language
# Code snippet
```
[Brief explanation]

## Integration with Agents

This skill is used by:
- **[Agent 1]**: [How agent uses this skill]
- **[Agent 2]**: [How agent uses this skill]

## Related Resources

- [Link to related skill]
- [Link to external documentation]
- [Link to tutorial]

---

For complete documentation, see [SKILL.md](SKILL.md)
```

### Step 5: Pattern Files (patterns/*.md)

Create individual pattern files for reusable templates:

```markdown
# [Pattern Name]

## Purpose
[What this pattern achieves]

## When to Use
- [Situation 1]
- [Situation 2]

## Template

```language
# Copy-paste template with placeholders
[PLACEHOLDER_1]
[PLACEHOLDER_2]
```

## Placeholders

- `[PLACEHOLDER_1]`: [Description of what to replace this with]
- `[PLACEHOLDER_2]`: [Description]

## Example Usage

```language
# Filled-in example
```

## Variations

### Variation 1: [Name]
```language
# Modified version for specific use case
```

### Variation 2: [Name]
```language
# Another variation
```

## Best Practices

1. [Practice 1]
2. [Practice 2]

---

**Pattern Version**: 1.0.0
```

### Step 6: Example Files (examples/*.md)

Create complete worked examples:

```markdown
# Example: [Example Name]

## Scenario
[Description of the real-world scenario this example addresses]

## Requirements
- [Requirement 1]
- [Requirement 2]

## Solution

### Step 1: [First Step]
```language
# Code for step 1
```

[Explanation of what this does]

### Step 2: [Second Step]
```language
# Code for step 2
```

[Explanation]

### Step 3: [Third Step]
```language
# Code for step 3
```

[Explanation]

## Complete Code

```language
# Full, runnable code combining all steps
```

## Output/Result

```
# Expected output
```

## Variations

### For [Different Scenario]
Change [specific part]:
```language
# Modified code
```

## Key Takeaways

- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]

---

**Example Last Updated**: [Date]
```

## Skill Design Principles

### 1. Focused Scope
Each skill should focus on ONE domain or capability:
- ✅ Good: "Testing Patterns" - comprehensive testing guide
- ❌ Bad: "Development Patterns" - too broad

### 2. Practical Patterns
Provide concrete, copy-paste-ready patterns:
- Include complete code examples
- Show multiple variations
- Explain when to use each pattern

### 3. Progressive Complexity
Structure content from simple to advanced:
1. **Overview**: High-level introduction
2. **Basic Patterns**: Simple, common use cases
3. **Intermediate**: More complex scenarios
4. **Advanced**: Edge cases, optimizations

### 4. Agent Integration
Document how agents use this skill:
- Which agents reference this skill?
- In what part of their workflow?
- What problems does it solve for them?

### 5. Maintainability
Keep skills up-to-date:
- Version all skill files
- Include last updated dates
- Document changes
- Link to external resources

## Common Skill Types

### Type 1: Technology Skill
**Purpose**: Deep dive into a specific tool or framework

**Structure**:
- Tool overview and capabilities
- Installation and setup
- Core concepts
- Common patterns
- Advanced techniques
- Troubleshooting

**Examples**: test-generation, dockerfile, api-design

### Type 2: Process Skill
**Purpose**: Document a workflow or methodology

**Structure**:
- Process overview
- Step-by-step guide
- Decision points
- Best practices
- Common pitfalls

**Examples**: git-workflow, code-review

### Type 3: Pattern Skill
**Purpose**: Collection of design patterns

**Structure**:
- Pattern catalog
- When to use each pattern
- Implementation examples
- Comparisons
- Anti-patterns

**Examples**: architectural-patterns, data-modeling-patterns

### Type 4: Reference Skill
**Purpose**: Quick reference guide

**Structure**:
- Commands/APIs/Functions
- Parameters and options
- Examples
- Tips and tricks

**Examples**: cli-reference, api-reference

## Integration with Agents

### In Agent Definitions
Reference skills in the agent's definition:

```markdown
## Skills & Specializations

### Testing
- Uses **test-generation** skill for creating test suites
- Uses **code-review** skill for quality standards
```

### In Agent Prompts
Tell the agent to use specific skills:

```markdown
## Instructions

When implementing this feature:
1. Refer to the **api-design** skill for REST API patterns
2. Use the **test-generation** skill for comprehensive tests
3. Follow the **git-workflow** skill for commits
```

## Validation Checklist

Before finalizing a skill:

**Structure:**
- [ ] SKILL.md exists and is comprehensive
- [ ] README.md provides quick start
- [ ] Directory structure is clear
- [ ] Files are properly organized

**Content:**
- [ ] Overview clearly explains purpose
- [ ] Capabilities are listed
- [ ] Patterns are practical and complete
- [ ] Code examples are runnable
- [ ] Best practices are documented
- [ ] Common pitfalls are covered
- [ ] Troubleshooting section included

**Integration:**
- [ ] Referenced by relevant agents
- [ ] Listed in skills README
- [ ] Versioned properly
- [ ] Last updated date included

**Quality:**
- [ ] Code examples are tested
- [ ] Explanations are clear
- [ ] No typos or errors
- [ ] Formatting is consistent

## Example: Creating a "Containerization" Skill

### Step 1: Define Purpose
- **What**: Docker and Kubernetes deployment patterns
- **Why**: Standardize container practices
- **Who**: devops-architect, backend-architect
- **When**: Deploying services, setting up infrastructure
- **How**: Dockerfile templates, K8s manifests, best practices

### Step 2: Create Structure
```bash
mkdir -p .claude/skills/containerization/{patterns,examples}
```

### Step 3: Create SKILL.md
Include:
- Docker fundamentals
- Dockerfile best practices
- Docker Compose patterns
- Kubernetes concepts
- K8s manifest templates
- Multi-stage builds
- Security practices

### Step 4: Create Patterns
- `patterns/multistage-dockerfile.md`: Multi-stage build template
- `patterns/kubernetes-deployment.md`: K8s deployment template
- `patterns/docker-compose.md`: Docker Compose template

### Step 5: Create Examples
- `examples/nodejs-app.md`: Complete Node.js containerization
- `examples/python-app.md`: Python app with dependencies
- `examples/microservices.md`: Multi-container setup

### Step 6: Update README
Add to `.claude/skills/README.md`:
```markdown
## containerization
Comprehensive guide for Docker and Kubernetes deployments. Includes Dockerfile templates, K8s manifests, and containerization best practices.

**Used by**: devops-architect, backend-architect
```

## Best Practices Summary

1. **One Skill, One Focus**: Each skill covers one domain
2. **Practical First**: Provide copy-paste-ready code
3. **Progressive Depth**: Simple to advanced
4. **Rich Examples**: Multiple real-world scenarios
5. **Agent Integration**: Clear agent usage
6. **Regular Updates**: Keep content current
7. **Version Control**: Track changes
8. **Clear Structure**: Consistent organization
9. **Searchable**: Good section headers
10. **Actionable**: Readers can immediately apply

## Troubleshooting

### Issue: Skill Too Broad
**Problem**: Skill covers too many topics
**Solution**: Split into multiple focused skills

### Issue: No Clear Use Cases
**Problem**: Skill is theoretical without practical examples
**Solution**: Add concrete examples and use cases

### Issue: Outdated Content
**Problem**: Technology has evolved, skill is old
**Solution**: Regular review and updates, version tracking

### Issue: Poor Agent Integration
**Problem**: Agents don't know when to use this skill
**Solution**: Clear "When to Use" sections, agent references

## Skill Maintenance

### Regular Reviews
- Quarterly: Check for outdated content
- After major tool updates: Update patterns
- Based on feedback: Add requested examples
- Version updates: Document changes

### Version Management
- **Major (X.0.0)**: Complete restructure
- **Minor (x.X.0)**: New patterns/examples
- **Patch (x.x.X)**: Fixes and updates

## Conclusion

Creating effective skills requires:
1. Clear, focused purpose
2. Practical, tested patterns
3. Comprehensive examples
4. Clear agent integration
5. Regular maintenance

Follow this skill's templates and principles to create valuable, reusable skills for your Claude Code system.

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: Claude Code Team
