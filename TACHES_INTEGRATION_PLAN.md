# TÂCHES Commands Integration Plan

**Date**: 2025-11-16
**Status**: Draft - Awaiting Expert Review
**Target Branch**: `claude/integrate-taches-prompts-01FKBNbG7zq1BrGfnMJ2orGZ`

## Executive Summary

This document outlines the integration strategy for incorporating TÂCHES slash commands from https://github.com/glittercowboy/taches-cc-prompts into the claude-force multi-agent orchestration system. The integration will enhance workflow management, context preservation, and meta-prompting capabilities.

## Source Analysis

### TÂCHES Repository Components

The TÂCHES repository provides three core command systems:

1. **Meta-Prompting** (`/meta-prompt`)
   - Enables Claude to refine its own prompts
   - Useful for complex refactoring and multi-step projects
   - Philosophy: "Tell Claude what you want, not what to do"

2. **Todo Management** (`/add-to-todos`, `/check-todos`)
   - `/add-to-todos`: Captures ideas mid-workflow without interruption
   - `/check-todos`: Displays active tasks and enables selection for focused work
   - Uses TO-DOS.md file in working directory
   - Structured format with context, files, problems, solutions

3. **Context Handoff** (`/whats-next`)
   - Generates handoff documentation for session continuity
   - Analyzes conversation to create structured handoff
   - Enables seamless work continuation in fresh sessions
   - Creates whats-next.md with original task, completed work, remaining work, context

## Target System Analysis

### Claude-Force Current State

**Existing Infrastructure:**
- 5 slash commands in `.claude/commands/`:
  - `/status` - Session status and progress
  - `/new-task` - Task initialization
  - `/run-agent` - Agent execution
  - `/run-workflow` - Workflow execution
  - `/validate-output` - Quality validation

**Architecture:**
- Modular layered architecture (UI → Orchestration → Services → Utilities)
- 19 specialized agents
- 10 pre-built workflows
- 11 integrated skills
- 6-layer governance system
- Performance tracking and analytics
- Marketplace integration

**Command Format:**
- Markdown files with frontmatter (description, usage)
- Detailed documentation with examples
- Support for options and flags
- Interactive and quick modes

## Integration Strategy

### Phase 1: Core Command Integration

#### 1.1 Meta-Prompting Integration

**Files to Create:**
- `.claude/commands/meta-prompt.md`

**Integration Approach:**
- Adapt meta-prompting for multi-agent workflows
- Integrate with existing agent orchestration
- Allow meta-prompting to suggest agent sequences
- Connect to workflow composer for dynamic workflow generation

**Claude-Force Enhancements:**
```markdown
Features to Add:
- Integration with AgentOrchestrator for dynamic workflow creation
- Support for agent-specific meta-prompting
- Connection to semantic selector for agent recommendations
- Performance tracking of meta-prompted tasks
```

**Compatibility Considerations:**
- Ensure meta-prompting respects governance rules
- Integrate with existing validation system
- Connect to performance tracker for analytics

#### 1.2 Todo Management Integration

**Files to Create:**
- `.claude/commands/add-to-todos.md`
- `.claude/commands/check-todos.md`

**File Structure:**
- Primary storage: `.claude/TO-DOS.md` (project-level)
- Format: Compatible with TÂCHES format
- Integration with existing `.claude/task.md` system

**Integration Approach:**
- Extend todo format to include agent/workflow metadata
- Add integration with `/new-task` for task creation from todos
- Connect to workflow system for automatic workflow suggestion
- Link with performance tracker to track todo completion metrics

**Claude-Force Enhancements:**
```markdown
Extended Todo Format:
- **[Action]** - [Description]
  - **Problem:** [Issue]
  - **Files:** [Paths with line numbers]
  - **Solution:** [Optional approach]
  - **Suggested Agent:** [agent-name] (NEW)
  - **Suggested Workflow:** [workflow-name] (NEW)
  - **Priority:** [High/Medium/Low] (NEW)
  - **Estimated Cost:** [$X.XX] (NEW)
```

**Workflow Integration:**
- When checking todos, analyze context and suggest appropriate agents/workflows
- Auto-populate `/new-task` from selected todo
- Track todo completion as part of session analytics

