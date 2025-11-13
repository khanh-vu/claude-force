# Task Template

> **Instructions**: Copy this template and fill in the sections. This file guides agent execution.

---

## Task: [Clear, Concise Title]

**Created**: [YYYY-MM-DD]
**Owner**: [Your Name/Team]
**Priority**: [High/Medium/Low]
**Type**: [Feature/Bug Fix/Refactor/Documentation/Infrastructure]

**Assigned Agent(s)**: [Agent name(s) - see agent selection guide below]
**Suggested Workflow**: [Workflow name - or "Custom" with sequence]

> **Agent Selection Guide**:
> - **Architecture Tasks**: frontend-architect, backend-architect, database-architect, solution-architect
> - **Implementation**: frontend-developer, python-expert, mobile-developer
> - **Code Quality**: code-reviewer, refactoring-expert
> - **Security**: security-specialist
> - **Performance**: performance-optimizer
> - **Testing**: qc-automation-expert
> - **Bug Fixing**: bug-investigator
> - **Documentation**: document-writer-expert, api-documenter
> - **Infrastructure**: devops-architect, deployment-integration-expert
> - **Guidance**: tech-lead-mentor, requirements-analyst
>
> **Common Workflows**:
> - `full-stack-feature` - Complete feature with frontend & backend
> - `frontend-only` - UI/UX feature
> - `backend-only` - API or service feature
> - `bug-fix` - Bug investigation and fix
> - `code-review` - Code review and quality check
> - `refactoring` - Code improvement
> - `documentation` - Documentation generation

---

## Objective

[1-2 paragraphs describing what needs to be accomplished and why]

**Example**:
```
Build a product catalog page that displays flower arrangements for an e-commerce site.
The catalog should support filtering by category, price range, and occasion. This feature
is critical for Q4 launch and needs to handle 10,000+ products efficiently.
```

---

## Requirements

### Functional Requirements
- [Requirement 1: What the system must do]
- [Requirement 2]
- [Requirement 3]

### Non-Functional Requirements
- **Performance**: [e.g., page load < 2s, API response < 200ms]
- **Scalability**: [e.g., handle 10K concurrent users]
- **Security**: [e.g., authentication required, data encryption]
- **Accessibility**: [e.g., WCAG 2.1 AA compliance]
- **Browser Support**: [e.g., Chrome, Firefox, Safari latest 2 versions]

### Technical Requirements
- **Stack**: [e.g., Next.js 14, TypeScript, PostgreSQL]
- **Frameworks**: [e.g., Tailwind CSS, shadcn/ui]
- **APIs**: [e.g., RESTful API, GraphQL]
- **Infrastructure**: [e.g., Vercel, AWS, Docker]

---

## Context

### Background
[Why this task is needed, history, business context]

### Assumptions
- [Assumption 1: e.g., Users have modern browsers]
- [Assumption 2: e.g., Database can be restructured]
- [Assumption 3: e.g., Third-party API is reliable]

### Constraints
- **Time**: [e.g., Must complete by Dec 1]
- **Budget**: [e.g., No additional infrastructure costs]
- **Technical**: [e.g., Must work with existing auth system]
- **Business**: [e.g., Cannot change pricing display logic]

### Dependencies
- [Dependency 1: e.g., Waiting for API key from vendor]
- [Dependency 2: e.g., Requires design mockups from UX team]
- [Dependency 3: e.g., Blocked by security audit completion]

---

## Acceptance Criteria

These must ALL be satisfied for the task to be complete:

- [ ] **Criterion 1**: [Specific, measurable, testable]
- [ ] **Criterion 2**: [Example: Products display in responsive grid]
- [ ] **Criterion 3**: [Example: Filters update results in < 500ms]
- [ ] **Criterion 4**: [Example: Unit test coverage > 80%]
- [ ] **Criterion 5**: [Example: No console errors in production]
- [ ] **Criterion 6**: [Example: Lighthouse score > 90]
- [ ] **Criterion 7**: [Example: Works on mobile devices]
- [ ] **Criterion 8**: [Example: Documentation updated]

---

## Scope

### In Scope
- [What IS included in this task]
- [Feature A]
- [Feature B]
- [Component C]

