---
description: Generate session handoff for continuity
usage: /handoff [--save PATH | --load | --auto]
---

# Handoff Command

Create structured handoff documentation for seamless session continuation.

## When to Use

**Perfect for:**
- End of work session (before closing)
- Before context window fills up
- Natural breakpoints (workflow completion)
- Switching to different task
- Team handoffs (sharing context)

**Timing:**
- Sessions > 2 hours: Recommended
- Before major breaks: Essential
- Complex workflows: Every phase completion

---

## Basic Usage

Generate handoff for current session:

```
/handoff
```

**What happens:**
1. Analyzes current session state
2. Extracts workflow progress
3. Captures decision context (WHY you made choices)
4. Prioritizes remaining work (P1/P2/P3)
5. Includes governance and performance metrics
6. Auto-detects confidence level
7. Saves to `.claude/whats-next.md` and archives

**Output:**
```markdown
## Session Handoff

**Session**: session-20251116-143022
**Started**: 2025-11-16 14:30
**Duration**: 4h 15m
**Status**: 🟢 High Confidence

---

## Original Task

**Title**: Build Product Catalog UI
**Priority**: 🔴 High
**Workflow**: full-stack-feature

Create responsive product catalog with filters, search, and pagination.
Support 1000+ products with good performance.

---

## Session Summary

**Key Decisions Made:**
- Chose PostgreSQL array types for product tags (better query performance than JSON)
- React Query for API caching with 5min stale time (balance freshness/performance)
- Filter state in URL params for shareable links
- Pagination set to 50 items/page (UX testing showed optimal)

**Critical Insights:**
- Backend API already handles sorting, don't duplicate in frontend
- Product images need lazy loading (performance issue discovered)
- Search debouncing at 300ms feels responsive (tested)

**Conversation Highlights:**
Spent first hour on architecture decisions (API design, state management).
Implemented core components mid-session. Discovered performance issue with
images late in session, added to todos for next session.

---

## Progress Summary

**Overall**: 5 of 8 agents complete (62%)

✅ frontend-architect
✅ database-architect
✅ backend-architect
✅ python-expert
✅ ui-components-expert
🔄 frontend-developer (Next - 60% complete)
⏳ qc-automation-expert
⏳ deployment-integration-expert

---

## Work Completed

**Completed Items:**
- ✅ Designed component architecture
- ✅ Created database schema with indexes
- ✅ Built REST API endpoints (/products, /search, /filter)
- ✅ Implemented ProductCard, FilterBar, SearchBox components

**Files Modified:**
- `src/components/ProductCard.tsx`: Created product card with image, price, tags
- `src/components/FilterBar.tsx`: Filter UI with category, price range, tags
- `src/api/products.py`: REST endpoints with pagination, sorting, filtering
- `database/schema.sql`: Product table with GIN index on tags array

**Agent Outputs:**
- **frontend-architect**: Component tree, state flow diagram, routing structure
- **database-architect**: Schema with indexes, migration scripts
- **backend-architect**: API spec (OpenAPI), caching strategy
- **python-expert**: Optimized queries with SQLAlchemy, bulk loading
- **ui-components-expert**: Responsive components with Tailwind CSS

---

## Next Steps

**PRIORITY 1 (Critical Path):**
- 🔴 Complete ProductList container component (ties everything together)
- 🔴 Implement lazy loading for product images (performance blocker)

**PRIORITY 2 (High Value):**
- 🟡 Add loading states and error boundaries
- 🟡 Implement pagination controls

**PRIORITY 3 (Nice to Have):**
- 🟢 Add sorting options (name, price, date)
- 🟢 Add filter presets (e.g., "On Sale", "New Arrivals")

**Dependencies:**
- QA testing depends on ProductList completion
- Deployment depends on QA passing

---

## Active Context

**Most Relevant Right Now:**
- 💡 ProductList needs virtualization for 1000+ products (react-window library)
- 💡 Images hosted on CDN, use srcset for responsive loading
- 💡 Filter state structure: `{ category: string[], priceRange: [min, max], tags: string[] }`

**Known Blockers:**
- ⚠️ CDN access not yet configured for images
  - Mitigation: Use placeholder images for development, add todo for ops

**Open Questions:**
- ❓ Should we pre-load next page of results? (UX vs bandwidth trade-off)
- ❓ Real-time stock updates or polling? (need product owner input)

---

## Quality Status

**Last Validation**: ✅ All Checks Pass

- Scorecard: 12/12 ✅
- Write Zone: Updated ✅
- Secrets: None detected ✅
- Format: Valid ✅

---

## Cost & Performance

💰 **Total Cost**: $2.45
⏱️ **Execution Time**: 4h 15m
🤖 **Agents Run**: 5 of 8
📊 **Tokens Used**: 45,230 tokens
📈 **Context Window**: 35.2% used

---

## Technical Context

Key decisions and gotchas:
- Using PostgreSQL array types for tags (better than JSONB for this use case)
- React Query configured with `staleTime: 300000` (5 minutes)
- Filter state managed in URL params: `?category=electronics&priceMin=100&priceMax=500`
- API pagination: limit/offset (consider cursor-based if performance issues)
- Image CDN URLs follow pattern: `${CDN_BASE}/products/${productId}/${size}.webp`
- Frontend validation matches backend (shared validation lib recommended)

---

## To Resume

**To Resume This Session:**

1. **Review this handoff** - Read session summary and active context above
2. **Start with**: Complete ProductList container component (PRIORITY 1)
3. **Continue workflow**: `/run-agent frontend-developer` (will resume from 60%)
4. **After frontend**: Run `/run-agent qc-automation-expert` for testing
5. **Validate**: Run `/validate-output` before proceeding to deployment

**Quick Start Command**:
```
/run-agent frontend-developer
```

---

**Generated**: 2025-11-16 18:45:22
**Saved to**: `.claude/handoffs/handoff-2025-11-16-184522.md`
```