#### 1.3 Context Handoff Integration

**Files to Create:**
- `.claude/commands/whats-next.md`

**File Structure:**
- Output: `.claude/whats-next.md`
- Optionally archive to `.claude/handoffs/handoff-YYYY-MM-DD-HHMMSS.md`

**Integration Approach:**
- Extend handoff to include multi-agent session state
- Capture workflow progress and agent outputs
- Include governance validation status
- Add performance metrics and cost summary
- Connect to `/status` command for comprehensive session snapshot

**Claude-Force Enhancements:**
```markdown
Extended Handoff Format:
<original_task>
[Task description from .claude/task.md]
</original_task>

<workflow_progress>
Workflow: [workflow-name]
Progress: X of Y agents complete (Z%)
[Agent execution summary with status]
</workflow_progress>

<work_completed>
[Completed work details]
[Files modified with links]
[Agent outputs summary]
</work_completed>

<work_remaining>
[Remaining tasks]
[Next agents to run]
[Pending dependencies]
</work_remaining>

<governance_status>
Validation: [Pass/Fail]
Scorecard: [X/Y checks pass]
Blockers: [List]
</governance_status>

<performance_metrics>
Total Cost: $X.XX
Execution Time: X hours Y minutes
Agents Executed: X
Token Usage: X tokens
</performance_metrics>

<context>
[Technical decisions, constraints, gotchas]
</context>
```

### Phase 2: Enhanced Integration Features

#### 2.1 Workflow Awareness

**Enhance `/check-todos`:**
- Scan `.claude/workflows/` for relevant workflows
- Match todo file paths to agent specializations
- Suggest workflow instead of single agent when appropriate
- Example: Plugin todos → suggest relevant workflow chain

#### 2.2 Cross-Command Integration

**Integration Points:**
1. `/add-to-todos` → `/check-todos` → `/new-task` → `/run-workflow`
2. `/run-workflow` → `/status` → `/whats-next`
3. `/meta-prompt` → `/run-workflow` (dynamic workflow generation)

**Data Flow:**
```
Todo Added → Todo Selected → Task Created → Workflow Executed → Status Tracked → Handoff Generated
```

#### 2.3 Analytics Integration

**Track Metrics:**
- Todo completion rates
- Todo-to-task conversion rates
- Handoff success rates (tasks resumed from handoffs)
- Meta-prompt effectiveness (success rate of generated workflows)

**Export Capabilities:**
- Add todo metrics to `claude-force analytics summary`
- Include handoff data in performance reports
- Track meta-prompt usage and outcomes

### Phase 3: Documentation and Testing

#### 3.1 Documentation Updates

**Files to Update:**
- `README.md` - Add new commands to CLI commands section
- `QUICK_START.md` - Include todo management workflow
- `docs/guides/` - Create comprehensive guide for workflow management
- `.claude/commands.md` - Document new commands

**New Documentation:**
- `docs/guides/WORKFLOW_MANAGEMENT.md` - Complete workflow guide
- `docs/guides/CONTEXT_HANDOFF.md` - Handoff best practices
- `docs/guides/META_PROMPTING.md` - Meta-prompting strategies

#### 3.2 Testing Strategy

**Unit Tests:**
- Test todo parsing and formatting
- Test handoff generation logic
- Test meta-prompt integration with orchestrator

**Integration Tests:**
- Test complete todo workflow (add → check → task → workflow)
- Test handoff generation from multi-agent session
- Test meta-prompt workflow generation

**User Acceptance Tests:**
- Verify commands work in real project scenarios
- Test cross-session continuity with handoffs
- Validate todo management in actual development workflow

### Phase 4: Marketplace Considerations

#### 4.1 wshobson/agents Compatibility

**Ensure Compatibility:**
- Commands work with marketplace agents
- Todo format supports marketplace agent metadata
- Handoffs include marketplace agent execution data

**Enhancement Opportunities:**
- Allow todos to suggest marketplace agents
- Include marketplace agent recommendations in meta-prompting
- Track marketplace agent performance in handoffs

## Implementation Roadmap

### Week 1: Core Commands
- [ ] Day 1-2: Implement `/meta-prompt`
- [ ] Day 3-4: Implement `/add-to-todos` and `/check-todos`
- [ ] Day 5: Implement `/whats-next`

