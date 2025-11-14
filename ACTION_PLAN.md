# P1 Enhancements - Action Plan
**Based on:** MULTI_PERSPECTIVE_REVIEW.md
**Created:** 2025-11-14
**Status:** ACTIVE

---

## 📋 Executive Summary

This action plan addresses the 10 priority items identified in the multi-perspective review to move claude-force from "production-ready for internal use" to "public launch ready."

**Timeline:** 3-4 weeks
**Effort:** ~15 days of work
**Risk Level:** LOW (all items are enhancements, no breaking changes)

---

## 🎯 Phase 1: Critical Items (P0) - Week 1-2

### P0-1: Plugin Signature Verification
**Priority:** CRITICAL
**Blocker for:** Public marketplace launch
**Timeline:** 1.5 weeks (7 working days)
**Complexity:** HIGH

**Scope:**
```
1. Design plugin signature system
   - Use GPG/PGP signatures for plugin packages
   - Create trusted publisher registry
   - Define signature verification flow

2. Implement verification in marketplace.py
   - Add signature checking before install
   - Create --trust flag for development/testing
   - Add verification bypass for builtin plugins

3. Create signing tools
   - claude-force sign-plugin <plugin-dir>
   - Auto-sign during contribution preparation
   - Key management documentation

4. Testing
   - Test with signed plugins
   - Test rejection of unsigned plugins
   - Test --trust flag functionality
```

**Files to modify:**
- `claude_force/marketplace.py` - Add verification logic
- `claude_force/contribution.py` - Add signing during preparation
- `claude_force/cli.py` - Add sign-plugin command
- `tests/test_marketplace.py` - Add signature tests

**Acceptance Criteria:**
- [ ] Unsigned plugins rejected by default
- [ ] --trust flag allows unsigned plugins
- [ ] Signing tool available in CLI
- [ ] Documentation for plugin publishers
- [ ] 100% test coverage for signature paths

**Dependencies:**
- `cryptography` library for signing
- GPG keyring for publisher keys

---

### P0-2: Onboarding Wizard
**Priority:** CRITICAL
**Blocker for:** User adoption
**Timeline:** 1 week (5 working days)
**Complexity:** MEDIUM

**Scope:**
```
1. Create interactive wizard command
   - claude-force wizard
   - Step-by-step guided setup
   - Collects: project type, goals, preferences

2. Smart defaults based on user input
   - Recommend template
   - Pre-select agents
   - Configure workflows

3. Progressive disclosure in help system
   - Group commands by skill level
   - Beginner / Intermediate / Advanced
   - Filter help output by level

4. Quick start tutorial
   - claude-force tour
   - Interactive walkthrough
   - Sample project creation
```

**Files to create:**
- `claude_force/wizard.py` - Wizard orchestration
- `claude_force/tour.py` - Interactive tutorial

**Files to modify:**
- `claude_force/cli.py` - Add wizard and tour commands
- Group help commands by level

**Acceptance Criteria:**
- [ ] Wizard reduces setup time by 50%
- [ ] Help output less overwhelming (grouped)
- [ ] Tour completes in <5 minutes
- [ ] New user can complete wizard without docs
- [ ] Test coverage >80%

**User Flow:**
```bash
$ claude-force wizard

🎯 Welcome to claude-force! Let's set up your project.

What type of project are you building?
  1. Web Application (React/Vue/Angular)
  2. API/Backend Service
  3. Data Pipeline
  4. Machine Learning
  5. Other

> 1

Great! I'll set up a web application project.

What's your primary goal?
  - Fast prototyping
  - Production-ready code
  - Learning/Experimentation

> Fast prototyping

Perfect! I recommend:
  ✓ Template: react-spa-starter
  ✓ Agents: frontend-architect, ui-designer
  ✓ Model: claude-haiku (fast & cheap)

Proceed with setup? [Y/n]
```

---

## 🔧 Phase 2: Important Items (P1) - Week 3-4

### P1-1: Refactor MarketplaceManager
**Priority:** IMPORTANT
**Blocker for:** Future maintainability
**Timeline:** 3 days
**Complexity:** MEDIUM

**Current Issue:**
```
marketplace.py MarketplaceManager: 500+ lines, 5+ responsibilities
- Plugin discovery
- Installation/uninstallation
- Dependency resolution
- Version management
- Source management
```

**Refactoring Plan:**
```
Split into 3 classes:

1. PluginRegistry
   - Discovery and metadata
   - Search and filtering
   - Source management

2. PluginInstaller
   - Installation/uninstallation
   - File operations
   - Post-install hooks

3. DependencyResolver
   - Dependency graph building
   - Resolution algorithms
   - Conflict detection

MarketplaceManager becomes orchestrator:
   - Delegates to specialized classes
   - Maintains backward compatibility
   - Public API unchanged
```

