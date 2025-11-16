---
description: Meta-prompt for complex workflow generation
usage: /meta-prompt "objective" [--budget AMOUNT] [--timeline TIME]
---

# Meta-Prompt Command

Let Claude refine complex objectives into concrete, executable workflows with governance validation.

## Philosophy

**"Tell Claude what you want, not what to do"**

Instead of manually designing agent sequences, describe your high-level goal. Meta-prompting:
- Refines your objective into specific requirements
- Proposes optimal agent workflows
- Validates against governance rules
- Provides alternatives and trade-offs
- Explains reasoning behind suggestions

---

## When to Use

**Perfect for:**
- Complex, multi-step projects
- Unfamiliar domains (don't know which agents to use)
- Architectural decisions (multiple valid approaches)
- Exploring solution space (what's possible?)
- Learning optimal patterns

**Not needed for:**
- Simple, single-agent tasks
- Well-known patterns you've done before
- When you already know exact agent sequence

---

## Basic Usage

Describe what you want to achieve:

```
/meta-prompt "I need to build a user authentication system with email verification"
```

**What happens:**
1. Analyzes your objective
2. Identifies requirements and constraints
3. Proposes concrete workflow with agents
4. Validates against governance (agents exist, budget, skills)
5. Provides alternatives and trade-offs
6. Explains reasoning

**Output:**
```markdown
## Meta-Prompting Analysis

### Refined Objective
Build a secure user authentication system with:
- Email/password registration
- Email verification (confirm email before access)
- Secure password storage (bcrypt/argon2)
- JWT-based session management
- Password reset flow
- Rate limiting for security

### Proposed Workflow

**Recommended**: `full-stack-feature` (customized)

**Agent Sequence** (8 agents, ~45-60 min, $3.20-4.50):
1. **backend-architect** - Design auth API endpoints, JWT strategy
2. **database-architect** - User schema, indexes, migrations
3. **security-specialist** - Review password storage, rate limiting, vulnerabilities
4. **python-expert** - Implement auth endpoints with FastAPI/Flask
5. **frontend-developer** - Login/register UI components
6. **email-specialist** - Email verification flow (optional: use existing templates)
7. **qc-automation-expert** - Security tests (SQL injection, XSS, CSRF)
8. **deployment-integration-expert** - Environment variables, secrets management

### Reasoning

**Why this sequence:**
- Backend first ensures API contract for frontend
- Security specialist early to catch design issues (cheaper than fixing later)
- Email specialist optional if using third-party service (Sendgrid, etc.)
- QA must include security tests for auth systems

**Alternatives Considered:**
1. **Simpler**: Skip email verification ($2.50, 35min)
   - Trade-off: Less secure, but faster to market
2. **More robust**: Add 2FA, OAuth providers ($6.00, 90min)
   - Trade-off: Better security, more complex

### Governance Validation

✅ **All checks passed**

- ✅ All agents available
- ✅ Required skills present (backend, database, security, frontend)
- ✅ Budget: $4.50 (within typical range)
- ✅ No security policy violations
- ✅ Timeline: ~60 min (reasonable for scope)

### Success Criteria

I'll know this is done when:
- [ ] Users can register with email/password
- [ ] Email verification required before access
- [ ] Passwords securely hashed (bcrypt/argon2)
- [ ] JWT tokens issued and validated
- [ ] Password reset flow works
- [ ] Security tests pass (no SQL injection, XSS, CSRF)
- [ ] Rate limiting prevents brute force

### Risk Assessment

**Potential risks:**
- ⚠️ Email delivery (use reliable service, test thoroughly)
- ⚠️ Token expiration handling (document clearly)
- ⚠️ Password reset security (verify email ownership)

---

**Ready to proceed?**
  [1] Run recommended workflow
  [2] Run alternative 1 (simpler)
  [3] Run alternative 2 (more robust)
  [4] Customize workflow
  [5] Save for later (add to todos)
  [0] Cancel

Your choice:
```

**After selecting option 1:**
```
✅ Running workflow: full-stack-feature (customized for auth)

Starting agent 1 of 8: backend-architect
Task: Design authentication API endpoints with JWT strategy...
```

---

## With Constraints

Specify budget and timeline:

```
/meta-prompt "Optimize database queries for better performance" --budget 2.00 --timeline "30 min"
```

**Output:**
```markdown
## Meta-Prompting Analysis

### Refined Objective
Optimize database queries with:
- Identify slow queries (N+1, missing indexes)
- Add appropriate indexes
- Optimize complex queries
- Implement query caching where beneficial

### Constraints

⚠️ **Budget**: $2.00 (tight)
⚠️ **Timeline**: 30 minutes (limited)

Given constraints, recommending focused approach.

### Proposed Workflow

**Recommended**: Single-agent approach (budget-optimized)

**Agent**: `database-architect` (Haiku model)
- **Cost**: ~$0.80 - $1.20
- **Time**: ~20-25 minutes
- **Scope**: Focus on quick wins (obvious missing indexes, N+1 queries)

**Tasks:**
1. Analyze query logs / slow query log
2. Identify top 5 slow queries
3. Add missing indexes
4. Suggest query rewrites for top issues
5. Document changes

### Reasoning

**Why single agent:**
- Budget constraint ($2.00) prevents multi-agent workflow
- Database optimization is specialized task (doesn't need full workflow)
- Haiku model sufficient for this type of analysis

**What's excluded** (to meet budget):
- ❌ Comprehensive performance testing (would need qc-automation-expert)
- ❌ Application-level caching strategy (would need backend-architect)
- ❌ Query rewrite testing (would need multiple iterations)

**If more budget available:**
- Add `performance-expert` for caching strategy (+$1.50, +25min)
- Add `qc-automation-expert` for load testing (+$1.00, +20min)

### Governance Validation

✅ **Passed (with warnings)**

- ✅ Agent available: database-architect
- ✅ Required skills: database
- ⚠️ Budget tight: minimal buffer for complex queries
- ✅ Timeline achievable for focused scope

### Trade-offs

**What you're getting:**
- Quick wins (obvious indexes, simple optimizations)
- Documented recommendations
- Fast turnaround

**What you're not getting:**
- Comprehensive performance testing
- Caching strategy
- Complex query rewrites

---

**Accept focused approach?**
  [1] Run focused optimization (single agent, $1.20, 25min)
  [2] Increase budget to $4.00 for comprehensive approach
  [3] Extend timeline to 60min (same budget, more thorough)
  [4] Save for later
  [0] Cancel
```

---

## Interactive Refinement

For complex or ambiguous objectives:

```
/meta-prompt "Make the application faster"
```

**Output:**
```
❓ Objective needs clarification

"Make the application faster" is broad. Let me help refine:

**What type of performance?**
  [1] Page load time (frontend optimization)
  [2] API response time (backend optimization)
  [3] Database queries (database optimization)
  [4] All of the above (comprehensive)

Your choice: 2

**API response time** - noted!

**Current baseline?**
  [a] Don't know (will measure first)
  [b] ~500ms average (need to reduce)
  [c] > 1 second (critical issue)

Your choice: c

**Target performance?**
  [a] < 500ms (moderate improvement)
  [b] < 200ms (significant improvement)
  [c] < 100ms (aggressive target)

Your choice: a

**Known bottlenecks?**
  [a] Don't know (analyze everything)
  [b] Database queries are slow
  [c] External API calls
  [d] Heavy computation

Your choice: b

✅ Refined objective:

"Optimize API response time from >1s to <500ms by focusing on database query optimization"

[Proceeds with meta-prompting analysis as shown above]
```

---

## Iterative Refinement

Meta-prompting validates and refines automatically (up to 3 iterations):

```
/meta-prompt "Build a ML model for price prediction"
```

**Iteration 1 - Governance Failure:**
```
❌ Governance validation failed

**Issues:**
- ❌ Agent 'ml-model-trainer' does not exist
- ❌ Missing required skill: tensorflow

**Guidance:**
- Use available agents (ai-engineer, data-engineer, python-expert)
- Work within existing skill set or install tensorflow skill

Refining approach...
```

**Iteration 2 - Adjusted:**
```
✅ Governance passed

**Refined Workflow** (uses available agents):

1. **data-engineer** - Data preprocessing and feature engineering
2. **ai-engineer** - Model selection and training (scikit-learn)
3. **python-expert** - Production-ready inference code
4. **qc-automation-expert** - Model validation tests

**Note**: Using scikit-learn instead of TensorFlow (available in current setup)

[Proceeds with validation and execution options]
```

---

## Advanced Usage

### Save Workflow for Reuse

```
/meta-prompt "Build authentication system" --save-workflow auth-workflow
```

Creates reusable workflow in `.claude/workflows/auth-workflow.md`

### Compare Alternatives

```
/meta-prompt "Deploy to cloud" --show-all-alternatives
```

Shows all viable approaches with cost/time trade-offs:

```
**Alternative 1**: AWS Deployment ($2.50, 40min)
**Alternative 2**: GCP Deployment ($2.50, 40min)
**Alternative 3**: Docker + Kubernetes ($4.00, 70min)
**Alternative 4**: Simple Heroku Deploy ($1.00, 15min)

[Detailed comparison table with pros/cons]
```

### Domain-Specific Meta-Prompting

```
/meta-prompt "Crypto trading bot with risk management" --domain crypto
```

Uses domain-specific knowledge (crypto agents, patterns, best practices).

---

## How It Works

### 1. Objective Analysis
- Extracts requirements from natural language
- Identifies implicit needs (e.g., "auth" implies security)
- Clarifies ambiguities through questions

### 2. Workflow Generation
- Maps requirements to agent capabilities
- Orders agents logically (dependencies)
- Estimates cost and timeline
- Suggests alternatives

### 3. Governance Validation
- **Agent availability**: All agents exist?
- **Budget compliance**: Within limits?
- **Skill requirements**: All skills available?
- **Safety checks**: No policy violations?

### 4. Iterative Refinement
- If validation fails, refines approach
- Provides specific guidance
- Max 3 iterations (prevents infinite loops)
- Convergence detection

### 5. Presentation
- Clear explanation of reasoning
- Alternatives with trade-offs
- Success criteria
- Risk assessment

---

## Governance Integration

Meta-prompting **always respects governance**:

### Validation Checkpoints

**Pre-Generation:**
- Validates constraints (budget, timeline, resources)
- Checks for policy conflicts

**Post-Generation:**
- Agent availability check
- Skill requirements check
- Budget validation
- Safety policy check

**If Validation Fails:**
- Explains violations clearly
- Provides guidance for fixes
- Refines automatically
- Falls back to closest valid workflow

### Example Governance Failure

```
❌ Governance validation failed (Iteration 1/3)

**Violations:**
1. Agent 'custom-ml-agent' does not exist
   → Fix: Use 'ai-engineer' instead
2. Budget limit exceeded ($8.50 > $5.00)
   → Fix: Reduce scope or increase budget
3. Missing skill: pytorch
   → Fix: Use scikit-learn (available) or install pytorch skill

**Refining workflow to address issues...**

[Iteration 2 with fixes]
```

---

## Best Practices

### Write Good Objectives

**Good Objectives** (specific, measurable):
- ✅ "Build user authentication with email verification and JWT tokens"
- ✅ "Optimize API response time from 1s to < 500ms"
- ✅ "Add comprehensive error handling to payment processing"

**Poor Objectives** (vague):
- ❌ "Make it better"
- ❌ "Fix the bugs"
- ❌ "Improve performance"

**If objective is vague:**
- Meta-prompting will ask clarifying questions
- Interactive refinement helps

### Set Realistic Constraints

**Budget:**
- Simple tasks: $1-2
- Medium complexity: $3-5
- Complex features: $6-10
- Major projects: $10-20

**Timeline:**
- Quick fixes: 15-30 min
- Single features: 30-60 min
- Multi-phase: 60-120 min
- Major work: 2-4 hours

### Review Reasoning

Always read the "Reasoning" section:
- Understand WHY agents are ordered this way
- Learn patterns for future
- Spot potential issues early

### Consider Alternatives

Don't always pick the first option:
- Simpler might be better (MVP approach)
- More robust might prevent future work
- Different approach might fit better

---

## Integration with Other Commands

### Meta-Prompt → Workflow

```
/meta-prompt "Build feature X"
# Reviews proposed workflow
# Selects option [1] Run recommended workflow
# Automatically executes /run-workflow with custom agents
```

### Meta-Prompt → Todo

```
/meta-prompt "Complex multi-month project"
# Too large for single workflow
# Selects [5] Save for later
# Creates todos for each phase
```

### Meta-Prompt → New Task

```
/meta-prompt "Build API integration"
# Reviews approach
# Selects [4] Customize workflow
# Exports to /new-task for manual review
```

---

## Examples

### Example 1: Learning Optimal Patterns

```
User: /meta-prompt "I need to add a new API endpoint for user profiles"

Output: [Shows recommended 3-agent workflow]
- backend-architect (design endpoint)
- python-expert (implement)
- api-documenter (document)

User learns: Simple endpoint needs architecture, implementation, docs
```

### Example 2: Budget Optimization

```
User: /meta-prompt "Code review the entire codebase" --budget 3.00

Output: [Shows budget is too low]
- Full codebase review would cost ~$15
- Recommends focused review (high-risk files only) for $2.80
- Or increase budget for comprehensive review

User: Selects focused approach
```

### Example 3: Discovering Capabilities

```
User: /meta-prompt "I want to build a Chrome extension"

Output: [Analyzes available agents]
- frontend-developer (UI)
- javascript-expert (extension logic)
- security-specialist (permissions review)
- api-documenter (extension docs)

User learns: System can handle Chrome extensions
```

---

## Troubleshooting

**Issue**: "Objective unclear - need refinement"
**Solution**: Answer clarifying questions or make objective more specific

**Issue**: "No valid workflow found after 3 iterations"
**Solution**: Constraints too tight or objective not achievable with current agents
- Relax budget/timeline constraints
- Install required skills
- Break into smaller objectives

**Issue**: "Governance validation keeps failing"
**Solution**: Review violations, likely:
- Agents don't exist (check available agents)
- Skills missing (install or change approach)
- Budget too low (increase or reduce scope)

**Issue**: "Proposed workflow seems wrong"
**Solution**: Meta-prompting is a suggestion, not requirement
- Use "Customize workflow" option
- Provide feedback (improves over time)
- Manual workflow still available

---

## Tips

**Start Broad, Refine Interactively**
- Initial objective can be vague
- Answer clarifying questions
- Iterates to specific plan

**Learn Patterns**
- Read reasoning sections
- Understand agent sequencing
- Apply to future manual workflows

**Use for Exploration**
- "What's possible with X?"
- "How would you approach Y?"
- Discover capabilities

**Combine with Todos**
- Save complex workflows as todos
- Break large goals into phases
- Plan incrementally

**Trust but Verify**
- Review proposed workflow
- Understand reasoning
- Customize if needed

---

## Limitations

**Not a Magic Bullet:**
- Can't create agents that don't exist
- Can't exceed system capabilities
- Requires some context from you

**Works Best When:**
- Objective is clear (or you answer questions)
- System has relevant agents
- Constraints are realistic

**Less Effective When:**
- Highly specialized/niche tasks
- Agents not available for domain
- Constraints impossible to meet

---

## Options Summary

| Option | Description | Example |
|--------|-------------|---------|
| `--budget AMOUNT` | Set max budget (USD) | `--budget 5.00` |
| `--timeline TIME` | Set max timeline | `--timeline "45 min"` |
| `--save-workflow NAME` | Save as reusable workflow | `--save-workflow auth-flow` |
| `--show-all-alternatives` | Show all options | `--show-all-alternatives` |
| `--domain DOMAIN` | Use domain knowledge | `--domain crypto` |
| `--auto-execute` | Run without confirmation | `--auto-execute` |

---

**Last Updated**: 2025-11-16