### Week 2: Integration & Enhancement
- [ ] Day 1-2: Integrate commands with existing system
- [ ] Day 3-4: Add claude-force enhancements
- [ ] Day 5: Cross-command integration

### Week 3: Testing & Documentation
- [ ] Day 1-2: Unit and integration tests
- [ ] Day 3-4: Documentation updates
- [ ] Day 5: User acceptance testing

### Week 4: Polish & Release
- [ ] Day 1-2: Bug fixes and refinements
- [ ] Day 3: Performance optimization
- [ ] Day 4: Final testing
- [ ] Day 5: Release and documentation

## Risk Assessment

### High Priority Risks

**R1: Command Namespace Conflicts**
- **Risk**: TÂCHES commands might conflict with existing commands
- **Mitigation**: Review all command names, ensure no conflicts
- **Status**: Low risk - no conflicts identified

**R2: File Format Incompatibility**
- **Risk**: TO-DOS.md format might not align with claude-force patterns
- **Mitigation**: Extend format while maintaining backward compatibility
- **Status**: Medium risk - requires careful design

**R3: Performance Impact**
- **Risk**: Additional file I/O and parsing could slow down commands
- **Mitigation**: Implement caching, optimize parsing logic
- **Status**: Low risk - minimal I/O operations

### Medium Priority Risks

**R4: User Experience Fragmentation**
- **Risk**: Too many commands could overwhelm users
- **Mitigation**: Create clear documentation and workflow guides
- **Status**: Medium risk - requires good UX design

**R5: Governance Bypass**
- **Risk**: Meta-prompting might circumvent governance rules
- **Mitigation**: Ensure meta-prompted workflows respect governance
- **Status**: Medium risk - requires validation layer

## Success Metrics

### Adoption Metrics
- Command usage frequency
- Todo completion rates
- Handoff usage in multi-session projects

### Quality Metrics
- Code coverage > 90% for new commands
- Documentation completeness
- User satisfaction (if collecting feedback)

### Performance Metrics
- Command execution time < 2 seconds
- Todo parsing performance
- Handoff generation time

## Open Questions for Expert Review

1. **Architecture Questions:**
   - Should TO-DOS.md be global or project-specific?
   - Should we integrate with existing `.claude/task.md` or keep separate?
   - How should meta-prompting interact with governance?

2. **Feature Scope Questions:**
   - Should we implement all TÂCHES features or start with subset?
   - Priority order: Meta-prompt vs Todo Management vs Handoff?
   - Should we extend TÂCHES features or keep minimal?

3. **Integration Questions:**
   - How deeply should commands integrate with orchestrator?
   - Should todos trigger automatic agent recommendations?
   - Should handoffs auto-populate next session's task?

4. **Technical Questions:**
   - File format: Extend TÂCHES format or create claude-force variant?
   - Storage: Use `.claude/` directory or separate location?
   - Caching: Should we cache parsed todos/handoffs?

5. **User Experience Questions:**
   - Command naming: Keep TÂCHES names or adapt for claude-force?
   - Workflow: Should commands be standalone or tightly integrated?
   - Documentation: Separate guide vs integrate into existing docs?

## Next Steps

1. **Expert Review** (This Document)
   - Frontend Architect: UI/UX perspective
   - Backend Architect: Integration architecture
   - Document Writer: Documentation strategy
   - Prompt Engineer: Meta-prompting design

2. **Feedback Incorporation**
   - Review expert feedback
   - Refine integration plan
   - Update roadmap based on feedback

3. **Implementation**
   - Create feature branch
   - Implement Phase 1 commands
   - Test and iterate

4. **Release**
   - Merge to main branch
   - Update documentation
   - Announce new features

## References

- **TÂCHES Repository**: https://github.com/glittercowboy/taches-cc-prompts
- **Claude-Force Architecture**: `/home/user/claude-force/ARCHITECTURE.md`
- **Existing Commands**: `/home/user/claude-force/.claude/commands/`
- **Project README**: `/home/user/claude-force/README.md`

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**Reviewers**: Pending
**Status**: Draft - Awaiting Expert Feedback