**Files to create:**
- `claude_force/plugin_registry.py`
- `claude_force/plugin_installer.py`
- `claude_force/dependency_resolver.py`

**Files to modify:**
- `claude_force/marketplace.py` - Refactor to use new classes
- `tests/test_marketplace.py` - Update tests

**Acceptance Criteria:**
- [ ] All existing tests pass
- [ ] No breaking API changes
- [ ] Each class <200 lines
- [ ] Cyclomatic complexity <10 per method
- [ ] Test coverage maintained at 100%

---

### P1-2: Template Indexing
**Priority:** IMPORTANT
**Blocker for:** Scaling to 100+ templates
**Timeline:** 2 days
**Complexity:** LOW-MEDIUM

**Current Issue:**
```
template_gallery.py: O(n) linear search
Performance:
  20 templates: <100ms ✅
  100 templates: ~300ms ⚠️
  500+ templates: >1s 🔴
```

**Solution:**
```
1. Create template index
   - SQLite database for metadata
   - Pre-computed keyword hashes
   - Full-text search support

2. Index structure
   - Templates table: id, name, description, category
   - Keywords table: template_id, keyword, weight
   - Index on keywords for fast lookup

3. Build index on startup
   - Lazy loading with caching
   - TTL: 5 minutes
   - Auto-rebuild on template changes

4. Fallback to linear search
   - If index unavailable
   - Graceful degradation
```

**Files to create:**
- `claude_force/template_index.py`

**Files to modify:**
- `claude_force/template_gallery.py` - Use index for search
- `tests/test_template_gallery.py` - Performance tests

**Acceptance Criteria:**
- [ ] Search <100ms for 100 templates
- [ ] Search <200ms for 500 templates
- [ ] Graceful fallback if index fails
- [ ] Index auto-rebuilds on changes
- [ ] Performance benchmarks in tests

**Performance Target:**
```
Before: O(n) = 300ms for 100 templates
After:  O(log n) = <100ms for 100 templates
Improvement: 3x faster
```

---

### P1-3: Centralized Logging Configuration
**Priority:** IMPORTANT
**Blocker for:** Production debugging
**Timeline:** 1 day
**Complexity:** LOW

**Current Issue:**
```
Each module: logger = logging.getLogger(__name__)
No central configuration
Can't change log level without code changes
```

**Solution:**
```
1. Create logging.yaml config
   - Define log levels per module
   - Configure formatters and handlers
   - Support multiple outputs

2. Add CLI flags
   --log-level=DEBUG|INFO|WARNING|ERROR
   --log-file=<path>
   --log-format=json|text

3. Environment variable support
   CLAUDE_FORCE_LOG_LEVEL
   CLAUDE_FORCE_LOG_FILE

4. Default configuration
   - Console: INFO level
   - File: DEBUG level (if --log-file)
   - Structured logging (JSON) option
```

**Files to create:**
- `claude_force/logging_config.yaml`
- `claude_force/logging_setup.py`

**Files to modify:**
- `claude_force/cli.py` - Add global logging flags
- All modules - Use centralized config

**Example Configuration:**
```yaml
version: 1
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter

handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    level: INFO
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /var/log/claude-force.log
    formatter: json
    level: DEBUG
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  claude_force:
    level: INFO
    handlers: [console]
  claude_force.marketplace:
    level: DEBUG
```

**Acceptance Criteria:**
- [ ] Single config file for all logging
- [ ] CLI flags work correctly
- [ ] Environment variables respected
- [ ] Log rotation configured
- [ ] JSON format option available

---

## 📊 Phase 3: Nice to Have (P2) - Backlog

### P2-1: Workflow Checkpointing
**Timeline:** 3 days
**Value:** Resume failed workflows

### P2-2: Event System
**Timeline:** 4 days
**Value:** Plugin extensibility

### P2-3: Version Migration
**Timeline:** 2 days
**Value:** Smooth upgrades

### P2-4: Progress Indicators
**Timeline:** 2 days
**Value:** Better UX

### P2-5: Performance Tests
**Timeline:** 2 days
**Value:** Prevent regressions

---

## 📅 Detailed Timeline

### Week 1: P0-1 (Plugin Security)
```
Day 1-2: Design signature system
  - Research GPG/PGP options
  - Design key management
  - Write technical spec

Day 3-4: Implement verification
  - Modify marketplace.py
  - Add signature checking
  - Create --trust flag

Day 5-6: Implement signing tools
  - Add sign-plugin command
  - Update contribution.py
  - Write documentation

Day 7: Testing & documentation
  - Write comprehensive tests
  - Update user docs
  - Code review
```

### Week 2: P0-2 (Onboarding)
```
Day 1-2: Wizard implementation
  - Create wizard.py
  - Interactive prompts
  - Template selection logic

Day 3: Tour implementation
  - Create tour.py
  - Sample project setup
  - Interactive walkthrough

Day 4: Help system refactoring
  - Group commands by level
  - Update help text
  - Progressive disclosure

Day 5: Testing & polish
  - User testing
  - Fix UX issues
  - Documentation
```