---

## Save to Custom Location

```
/handoff --save ~/project-handoffs/feature-catalog.md
```

**Output:**
```
✅ Handoff generated
📄 Saved to: /home/user/project-handoffs/feature-catalog.md
📄 Also saved to: .claude/whats-next.md (for easy access)
```

---

## Load Previous Handoff

Resume from a previous session:

```
/handoff --load
```

**Output:**
```
📂 Available handoffs:

Recent:
  [1] handoff-2025-11-16-184522.md (4 hours ago)
  [2] handoff-2025-11-16-103015.md (8 hours ago)
  [3] handoff-2025-11-15-170033.md (yesterday)

Archive:
  [4] Browse archive...

Select handoff to load (1-4) or [0] to cancel:
```

**After selecting:**
```
📋 Loaded handoff from: 2025-11-16 18:45

Session: Build Product Catalog UI
Progress: 5 of 8 agents (62%)
Status: 🟢 High Confidence

Next Steps:
1. Complete ProductList container component
2. Implement lazy loading for images
3. Continue with frontend-developer agent

💡 Ready to resume? Run: /run-agent frontend-developer
```

---

## Auto-Handoff Mode

Automatic handoffs at intervals:

```
/handoff --auto
```

**What happens:**
- Monitors session duration
- Auto-generates handoff every 2 hours
- Alerts when approaching context limit
- Suggests handoff at natural breakpoints

**Output:**
```
🤖 Auto-handoff enabled

Will generate handoff:
  ⏰ Every 2 hours
  📊 When context > 80% full
  🎯 At workflow phase completions

Current session: 1h 15m (next handoff in 45m)

To disable: /handoff --auto-off
```

---

## Handoff Structure

Handoffs include:

### 1. Session Metadata
- Session ID, start time, duration
- Confidence level (High/Medium/Low)
- Status indicator

### 2. Session Summary (WHY)
- **Key Decisions**: Major choices made and rationale
- **Critical Insights**: Important discoveries
- **Conversation Highlights**: Flow of the session

### 3. Progress
- Workflow status (if applicable)
- Agent execution summary
- Completion percentage

### 4. Work Completed
- Completed items with details
- Files modified with descriptions
- Agent outputs summary

### 5. Work Remaining (Priority Ordered)
- **P1 Critical**: Blocks everything else
- **P2 High**: Important but not blocking
- **P3 Nice to Have**: Can be deferred
- Dependencies mapped

### 6. Active Context (for AI)
- **Most Relevant**: Top 2-3 critical facts
- **Known Blockers**: Issues with mitigations
- **Open Questions**: Unresolved decisions

### 7. Quality Status
- Validation results
- Scorecard summary
- Governance compliance

### 8. Performance Metrics
- Total cost
- Execution time
- Token usage
- Context window usage

### 9. Technical Context
- Design decisions with rationale
- Gotchas and non-obvious behaviors
- Configuration details

### 10. Resume Instructions
- Specific next steps
- Commands to run
- What to review first

---

## Confidence Levels

Handoffs auto-detect confidence based on completeness:

