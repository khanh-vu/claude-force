# Issues Tracker - P0/P1 Action Items
**Project:** claude-force
**Based on:** MULTI_PERSPECTIVE_REVIEW.md + ACTION_PLAN.md
**Created:** 2025-11-14

---

## 🔴 P0: Critical (Before Public Launch)

### Issue #1: Plugin Signature Verification System
**Priority:** P0 (CRITICAL)
**Status:** 🟡 TODO
**Assignee:** TBD
**Labels:** security, marketplace, blocker
**Milestone:** Public Launch
**Estimated Effort:** 7 days

**Description:**
Implement GPG/PGP-based signature verification for marketplace plugins to prevent supply chain attacks and ensure plugin integrity.

**Problem Statement:**
Currently, plugins can be installed from external sources without any verification of their authenticity or integrity. This creates a security risk where malicious actors could distribute compromised plugins.

**Acceptance Criteria:**
- [ ] Unsigned plugins are rejected by default
- [ ] `--trust` flag allows unsigned plugins for development
- [ ] `claude-force sign-plugin <plugin-dir>` command available
- [ ] Signature verification integrated into install flow
- [ ] Documentation for plugin publishers on signing process
- [ ] Test coverage >95% for all signature code paths
- [ ] Security audit completed and approved

**Technical Approach:**
```python
# 1. Add to marketplace.py
class PluginSignature:
    def verify(plugin_path: str, signature_path: str) -> bool:
        # Verify GPG signature
        pass

# 2. Modify install flow
def install_plugin(plugin_id: str, trust: bool = False):
    if not trust and not verify_signature(plugin_path):
        raise SecurityError("Plugin signature verification failed")
    # Continue installation
```

**Files to Modify:**
- `claude_force/marketplace.py`
- `claude_force/contribution.py`
- `claude_force/cli.py`
- `tests/test_marketplace.py`
- `tests/test_contribution.py`

**Dependencies:**
- `cryptography>=41.0.0`
- `python-gnupg>=0.5.0`