### Out of Scope
- [What IS NOT included - for later]
- [Feature X - separate task]
- [Feature Y - not planned]
- [Component Z - existing solution adequate]

---

## Resources

### Design Assets
- [Link to Figma]: https://...
- [Link to style guide]: https://...
- [Link to mockups]: https://...

### Documentation
- [API documentation]: https://...
- [Technical specs]: https://...
- [Related PRs/issues]: https://...

### Data
- [Sample data]: https://...
- [Test accounts]: https://...
- [Database schema]: https://...

---

## Deliverables

The agents should produce:

### Code
- [ ] [File/component 1]: e.g., `app/catalog/page.tsx`
- [ ] [File/component 2]: e.g., `components/ProductCard.tsx`
- [ ] [File/component 3]: e.g., `api/products.ts`

### Tests
- [ ] [Unit tests for X]
- [ ] [Integration tests for Y]
- [ ] [E2E tests for critical flows]

### Documentation
- [ ] [README updates]
- [ ] [API documentation]
- [ ] [Component usage examples]

### Configuration
- [ ] [Environment variables]
- [ ] [Deployment config]
- [ ] [CI/CD pipeline updates]

---

## Success Metrics

How we'll measure success:

- **Metric 1**: [e.g., Page load time < 2s]
- **Metric 2**: [e.g., Conversion rate increase 10%]
- **Metric 3**: [e.g., Zero critical bugs in first week]
- **Metric 4**: [e.g., 95% positive user feedback]

---

## Workflow

**Selected Workflow**: [Workflow name from header - or define custom below]

**Agent Execution Sequence**:

1. **[agent-name]** - [What this agent will do]
   - Skills needed: [List relevant skills]
   - Dependencies: [What must be complete first]
   - Output: [What will be delivered]

2. **[agent-name]** - [What this agent will do]
   - Skills needed: [List relevant skills]
   - Dependencies: [Previous agent's output]
   - Output: [What will be delivered]

[Continue for all agents in sequence...]

**Example for Full-Stack Feature**:
1. **requirements-analyst** - Clarify requirements and edge cases
2. **frontend-architect** - Define component architecture and routing
3. **database-architect** - Design schema and indexes
4. **backend-architect** - Design API endpoints and data flow
5. **security-specialist** - Review architecture for security issues
6. **python-expert** - Implement backend services
7. **ui-components-expert** - Build reusable UI components
8. **frontend-developer** - Implement pages and integration
9. **code-reviewer** - Review all code for quality
10. **qc-automation-expert** - Create comprehensive test suite
11. **performance-optimizer** - Optimize bottlenecks
12. **deployment-integration-expert** - Configure deployment

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1: e.g., Third-party API unreliable] | High | Medium | Implement caching and fallback |
| [Risk 2: e.g., Performance issues at scale] | Medium | Low | Load testing in staging |
| [Risk 3: e.g., Browser compatibility] | Low | Medium | Cross-browser testing |

---

## Timeline

**Estimated Duration**: [X days/weeks]

### Phase 1: Planning & Architecture (Day 1-2)
- Architecture agents define structure
- Designs reviewed and approved

### Phase 2: Implementation (Day 3-7)
- Backend and frontend development
- Component creation

### Phase 3: Testing & QA (Day 8-9)
- Test creation and execution
- Bug fixes

### Phase 4: Deployment (Day 10)
- Deployment configuration
- Production rollout

---

## Notes

[Any additional context, special instructions, or important information]

**Example**:
```
- This is a high-visibility feature for marketing campaign
- CEO will review before launch
- Coordinate with marketing team for launch timing
- Consider A/B testing different layouts
```

---

## Approval

**Approved By**: [Name/Team]  
**Date**: [YYYY-MM-DD]  
**Sign-off**: [Signature/Acknowledgment]

---

## Updates Log

Track changes to requirements:

| Date | Change | Reason | Approved By |
|------|--------|--------|-------------|
| 2025-11-13 | Added mobile requirement | Market research | Product Team |
| 2025-11-14 | Changed DB from MySQL to PostgreSQL | Performance needs | Tech Lead |

---

**Version**: 1.0.0  
**Status**: [Draft/Approved/In Progress/Complete]
