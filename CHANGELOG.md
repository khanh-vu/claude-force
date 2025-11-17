# Changelog

All notable changes to claude-force will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-17

### Added

#### TÂCHES Workflow Management Integration

- **Todo Management System** (`/todos` command)
  - AI-optimized task capture with smart fields (why it matters, success criteria, required capabilities)
  - Automatic agent recommendations via semantic matching
  - Duplicate detection with similarity scoring
  - Priority and complexity tracking
  - Archive management for completed tasks
  - Hash-based cache invalidation for performance
  - File locking for concurrent access safety

- **Session Handoff System** (`/handoff` command)
  - Comprehensive session state capture
  - Priority-ordered work classification (P1/P2/P3)
  - Active context tracking for continuity
  - Auto-confidence level detection (High/Medium/Low)
  - Governance status integration
  - Performance metrics aggregation
  - Handoff archival with timestamps

- **Meta-Prompting System** (`/meta-prompt` command)
  - LLM-powered workflow generation
  - Iterative refinement with convergence detection (up to 3 iterations)
  - 4-checkpoint governance validation (agent availability, budget, skills, safety)
  - Success criteria definition
  - Risk assessment and mitigation
  - Alternative approach consideration
  - Structured XML I/O for Claude API

#### Data Models (1,080 lines)

- `TodoItem` model with AI-optimized fields, enums, and markdown serialization
- `Handoff` model with session metadata and priority work tracking
- `MetaPrompt` request/response models with governance compliance

#### Service Layer (1,300 lines)

- `TodoManager` service with CRUD operations, agent recommendations, and caching
- `HandoffGenerator` service with session extraction and confidence detection
- `MetaPrompter` service with LLM integration and governance validation

#### Orchestrator Integration

- Lazy-loaded service properties: `todos`, `handoffs`, `meta_prompt`
- Helper methods: `get_available_skills()`, `get_agent_info()`
- Seamless integration with existing orchestrator architecture

#### Testing (1,000+ lines, 70+ tests)

- `test_todo_manager.py` - 35 comprehensive tests
- `test_handoff_generator.py` - 20 tests for handoff generation
- `test_meta_prompter.py` - 25 tests for meta-prompting and governance

#### Documentation (3,000+ lines)

- `docs/architecture/TACHES_ARCHITECTURE.md` - Complete technical architecture
- `TACHES_IMPLEMENTATION_COMPLETE.md` - Implementation summary
- `EXPERT_REVIEW_SUMMARY.md` - Expert review feedback
- `RELEASE_NOTES_v1.1.0.md` - Comprehensive release notes
- Command documentation for all three new slash commands

### Fixed

- **Critical Fixes**
  - Removed duplicate `get_agent_info()` method in orchestrator.py
  - Implemented real LLM integration in MetaPrompter (was placeholder)
  - Fixed archive file race condition with fcntl file locking
  - Enhanced all exception handlers with logging (8 handlers updated)

- **Important Improvements**
  - Implemented `Handoff.from_markdown()` with clear NotImplementedError and helpful message
  - Added validation to `TodoItem.from_markdown()` parser
  - Path traversal security checks in todo file paths
  - Required field validation (action cannot be empty)

- **Performance**
  - Enhanced cache invalidation strategy (size + mtime + content hash)
  - Prevents stale cache data for rapid successive writes
  - File locking prevents data corruption from concurrent access

- **Code Quality**
  - Fixed all ruff lint errors (unused imports, forward references)
  - Formatted all code with black formatter
  - Added TYPE_CHECKING imports for circular import prevention
  - Improved type hints throughout codebase

### Changed

- Cache key generation now uses hash-based approach instead of mtime-only
- Exception handlers now log warnings/debug messages instead of silent failures
- Service layer uses lazy loading pattern for better performance

### Security

- Path validation prevents path traversal attacks in todo file paths
- Input validation in all markdown parsers
- Secure file locking implementation with fcntl

## [1.0.0] - 2025-11-15

### Bug Fixes

- Replace invalid --no-cov flag with -p no:cov in workflows (71d0780)
- Use API token auth for PyPI, add tag fetching for changelog (f41acdf)
- Add PyYAML dependency for template parsing (a25c13b)
- Replace pypa action with direct twine upload to avoid OIDC (49e4de6)
- Replace pypa action with direct twine upload to avoid OIDC (8e90450)
- Install git-cliff directly instead of using outdated action (eb7fd26)
- Remove commit.link from changelog template to fix rendering error (ade66c3)
- Resolve API key and timing issues in async orchestrator tests (4adbce3)
- Add issues:write permission for post-release announcements (dee01e9)

### Documentation

- Update CHANGELOG with PyYAML dependency fix (be512c5)
- Add expert review of release workflow (1704a33)
- Add comprehensive PR documentation (c79bc04)
- Update changelog for v1.0.0 (25bce96)
- Update changelog for v1.0.0 (89fc389)

### Miscellaneous Tasks

- Update release metrics report (3ea01f2)
- Update release metrics report (fc0bd0d)
- Update release metrics report (5929e99)
- Update release metrics report (9bdb963)
- Update release metrics report (fb27368)
- Update release metrics report (b4c9793)
- Update release metrics report (6aaaf28)
- Update release metrics report (111abe1)
- Update release metrics report (2fe082c)
- Update release metrics report (bc26f4d)
- Update release metrics report (9a403cc)
- Update release metrics report (951d7a4)
- Update release metrics report (55bea49)
- Update release metrics report (414e82e)
- Update release metrics report (9c4b971)
- Update release metrics report (30815a9)
- Bump version to 1.0.0 for initial release (7cc7bf1)

### Testing

- Add comprehensive fresh installation test suite (eb2f738)

<!-- generated by git-cliff -->