**🟢 High Confidence**
- Clear original task
- Work completed documented
- Work remaining prioritized
- Active context defined
- Governance passed

**🟡 Medium Confidence**
- Some context missing
- Work remaining not fully prioritized
- Some gaps in documentation

**🔴 Low Confidence**
- Missing critical context
- Work remaining unclear
- Governance issues
- Recommend additional documentation

---

## Best Practices

### When to Generate Handoffs

**Always:**
- Before ending work session
- Before switching tasks
- After completing workflow phase
- When context window > 80%

**Consider:**
- Every 2-4 hours for long sessions
- Before major architectural decisions
- When sharing work with team

### What Makes a Good Handoff

**Capture WHY, not just WHAT:**
- ✅ "Chose PostgreSQL arrays because faster queries for tag filtering"
- ❌ "Using PostgreSQL arrays"

**Prioritize Work:**
- ✅ "P1: Complete ProductList (blocks QA). P2: Add loading states."
- ❌ "Need to finish ProductList and loading states"

**Active Context:**
- ✅ "ProductList needs virtualization (1000+ products, use react-window)"
- ❌ "ProductList not done"

**Technical Gotchas:**
- ✅ "Filter state in URL: `?category=X&priceMin=Y` - matches API params"
- ❌ "Filters work"

---

## Use Cases

### Use Case 1: Long Session Break

```
# After 4 hours of work
/handoff

# Next day
/handoff --load    # Select yesterday's handoff
/status           # Verify current state
/run-agent [next-agent]
```

### Use Case 2: Team Handoff

```
# Developer A finishing work
/handoff --save team-handoffs/catalog-feature.md

# Developer B starting
/handoff --load
# Read handoff
/run-agent [next-agent]
```

### Use Case 3: Context Window Management

```
# Context at 85%
⚠️ Context window high (85%) - recommend handoff

/handoff
# Session state preserved

# Start fresh context
/new-task    # Load next task
# Previous work context available in handoff
```

### Use Case 4: Multi-Day Project

```
# Day 1 EOD
/handoff

# Day 2 Start
/handoff --load
# Review decisions and context
/run-workflow [continue]

# Day 2 EOD
/handoff    # Cumulative progress
```

---

## Integration with Other Commands

### Workflow Integration

```
/run-workflow full-stack-feature
# ... workflow runs ...
# Phase 1 complete
/handoff    # Capture phase 1 state
# ... continue workflow ...
```

### Status Integration

```
/status     # Check current progress
/handoff    # Generate detailed handoff
```

### Todo Integration

```
/handoff    # Generate handoff
# Review "Open Questions"
# Add questions as todos
/todos --add "Decide on real-time stock updates strategy"
```

---

## Advanced Features

### Handoff Comparison

```
/handoff --compare handoff-2025-11-15.md handoff-2025-11-16.md
```

Shows progress delta between sessions.

### Handoff Templates

Create custom handoff templates:

```
/handoff --template minimal    # Brief format
/handoff --template detailed   # Full format (default)
/handoff --template team       # Team-focused format
```

### Export Formats

```
/handoff --format markdown    # Default
/handoff --format pdf         # PDF export
/handoff --format json        # Structured data
```

---

## Troubleshooting

**Issue**: "No active session to handoff"
**Solution**: Handoff requires active task. Run `/new-task` first.

**Issue**: "Handoff confidence is LOW"
**Solution**: Add more context manually:
- Review session summary
- Define work remaining priorities
- Document technical decisions

**Issue**: "Cannot load handoff"
**Solution**: Check file exists in `.claude/handoffs/`. Verify format is valid.

**Issue**: "Handoff file too large"
**Solution**: Archive old handoffs. Use `--template minimal` for large sessions.

---

## Files

- **Current**: `.claude/whats-next.md` - Latest handoff (easy to find)
- **Archive**: `.claude/handoffs/handoff-YYYY-MM-DD-HHMMSS.md` - All handoffs
- **Custom**: Any path specified with `--save`

---

## Tips

**Auto-Archive**
- Handoffs automatically saved with timestamps
- Easy to track project history
- Compare progress over time

**Session Continuity**
- Always read previous handoff before resuming
- Update handoff if plans change mid-session
- Use handoffs for retrospectives

**Context Compression**
- Handoffs summarize without losing critical info
- Focus on WHY and decisions, not implementation details
- AI can expand from handoff when needed

**Team Collaboration**
- Share handoffs for seamless collaboration
- Include enough context for others to continue
- Document assumptions and constraints

---

**Last Updated**: 2025-11-16