**Related Issues:** None
**Blocks:** Public marketplace launch
**References:**
- [NPM package signing](https://docs.npmjs.com/about-package-signatures)
- [PyPI PGP signatures](https://pypi.org/help/#pgp)

---

### Issue #2: Onboarding Wizard for New Users
**Priority:** P0 (CRITICAL)
**Status:** 🟡 TODO
**Assignee:** TBD
**Labels:** ux, cli, enhancement, blocker
**Milestone:** Public Launch
**Estimated Effort:** 5 days

**Description:**
Create an interactive wizard to guide new users through initial setup, reducing onboarding time from ~30 minutes to <10 minutes.

**Problem Statement:**
New users face overwhelming choice when running `claude-force --help` (25+ commands). No guided setup process leads to:
- High drop-off during onboarding
- Users unsure which commands to run first
- Suboptimal configuration choices

**Acceptance Criteria:**
- [ ] `claude-force wizard` command implemented
- [ ] Interactive prompts for project type, goals, preferences
- [ ] Automatic template selection based on answers
- [ ] Pre-configured agents and workflows
- [ ] Setup time reduced by >50% (target: <10 minutes)
- [ ] `claude-force tour` interactive tutorial
- [ ] Help commands grouped by skill level (Beginner/Advanced)
- [ ] User testing with 5+ new users shows >80% completion rate

**User Flow:**
```
$ claude-force wizard

🎯 Welcome to claude-force! Let's set up your project.

Step 1/5: What type of project are you building?
  1. Web Application (React/Vue/Angular)
  2. API/Backend Service
  3. Data Pipeline
  4. Machine Learning
  5. Other

  [Navigation: ↑↓ arrows, Enter to select, q to quit]

> 1

Step 2/5: What's your primary goal?
  • Fast prototyping
  • Production-ready code
  • Learning/Experimentation

> Fast prototyping

Step 3/5: Choose your AI model preference:
  • claude-haiku (fastest, cheapest)
  • claude-sonnet (balanced, recommended)
  • claude-opus (highest quality)

> claude-sonnet

Step 4/5: Select agents for your project:
  ✓ frontend-architect (recommended)
  ✓ ui-designer (recommended)
  ☐ api-designer
  ☐ test-engineer

  [Space to toggle, Enter to continue]

Step 5/5: Summary
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Project type: Web Application
  Template: react-spa-starter
  Agents: frontend-architect, ui-designer
  Model: claude-sonnet
  Estimated setup time: 2 minutes
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Create project? [Y/n] y

✨ Creating your project...
  ✓ Initializing .claude/ directory
  ✓ Installing template: react-spa-starter
  ✓ Configuring agents
  ✓ Setting up workflows

🎉 Setup complete! Next steps:
  1. cd my-project
  2. claude-force run-agent frontend-architect "Create homepage"
  3. Try: claude-force tour (interactive tutorial)
```

**Technical Approach:**
```python
# New file: claude_force/wizard.py
class SetupWizard:
    def run(self):
        # Interactive prompts using questionary or PyInquirer
        project_type = self.prompt_project_type()
        goal = self.prompt_goal()
        model = self.prompt_model()
        agents = self.prompt_agents(project_type)

        # Generate config
        config = self.generate_config(project_type, goal, model, agents)

        # Execute setup
        self.create_project(config)
```

**Files to Create:**
- `claude_force/wizard.py` - Main wizard logic
- `claude_force/tour.py` - Interactive tutorial
- `claude_force/prompts.py` - Reusable prompt components

**Files to Modify:**
- `claude_force/cli.py` - Add wizard and tour commands
- Help text grouping by skill level

**Dependencies:**
- `questionary>=2.0.0` OR `PyInquirer>=1.0.3`
- `rich>=13.0.0` (for better formatting)

**Related Issues:** None
**Blocks:** User adoption
**References:**
- [Cargo init workflow](https://doc.rust-lang.org/cargo/guide/creating-a-new-project.html)
- [Create React App](https://create-react-app.dev/docs/getting-started/)

---

## 🟡 P1: Important (Next Sprint)

### Issue #3: Refactor MarketplaceManager (Too Many Responsibilities)
**Priority:** P1 (IMPORTANT)
**Status:** 🟡 TODO
**Assignee:** TBD
**Labels:** refactoring, technical-debt, architecture
**Milestone:** v2.1
**Estimated Effort:** 3 days

**Description:**
Split MarketplaceManager (500+ lines, 5 responsibilities) into 3 focused classes following Single Responsibility Principle.

**Problem Statement:**
`marketplace.py::MarketplaceManager` has grown to 500+ lines with cyclomatic complexity of 12 in `install_plugin()`. This violates SRP and makes the code:
- Hard to test (requires mocking many dependencies)
- Hard to maintain (changes ripple across responsibilities)
- Hard to extend (no clear extension points)

**Current Responsibilities:**
1. Plugin discovery and search
2. Installation/uninstallation
3. Dependency resolution
4. Version management
5. Source management

**Acceptance Criteria:**
- [ ] Create `PluginRegistry` class (discovery, metadata, search)
- [ ] Create `PluginInstaller` class (install/uninstall, file ops)
- [ ] Create `DependencyResolver` class (dependency graph, resolution)
- [ ] `MarketplaceManager` becomes orchestrator only
- [ ] All existing tests pass (331 tests, 100% rate)
- [ ] No breaking API changes (backward compatible)
- [ ] Each class <200 lines
- [ ] Cyclomatic complexity <10 per method
- [ ] Maintainability Index improved >85

**Technical Approach:**
```python
# New: plugin_registry.py
class PluginRegistry:
    """Handles plugin discovery and metadata."""
    def search(query: str) -> List[Plugin]
    def get_plugin(plugin_id: str) -> Plugin
    def list_sources() -> List[PluginSource]

# New: plugin_installer.py
class PluginInstaller:
    """Handles installation and file operations."""
    def install(plugin: Plugin) -> bool
    def uninstall(plugin_id: str) -> bool
    def verify_installation(plugin_id: str) -> bool

# New: dependency_resolver.py
class DependencyResolver:
    """Handles dependency resolution."""
    def resolve(plugin: Plugin) -> List[Plugin]
    def detect_conflicts(plugins: List[Plugin]) -> List[Conflict]
    def build_install_order(plugins: List[Plugin]) -> List[Plugin]

# Modified: marketplace.py
class MarketplaceManager:
    """Orchestrates plugin operations."""
    def __init__(self):
        self.registry = PluginRegistry()
        self.installer = PluginInstaller()
        self.resolver = DependencyResolver()

    def install_plugin(self, plugin_id: str):
        plugin = self.registry.get_plugin(plugin_id)
        deps = self.resolver.resolve(plugin)
        for dep in deps:
            self.installer.install(dep)
        self.installer.install(plugin)
```

**Files to Create:**
- `claude_force/plugin_registry.py`
- `claude_force/plugin_installer.py`
- `claude_force/dependency_resolver.py`
- `tests/test_plugin_registry.py`
- `tests/test_plugin_installer.py`
- `tests/test_dependency_resolver.py`

**Files to Modify:**
- `claude_force/marketplace.py` - Refactor to use new classes
- `tests/test_marketplace.py` - Update to test orchestration

**Migration Plan:**
1. Create new classes with full test coverage
2. Gradually move code from MarketplaceManager
3. Update MarketplaceManager to delegate
4. Maintain public API compatibility
5. Deprecate old internal methods (keep for 1 release)

**Related Issues:** None
**Blocks:** Future scalability
**References:**
- MULTI_PERSPECTIVE_REVIEW.md Section 4.1

---

### Issue #4: Template Indexing for Fast Search
**Priority:** P1 (IMPORTANT)
**Status:** 🟡 TODO
**Assignee:** TBD
**Labels:** performance, enhancement, scalability
**Milestone:** v2.1
**Estimated Effort:** 2 days

**Description:**
Add SQLite-based indexing for template search to improve performance from O(n) to O(log n), targeting 3x speedup for 100+ templates.

**Problem Statement:**
Current template search is O(n) linear scan through all templates:
- 20 templates: <100ms ✅
- 100 templates: ~300ms ⚠️
- 500+ templates: >1000ms 🔴

This will become a bottleneck as the template gallery grows.

**Acceptance Criteria:**
- [ ] SQLite index for template metadata
- [ ] Full-text search on keywords
- [ ] Search <100ms for 100 templates (3x improvement)
- [ ] Search <200ms for 500 templates
- [ ] Index auto-rebuilds on template changes
- [ ] Graceful fallback to linear search if index unavailable
- [ ] Performance benchmarks in test suite
- [ ] No changes to public API

**Performance Targets:**
```
Before (O(n)):
- 20 templates: 80ms
- 100 templates: 300ms
- 500 templates: 1200ms

After (O(log n)):
- 20 templates: 50ms
- 100 templates: 90ms (3x faster)
- 500 templates: 180ms (6x faster)
```

**Technical Approach:**
```python
# New: template_index.py
class TemplateIndex:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._create_schema()

    def _create_schema(self):
        """
        CREATE TABLE templates (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            category TEXT
        );
        CREATE TABLE keywords (
            template_id TEXT,
            keyword TEXT,
            weight REAL,
            FOREIGN KEY(template_id) REFERENCES templates(id)
        );
        CREATE INDEX idx_keywords ON keywords(keyword);
        CREATE VIRTUAL TABLE templates_fts USING fts5(
            id, name, description, keywords
        );
        """

    def build_index(self, templates: List[Template]):
        """Populate index from templates."""

    def search(self, query: str) -> List[str]:
        """Fast search using index."""
        # Use FTS5 full-text search
        # Return template IDs ranked by relevance

# Modified: template_gallery.py
class TemplateGallery:
    def __init__(self):
        self.index = TemplateIndex()
        self._lazy_build_index()

    def search(self, query: str):
        try:
            # Try indexed search first
            return self.index.search(query)
        except Exception:
            # Fallback to linear search
            return self._linear_search(query)
```

**Files to Create:**
- `claude_force/template_index.py`
- `tests/test_template_index.py`
- `tests/performance/test_template_search_perf.py`

**Files to Modify:**
- `claude_force/template_gallery.py` - Use index
- `tests/test_template_gallery.py` - Add performance tests

**Dependencies:**
- SQLite3 (built-in, no new dependency)
- FTS5 extension (check availability, fallback if missing)

**Related Issues:** None
**Blocks:** Scaling to 100+ templates
**References:**
- [SQLite FTS5](https://www.sqlite.org/fts5.html)
- MULTI_PERSPECTIVE_REVIEW.md Section 3.1

---

### Issue #5: Centralized Logging Configuration
**Priority:** P1 (IMPORTANT)
**Status:** 🟡 TODO
**Assignee:** TBD
**Labels:** operations, logging, enhancement
**Milestone:** v2.1
**Estimated Effort:** 1 day

**Description:**
Create centralized logging configuration to enable runtime log level changes, structured logging, and better debugging in production.

**Problem Statement:**
Currently each module configures logging independently:
```python
logger = logging.getLogger(__name__)
```

Issues:
- Can't change log levels without code changes
- No structured logging option
- Hard to debug production issues
- No log rotation configuration

**Acceptance Criteria:**
- [ ] Single `logging_config.yaml` for all logging
- [ ] CLI flags: `--log-level`, `--log-file`, `--log-format`
- [ ] Environment variables: `CLAUDE_FORCE_LOG_LEVEL`, `CLAUDE_FORCE_LOG_FILE`
- [ ] JSON structured logging option
- [ ] Log rotation configured (10MB files, 5 backups)
- [ ] Backward compatible (existing code works unchanged)
- [ ] Documentation for log configuration

**Technical Approach:**
```yaml
# logging_config.yaml
version: 1
disable_existing_loggers: false

formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    stream: ext://sys.stdout
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
    propagate: false

  claude_force.marketplace:
    level: DEBUG
    handlers: [console, file]

root:
  level: WARNING
  handlers: [console]
```

```python
# New: logging_setup.py
import logging.config
import yaml
from pathlib import Path

def setup_logging(
    config_file: str = None,
    log_level: str = None,
    log_file: str = None,
    log_format: str = "text"
):
    """Configure logging from file and CLI overrides."""

    # Load base config
    if config_file:
        with open(config_file) as f:
            config = yaml.safe_load(f)
    else:
        config = _get_default_config()

    # Apply CLI overrides
    if log_level:
        config['loggers']['claude_force']['level'] = log_level.upper()

    if log_file:
        config['handlers']['file']['filename'] = log_file
        config['loggers']['claude_force']['handlers'].append('file')

    if log_format == "json":
        config['handlers']['console']['formatter'] = 'json'

    # Apply environment variable overrides
    import os
    if env_level := os.getenv('CLAUDE_FORCE_LOG_LEVEL'):
        config['loggers']['claude_force']['level'] = env_level.upper()

    logging.config.dictConfig(config)
```

**Files to Create:**
- `claude_force/logging_config.yaml`
- `claude_force/logging_setup.py`
- `tests/test_logging_setup.py`

**Files to Modify:**
- `claude_force/cli.py` - Add global logging flags
- `claude_force/__init__.py` - Initialize logging on import
- All modules - No changes needed (use existing `getLogger`)

**CLI Usage:**
```bash
# Set log level
claude-force --log-level=DEBUG list-agents

# Log to file
claude-force --log-file=/tmp/debug.log run-agent foo

# JSON format
claude-force --log-format=json --log-file=/var/log/cf.json run-workflow bar

# Environment variable
export CLAUDE_FORCE_LOG_LEVEL=DEBUG
claude-force list-agents
```

**Dependencies:**
- `python-json-logger>=2.0.0` (optional, for JSON format)
- `pyyaml>=6.0` (already required)

**Related Issues:** None
**Blocks:** Production debugging
**References:**
- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- MULTI_PERSPECTIVE_REVIEW.md Section 6.1

---

## 📋 P2: Nice to Have (Backlog)

### Issue #6: Workflow Checkpointing for Resume
**Priority:** P2
**Status:** 📝 BACKLOG
**Estimated Effort:** 3 days

**Description:**
Add workflow checkpointing to enable resuming failed workflows from the last successful step instead of restarting from the beginning.

**Value:** User can resume expensive multi-step workflows without re-running completed steps.

---

### Issue #7: Event System for Plugin Extensibility
**Priority:** P2
**Status:** 📝 BACKLOG
**Estimated Effort:** 4 days

**Description:**
Implement event bus architecture to allow plugins to react to system events (agent_started, workflow_completed, etc.).

**Value:** Enables plugin ecosystem to add analytics, logging, notifications without core changes.

---

### Issue #8: Version Migration System
**Priority:** P2
**Status:** 📝 BACKLOG
**Estimated Effort:** 2 days

**Description:**
Add schema versioning and migration system for .claude/claude.json config format changes.

**Value:** Smooth upgrades without breaking existing user setups.

---

### Issue #9: Progress Indicators for Long Operations
**Priority:** P2
**Status:** 📝 BACKLOG
**Estimated Effort:** 2 days

**Description:**
Add progress bars and spinners for multi-step operations (installation, workflows, etc.).

**Value:** Better UX, users know system isn't frozen.

---

### Issue #10: Performance Regression Tests
**Priority:** P2
**Status:** 📝 BACKLOG
**Estimated Effort:** 2 days

**Description:**
Add automated performance benchmarks to CI to catch regressions early.

**Value:** Maintain fast execution as codebase grows.

---

## 📊 Issue Status Summary

```
Total Issues: 10
  P0 (Critical): 2 🔴
  P1 (Important): 3 🟡
  P2 (Nice to Have): 5 🔵

Status Breakdown:
  TODO: 5
  IN PROGRESS: 0
  IN REVIEW: 0
  DONE: 0
  BACKLOG: 5

Estimated Total Effort: 20 days
  P0: 12 days
  P1: 6 days
  P2: 13 days (backlog)
```

---

## 🔄 Workflow

### Issue States
- 📝 **BACKLOG** - Planned but not started
- 🟡 **TODO** - Ready to start
- 🔵 **IN PROGRESS** - Actively being worked on
- 🟣 **IN REVIEW** - Code complete, awaiting review
- 🟢 **DONE** - Completed and merged
- 🔴 **BLOCKED** - Cannot proceed (dependency issue)

### Issue Lifecycle
```
BACKLOG → TODO → IN PROGRESS → IN REVIEW → DONE
                      ↓ (if blocked)
                    BLOCKED → IN PROGRESS
```

---

## 📝 Notes

- Issues are ordered by priority within each tier
- Estimated effort is for a single developer
- Some P1 items can be parallelized
- P2 items are nice-to-have, not required for launch
- Update issue status as work progresses
- Link to actual GitHub issues once created

---

**Last Updated:** 2025-11-14
**Next Review:** After P0 completion