### Week 3: P1-1 & P1-2
```
Day 1-3: MarketplaceManager refactor
  - Create PluginRegistry
  - Create PluginInstaller
  - Create DependencyResolver
  - Update tests

Day 4-5: Template indexing
  - Create template_index.py
  - Build SQLite index
  - Performance benchmarks
```

### Week 4: P1-3 & Launch Prep
```
Day 1: Centralized logging
  - Create logging config
  - Update all modules
  - Test integration

Day 2-3: Integration testing
  - End-to-end tests
  - Performance validation
  - Security audit

Day 4-5: Launch preparation
  - Update documentation
  - Create release notes
  - Marketing materials
```

---

## 🎯 Success Metrics

### P0 Completion Metrics
- [ ] All unsigned plugins rejected (0 bypasses without --trust)
- [ ] New user setup time <10 minutes (down from ~30 min)
- [ ] Wizard completion rate >80%
- [ ] Zero security vulnerabilities in audit

### P1 Completion Metrics
- [ ] MarketplaceManager complexity <8 (down from 12)
- [ ] Template search <100ms for 100 templates (3x improvement)
- [ ] Log level changes without code modification
- [ ] All tests pass (331+)

### Overall Project Health
- [ ] Test coverage >85%
- [ ] Maintainability Index >80
- [ ] Zero critical bugs
- [ ] Documentation complete

---

## 🚧 Risk Mitigation

### Risk 1: Signature System Complexity
**Impact:** HIGH
**Probability:** MEDIUM
**Mitigation:**
- Start with simple GPG signatures
- Use existing libraries (cryptography, gnupg)
- Provide clear key management docs
- Fallback to --trust flag for development

### Risk 2: Breaking Changes During Refactor
**Impact:** HIGH
**Probability:** LOW
**Mitigation:**
- Maintain backward compatibility
- Extensive test coverage before changes
- Feature flags for gradual rollout
- Rollback plan ready

### Risk 3: Performance Regression
**Impact:** MEDIUM
**Probability:** LOW
**Mitigation:**
- Add performance benchmarks
- Test with large template sets
- Monitor execution time in CI
- Graceful degradation if index fails

---

## 📦 Deliverables

### P0 Phase
1. Plugin signature verification system
2. Signing tools and documentation
3. Onboarding wizard (`claude-force wizard`)
4. Interactive tour (`claude-force tour`)
5. Improved help system (grouped commands)
6. Security audit report

### P1 Phase
1. Refactored marketplace (3 classes)
2. Template indexing system
3. Centralized logging configuration
4. Performance benchmarks
5. Updated documentation

### Launch Phase
1. Release notes
2. Migration guide
3. Public documentation site
4. Demo videos
5. Launch announcement

---

## 👥 Resource Requirements

**Engineering:**
- 1 developer (full-time, 3-4 weeks)
- Code review support

**Security:**
- 1 security reviewer (2 days for audit)

**Documentation:**
- Technical writer (3 days for public docs)

**Optional:**
- UX designer (2 days for wizard flow)
- DevOps (1 day for deployment setup)

---

## ✅ Approval Checklist

### Before Starting P0
- [x] Action plan reviewed
- [ ] Timeline approved
- [ ] Resources allocated
- [ ] Dependencies identified

### Before Starting P1
- [ ] P0 items completed
- [ ] Security audit passed
- [ ] User testing completed
- [ ] No blocking bugs

### Before Public Launch
- [ ] All P0+P1 items completed
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] Security sign-off
- [ ] Marketing ready

---

## 📞 Status Updates

**Weekly standup format:**
```
Completed this week:
- [List completed items]

In progress:
- [Current work]

Blockers:
- [Any issues]

Next week:
- [Planned work]

Metrics:
- Tests passing: X/331
- Code coverage: X%
- Performance: X ms
```

---

## 🎉 Launch Readiness Criteria

### Technical Readiness
- [ ] All P0 items complete
- [ ] All P1 items complete
- [ ] 100% test pass rate
- [ ] Performance targets met
- [ ] Security audit approved

### Documentation Readiness
- [ ] User guide complete
- [ ] API documentation updated
- [ ] Plugin developer guide
- [ ] Video tutorials created
- [ ] FAQ published

### Operational Readiness
- [ ] Monitoring configured
- [ ] Error tracking setup
- [ ] Backup/restore tested
- [ ] Rollback plan ready
- [ ] Support process defined

### Marketing Readiness
- [ ] Launch announcement written
- [ ] Demo prepared
- [ ] Screenshots/videos ready
- [ ] Social media plan
- [ ] Press kit available

---

**Status:** READY TO START
**Next Action:** Create tracking issues for P0/P1 items
**Owner:** Development team
**Target Launch:** 4 weeks from start date
